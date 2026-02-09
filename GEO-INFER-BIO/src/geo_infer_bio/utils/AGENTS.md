# Agent
: utils

## Scope
 This directory contains utils components for the module. It provides 2 classes and 0 functions.

## Classes
 and Functions

### DataValidator
 A class for validating biological data.

**Methods**:
- `validate_sequence(sequence: Union[str, Seq], sequence_type: str) -> bool`: Validate a biological sequence.
- `validate_spatial_coordinates(latitude: float, longitude: float) -> bool`: Validate spatial coordinates.
- `validate_spatial_dataframe(df: pd.DataFrame, required_columns: Optional[List[str]]) -> bool`: Validate spatial data DataFrame.
- `validate_sequence_record(record: SeqRecord, check_spatial: bool) -> Dict[str, bool]`: Validate a sequence record.
- `validate_alignment(alignment: MultipleSeqAlignment) -> Dict[str, bool]`: Validate a multiple sequence alignment.
- `validate_gc_content(gc_content: float, sequence_length: int) -> bool`: Validate GC content calculation.
- `validate_motif(motif: str, sequence_type: str) -> bool`: Validate a DNA/RNA motif.
- `validate_coding_region(start: int, end: int, sequence_length: int, min_length: int) -> bool`: Validate a coding region.

### BioVisualizer
 A class for visualizing biological data with spatial context.

**Methods**:
- `plot_spatial_distribution(data: pd.DataFrame, output_path: Optional[str], title: str) -> None`: Plot spatial distribution of biological features.
- `plot_gc_distribution(data: pd.DataFrame, output_path: Optional[str]) -> None`: Plot GC content distribution.
- `plot_motif_density(data: pd.DataFrame, output_path: Optional[str]) -> None`: Plot motif density distribution.
- `plot_coding_potential(data: pd.DataFrame, output_path: Optional[str]) -> None`: Plot coding potential distribution.
- `plot_sequence_alignment(alignment, output_path: Optional[str]) -> None`: Plot sequence alignment.

## Capabilities

- **2 classes** for core functionality

## Integration

- **Location**: `GEO-INFER-BIO/src/geo_infer_bio/utils`
- **Type**: Directory Node
