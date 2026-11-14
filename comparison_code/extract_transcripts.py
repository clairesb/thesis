import argparse
import gzip
import json
import logging
import yaml
import pandas as pd

from pathlib import Path

"""
Extract per-song results from zipped output files in run directories.
Expected directory structure:
    root_path/01-ss-long-sep-segmentation_alg-run_no/output.gz
where sep is mdx_extra, original, or vocal_stem, and segmentation_alg is native or
rmsvad. 

Usage:
    python extract_songs.py --root_path /path/to/root --yaml_path /path/to/yaml_with_fields
"""

def forced_bool(val:str):
    """
    Drafted by claude. Thanks Claude!
    """
    if isinstance(val, bool):
        return val
    if val.lower() in ("true", "t", "yes", "y", "1"):
        return True
    if val.lower() in ("false", "f", "no", "n", "0"):
        return False
    raise argparse.ArgumentTypeError(f"Expected true/false, got '{val}'")

def run_info(filepath: Path) -> dict:
    """
    Extract some extra fields based on the filepath
    (mix, segmentation algorithm, and run #)
    """
    dir_name = filepath.parent.name
    _, mix, segmentation_alg, run_no = dir_name.rsplit("-", 3)
    extra_fields = {"mix": mix,
                    "segmentation_algorithm": segmentation_alg,
                    "run_number": int(run_no) if run_no.isdigit() else run_no}
    return extra_fields

def load_fields(yaml_file: Path) -> dict:
    """
    Load desired fields and paths from yaml file
    """
    with open(yaml_file) as f:
        return yaml.safe_load(f)["fields"]

def output_files(root:Path, pattern:str = "*output.gz") -> list[Path]:
    """
    Get a list of all the output files
    They're named output.gz by default
    """
    return [f for f in root.rglob(pattern) if f.is_file()]

def read_file(file:Path) -> list[dict]:
    """
    Read output files into a list of dicts, where one dict corresponds
    to info from one song.
    """
    try:
        with gzip.open(file, "rt", encoding='utf-8') as f:
            records = [json.loads(line) for line in f if line.strip()]
            return records
    except (OSError, EOFError, json.JSONDecodeError) as e:
        print(f"{file}: {e}")
        return []

def parse_nested_field(record: dict, key_path: list):
    """
    Input: path to desired field (e.g., ['infer', 'asr_samples', 0, 'hyp'])
    Output: field value (e.g., lyrics, formatted as a string)
    """
    val = record
    try:
        for k in key_path:
            val = val[k]
    except (KeyError, IndexError, TypeError):
        return None
    return val

def compute_hal_rate(record:dict, threshold:int = 10) -> float:
    alignments = parse_nested_field(record,
                                    ['eval', 'wo', 'alignments', 0])
    hit = sub = dels = ins = hal = 0
    for alignment in alignments:
        ref_len = alignment["ref_end_idx"] - alignment["ref_start_idx"]
        hyp_len = alignment["hyp_end_idx"] - alignment["hyp_start_idx"]
        t = alignment["type"]
        if t == "equal":
            hit += ref_len
        elif t == "delete":
            dels += ref_len
        elif t == "substitute":
            sub += ref_len
            if ref_len > threshold:
                hal+= ref_len
        elif t == "insert":
            ins += hyp_len
            if hyp_len > threshold:
                hal += hyp_len
    tot = hit + sub + dels
    return hal/tot

def parse_record(record:dict, filename:Path, fields:dict) -> dict:
    simplified_record = {}
    simplified_record['hal_rate'] = compute_hal_rate(record)
    extras = run_info(filename)
    simplified_record = simplified_record | extras
    for field in fields.keys():
        simplified_record[field] = parse_nested_field(record, fields[field])
    return simplified_record

def parse_file(filename:Path, fields:dict) -> list:
    records = read_file(filename)
    record_list = []
    for record in records:
        record_list.append(parse_record(record, filename, fields))
    return record_list

def main():
    parser = argparse.ArgumentParser(description=__doc__, 
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root_path", required=True, type=Path, 
                        help="Directory containing the run folders")
    parser.add_argument("--yaml_path", required=True, type=Path,
                        help="path to yaml file containing desired fields and their paths")
    args = parser.parse_args()
    files = output_files(args.root_path)
    field_dict = load_fields(args.yaml_path)
    records = []
    for file in files:
        records.extend(parse_file(file, field_dict))
    record_df = pd.DataFrame(records)
    record_df.to_csv('simplified_records_for_slides.csv')



if __name__=="__main__":
    main()