"""
REST API for GEO-INFER-BIO.
"""
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
import pandas as pd
from pathlib import Path
import tempfile
import json

from ..core.sequence_analysis import SequenceAnalyzer
from ..utils.validation import DataValidator
from ..utils.visualization import BioVisualizer


class SpatialData(BaseModel):
    """Spatial data model."""
    latitude: float
    longitude: float


class SequenceData(BaseModel):
    """Sequence data model."""
    id: str
    sequence: str
    spatial_data: Optional[SpatialData] = None


class AnalysisResult(BaseModel):
    """Analysis result model."""
    sequence_id: str
    gc_content: float
    motif_count: int
    coding_regions: int
    spatial_data: Optional[SpatialData] = None


app = FastAPI(
    title="GEO-INFER-BIO API",
    description="API for biological sequence analysis with spatial context",
    version="0.1.0",
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "GEO-INFER-BIO API",
        "version": "0.1.0",
        "description": "API for biological sequence analysis with spatial context",
    }


@app.post("/analyze/sequence", response_model=AnalysisResult)
async def analyze_sequence(sequence_data: SequenceData):
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
        raise HTTPException(status_code=400, detail="Invalid sequence")
    
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


@app.post("/analyze/file")
async def analyze_file(
    file: UploadFile = File(...),
    spatial_data: Optional[UploadFile] = File(None),
):
    """
    Analyze sequences from a file.
    
    Args:
        file: FASTA file containing sequences
        spatial_data: Optional CSV file containing spatial data
        
    Returns:
        Analysis results
    """
    analyzer = SequenceAnalyzer()
    validator = DataValidator()
    
    # Save uploaded files temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".fasta") as fasta_temp:
        fasta_temp.write(await file.read())
        fasta_path = fasta_temp.name
    
    spatial_df = None
    if spatial_data:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as spatial_temp:
            spatial_temp.write(await spatial_data.read())
            spatial_path = spatial_temp.name
            spatial_df = pd.read_csv(spatial_path)
    
    # Load and validate sequences
    sequences = analyzer.load_sequence(fasta_path)
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
        
        result = {
            "sequence_id": record.id,
            "gc_content": gc_content,
            "motif_count": len(motifs),
            "coding_regions": len(coding_regions),
        }
        
        if hasattr(record, "spatial_data"):
            result["spatial_data"] = {
                "latitude": record.spatial_data.iloc[0]["latitude"],
                "longitude": record.spatial_data.iloc[0]["longitude"],
            }
        
        results.append(result)
    
    # Clean up temporary files
    Path(fasta_path).unlink()
    if spatial_data:
        Path(spatial_path).unlink()
    
    return results


@app.post("/visualize/spatial")
async def visualize_spatial(
    analysis_results: List[AnalysisResult],
    output_format: str = "png",
):
    """
    Generate spatial visualizations of analysis results.
    
    Args:
        analysis_results: List of analysis results
        output_format: Output format for visualizations
        
    Returns:
        Visualization data
    """
    visualizer = BioVisualizer()
    
    # Convert results to DataFrame
    df = pd.DataFrame([result.dict() for result in analysis_results])
    
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
        visualizations = {}
        for plot_file in [gc_plot, motif_plot, coding_plot]:
            with open(plot_file, "rb") as f:
                visualizations[plot_file.stem] = f.read()
        
        return visualizations


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"} 