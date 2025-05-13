"""
Sequence analysis module for GEO-INFER-BIO.
"""

from typing import Dict, List, Optional, Union
import numpy as np
import pandas as pd
from Bio import SeqIO, AlignIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from Bio.Align import MultipleSeqAlignment
from Bio.Data import CodonTable
from Bio.SubsMat import MatrixInfo as matlist
from Bio import pairwise2
from Bio.pairwise2 import format_alignment

from ..utils.validation import DataValidator
from ..utils.visualization import BioVisualizer


class SequenceAnalyzer:
    """A class for analyzing biological sequences with spatial context."""

    def __init__(self):
        """Initialize the SequenceAnalyzer."""
        self.validator = DataValidator()
        self.visualizer = BioVisualizer()
        self.codon_table = CodonTable.standard_dna_table

    def load_sequence(
        self, file_path: str, format: str = "fasta"
    ) -> Union[SeqRecord, List[SeqRecord]]:
        """
        Load sequence data from a file.

        Args:
            file_path: Path to the sequence file
            format: File format (default: "fasta")

        Returns:
            Sequence record(s) from the file
        """
        return list(SeqIO.parse(file_path, format))

    def align_sequences(
        self,
        sequences: List[SeqRecord],
        algorithm: str = "global",
        gap_open: float = -10,
        gap_extend: float = -0.5,
    ) -> MultipleSeqAlignment:
        """
        Align multiple sequences using pairwise alignment.

        Args:
            sequences: List of sequence records
            algorithm: Alignment algorithm ("global" or "local")
            gap_open: Gap opening penalty
            gap_extend: Gap extension penalty

        Returns:
            Multiple sequence alignment
        """
        alignments = []
        for i in range(len(sequences)):
            for j in range(i + 1, len(sequences)):
                if algorithm == "global":
                    alignments.append(
                        pairwise2.align.globalms(
                            sequences[i].seq,
                            sequences[j].seq,
                            2,
                            -1,
                            gap_open,
                            gap_extend,
                        )
                    )
                else:
                    alignments.append(
                        pairwise2.align.localms(
                            sequences[i].seq,
                            sequences[j].seq,
                            2,
                            -1,
                            gap_open,
                            gap_extend,
                        )
                    )
        return MultipleSeqAlignment(alignments)

    def calculate_gc_content(self, sequence: Seq) -> float:
        """
        Calculate GC content of a sequence.

        Args:
            sequence: DNA/RNA sequence

        Returns:
            GC content as a percentage
        """
        gc_count = sequence.count("G") + sequence.count("C")
        return (gc_count / len(sequence)) * 100

    def find_motifs(
        self, sequence: Seq, motif_length: int = 6
    ) -> Dict[str, List[int]]:
        """
        Find repeated motifs in a sequence.

        Args:
            sequence: DNA/RNA sequence
            motif_length: Length of motifs to search for

        Returns:
            Dictionary of motifs and their positions
        """
        motifs = {}
        for i in range(len(sequence) - motif_length + 1):
            motif = str(sequence[i:i + motif_length])
            if motif in motifs:
                motifs[motif].append(i)
            else:
                motifs[motif] = [i]
        return {k: v for k, v in motifs.items() if len(v) > 1}

    def calculate_sequence_similarity(
        self, seq1: Seq, seq2: Seq
    ) -> float:
        """
        Calculate sequence similarity using BLOSUM62 matrix.

        Args:
            seq1: First sequence
            seq2: Second sequence

        Returns:
            Similarity score
        """
        matrix = matlist.blosum62
        score = 0
        for a, b in zip(seq1, seq2):
            try:
                score += matrix[(a, b)]
            except KeyError:
                try:
                    score += matrix[(b, a)]
                except KeyError:
                    continue
        return score / max(len(seq1), len(seq2))

    def predict_coding_regions(
        self, sequence: Seq, min_length: int = 100
    ) -> List[Dict[str, int]]:
        """
        Predict potential coding regions in a sequence.

        Args:
            sequence: DNA sequence
            min_length: Minimum length of coding region

        Returns:
            List of predicted coding regions with start/end positions
        """
        coding_regions = []
        start_codons = ["ATG"]
        stop_codons = ["TAA", "TAG", "TGA"]

        for frame in range(3):
            for i in range(frame, len(sequence) - 2, 3):
                codon = str(sequence[i:i + 3])
                if codon in start_codons:
                    start_pos = i
                    for j in range(i + 3, len(sequence) - 2, 3):
                        codon = str(sequence[j:j + 3])
                        if codon in stop_codons:
                            if j - start_pos >= min_length:
                                coding_regions.append({
                                    "frame": frame,
                                    "start": start_pos,
                                    "end": j + 2,
                                })
                            break
        return coding_regions

    def analyze_spatial_distribution(
        self,
        sequences: List[SeqRecord],
        spatial_data: pd.DataFrame,
    ) -> Dict[str, pd.DataFrame]:
        """
        Analyze spatial distribution of sequence features.

        Args:
            sequences: List of sequence records
            spatial_data: DataFrame containing spatial coordinates

        Returns:
            Dictionary of spatial analyses
        """
        results = {
            "gc_content": [],
            "motif_density": [],
            "coding_potential": [],
        }

        for seq, spatial in zip(sequences, spatial_data.itertuples()):
            gc = self.calculate_gc_content(seq.seq)
            motifs = self.find_motifs(seq.seq)
            coding_regions = self.predict_coding_regions(seq.seq)

            results["gc_content"].append({
                "sequence_id": seq.id,
                "gc_content": gc,
                "latitude": spatial.latitude,
                "longitude": spatial.longitude,
            })

            results["motif_density"].append({
                "sequence_id": seq.id,
                "motif_count": len(motifs),
                "latitude": spatial.latitude,
                "longitude": spatial.longitude,
            })

            results["coding_potential"].append({
                "sequence_id": seq.id,
                "coding_regions": len(coding_regions),
                "latitude": spatial.latitude,
                "longitude": spatial.longitude,
            })

        return {
            k: pd.DataFrame(v) for k, v in results.items()
        }

    def visualize_spatial_patterns(
        self,
        spatial_analysis: Dict[str, pd.DataFrame],
        output_path: Optional[str] = None,
    ) -> None:
        """
        Visualize spatial patterns in sequence features.

        Args:
            spatial_analysis: Dictionary of spatial analyses
            output_path: Optional path to save visualization
        """
        self.visualizer.plot_spatial_distribution(
            spatial_analysis,
            output_path=output_path,
        ) 