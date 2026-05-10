
import sys
import pickle
import os
os.chdir('/media/daniele/Daniele2TB/repo/Ens-Nowcasting_radar_FBK')

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

from cartopy.io.shapereader import Reader
from cartopy.feature import ShapelyFeature


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

states = cfeature.NaturalEarthFeature(category='cultural', name='admin_1_states_provinces_lines', scale='10m', facecolor='none')

dict_proiezione = {
    'PlateCarree': ccrs.PlateCarree(),
    'Mercator': ccrs.Mercator(), # Quella che usa Francesco Silvestro per le immagini radar
    'LambertConformal': ccrs.Orthographic(central_longitude=10, central_latitude=42),
    'Orthographic': ccrs.Orthographic(central_longitude=10, central_latitude=42),
    'EuroPP': ccrs.EuroPP(),
    'Robinson': ccrs.Robinson(),
    'NorthPolarStereo': ccrs.NorthPolarStereo(),
}

# %%
### CONFIGURAZIONE
### Posso lanciare lo script anche passandogli una data: es. "2026-01-01 00:00:00"

# from irene.convgru_ensemble import RadarLightningModel
# modello = RadarLightningModel.from_pretrained("it4lia/irene")
# pickle.dump(modello, open('./modello.pkl', 'wb'))
modello = pickle.load(open('./modello.pkl', 'rb'))

coordinate = (6.7, 10.4, 43.5, 45.1)
nome_proiezione = 'Mercator'
numero_membri, ore_previsione, ore_osservato_per_predict = 10, 2, 1
cartella_shapefile = './../../shapefile'

#################

data_str = sys.argv[1] if len(sys.argv) > 1 else None
if data_str:
    data_inizio_previsione_UTC = pd.Timestamp(data_str)
else:
    data_inizio_previsione_UTC = pd.Timestamp.today().tz_localize('Europe/Rome').tz_convert('UTC').floor('min').tz_convert(None)

# data_inizio_previsione_UTC = pd.to_datetime("2026-05-10 10:15:00")

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

ds_proj = ccrs.TransverseMercator(
    central_longitude=ds_pred.crs.attrs['longitude_of_central_meridian'],
    central_latitude=ds_pred.crs.attrs['latitude_of_projection_origin'],
    scale_factor=ds_pred.crs.attrs['scale_factor_at_central_meridian']
)

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
print(f'    {nome_proiezione=}')
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

    # Quando genero anche gli osservati devo eliminare i file .pkl perché pesano troppo
    # Devo pensare a come far partire lo stesso script ma 3 ore dopo
    # Lo faccio con lo script nowcasting_passato.py

else:
    print('    Faccio il forecast...')
    t = time.time()
    forecasts = modello.predict(ds_pred.RR, forecast_steps=int(12 * ore_previsione), ensemble_size=numero_membri)
    f_printa_tempo_trascorso(t, time.time(), '    Forecast in')
    if (t - data_inizio_previsione_UTC.timestamp()) / 3600 < 6:
        pickle.dump(forecasts, open(f'{cartella_plot}/{file_forecast}', 'wb'))

print('    Calcolo media, perc80 e massimo...')
media = np.mean(forecasts, axis=0)
perc80 = np.quantile(forecasts, axis=0, q=0.8)
massimo = np.max(forecasts, axis=0) # worst case

# %%
print('\n    Stampo le previsioni...')

nomi_shapefile = ['ita_confini', 'fra_confini', 'ita_regioni', 'zone', 'comprensori']
lista_percorsi_shapefile = [
    f'{cartella_shapefile}/gadm41_ITA_shp/gadm41_ITA_0.shp',
    f'{cartella_shapefile}/gadm41_FRA_shp/gadm41_FRA_0.shp',
    f'{cartella_shapefile}/gadm41_ITA_shp/gadm41_ITA_1.shp',
    f'{cartella_shapefile}/AreeAllerta/ZoneAllertaLiguria_wgs84_epsg4326.shp',
    f'{cartella_shapefile}/Comprensori_idrologici/ComprensoriIdrologici_Roya_wgs84_epsg4326.shp',
]

_SHAPE_CACHE = {x: None for x in nomi_shapefile}

for p, shp in zip(nomi_shapefile, lista_percorsi_shapefile):
    _SHAPE_CACHE[p] = list(Reader(shp).geometries())

def add(ax, geom, lw):
    feat = ShapelyFeature(
        geom,
        ccrs.PlateCarree(),
        facecolor='none',
        edgecolor='black',
        lw=lw
    )
    ax.add_feature(feat, zorder=0)

