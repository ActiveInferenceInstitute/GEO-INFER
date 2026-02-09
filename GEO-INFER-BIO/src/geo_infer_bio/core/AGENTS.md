# Agent
: core 

## Scope
 This directory contains core components for the module. It provides 1 classes and 0 functions. 

## Classes
 and Functions 

### SequenceAnalyzer
 A class for analyzing biological sequences with spatial context.

**Methods**:
- `load_sequence(file_path: str, format: str) -> Union[SeqRecord, List[SeqRecord]]`: Load sequence data from a file.
- `align_sequences(sequences: List[SeqRecord], algorithm: str, gap_open: float, gap_extend: float) -> MultipleSeqAlignment`: Align multiple sequences using pairwise alignment.
- `calculate_gc_content(sequence: Seq) -> float`: Calculate GC content of a sequence.
- `find_motifs(sequence: Seq, motif_length: int) -> Dict[str, List[int]]`: Find repeated motifs in a sequence.
- `calculate_sequence_similarity(seq1: Seq, seq2: Seq) -> float`: Calculate sequence similarity using BLOSUM62 matrix.
- `predict_coding_regions(sequence: Seq, min_length: int) -> List[Dict[str, int]]`: Predict potential coding regions in a sequence.
- `analyze_spatial_distribution(sequences: List[SeqRecord], spatial_data: pd.DataFrame) -> Dict[str, pd.DataFrame]`: Analyze spatial distribution of sequence features.
- `visualize_spatial_patterns(spatial_analysis: Dict[str, pd.DataFrame], output_path: Optional[str]) -> None`: Visualize spatial patterns in sequence features. 

## Capabilities
 
- **1 classes** for core functionality 

## Integration
 
- **Location**: `GEO-INFER-BIO/src/geo_infer_bio/core` 
- **Type**: Directory Node
