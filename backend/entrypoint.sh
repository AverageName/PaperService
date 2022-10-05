#!/bin/bash

python3 db/create_tables.py
uvicorn main:app --host 0.0.0.0 --port 8000
