FROM python:3.6

COPY . /app

WORKDIR /app

RUN pip install -r requirements.txt \
    && groupadd -r admin && useradd -r -g admin admin

USER admin

ENV ENV_TYPE=PRODUCTION

ENTRYPOINT [ "python", "server.py", "-w", "ebay_report_server"]
