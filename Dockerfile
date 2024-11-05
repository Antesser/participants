FROM python:3.12

RUN mkdir /participants

RUN apt update && apt install -y libsm6 libxext6 ffmpeg libfontconfig1 libxrender1 libgl1-mesa-glx

WORKDIR /participants

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .
