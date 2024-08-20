import pandas as pd
import os
from VaxiJen import VaxiJen
from SignalP import SignalP
from TMHMM import TMHMM
from DeepLoc import DeepLoc


def read_fasta_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    
    sequences = []
    current_sequence = ''
    for line in lines:
        if line.startswith('>'):
            if current_sequence:
                sequences.append(current_sequence + '\n')
            current_sequence = line
        else:
            current_sequence += line.strip()
    
    if current_sequence:
        sequences.append(current_sequence + '\n')
    
    return sequences

def write_fasta_file(sequences, file_name):
    with open(file_name, 'w') as file:
        file.writelines(sequences)

def filter_sequences(sequences, max_length=6000):
    filtered_sequences = []
    large_sequences = []
    for seq in sequences:
        if len(seq) <= max_length:
            filtered_sequences.append(seq)
        else:
            large_sequences.append(seq)
    return filtered_sequences, large_sequences

def split_sequences(sequences, batch_size=500):
    num_files = (len(sequences) // batch_size) + 1
    for i in range(num_files):
        start = i * batch_size
        end = (i + 1) * batch_size
        if end > len(sequences):
            end = len(sequences)
        batch = sequences[start:end]
        write_fasta_file(batch, f'output_{i+1}.fasta')

# Function to process multiple output files and merge the DataFrames
def process_multiple_output_files(output_folder, vaxi_file_path):
    # Run VaxiJen once and get the DataFrame
    vaxijenDF = VaxiJen(vaxi_file_path)
    
    merged_dfs = []  # List to store merged DataFrames
    for file_name in os.listdir(output_folder):
        if file_name.startswith('output'):
            file_path = os.path.join(output_folder, file_name)
            print(file_path)

            # Run SignalP, TMHMM, and DeepLoc for each file
            signalpDF = SignalP(file_path)
            tmhmmDF = TMHMM(file_path)
            deeplocDF = DeepLoc(file_path)

            # Merge the DataFrames from SignalP, TMHMM, and DeepLoc
            merged_df = pd.merge(signalpDF, tmhmmDF, on='Protein_ID', how='outer')
            merged_df = pd.merge(merged_df, deeplocDF, on='Protein_ID', how='outer')

            # Append the merged DataFrame to the list
            merged_dfs.append(merged_df)
    
    # Concatenate all merged DataFrames from SignalP, TMHMM, and DeepLoc
    final_merged_df = pd.concat(merged_dfs, ignore_index=True)

    # Merge the VaxiJen DataFrame with the final merged DataFrame
    final_merged_df = pd.merge(final_merged_df, vaxijenDF, on='Protein_ID', how='outer')

    # Save the final merged DataFrame to an Excel file
    final_merged_df.to_excel('merged_data.xlsx', index=False)
 

def main():
    # edit file_path for the tharget sequnces
    file_path = 'UP000000429.fasta'
    sequences = read_fasta_file(file_path)
    filtered_sequences, large_sequences = filter_sequences(sequences)
    split_sequences(filtered_sequences)
    
    if large_sequences:
        write_fasta_file(large_sequences, 'large_sequences.fasta')

    # Specify the folder containing the output files
    output_folder = r'C:\Users\LeLWa\Desktop\DATABASE_VACCINE'
    vaxi_file_path = r'C:\Users\LeLWa\Desktop\DATABASE_VACCINE\UP000000429.fasta'
    
    # Process multiple output files and pass processed sequences to subsequent codes
    process_multiple_output_files(output_folder,vaxi_file_path )

# Entry point
if __name__ == '__main__':
    main()
