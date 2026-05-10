from flask import Flask, render_template, request, send_from_directory, abort
from datetime import datetime, timezone
import os
import glob

app = Flask(__name__)

BASE_FOLDER = "/media/daniele/Daniele2TB/repo/Ens-Nowcasting_radar_FBK/plot"


@app.route('/image/<path:filename>')
def image(filename):
    full_path = os.path.join(BASE_FOLDER, filename)

    if not os.path.exists(full_path):
        return abort(404)

    return send_from_directory(BASE_FOLDER, filename)


def trova_ultimo_run():

    pattern = os.path.join(BASE_FOLDER, "*", "*", "*", "*")
    cartelle = glob.glob(pattern)

    runs_validi = []
    now_utc = datetime.now(timezone.utc)

    for c in cartelle:

        try:
            png_files = glob.glob(os.path.join(c, "*.png"))
            if not png_files:
                continue

            rel = os.path.relpath(c, BASE_FOLDER)
            anno, mese, giorno, hhmm = rel.split(os.sep)

            dt = datetime(
                int(anno),
                int(mese),
                int(giorno),
                int(hhmm[:2]),
                int(hhmm[2:]),
                tzinfo=timezone.utc
            )

            if dt <= now_utc:
                runs_validi.append((dt, c))

        except Exception:
            pass

    if not runs_validi:
        return None

    runs_validi.sort(key=lambda x: x[0])
    return runs_validi[-1][0]


@app.route("/", methods=["GET", "POST"])
def index():

    files = []
    urls = []
    indice = 0

    data = ""
    time = "00:00"

    if request.method == "POST":

        action = request.form.get("action")
        indice = int(request.form.get("indice", 0))

        # valore dal form (può essere None)
        time_form = request.form.get("time")

        # =========================================
        # ULTIMO RUN
        # =========================================
        if action == "latest":

            ultimo_run = trova_ultimo_run()

            if ultimo_run:
                data = ultimo_run.strftime("%Y-%m-%d")
                time = ultimo_run.strftime("%H:%M")

            if not time:
                time = request.form.get("time", "00:00")
                
        # =========================================
        # LOAD / DEFAULT
        # =========================================
        elif action == "load":

            data = request.form.get("date")

            if time_form:
                time = time_form

            indice = 0

        # =========================================
        # CASO NORMALE
        # =========================================
        else:

            data = request.form.get("date")

            if time_form:
                time = time_form

        # =========================================
        # CARICAMENTO IMMAGINI
        # =========================================
        if data and time:

            anno, mese, giorno = data.split("-")
            ora, minuto = time.split(":")

            cartella = os.path.join(
                BASE_FOLDER,
                anno,
                mese,
                giorno,
                f"{ora}{minuto}"
            )

            print("Cartella:", cartella)

            if os.path.exists(cartella):

                files = sorted(glob.glob(os.path.join(cartella, "*.png")))

                urls = [
                    "/image/" + os.path.relpath(f, BASE_FOLDER).replace("\\", "/")
                    for f in files
                ]

                if urls:
                    indice = max(0, min(indice, len(urls) - 1))

    immagine_corrente = urls[indice] if urls else None

    return render_template(
        "index.html",
        immagini=urls,
        immagine_corrente=immagine_corrente,
        indice=indice,
        data=data,
        time=time
    )


if __name__ == "__main__":
    app.run(debug=True, port=5001)