FROM python:3.7-slim

RUN mkdir /app
WORKDIR /app

RUN apt-get update \
    && apt-get install -y g++ python3-dev libpq-dev \
    && rm -rf /var/lib/apt/lists/*

ADD requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
ADD . /app/

EXPOSE 80

ENTRYPOINT [ "python" ]
CMD ["app.py"]