import os
import uuid
import atexit
import json

import redis
from flask import Flask, request, jsonify
from prometheus_flask_exporter import PrometheusMetrics
from jaeger_client import Config
from opentracing.propagation import Format


app = Flask(__name__)
metrics = PrometheusMetrics(app)
metrics.info('app_info', 'Application info', version='1.0.3')

config = Config(
    config={
        'sampler': {
            'type': 'const',
            'param': 1,
        },
        'logging': True,
    },
    service_name='run-controller',
    validate=True,
)

tracer = config.initialize_tracer()


@app.route("/", methods=('POST',))
def main(r=request):
    span_ctx = tracer.extract(Format.HTTP_HEADERS, request.headers)
    with tracer.start_active_span('processRun', finish_on_close=True, child_of=span_ctx) as scope:
        request_id = str(uuid.uuid4())
        app.logger.debug("Received request %s to /", request_id)

        with tracer.start_active_span('validatePayload', finish_on_close=True) as scope:
            content = r.json

            app.logger.debug("Request %s positively validated", request_id)

        workout_id = content["workout_id"]
        app.logger.debug("Processing workout %s in request %s", workout_id, request_id)

        with tracer.start_active_span('calculateScore', finish_on_close=True) as scope:
            # TODO: actually calculate the run score based on random and log the random && score + request id!
            score = 73
            content["score"] = score

        with tracer.start_active_span('storeRun', finish_on_close=True) as scope:
            r = redis.Redis(host=os.environ["REDIS_HOST"], password=os.environ["REDIS_PASSWORD"])
            r.set(workout_id, json.dumps(content))
            app.logger.debug("Persisted workout %s in db for request %s", workout_id, request_id)

        return jsonify({"workout_id": workout_id, "score": score})


@app.route("/divide", methods=('GET',))
def divide(r=request):
    return jsonify({"results": 5/0})


@app.route("/health", methods=('GET',))
@metrics.do_not_track()
def health():
    return jsonify({"status": "ok"})

def shutdown_hook():
    app.logger.info("Gracefully shutting down")

if __name__ == "__main__":
    port = os.environ["PORT"]
    debug = bool(os.environ.get("DEBUG"))

    atexit.register(shutdown_hook)

    app.run('0.0.0.0', debug=debug, port=port)
