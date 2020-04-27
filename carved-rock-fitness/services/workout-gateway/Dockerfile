FROM alpine

RUN apk add --no-cache python3 py-pip

ADD requirements.txt /app/requirements.txt

RUN pip3 install -r /app/requirements.txt

ADD . /app/

ENV DEBUG_METRICS=y

ENV PORT=8000

ENV DEBUG=y

EXPOSE 8000

CMD python3 /app/main.py
