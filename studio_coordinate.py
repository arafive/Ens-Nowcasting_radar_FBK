
import os
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.colors as mcolors

from cartopy.io.shapereader import Reader
from cartopy.feature import ShapelyFeature

def f_shapefile(ax, plotta_aree_allertamento, plotta_comprensori):
    ax.add_feature(ShapelyFeature(Reader('./../../shapefile/gadm41_ITA_shp/gadm41_ITA_0.shp').geometries(), ccrs.PlateCarree(), facecolor='none', edgecolor='black', lw=0.4), alpha=1, zorder=0)
    ax.add_feature(ShapelyFeature(Reader('./../../shapefile/gadm41_ITA_shp/gadm41_ITA_1.shp').geometries(), ccrs.PlateCarree(), facecolor='none', edgecolor='black', lw=0.2), alpha=1, zorder=0)
    
    for cartella_stato in [x for x in os.listdir('./../../shapefile') if x.startswith('gadm41')]:
        stato = cartella_stato.split('_')[1]
        if stato == 'ITA':
            continue
        else:
            ax.add_feature(ShapelyFeature(Reader(f'./../../shapefile/gadm41_{stato}_shp/gadm41_{stato}_0.shp').geometries(), ccrs.PlateCarree(), facecolor='none', edgecolor='black', lw=0.4), alpha=1, zorder=0)

    if plotta_aree_allertamento:
        ax.add_feature(ShapelyFeature(Reader('./../../shapefile/AreeAllerta/ZoneAllertaLiguria_wgs84_epsg4326.shp').geometries(), ccrs.PlateCarree(), facecolor='none', edgecolor='black', lw=0.2), alpha=1, zorder=0)
    if plotta_comprensori:
        ax.add_feature(ShapelyFeature(Reader('./../../shapefile/Comprensori_idrologici/ComprensoriIdrologici_Roya_wgs84_epsg4326.shp').geometries(), ccrs.PlateCarree(), facecolor='none', edgecolor='black', lw=0.1), alpha=1, zorder=0)

# --------------------

coordinate = (6.7, 10.4, 43.5, 45.1)

states = cfeature.NaturalEarthFeature(
    category='cultural',
    name='admin_1_states_provinces_lines',
    scale='10m',
    facecolor='none'
)

username, access_key, dataset = "Daniele_Carnevale", "15fcff78d4194bc4beacda6173861e6d", "italian-radar-dpc-sri.zarr"
dataset_url = f"https://{username}:{access_key}@api.arcodatahub.com/S3/{dataset}"

ds = xr.open_dataset(dataset_url, engine="zarr").sel(time=slice('2026-05-11 10:00:00', '2026-05-11 20:00:00'))

dict_proiezione = {
    'PlateCarree': ccrs.PlateCarree(),
    'Mercator': ccrs.Mercator(), # Quella che usa Francesco Silvestro per le immagini radar
    'LambertConformal': ccrs.Orthographic(central_longitude=10, central_latitude=42),
    'Orthographic': ccrs.Orthographic(central_longitude=10, central_latitude=42),
    'EuroPP': ccrs.EuroPP(),
    'Robinson': ccrs.Robinson(),
    'NorthPolarStereo': ccrs.NorthPolarStereo(),
    }
nome_proiezione = 'Mercator'

ds_proj = ccrs.TransverseMercator(
        central_longitude=ds.crs.attrs['longitude_of_central_meridian'],
        central_latitude=ds.crs.attrs['latitude_of_projection_origin'],
        scale_factor=ds.crs.attrs['scale_factor_at_central_meridian']
        )

# %%
# --------------------

livelli = [0.2, 0.5, 1, 2, 3, 5, 7, 10, 15, 20, 25, 35, 45, 60, 75, 90, 120, 150, 180, 210]
labels = [str(x) for x in [0.2, 0.5, 1, 2, 3, 5, 7, 10, 15, 20, 25, 35, 45, 60, 75, 90, 120, 150, 180, 210]]
colori = ['#ffffff', '#e0ebff', '#b5c9ff', '#8eb2ff', '#7f96ff', '#6370f7', '#009f1e', '#3cbc3d', '#b9f96e', '#fff914', '#fac81e', '#eb9628', '#fa3c3c', '#cd005a', '#b400b4', '#9600c8', '#a064dc', '#be8cc8', '#e1afc3', '#e1c8be', '#f0dce1']

cmap = mcolors.ListedColormap(colori[1:-1])
cmap.set_under(colori[0])
cmap.set_over(colori[-1])
norm = mcolors.BoundaryNorm(livelli, cmap.N)
dict_comuni = {'cmap': cmap, 'norm': norm, 'zorder': -1}

for i in range(100, 110):
    fig, ax = plt.subplots(figsize=(9, 9), subplot_kw={'projection': dict_proiezione[nome_proiezione]})
    
    ax.set_extent(coordinate, crs=ccrs.PlateCarree())
    
    ax.coastlines(linewidth=0.5); ax.add_feature(states, linewidth=0.2); ax.add_feature(cfeature.BORDERS, linewidth=0.4)
    # f_shapefile(ax, True, True) # È troppo lento
    
    is_all_nan = np.isnan(ds.RR.isel(time=i).values).all()
    if is_all_nan:
        lon_min, lon_max, lat_min, lat_max = coordinate
    
        ax.fill(
            [lon_min, lon_max, lon_max, lon_min],
            [lat_min, lat_min, lat_max, lat_max],
            color='darkgrey',
            transform=ccrs.PlateCarree(),
            zorder=-10
        )
        
    else:
        # cf = ax.contourf(ds.x, ds.y, ds.RR.isel(time=i), transform=ds_proj, extend='both', **dict_comuni)
        pcm = ax.pcolormesh(ds.x, ds.y, ds.RR.isel(time=i), transform=ds_proj, **dict_comuni)
    
    plt.title(f'{coordinate=}, {nome_proiezione=}', loc='left', fontsize=9)
    plt.show()
    plt.close()
