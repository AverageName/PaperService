FROM python:3.9

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY db backend/db
COPY topic_modeling backend/topic_modeling
COPY recommender backend/recommender
COPY create_database.py backend/create_database.py
COPY drop_database.py backend/drop_database.py
COPY fill_database.py backend/fill_database.py
COPY main.py backend/main.py
COPY bot.py backend/bot.py
COPY entrypoint.sh entrypoint.sh

EXPOSE 8000

WORKDIR backend
