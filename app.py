from flask import Flask, render_template, request, send_from_directory, abort
from datetime import datetime, timezone
import os
import glob

app = Flask(__name__)

BASE_FOLDER = "/media/daniele/Daniele2TB/repo/Ens-Nowcasting_radar_FBK/plot"

# Serve immagini correttamente
@app.route('/image/<path:filename>')
def image(filename):
    full_path = os.path.join(BASE_FOLDER, filename)

    if not os.path.exists(full_path):
        return abort(404)

    # IMPORTANT: serve da BASE_FOLDER, non "/"
    return send_from_directory(BASE_FOLDER, filename)

def trova_ultimo_run():

    pattern = os.path.join(
        BASE_FOLDER,
        "*", "*", "*", "*"
    )

    cartelle = glob.glob(pattern)

    runs_validi = []

    now_utc = datetime.now(timezone.utc)

    for c in cartelle:

        try:

            rel = os.path.relpath(c, BASE_FOLDER)

            anno, mese, giorno, hhmm = rel.split(os.sep)

            ora = hhmm[:2]
            minuto = hhmm[2:]

            dt = datetime(
                int(anno),
                int(mese),
                int(giorno),
                int(ora),
                int(minuto),
                tzinfo=timezone.utc
            )

            # evita run future
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
    ora = "00"
    minuto = "00"

    if request.method == "POST":

        action = request.form.get("action")

        indice = int(request.form.get("indice", 0))

        # =========================================
        # BOTTONE "ULTIMO RUN"
        # =========================================
        if action == "latest":

            ultimo_run = trova_ultimo_run()

            if ultimo_run:

                data = ultimo_run.strftime("%Y-%m-%d")
                ora = ultimo_run.strftime("%H")
                minuto = ultimo_run.strftime("%M")

        else:

            data = request.form.get("date")
            ora = request.form.get("hour")
            minuto = request.form.get("minute")

        # se clicco "Carica dalla prima"
        if action == "load":
            indice = 0

        # =========================================
        # CARICAMENTO IMMAGINI
        # =========================================
        if data:

            anno, mese, giorno = data.split("-")

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

                if len(urls) > 0:
                    indice = max(0, min(indice, len(urls) - 1))

    immagine_corrente = None

    if urls:
        immagine_corrente = urls[indice]

    return render_template(
        "index.html",
        immagini=urls,
        immagine_corrente=immagine_corrente,
        indice=indice,
        data=data,
        ora=ora,
        minuto=minuto
    )


if __name__ == "__main__":
    app.run(debug=True, port=5001)

