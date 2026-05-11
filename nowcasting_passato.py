
# TODO
# Script che gira ogni 5 minuti.
# Controlla nella cartella plot se ci sono file di forecast più vecchi di 3 ore
# Quelli che trova:
    # li mette in una lista
    # crea le date con pandas
    # lancia lo script nowcasting.py
    # Cancella il file di forecast
    
import os
import glob
import time

import locale
locale.setlocale(locale.LC_TIME, 'it_IT.UTF-8')

import pandas as pd

cartella_forecast = './plot'
python = '/home/daniele/Scrivania/dani/bin/python'
os.chdir('/media/daniele/Daniele2TB/repo/Ens-Nowcasting_radar_FBK')

adesso = time.time()
soglia = adesso - 3 * 60 * 60
print('\n')

lista_file_forecast = glob.glob('./plot/**/forecast*', recursive=True)
lista_tempi = [os.path.getmtime(x) for x in lista_file_forecast]
lista_file_forecast_vecchi = [x for x, y in zip(lista_file_forecast, lista_tempi) if y < soglia]

print('lista_file_forecast:')
for (i, j), k in zip(enumerate(lista_file_forecast, 1), lista_tempi):
    t = (adesso - k) / 3600
    print(f'{i} {j} {round(t, 2)}')

print()

print('lista_file_forecast_vecchi:')
for i, j in enumerate(lista_file_forecast_vecchi, 1):
    print(f'{i} {j}')

print()
# ss
# Ne faccio 3 alla volta, tanto lo metto in crontab ogni 5/10 minuti
for i in lista_file_forecast_vecchi[:3]:
    anno = i.split('/')[2]
    mese = i.split('/')[3]
    giorno = i.split('/')[4]
    ora_minuti = i.split('/')[5]
    
    tempo = pd.to_datetime(f'{anno}-{mese}-{giorno} {ora_minuti[:2]}:{ora_minuti[2:]}:00') + pd.Timedelta(minutes=15)
    
    comando = f'{python} -u nowcasting.py "{str(tempo)}" >> log_passato.log 2>&1'
    print(comando)
    os.system(comando)
    
    comando = f'rm {i} >> log_passato.log 2>&1'
    print(comando)
    os.system(comando)
    
print('----------------')
