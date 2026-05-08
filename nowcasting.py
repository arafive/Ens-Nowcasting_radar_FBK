
import sys
import pickle
import os

import locale
locale.setlocale(locale.LC_TIME, 'it_IT.UTF-8')

import time
import xarray as xr
import numpy as np
import pandas as pd
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

from datetime import timedelta
os.chdir('/media/daniele/Daniele2TB/repo/Ens-Nowcasting_radar_FBK/irene')
from irene.convgru_ensemble import RadarLightningModel
os.chdir('/media/daniele/Daniele2TB/repo/Ens-Nowcasting_radar_FBK')


def f_printa_tempo_trascorso(t_inizio, t_fine, nota=False):
    """Printa il tempo trascorso."""
    elapsed_tempo = timedelta(seconds=t_fine - t_inizio)

    giorni = f'{elapsed_tempo.days:01}'
    ore = f'{elapsed_tempo.seconds // 3600:02}'
    minuti = f'{elapsed_tempo.seconds // 60 % 60:02}'
    secondi = f'{elapsed_tempo.seconds % 60:02}'
    millisecondi = elapsed_tempo.microseconds / 1000

    msg = f'{int(secondi)}.{int(millisecondi)} sec'

    if int(minuti) > 0:
        msg = f'{minuti}:{secondi} min'

    if int(ore) > 0:
        msg = f'{ore}:{minuti}:{secondi} ore'

    if int(giorni) > 0:
        if int(giorni) == 1:
            msg = f'{giorni} giorno, {ore}:{minuti}:{secondi} ore'
        else:
            msg = f'{giorni} giorni, {ore}:{minuti}:{secondi} ore'

    if nota:
        msg = f'{nota}: {msg}'

    print(msg)


livelli = [0.2, 0.5, 1, 2, 3, 5, 7, 10, 15, 20, 25, 35, 45, 60, 75, 90, 120, 150, 180, 210]
labels = [str(x) for x in [0.2, 0.5, 1, 2, 3, 5, 7, 10, 15, 20, 25, 35, 45, 60, 75, 90, 120, 150, 180, 210]]
colori = ['#ffffff', '#e0ebff', '#b5c9ff', '#8eb2ff', '#7f96ff', '#6370f7', '#009f1e', '#3cbc3d', '#b9f96e', '#fff914', '#fac81e', '#eb9628', '#fa3c3c', '#cd005a', '#b400b4', '#9600c8', '#a064dc', '#be8cc8', '#e1afc3', '#e1c8be', '#f0dce1']

cmap = mcolors.ListedColormap(colori[1:-1])
cmap.set_under(colori[0])
cmap.set_over(colori[-1])
norm = mcolors.BoundaryNorm(livelli, cmap.N)

username, access_key, dataset = "Daniele_Carnevale", "15fcff78d4194bc4beacda6173861e6d", "italian-radar-dpc-sri.zarr"
dataset_url = f"https://{username}:{access_key}@api.arcodatahub.com/S3/{dataset}"

states = cfeature.NaturalEarthFeature(
    category='cultural',
    name='admin_1_states_provinces_lines',
    scale='10m',
    facecolor='none'
)

# TODO Aggiungi il bottone "Ultima previsione"

# FATTO Riduci la dimensione in kb delle immagini
# FATTO Aggiungi "sono le ore UTC" nell'html
# FATTO Salva le previsioni in un .pkl

# %%
### CONFIGURAZIONE
### Posso lanciare lo script anche passandogli una data: es. "2026-01-01 00:00:00"

modello = RadarLightningModel.from_pretrained("it4lia/irene")
coordinate = (7.2, 10.3, 43.4, 45.5)
numero_membri, ore_previsione, ore_osservato_per_predict = 10, 2, 1

#################

data_str = sys.argv[1] if len(sys.argv) > 1 else None
if data_str:
    data_inizio_previsione_UTC = pd.Timestamp(data_str)
else:
    data_inizio_previsione_UTC = pd.Timestamp.today().tz_localize('Europe/Rome').tz_convert('UTC').floor('min').tz_convert(None)

# data_inizio_previsione_UTC = pd.to_datetime('2026-05-06 15:30')