def f_crea_plot(args):
    
    tempo_UTC, args_ds_obs, args_media, args_perc80, args_massimo = args
    
    dict_comuni = {'cmap': cmap, 'norm': norm, 'zorder': -1}
    fig, axs = plt.subplots(2, 2, figsize=(9, 7), subplot_kw={'projection': dict_proiezione[nome_proiezione]}, gridspec_kw={'wspace': 0.01, 'hspace': 0.1})
    
    tempo_LOCAL = tempo_UTC.tz_localize('UTC').tz_convert('Europe/Rome')
    
    datasets = [args_ds_obs, args_media, args_perc80, args_massimo]
    titoli = ["Osservato", f"Media su {numero_membri} membri", "80° percentile", "Massimo"]
    titolo_UTC = f"Previsto: {tempo_UTC.strftime('%d %B %Y %H:%M')} UTC"
    titolo_LOC = f"Previsto: {tempo_LOCAL.strftime('%d %B %Y %H:%M')} locale"
    
    for ax, data, titolo in zip(axs.flat, datasets, titoli):
        
        cf = ax.contourf(ds_pred.x, ds_pred.y, data, transform=ds_proj, levels=livelli, extend='both', **dict_comuni)
        # ax.contour(ds_pred.x, ds_pred.y, data, transform=ds_proj, levels=livelli, colors='black', linewidths=0.15, zorder=dict_comuni['zorder'])

        ax.set_extent(coordinate, crs=ccrs.PlateCarree())
        
        ax.coastlines(linewidth=0.5); ax.add_feature(cfeature.BORDERS, linewidth=0.7); ax.add_feature(states, linewidth=0.1)
        add(ax, _SHAPE_CACHE['ita_confini'], 0.4); add(ax, _SHAPE_CACHE['fra_confini'], 0.4)
        add(ax, _SHAPE_CACHE['ita_regioni'], 0.2); add(ax, _SHAPE_CACHE['zone'], 0.2)
        # add(ax, _SHAPE_CACHE['comprensori'], 0.1)
        
        ax.set_title(titolo, loc='left', fontsize=9)
        if titolo == 'Osservato':
            ax.set_title(titolo_UTC, loc='right', fontsize=9)
        if titolo == f"Media su {numero_membri} membri":
            ax.set_title(titolo_LOC, loc='right', fontsize=9)
            
    fig.subplots_adjust(left=0.01, right=0.99, bottom=0.06, top=0.90, wspace=0.01, hspace=0.01)
    
    # extend='both' non serve se uso contourf
    cbar = fig.colorbar(cf, ax=axs.ravel().tolist(), orientation='horizontal', ticks=livelli, pad=0.01, fraction=0.025, aspect=50)
    
    cbar.set_ticklabels(labels)
    cbar.ax.tick_params(labelsize=8)
    cbar.ax.text(1.03, -0.96, "mm/h", transform=cbar.ax.transAxes, va='center', ha='left', fontsize=9)
    
    nome_plot = f"prev_{tempo_UTC.strftime('%Y-%m-%d_%H%M')}.png"
    plt.savefig(f"{cartella_plot}/{nome_plot}", dpi=200, bbox_inches='tight', pad_inches=0.02)
    
    ### Riduco la dimensione in kB
    ### !!! convert su Fedora/Rocky
    # comando = f'magick {cartella_plot}/{nome_plot} -strip -colors 128 {cartella_plot}/{nome_plot}'
    comando = f'magick {cartella_plot}/{nome_plot} -strip -colors 64 PNG8:{cartella_plot}/{nome_plot}'
    os.system(comando)
    
    # plt.show()
    plt.close(fig)
    
    print(f'    {nome_plot}')
    
    return nome_plot


lista_ds_obs = [ds_obs.sel(time=x).RR.values for x in tempi_previsti]
lista_media = [media[x, ...] for x in range(len(tempi_previsti))]
lista_perc80 = [perc80[x, ...] for x in range(len(tempi_previsti))]
lista_massimo = [massimo[x, ...] for x in range(len(tempi_previsti))]

from concurrent.futures import ProcessPoolExecutor

with ProcessPoolExecutor(max_workers=8) as executor:
    risultati = list(executor.map(f_crea_plot, zip(tempi_previsti, lista_ds_obs, lista_media, lista_perc80, lista_massimo)))

che_ore_sono_LOC = pd.Timestamp.today().floor('s')
che_ore_sono_UTC = che_ore_sono_LOC.tz_localize('Europe/Rome').tz_convert('UTC').tz_localize(None)
print(f"\nFatto. Sono le {che_ore_sono_UTC} UTC, {che_ore_sono_LOC} locali")
print('-----------------------------------------------------------------------\n')
