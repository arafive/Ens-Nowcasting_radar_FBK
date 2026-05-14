#!/bin/bash

# Lo rendo eseguibile con: chmod +x sync_meteo-dev.sh
# Problemi si sync con https://chatgpt.com/share/6a05d1e4-5690-83eb-a0ee-7af4cb8117b6

LOCKFILE="/tmp/sync_png.lock"

# Evita esecuzioni multiple contemporanee
if [ -e "$LOCKFILE" ]; then
    echo "$(date): script già in esecuzione"
    exit 1
fi

trap "rm -f $LOCKFILE" EXIT
touch "$LOCKFILE"

# Directory dove vuoi salvare i file
DEST="/home/cfmi.arpal.org/daniele.carnevale/Scrivania/Ens-Nowcasting_radar_FBK"

# Vai nella directory di destinazione
cd "$DEST" || exit 1

# Esegui rsync
rsync -rahzPuv --update --modify-window=1 --info=progress2 \
    --include='*/' \
    --include='*.png' \
    --exclude='*' \
    meteo@meteo-dev:/home/cfmi.arpal.org/meteo/QnapDevMeteo/Ens-Nowcasting_radar_FBK/plot .

echo "$(date): sincronizzazione completata"
