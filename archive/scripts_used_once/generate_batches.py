import pandas as pd
from pathlib import Path

BATCH_SIZE = 25

input_files = [
    "1grams_german.csv",
    "2grams_german.csv",
    "3grams_german.csv",
    "4grams_german.csv",
    "5grams_german.csv"
]

base_dir = Path(r"d:\ngram")
output_dir = base_dir / "output"

# ensure output dir exists
output_dir.mkdir(parents=True, exist_ok=True)

total_batch_count = 0

for file_name in input_files:
    file_path = base_dir / file_name
    
    if not file_path.exists():
        print(f"[-] Missing: {file_name}")
        continue
    
    print(f"[*] Found: {file_name}")
    
    try:
        # Read the CSV file, preserving everything as string to prevent auto-conversions
        df = pd.read_csv(file_path, encoding='utf-8', dtype=str, keep_default_na=False)
        
        # Check if 'ngram' column exists
        if 'ngram' not in df.columns:
            print(f"    [-] Missing 'ngram' column in {file_name}")
            continue
            
        # Extract ngram column
        ngrams = df['ngram'].tolist()
        total_ngrams = len(ngrams)
        print(f"    [+] Extracted {total_ngrams} ngrams")
        
        # Create output subfolder
        source_name = file_path.stem
        subfolder = output_dir / source_name
        subfolder.mkdir(parents=True, exist_ok=True)
        
        # Prepare batches
        summary_data = []
        batch_number = 1
        
        for i in range(0, total_ngrams, BATCH_SIZE):
            batch = ngrams[i:i + BATCH_SIZE]
            
            # Format zero-padded batch number
            batch_num_str = f"{batch_number:03d}"
            output_txt_filename = f"batch_{batch_num_str}_ngrams.txt"
            output_txt_path = subfolder / output_txt_filename
            
            # Write to txt file (no headers, no blank lines between, exactly one per line)
            with open(output_txt_path, 'w', encoding='utf-8', newline='\n') as f:
                for item in batch:
                    f.write(f"{item}\n")
            
            # Add to summary
            start_row = i + 1
            end_row = i + len(batch)
            summary_data.append({
                "source_file": file_name,
                "batch_number": batch_number,
                "rows": len(batch),
                "start_row_1_indexed": start_row,
                "end_row_1_indexed": end_row,
                "first_ngram": batch[0],
                "last_ngram": batch[-1],
                "output_txt_file": output_txt_filename
            })
            
            batch_number += 1
            total_batch_count += 1
            
        # Save summary CSV
        summary_df = pd.DataFrame(summary_data)
        summary_csv_path = subfolder / "batches_summary.csv"
        summary_df.to_csv(summary_csv_path, index=False, encoding='utf-8')
        
        print(f"    [+] Created {batch_number - 1} batch files")
        
    except Exception as e:
        print(f"    [-] Error processing {file_name}: {e}")

print(f"\n[=] Final total batch count: {total_batch_count}")
