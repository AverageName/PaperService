#!usr/bin/python

import sys
from tqdm import tqdm
import re

def create_new_json_wo_numberint(old_json_path, 
                                 report_every=10_000_000, 
                                 total=409_129_302):
    with open(old_json_path) as old_json:
        with open("dblpv13_wo_numberint111.json", "w") as new_json:
            for line_num, old_line in enumerate(tqdm(old_json, total=total)):
                new_line = old_line
                new_line = re.sub(r'NumberInt\((\d+)\)', r"\1", new_line)
                new_line = re.sub(r'NumberInt\(\)', "null", new_line)
                new_json.write(new_line)
               # if line_num % report_every == 0:
               #     print(f"{line_num} lines processed")

def main():
    create_new_json_wo_numberint(sys.argv[1])

if __name__ == "__main__":
    main()
