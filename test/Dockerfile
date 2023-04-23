FROM python:3.10-buster
WORKDIR /app
COPY requirements.txt requirements.txt
RUN wget -qO - https://www.mongodb.org/static/pgp/server-5.0.asc | apt-key add -
RUN echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/debian buster/mongodb-org/5.0 main" | tee /etc/apt/sources.list.d/mongodb-org-5.0.list
RUN echo "deb http://deb.debian.org/debian buster-backports main" >> /etc/apt/sources.list.d/backports.list
RUN apt-get update && apt-get install -y libsystemd-dev mongodb-org
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .

RUN mkdir -p /data/db

EXPOSE 8000

CMD mongod --fork --logpath /var/log/mongodb.log && uvicorn app:fast_app --host 0.0.0.0 --port 8000

