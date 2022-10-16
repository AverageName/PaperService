#!/bin/bash

if [[ -v RUN_TESTS ]]; then
    # to do: print results to docker logs (I can't see them in docker desktop)
    python3 -m unittest discover
fi

python3 create_database.py
uvicorn main:app --host 0.0.0.0 --port 8000