data_inizio_previsione_UTC = (data_inizio_previsione_UTC - pd.Timedelta(minutes=15)).tz_localize('UTC')
data_inizio_previsione_LOC = data_inizio_previsione_UTC.tz_convert('Europe/Rome')

ds_pred = xr.open_dataset(dataset_url, engine="zarr").sel(
    time=slice(data_inizio_previsione_UTC.tz_convert(None) - pd.Timedelta(hours=ore_osservato_per_predict),
               data_inizio_previsione_UTC.tz_convert(None))
)

ds_obs = xr.open_dataset(dataset_url, engine="zarr").sel(
    time=slice(data_inizio_previsione_UTC.tz_convert(None),
               data_inizio_previsione_UTC.tz_convert(None) + pd.Timedelta(hours=ore_previsione))
)

cartella_plot = f"plot/{data_inizio_previsione_UTC.strftime('%Y/%m/%d/%H%M')}"
os.makedirs(cartella_plot, exist_ok=True)

#################

che_ore_sono_LOC = pd.Timestamp.today().floor('s')
che_ore_sono_UTC = che_ore_sono_LOC.tz_localize('Europe/Rome').tz_convert('UTC').tz_localize(None)
print(f"\nSono le {che_ore_sono_UTC} UTC, {che_ore_sono_LOC} locali\n")

print('Configurazione')
print(f"    Ora UTC: {data_inizio_previsione_UTC}")
print(f"    Ora LOC: {data_inizio_previsione_LOC}")
print()
print(f'    {numero_membri=}')
print(f'    {ore_previsione=}')
print(f'    {ore_osservato_per_predict=}')
print(f'    {cartella_plot=}')
print()

print('    Istanti usati per il predict:')
istanti_usati_per_predict = list(pd.to_datetime(ds_pred.time.values))[::-1]
print(f"    {istanti_usati_per_predict[0]} UTC - {istanti_usati_per_predict[0].tz_localize('UTC').tz_convert('Europe/Rome').tz_localize(None)} LOC")
print("    ...")
print(f"    {istanti_usati_per_predict[-1]} UTC - {istanti_usati_per_predict[-1].tz_localize('UTC').tz_convert('Europe/Rome').tz_localize(None)} LOC")

tempi_previsti = pd.date_range(pd.to_datetime(ds_pred.time.values[-1]) + pd.Timedelta(minutes=5), freq='5min', periods=int(12 * ore_previsione))
print('\n    Tempi previsti:')
print(f"    {tempi_previsti[0]} UTC - {tempi_previsti[0].tz_localize('UTC').tz_convert('Europe/Rome').tz_localize(None)} LOC")
print("    ...")
print(f"    {tempi_previsti[-1]} UTC - {tempi_previsti[-1].tz_localize('UTC').tz_convert('Europe/Rome').tz_localize(None)} LOC")
print()

""" La logica che c'è dietro il predict è questa
    Gli passo gli istanti dentro ds_pred.
    Es UTC. 2026-05-06 15:15:00, 2026-05-06 15:10:00, ... 2026-05-06 14:15:00. Gli ho passato in questo caso 1 ora
    
    Il predict prevede {ore_previsione} ore, dove il primo istante previsto sarà il 2026-05-06 15:15:00 + 5min
    Es UTC. 2026-05-06 15:20:00, 2026-05-06 15:25:00 ... che si troveranno nella cartella 2026/05/06/1515
    
    Possiamo dire che 2026/05/06/1515 è la cartella col nome dell'analisi

"""

# %%
file_forecast = f'forecasts_n{numero_membri}_tp{ore_previsione}_to{ore_osservato_per_predict}.pkl'

if os.path.exists(f'{cartella_plot}/{file_forecast}'):
    print('    Trovato file del forecast')
    forecasts = pickle.load(open(f'{cartella_plot}/{file_forecast}', 'rb'))
    tempo_file_forecast = os.path.getmtime(f'{cartella_plot}/{file_forecast}')

    if time.time() - tempo_file_forecast > 6 * 60 * 60:
        print("    Il file è più vecchio di 6 ore. Lo elimino e genero le nuove immagini con gli osservati.")
        # os.system(f'rm {cartella_plot}/{file_forecast}')
        
        # TODO Quando genero anche gli osservati devo eliminare i file .pkl perché pesano troppo
        # Devo pensare a come far partire lo stesso script ma 6 ore dopo

