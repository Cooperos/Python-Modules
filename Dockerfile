FROM hub.nexus.consyst.ru/python:3.10.8

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y locales \
    && localedef -i ru_RU -c -f UTF-8 -A /usr/share/locale/locale.alias ru_RU.UTF-8
ENV LANG ru_RU.utf8

RUN apt-get update && apt-get install -y \
    libreoffice-calc \
    python3-uno \
    fontconfig \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p assets output public\
    && chmod 777 assets \
    && chmod 777 output

COPY app/ ./app/

ENV PYTHONPATH=/app
ENV HOME=/tmp
ENV UNO_PATH=/usr/lib/libreoffice/program
ENV PYTHONUNBUFFERED=1

CMD ["python", "-m", "app.api.run_api"]
