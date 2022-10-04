FROM python:3.9

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY db db
COPY app app 
COPY entrypoint.sh entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]
