FROM python:3.12

RUN mkdir /participants

WORKDIR /participants

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .
