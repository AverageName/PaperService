#!/bin/bash

python3 create_database.py
#uvicorn main:app --host 0.0.0.0 --port 8000
python3 bot.py
