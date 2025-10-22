FROM python:3.11-slim
WORKDIR /app

RUN apt-get update && apt-get install -y build-essential libffi-dev   

COPY ./requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

COPY . /app/

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]