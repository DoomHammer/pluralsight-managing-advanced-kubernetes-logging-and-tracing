FROM alpine

RUN apk add --no-cache python3 py-pip

ADD requirements.txt /app/requirements.txt

RUN pip install -r /app/requirements.txt

ADD . /app/

ENV DEBUG_METRICS=y

ENV PORT=8080

ENV DEBUG=y

EXPOSE 8080

CMD python /app/main.py
