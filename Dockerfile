FROM python:3.9

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY create_tables.py create_tables.py
COPY crud.py crud.py
COPY entrypoint.sh entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]
