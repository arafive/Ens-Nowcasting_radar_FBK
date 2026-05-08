README.txt

:Author: daniele
:Email: daniele@skaftafell
:Date: 2026-05-08 08:53

La repository si trova in https://it4lia-aifactory.eu/it/repository/ cliccando sul bottone "Vai a HuggingFace", e dopo "it4lia/irene"

########### parte generazione immagini

1. Clona la repository:
    git clone https://huggingface.co/it4lia/irene
    rm -rf irene/.git*

2. Tutto è regolato da nowcasting.py
    Può essere lanciato da solo passandogli una data UTC (es. python3 nowcasting.py "2020-01-01 00:00:00")
    Messo in crontab -e gira da solo. Ha un delay di 10 minuti rispetto al tempo attuale perché se l'ultimo istante non ha pioggia non verrà prevista mai pioggia.
    In crontab viene fatto dirare alle 00, 15, 30, 45 di ogni ora.
    La cartella, per esempio, 2020/10/07/2045 conterrà le previsioni a partire dalle 20:45, cioè il primo istante veramente previsto.

Ci sono dei TODO da fare scritti dentro nowcasting.py

########### parte web

Avviare flask in background:
nohup flask run --host=0.0.0.0 --port=5001 > log_nowcasting.log 2>&1 &

ip di questo computer ARPAL: 10.24.50.225 (trovato con >>> hostname -I)
Link: http://10.24.50.225:5001

>>> Cosa ho fatto per far vedere il link anche con la VPN <<<
sudo systemctl status firewalld
sudo firewall-cmd --permanent --add-port=5001/tcp
sudo firewall-cmd --reload
sudo firewall-cmd --list-ports

Maggiori dettagli su questa chat: https://chatgpt.com/c/688f02a0-cebc-8326-8022-c757edab1687
