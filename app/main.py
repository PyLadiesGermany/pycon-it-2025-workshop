import json
import requests
import random
import time

from codecarbon import track_emissions, EmissionsTracker
from http.server import HTTPServer
from os import getenv
from prometheus_client import MetricsHandler, Counter
from string import Template

from transformers import pipeline
from util import artificial_503, artificial_latency
from urllib.parse import urlparse, parse_qs

# load environment variables from .env file
from dotenv import load_dotenv

load_dotenv()


HOST_NAME = "0.0.0.0"  # This will map to available port in docker
PORT_NUMBER = 8001
ELECTRICITY_MAP_API_KEY = getenv("ELECTRICITY_MAP_API_KEY")

# GIVEN ZONE - FEEL FREE TO CHANGE
ZONE = "DE"
carbon_intensity_url = (
    f"https://api.electricitymap.org/v3/carbon-intensity/latest?zone={ZONE}"
)

with open("./templates/carbonIntensity.html", "r") as f:
    html_string = f.read()
html_template = Template(html_string)

# Load the predict-intensity HTML template
with open("./templates/predict_intensity.html", "r") as f:
    predict_html = f.read()

# carbon intensity predictor for low/medium/high
predictor = pipeline(
    "text-classification",
    model="jessica-ecosia/carbon-intensity-classifier",
    device=-1,  # CPU
)

tracker = EmissionsTracker(
    project_name="python-app",
    save_to_prometheus=True,
    prometheus_url="http://pushgateway:9091",
)

requestCounter = Counter(
    "requests_total", "total number of requests", ["status", "endpoint"]
)


def fetch_carbon_intensity():
    r = (
        requests.get(carbon_intensity_url, auth=("auth-token", ELECTRICITY_MAP_API_KEY))
        if random.random() > 0.15
        else artificial_503()
    )
    if r.status_code == 200:
        return r.json()["carbonIntensity"]
    return 0


class HTTPRequestHandler(MetricsHandler):
    @artificial_latency
    def get_carbon_intensity(self):
        self.do_HEAD()
        carbon_intensity = fetch_carbon_intensity()
        bytes_template = bytes(
            html_template.substitute(counter=carbon_intensity, zone=ZONE), "utf-8"
        )
        self.wfile.write(bytes_template)

    @track_emissions()
    def predict_intensity(self):
        # Expecting query: /predict_carbon_intensity?text=your+activity+description
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        text = params.get("text", [""])[0]
        if not text:
            self.send_error(400, "Missing `text` query parameter")
            return

        # Run zero-shot classification
        result = predictor(text)

        # Build and send JSON response
        payload = {
            "sequence": text,
            "classification": result[0].get("label", "unknown"),
            "score": round(result[0].get("score", 0.0), 2),
        }
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(payload).encode("utf-8"))
        return

    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")

        self.end_headers()

    def do_GET(self):
        endpoint = self.path
        if endpoint == "/carbon_intensity":
            requestCounter.labels(status=200, endpoint=endpoint).inc()
            return self.get_carbon_intensity()

        elif endpoint == "/background_image":
            with open("./templates/forest-background.jpg", "rb") as f:
                self.send_response(200)
                self.send_header("Content-type", "image/jpg")
                self.end_headers()
                self.wfile.write(f.read())

        elif endpoint == "/predict":
            # Serve the HTML form for carbon intensity prediction
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(predict_html.encode("utf-8"))
            return

        elif endpoint.startswith("/predict_carbon_intensity"):
            return self.predict_intensity()

        elif endpoint == "/metrics":
            return super(HTTPRequestHandler, self).do_GET()

        else:
            self.send_error(404)


if __name__ == "__main__":
    myServer = HTTPServer((HOST_NAME, PORT_NUMBER), HTTPRequestHandler)
    print(time.asctime(), "Server Starts - %s:%s" % (HOST_NAME, PORT_NUMBER))
    try:
        myServer.serve_forever()
    except KeyboardInterrupt:
        pass
    myServer.server_close()
    print(time.asctime(), "Server Stops - %s:%s" % (HOST_NAME, PORT_NUMBER))
