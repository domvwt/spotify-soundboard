from flask import Flask
import spotify_dash.jobs.maintain_data_asset as mda

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def run_update():
    mda.main(mode="update")
    return "Process complete - see container logs for more info."


if __name__ == "__main__":
    app.run(port=8080)
