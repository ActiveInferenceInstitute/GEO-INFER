"""
Tests for the sequence analysis module.
"""
import pytest
import pandas as pd
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from Bio.Align import MultipleSeqAlignment

from geo_infer_bio.core.sequence_analysis import SequenceAnalyzer


@pytest.fixture
def sequence_analyzer():
    """Create a SequenceAnalyzer instance for testing."""
    return SequenceAnalyzer()


@pytest.fixture
def sample_sequences():
    """Create sample sequences for testing."""
    return [
        SeqRecord(Seq("ATGCGTACGTAGCTAGCTAG"), id="seq1"),
        SeqRecord(Seq("GCTAGCTAGCTAGCTAGCTA"), id="seq2"),
        SeqRecord(Seq("TAGCTAGCTAGCTAGCTAGC"), id="seq3"),
    ]


@pytest.fixture
def sample_spatial_data():
    """Create sample spatial data for testing."""
    return pd.DataFrame({
        "latitude": [40.7128, 34.0522, 51.5074],
        "longitude": [-74.0060, -118.2437, -0.1278],
    })


def test_load_sequence(sequence_analyzer, tmp_path):
    """Test loading sequence data from a file."""
    # Create a temporary FASTA file
    fasta_content = ">seq1\nATGCGTACGTAGCTAGCTAG\n>seq2\nGCTAGCTAGCTAGCTAGCTA"
    fasta_file = tmp_path / "test.fasta"
    fasta_file.write_text(fasta_content)

    # Test loading
    sequences = sequence_analyzer.load_sequence(str(fasta_file))
    assert len(sequences) == 2
    assert sequences[0].id == "seq1"
    assert sequences[1].id == "seq2"


def test_calculate_gc_content(sequence_analyzer):
    """Test GC content calculation."""
    sequence = Seq("ATGCGTACGTAGCTAGCTAG")
    gc_content = sequence_analyzer.calculate_gc_content(sequence)
    assert 0 <= gc_content <= 100
    assert gc_content == 45.0  # 9 G/C out of 20 bases


def test_find_motifs(sequence_analyzer):
    """Test motif finding."""
    sequence = Seq("ATGCGTACGTAGCTAGCTAG")
    motifs = sequence_analyzer.find_motifs(sequence, motif_length=4)
    assert isinstance(motifs, dict)
    assert "TAGC" in motifs
    assert len(motifs["TAGC"]) > 1


def test_calculate_sequence_similarity(sequence_analyzer):
    """Test sequence similarity calculation."""
    seq1 = Seq("ATGCGTACGTAGCTAGCTAG")
    seq2 = Seq("ATGCGTACGTAGCTAGCTAG")
    similarity = sequence_analyzer.calculate_sequence_similarity(seq1, seq2)
    assert 0 <= similarity <= 1
    assert similarity == 1.0  # Identical sequences


def test_predict_coding_regions(sequence_analyzer):
    """Test coding region prediction."""
    sequence = Seq("ATGAAATAA")  # Simple coding region
    regions = sequence_analyzer.predict_coding_regions(sequence, min_length=3)
    assert len(regions) > 0
    assert regions[0]["start"] == 0
    assert regions[0]["end"] == 8


def test_analyze_spatial_distribution(
    sequence_analyzer, sample_sequences, sample_spatial_data
):
    """Test spatial distribution analysis."""
    results = sequence_analyzer.analyze_spatial_distribution(
        sample_sequences, sample_spatial_data
    )
    assert isinstance(results, dict)
    assert "gc_content" in results
    assert "motif_density" in results
    assert "coding_potential" in results

    # Check DataFrame structure
    for df in results.values():
        assert isinstance(df, pd.DataFrame)
        assert "sequence_id" in df.columns
        assert "latitude" in df.columns
        assert "longitude" in df.columns


def test_visualize_spatial_patterns(
    sequence_analyzer, sample_sequences, sample_spatial_data, tmp_path
):
    """Test spatial pattern visualization."""
    results = sequence_analyzer.analyze_spatial_distribution(
        sample_sequences, sample_spatial_data
    )
    output_path = tmp_path / "spatial_patterns.png"
    sequence_analyzer.visualize_spatial_patterns(
        results, output_path=str(output_path)
    )
    assert output_path.exists() 