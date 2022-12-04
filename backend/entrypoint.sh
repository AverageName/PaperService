#!/bin/bash

python create_database.py
python fill_database.py --filename /data/dblpv13.json
# uvicorn main:app --host 0.0.0.0 --port 8000
python bot.py
