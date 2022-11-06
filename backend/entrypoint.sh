#!/bin/bash

python create_database.py
# uvicorn main:app --host 0.0.0.0 --port 8000
python bot.py
