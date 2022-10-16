FROM python:3.9

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY app app 
COPY db app
COPY bot.py app/bot.py
COPY entrypoint.sh app/entrypoint.sh
EXPOSE 8000

WORKDIR app
#ENTRYPOINT ["./entrypoint.sh"]
