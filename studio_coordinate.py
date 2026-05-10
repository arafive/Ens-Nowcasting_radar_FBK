
import os
import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

from cartopy.io.shapereader import Reader
from cartopy.feature import ShapelyFeature

def f_shapefile(ax, plotta_aree_allertamento, plotta_comprensori):
    ax.add_feature(ShapelyFeature(Reader('./../../shapefile/gadm41_ITA_shp/gadm41_ITA_0.shp').geometries(), ccrs.PlateCarree(), facecolor='none', edgecolor='black', lw=0.6), alpha=1, zorder=0)
    ax.add_feature(ShapelyFeature(Reader('./../../shapefile/gadm41_ITA_shp/gadm41_ITA_1.shp').geometries(), ccrs.PlateCarree(), facecolor='none', edgecolor='black', lw=0.3), alpha=1, zorder=0)
    
    for cartella_stato in [x for x in os.listdir('./../../shapefile') if x.startswith('gadm41')]:
        stato = cartella_stato.split('_')[1]
        if stato == 'ITA':
            continue
        else:
            ax.add_feature(ShapelyFeature(Reader(f'./../../shapefile/gadm41_{stato}_shp/gadm41_{stato}_0.shp').geometries(), ccrs.PlateCarree(), facecolor='none', edgecolor='black', lw=0.6), alpha=1, zorder=0)

    if plotta_aree_allertamento:
        ax.add_feature(ShapelyFeature(Reader('./../../shapefile/AreeAllerta/ZoneAllertaLiguria_wgs84_epsg4326.shp').geometries(), ccrs.PlateCarree(), facecolor='none', edgecolor='black', lw=0.3), alpha=1, zorder=0)
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

ds = xr.open_dataset(dataset_url, engine="zarr").sel(time=slice('2025-09-01 18:00:00', '2025-09-02 02:00:00'))

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

# --------------------

fig, ax = plt.subplots(figsize=(9, 9), subplot_kw={'projection': dict_proiezione[nome_proiezione]})

ax.set_extent(coordinate, crs=ccrs.PlateCarree())

ax.coastlines(linewidth=0.5); ax.add_feature(states, linewidth=0.2); ax.add_feature(cfeature.BORDERS, linewidth=0.4)
# f_shapefile(ax, True, False)

pcm = ax.pcolormesh(
    ds.x,
    ds.y,
    ds.RR.isel(time=0),
    transform=ds_proj,
    shading='auto'
)

plt.title(f'{coordinate=}, {nome_proiezione=}', loc='left', fontsize=9)
plt.show()
plt.close()
