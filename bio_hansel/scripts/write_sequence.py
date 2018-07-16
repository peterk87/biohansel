from typing import Dict

import pandas as pd

from Bio import SeqIO


def write_sequences(output_directory: str, reference_genome_path: str,
                    results_dict: Dict[str, pd.DataFrame], schema_name: str,
                    sequence_length: int) -> None:
    """Collects the sequences from the reference genome by going through the list of dataframes and outputting the
    associated sequences at that SNV location

    Args:
        output_directory:directory where the schema would be located as indicated by the user
        reference_genome_path: file path to where the reference genome is located
        results_dict: specifies the list of genomes and their associated group
        schema_name: the name of the output schema file
        sequence_length: the length of additional sequences to be added to the beginning and end of the SNV

    Returns:
        results_dict: updated dictionary with snv sequences for both the reference genome and alternate snv
        Creates schema file in the output directory specified by the user


    """
    for key, value in results_dict.items():
        group = key
        with open(f"{output_directory}/{schema_name}.fasta", "a+") as file:
            gb_record = [
                record
                for record in SeqIO.parse(reference_genome_path, "genbank")
            ]
            max_sequence_value = len(gb_record[0].seq)
            sequences = str(gb_record[0].seq)
            ref_seqs = value.POS.apply(
                get_sub_sequences,
                args=(sequences, sequence_length, max_sequence_value))
            alt_seqs = ref_seqs.str.slice(
                0, sequence_length) + value.ALT + ref_seqs.str.slice(
                    sequence_length + 1, sequence_length + sequence_length + 1)

            value['ref_sequences'] = ref_seqs
            value['alt_sequences'] = alt_seqs
            for row in value.iterrows():
                attribute_value = row.iloc[3]
                position = row['POS']
                reference_snv = row['ref_sequences']
                alternate_snv = row['alt_sequences']
                # if the ratio is above 1, then it means that it is positive and takes the alternate snv form
                if attribute_value > 0:
                    file.write(f'''
                        >{position}-{group}
                        {alternate_snv}
                        >negative{position}-{group}
                        {reference_snv}
                        ''')
                # if the ratio is below 1, then it means that it remains negative
                else:
                    file.write(f'''
                        >{position}-{group}
                        {reference_snv}
                        >negative{position}-{group}
                        {alternate_snv}
                        ''')
    return results_dict


def get_sub_sequences(position: int, seq: str, sequence_length: int,
                      max_sequence_value: int) -> str:
    """Get the sequences that are before are after the specified SNV
    Args:
        position: the position of the SNV based off of the reference genome
        seq: the set of sequences from the reference genome
        sequence_length: the amount of upstream and downstream sequences added to the SNV and included in the schema
                        output
        max_sequence_value: the length of the reference genome

    Returns:
        sequence_sequence: the sequence that is found at the specified genome positions from the reference genome

    """
    specific_sequence = seq[max(0, position - (sequence_length + 1)):min(
        max_sequence_value, position + sequence_length)]