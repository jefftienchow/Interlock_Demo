FROM python:3.7

WORKDIR /usr/src/app/sensor

COPY requirements.txt ./

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python","./generate.py"]