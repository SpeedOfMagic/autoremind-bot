FROM python:3.10

COPY requirements.txt .
COPY src .

RUN pip install -r requirements.txt

ARG telegram_token
ENV TELEGRAM_TOKEN ${telegram_token}

CMD python3 main.py --telegram-token ${TELEGRAM_TOKEN}