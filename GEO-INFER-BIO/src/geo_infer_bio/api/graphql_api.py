"""
GraphQL API for GEO-INFER-BIO.
"""
from typing import List, Optional, Dict, Any
import strawberry
from strawberry.fastapi import GraphQLRouter
from fastapi import FastAPI
import pandas as pd
from pathlib import Path
import tempfile

from ..core.sequence_analysis import SequenceAnalyzer
from ..utils.validation import DataValidator
from ..utils.visualization import BioVisualizer


@strawberry.type
class SpatialData:
    """Spatial data type."""
    latitude: float
    longitude: float


@strawberry.type
class SequenceData:
    """Sequence data type."""
    id: str
    sequence: str
    spatial_data: Optional[SpatialData] = None


@strawberry.type
class AnalysisResult:
    """Analysis result type."""
    sequence_id: str
    gc_content: float
    motif_count: int
    coding_regions: int
    spatial_data: Optional[SpatialData] = None


@strawberry.type
class VisualizationData:
    """Visualization data type."""
    gc_content: str
    motif_density: str
    coding_potential: str


@strawberry.type
class Query:
    """Query type."""
    @strawberry.field
    def analyze_sequence(self, sequence_data: SequenceData) -> AnalysisResult:
        """
        Analyze a single sequence.
        
        Args:
            sequence_data: Sequence data with optional spatial context
            
        Returns:
            Analysis results
        """
        analyzer = SequenceAnalyzer()
        validator = DataValidator()
        
        # Validate sequence
        if not validator.validate_sequence(sequence_data.sequence):
            raise ValueError("Invalid sequence")
        
        # Create SeqRecord
        from Bio.SeqRecord import SeqRecord
        from Bio.Seq import Seq
        record = SeqRecord(
            Seq(sequence_data.sequence),
            id=sequence_data.id,
        )
        
        # Add spatial data if provided
        if sequence_data.spatial_data:
            record.spatial_data = pd.DataFrame([{
                "latitude": sequence_data.spatial_data.latitude,
                "longitude": sequence_data.spatial_data.longitude,
            }])
        
        # Perform analysis
        gc_content = analyzer.calculate_gc_content(record.seq)
        motifs = analyzer.find_motifs(record.seq)
        coding_regions = analyzer.predict_coding_regions(record.seq)
        
        return AnalysisResult(
            sequence_id=sequence_data.id,
            gc_content=gc_content,
            motif_count=len(motifs),
            coding_regions=len(coding_regions),
            spatial_data=sequence_data.spatial_data,
        )
    
    @strawberry.field
    def analyze_file(
        self, file_path: str, spatial_data_path: Optional[str] = None
    ) -> List[AnalysisResult]:
        """
        Analyze sequences from a file.
        
        Args:
            file_path: Path to FASTA file
            spatial_data_path: Optional path to CSV file with spatial data
            
        Returns:
            List of analysis results
        """
        analyzer = SequenceAnalyzer()
        validator = DataValidator()
        
        # Load sequences
        sequences = analyzer.load_sequence(file_path)
        
        # Load spatial data if provided
        spatial_df = None
        if spatial_data_path:
            spatial_df = pd.read_csv(spatial_data_path)
        
        results = []
        for i, record in enumerate(sequences):
            # Add spatial data if available
            if spatial_df is not None and i < len(spatial_df):
                record.spatial_data = spatial_df.iloc[[i]]
            
            # Validate sequence
            validation = validator.validate_sequence_record(record)
            if not all(validation.values()):
                continue
            
            # Perform analysis
            gc_content = analyzer.calculate_gc_content(record.seq)
            motifs = analyzer.find_motifs(record.seq)
            coding_regions = analyzer.predict_coding_regions(record.seq)
            
            result = AnalysisResult(
                sequence_id=record.id,
                gc_content=gc_content,
                motif_count=len(motifs),
                coding_regions=len(coding_regions),
            )
            
            if hasattr(record, "spatial_data"):
                result.spatial_data = SpatialData(
                    latitude=record.spatial_data.iloc[0]["latitude"],
                    longitude=record.spatial_data.iloc[0]["longitude"],
                )
            
            results.append(result)
        
        return results
    
    @strawberry.field
    def visualize_spatial(
        self, analysis_results: List[AnalysisResult]
    ) -> VisualizationData:
        """
        Generate spatial visualizations of analysis results.
        
        Args:
            analysis_results: List of analysis results
            
        Returns:
            Visualization data
        """
        visualizer = BioVisualizer()
        
        # Convert results to DataFrame
        df = pd.DataFrame([{
            "sequence_id": result.sequence_id,
            "gc_content": result.gc_content,
            "motif_count": result.motif_count,
            "coding_regions": result.coding_regions,
            "latitude": result.spatial_data.latitude if result.spatial_data else None,
            "longitude": result.spatial_data.longitude if result.spatial_data else None,
        } for result in analysis_results])
        
        # Generate visualizations
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            
            # GC content distribution
            gc_plot = output_dir / "gc_content.png"
            visualizer.plot_gc_distribution(df, output_path=str(gc_plot))
            
            # Motif density
            motif_plot = output_dir / "motif_density.png"
            visualizer.plot_motif_density(df, output_path=str(motif_plot))
            
            # Coding potential
            coding_plot = output_dir / "coding_potential.png"
            visualizer.plot_coding_potential(df, output_path=str(coding_plot))
            
            # Read visualization files
            with open(gc_plot, "rb") as f:
                gc_content = f.read()
            with open(motif_plot, "rb") as f:
                motif_density = f.read()
            with open(coding_plot, "rb") as f:
                coding_potential = f.read()
            
            return VisualizationData(
                gc_content=gc_content,
                motif_density=motif_density,
                coding_potential=coding_potential,
            )
    
    @strawberry.field
    def health_check(self) -> str:
        """Health check query."""
        return "healthy"


schema = strawberry.Schema(query=Query)
graphql_app = GraphQLRouter(schema)
app = FastAPI()
app.include_router(graphql_app, prefix="/graphql") 