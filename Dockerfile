FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    libpq-dev gcc python3-dev musl-dev zlib1g-dev libjpeg-dev \
    graphviz \
    && rm -rf /var/lib/apt/lists/*

# Системные зависимости
RUN apt-get update && apt-get install -y \
    libpq-dev gcc python3-dev musl-dev zlib1g-dev libjpeg-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /code

COPY requirements.txt .

# Зависимости    
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app .