else:
    print('    Faccio il forecast...')
    t = time.time()
    forecasts = modello.predict(ds_pred.RR, forecast_steps=int(12 * ore_previsione), ensemble_size=numero_membri)
    f_printa_tempo_trascorso(t, time.time(), '    Forecast in')
    pickle.dump(forecasts, open(f'{cartella_plot}/{file_forecast}', 'wb'))

print('    Calcolo media, perc80 e massimo...')
media = np.mean(forecasts, axis=0)
perc80 = np.quantile(forecasts, axis=0, q=0.8)
massimo = np.max(forecasts, axis=0) # worst case

# %%
print('\n    Stampo le previsioni...')

dict_comuni = {'levels': livelli, 'extend': 'both', 'cmap': cmap, 'norm': norm, 'zorder': -1}

for i, tempo_UTC in enumerate(tempi_previsti):
    fig, axs = plt.subplots(2, 2, figsize=(9, 7), subplot_kw={'projection': ccrs.PlateCarree()}, gridspec_kw={'wspace': 0.01, 'hspace': 0.1})
    
    tempo_LOCAL = tempo_UTC.tz_localize('UTC').tz_convert('Europe/Rome')
    
    datasets = [ds_obs.sel(time=tempo_UTC).RR, media[i, ...], perc80[i, ...], massimo[i, ...]]
    titoli = ["Osservato", f"Media su {numero_membri} membri", "80° percentile", "Massimo"]
    titolo_UTC = f"Previsto: {tempo_UTC.strftime('%d %B %Y %H:%M')} UTC"
    titolo_LOC = f"Previsto: {tempo_LOCAL.strftime('%d %B %Y %H:%M')} locale"
    
    cf = None
    
    for ax, data, titolo in zip(axs.flat, datasets, titoli):
        cf = ax.contourf(ds_pred.lon, ds_pred.lat, data, **dict_comuni)
    
        ax.contour(ds_pred.lon, ds_pred.lat, data, levels=livelli, colors='black', linewidths=0.2)
        ax.set_extent(coordinate, crs=ccrs.PlateCarree())
        ax.coastlines(linewidth=0.5)
        ax.add_feature(cfeature.BORDERS, linewidth=0.4)
        ax.add_feature(states, linewidth=0.2)
        ax.set_title(titolo, loc='left', fontsize=9)
        if titolo == 'Osservato':
            ax.set_title(titolo_UTC, loc='right', fontsize=9)
        if titolo == f"Media su {numero_membri} membri":
            ax.set_title(titolo_LOC, loc='right', fontsize=9)
            
    fig.subplots_adjust(
        left=0.01,
        right=0.99,
        bottom=0.06,
        top=0.90,
        wspace=0.01,
        hspace=0.01
    )
    
    cbar = fig.colorbar(
        cf,
        ax=axs.ravel().tolist(),
        orientation='horizontal',
        ticks=livelli,
        pad=0.01,
        fraction=0.025,
        aspect=50
    )
    
    cbar.set_ticklabels(labels)
    cbar.ax.tick_params(labelsize=8)
    
    cbar.ax.text(
        1.03, -1,
        "mm/h",
        transform=cbar.ax.transAxes,
        va='center',
        ha='left',
        fontsize=9
    )
    
    nome_plot = f"prev_{tempo_UTC.strftime('%Y-%m-%d_%H%M')}.png"
    plt.savefig(
        f"{cartella_plot}/{nome_plot}",
        dpi=200,
        bbox_inches='tight',
        pad_inches=0.02
    )
    
    ### Riduco la dimensione in kB
    comando = f'magick {cartella_plot}/{nome_plot} -strip -colors 128 {cartella_plot}/{nome_plot}'
    os.system(comando)
    
    # plt.show()
    plt.close()
    
che_ore_sono_LOC = pd.Timestamp.today().floor('s')
che_ore_sono_UTC = che_ore_sono_LOC.tz_localize('Europe/Rome').tz_convert('UTC').tz_localize(None)
print(f"\nFatto. Sono le {che_ore_sono_UTC} UTC, {che_ore_sono_LOC} locali")
print('-----------------------------------------------------------------------\n')
