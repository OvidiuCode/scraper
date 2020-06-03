FROM python:3.8

WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt
RUN apt-get update && apt-get install -y postgresql-client

COPY . /app

CMD ["uvicorn", "app:app"]
EXPOSE 8000