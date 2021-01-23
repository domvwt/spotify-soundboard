from flask import Flask
from multiprocessing import Process
import spotify_dash.jobs.maintain_data_asset as mda

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def run_update():
    mda.main(mode="update")
    proc = Process(target=lambda x: mda.main(mode="update"))
    proc.start()
    return "Data update process triggered - see container logs for more info."


if __name__ == "__main__":
    app.run(port=8080)
