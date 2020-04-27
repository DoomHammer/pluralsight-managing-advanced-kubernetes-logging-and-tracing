import os
import sys
import uuid
import atexit
import requests
import time
import json
from dataclasses import dataclass, asdict
from enum import Enum
from typing import Dict

from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from prometheus_flask_exporter import PrometheusMetrics
from jaeger_client import Config
from opentracing.propagation import Format


app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
metrics = PrometheusMetrics(app)
metrics.info('workout_gateway', 'Workout Gateway', version='1.0.3')

config = Config(
    config={
        'sampler': {
            'type': 'const',
            'param': 1,
        },
        'logging': True,
    },
    service_name='workout-gateway',
    validate=True,
)
tracer = config.initialize_tracer()


class WorkoutKind(Enum):
    RUNNING = "running"
    JUMPING = "jumping"
    SWIMMING = "swimming"


RUN_CONTROLLER_URL = "please provide url via env vars"


@dataclass
class Workout:
    kind: WorkoutKind
    begin: int
    end: int
    other: Dict

    @classmethod
    def from_dict(cls, d: Dict) -> "Workout":
        kind = d.pop("kind")
        if kind not in set(map(lambda e: e[1].value, dict(WorkoutKind.__members__).items())):
            raise ValueError("'{}' is not a WorkoutKind".format(kind))

        begin = int(d.pop("begin"))
        if not 0 <= begin < 2459:
            raise ValueError("Wrong value for begin!")

        end = int(d.pop("end"))
        if not 0 <= end < 2459:
            raise ValueError("Wrong value for end!")

        other = d

        return cls(kind=kind, begin=begin, end=end, other=other)

    def as_dict(self) -> Dict:
        d = asdict(self)
        do = d.pop("other")
        d.pop("kind")
        d.update(do)

        return d


def do_some_work(x: int) -> int:
    """Efficiently computes a simple polynomial just for kicks

    5 + 3x + 4x^2
    """
    return 5 + x * (3 + x * (4))

@app.route("/", methods=('POST',))
@cross_origin()
def main(r=request):
    try:
        mt_in = time.monotonic()
        with tracer.start_active_span('processWorkout', finish_on_close=True) as scope:
            request_id = str(uuid.uuid4())

            log = {
                "monotonic_time": mt_in,
                "event_t": "request",
                "request_id": request_id,
                "path": "/",
                "errors": [],
            }

            with tracer.start_active_span('validatePayload', finish_on_close=True) as scope:
                content = r.json

                try:
                    workout = Workout.from_dict(content)
                except KeyError as e:
                    e_msg = "Missing required field %s" % e

                    log["validated"] = False
                    log["errors"].append(e_msg)

                    return e_msg, 400
                except ValueError as e:
                    e_msg = str(e)

                    log["validated"] = False
                    log["errors"].append(e_msg)

                    return e_msg, 400

                log["validated"] = True

            with tracer.start_active_span('process', finish_on_close=True) as scope:
                with tracer.start_active_span('prepare', finish_on_close=True) as scope:
                    _workout_id = uuid.uuid4()
                    workout_id = str(_workout_id)
                    p = do_some_work(int(content["intensity"]))
                    log["p"] = p

                with tracer.start_active_span('call downstream', finish_on_close=True) as scope:
                    try:
                        headers = {}
                        tracer.inject(scope.span, Format.HTTP_HEADERS, headers)
                        payload = {**workout.as_dict(), "workout_id": workout_id}

                        r = requests.post(RUN_CONTROLLER_URL, json=payload, headers=headers)
                    except requests.exceptions.ConnectionError:
                        log["errors"].append("Downstream not avaible")
                        return "Something went wrong on our side :C", 500

                with tracer.start_active_span('postprocess', finish_on_close=True) as scope:
                    downstream_status = r.status_code
                    log["downstream_response_code"] = r.status_code

                    try:
                        r.raise_for_status()
                    except requests.exceptions.HTTPError:
                        log["errors"] = "Downstream errored"

                        if downstream_status == 500:
                           msg = "Something went wrong on our side :C"
                        else:
                            msg = r.text

                        return msg, downstream_status
                    else:
                        log["workout_id"] = workout_id
                        score = r.json()["score"]
                        p2 = do_some_work(score)
                        log["p2_over_score"] = p2

                return r.json()
    finally:
        print(json.dumps(log), file=sys.stderr)


@app.route("/health", methods=('GET',))
@metrics.do_not_track()
def health():
    return jsonify({"status": "ok"})

def shutdown_hook():
    log = {
        "event_t": "shutdown",
        "wall_time": time.time(),
        "monotonic_time": time.monotonic(),
        "errors": [],
    }
    print(json.dumps(log), file=sys.stderr)

if __name__ == "__main__":
    port = os.environ["PORT"]
    RUN_CONTROLLER_URL = os.environ["RUN_CONTROLLER_URL"]
    debug = bool(os.environ.get("DEBUG"))

    atexit.register(shutdown_hook)

    log = {
        "event_t": "startup",
        "wall_time": time.time(),
        "monotonic_time": time.monotonic(),
        "config": {
            "port": int(port),
            "run_controller_url": RUN_CONTROLLER_URL,
            "debug": debug
        },
        "errors": [],
    }
    print(json.dumps(log), file=sys.stderr)

    app.run('0.0.0.0', debug=debug, port=port)
