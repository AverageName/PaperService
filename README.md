# PaperService

Перед тем как запустить сервис, нужно создать файл `.env`, прописать в нем следующее:    
`POSTGRES_PASSWORD=admin`    

Чтобы запустить сервис, надо запустить следующую команду:   
`docker-compose up --build`


Для БД используется PostgreSQL, для взаимодействия с ней используется SQLAlchemy ORM.
