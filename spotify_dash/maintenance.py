from flask import Flask, request
from multiprocessing import Process
import spotify_dash.jobs.maintain_data_asset as mda

app = Flask(__name__)


@app.route("/", methods=["POST"])
def run_update():
    envelope = request.get_json()

    if not envelope:
        msg = "no Pub/Sub message received"
        print(f"error: {msg}")
        return f"Bad Request: {msg}", 400

    if not isinstance(envelope, dict) or "message" not in envelope:
        msg = "invalid Pub/Sub message format"
        print(f"error: {msg}")
        return f"Bad Request: {msg}", 400

    pubsub_message = envelope["message"]

    if isinstance(pubsub_message, dict) and "data" in pubsub_message:
        proc = Process(target=mda.main(mode="update", daemon=True))
        proc.start()

    return ("Data update process triggered.", 204)


if __name__ == "__main__":
    app.run(port=8080)
