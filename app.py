from flask import Flask, jsonify, render_template, request

from models.predictor import TrafficPredictor
from models.router import TrafficRouter

app = Flask(__name__)
predictor = TrafficPredictor()
router = TrafficRouter()


@app.route("/")
def dashboard():
    return render_template("index.html")


@app.route("/api/predict", methods=["POST"])
def predict_congestion():
    payload = request.get_json(silent=True) or {}
    segment_ids = payload.get("segment_ids", [])
    timestamp = payload.get("timestamp")
    weather = payload.get("weather", {})

    if not segment_ids or timestamp is None:
        return jsonify({"error": "segment_ids and timestamp are required"}), 400

    predictions = predictor.predict(segment_ids=segment_ids, timestamp=timestamp, weather=weather)
    return jsonify({"predictions": predictions})


@app.route("/api/route", methods=["POST"])
def recommend_route():
    payload = request.get_json(silent=True) or {}
    start = payload.get("start")
    end = payload.get("end")
    timestamp = payload.get("timestamp")
    weather = payload.get("weather", {})
    algorithm = payload.get("algorithm", "dijkstra")

    if not start or not end:
        return jsonify({"error": "start and end coordinates are required"}), 400

    edge_predictions = predictor.predict_for_edges(
        edge_ids=router.edge_ids,
        timestamp=timestamp,
        weather=weather,
    )

    route = router.recommend_route(
        start=start,
        end=end,
        edge_predictions=edge_predictions,
        algorithm=algorithm,
    )
    return jsonify(route)


if __name__ == "__main__":
    app.run()
