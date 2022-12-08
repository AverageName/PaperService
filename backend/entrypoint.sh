#!/bin/bash

python create_database.py
python fill_database.py --filename /data/preprocessed_top_50k_papers_by_n_citation.csv
# uvicorn main:app --host 0.0.0.0 --port 8000
python bot.py
