from flask import Flask
from multiprocessing import Process
import spotify_dash.jobs.maintain_data_asset as mda

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def run_update():
    proc = Process(target=mda.main(mode="update", daemon=True))
    proc.start()
<<<<<<< HEAD
    return "Data update process triggered - see container logs for more info.", 202
=======
    return "Data update process triggered - see container logs for more info.", 200
>>>>>>> 5c9eb81ec3386e726e3f52b40508a3b2cf76bd85


if __name__ == "__main__":
    app.run(port=8080)
