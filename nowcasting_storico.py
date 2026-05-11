import os

import locale
locale.setlocale(locale.LC_TIME, 'it_IT.UTF-8')

import pandas as pd

cartella_forecast = './plot'
python = '~/Scrivania/daniele/ambiente_daniele/dani/bin/python'
os.chdir('/home/cfmi.arpal.org/daniele.carnevale/Scrivania/Ens-Nowcasting_radar_FBK')

lista_tempi = pd.date_range('2025-09-01 15:00:00', '2025-09-02 02:00:00', freq='5min')

for tempo in lista_tempi:
    
    comando = f'{python} -u nowcasting.py "{str(tempo)}" >> log_storico.log 2>&1'
    print(comando)
    os.system(comando)
    
print('----------------')
