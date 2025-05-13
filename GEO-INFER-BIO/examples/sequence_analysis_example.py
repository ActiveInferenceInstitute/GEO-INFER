"""
Example script demonstrating the usage of GEO-INFER-BIO sequence analysis.
"""
import pandas as pd
from pathlib import Path
from geo_infer_bio.core.sequence_analysis import SequenceAnalyzer
from geo_infer_bio.utils.visualization import BioVisualizer


def main():
    """Run the example analysis."""
    # Initialize the analyzer
    analyzer = SequenceAnalyzer()
    visualizer = BioVisualizer()

    # Create sample data directory if it doesn't exist
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)

    # Create sample sequences
    sequences = [
        ">seq1\nATGCGTACGTAGCTAGCTAG",
        ">seq2\nGCTAGCTAGCTAGCTAGCTA",
        ">seq3\nTAGCTAGCTAGCTAGCTAGC",
    ]

    # Save sequences to file
    fasta_file = data_dir / "sample_sequences.fasta"
    fasta_file.write_text("\n".join(sequences))

    # Create sample spatial data
    spatial_data = pd.DataFrame({
        "latitude": [40.7128, 34.0522, 51.5074],
        "longitude": [-74.0060, -118.2437, -0.1278],
    })

    # Load sequences
    print("Loading sequences...")
    seq_records = analyzer.load_sequence(str(fasta_file))
    print(f"Loaded {len(seq_records)} sequences")

    # Calculate GC content
    print("\nCalculating GC content...")
    for seq in seq_records:
        gc = analyzer.calculate_gc_content(seq.seq)
        print(f"GC content for {seq.id}: {gc:.2f}%")

    # Find motifs
    print("\nFinding motifs...")
    for seq in seq_records:
        motifs = analyzer.find_motifs(seq.seq, motif_length=4)
        print(f"Motifs found in {seq.id}:")
        for motif, positions in motifs.items():
            print(f"  {motif}: {positions}")

    # Predict coding regions
    print("\nPredicting coding regions...")
    for seq in seq_records:
        regions = analyzer.predict_coding_regions(seq.seq)
        print(f"Coding regions in {seq.id}:")
        for region in regions:
            print(f"  Frame {region['frame']}: {region['start']}-{region['end']}")

    # Analyze spatial distribution
    print("\nAnalyzing spatial distribution...")
    spatial_analysis = analyzer.analyze_spatial_distribution(
        seq_records, spatial_data
    )

    # Visualize results
    print("\nGenerating visualizations...")
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    # Plot GC content distribution
    gc_plot = output_dir / "gc_content_distribution.png"
    visualizer.plot_gc_distribution(
        spatial_analysis["gc_content"],
        output_path=str(gc_plot),
    )
    print(f"GC content plot saved to {gc_plot}")

    # Plot motif density
    motif_plot = output_dir / "motif_density.png"
    visualizer.plot_motif_density(
        spatial_analysis["motif_density"],
        output_path=str(motif_plot),
    )
    print(f"Motif density plot saved to {motif_plot}")

    # Plot coding potential
    coding_plot = output_dir / "coding_potential.png"
    visualizer.plot_coding_potential(
        spatial_analysis["coding_potential"],
        output_path=str(coding_plot),
    )
    print(f"Coding potential plot saved to {coding_plot}")

    print("\nAnalysis complete! Check the output directory for visualizations.")


if __name__ == "__main__":
    main() 