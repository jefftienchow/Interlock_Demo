FROM python:3.7

WORKDIR /usr/src/app/actuator

RUN pip install --upgrade pip

COPY . .

CMD ["python","./stop_go.py"]