import os
import pandas as pd
import geopandas as gpd
import requests
import folium
from transliterate import translit 


url = "https://naturalearth.s3.amazonaws.com/110m_cultural/ne_110m_admin_0_countries.zip"
zip_path = "countries.zip"
extract_path = "data/ne_countries"

if not os.path.exists(extract_path):
    os.makedirs(extract_path, exist_ok=True)
    r = requests.get(url)
    with open(zip_path, "wb") as f:
        f.write(r.content)

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_path)

world = gpd.read_file(f"{extract_path}/ne_110m_admin_0_countries.shp")
kazakhstan = world[world['ADMIN'] == 'Kazakhstan']

source_path = os.path.join('data', 'source', 'gns_1_2.gpkg')
source = gpd.read_file(source_path, layer='gns_1_2')

select_path = os.path.join('data', 'source', 'selected.geojson')
select = gpd.read_file(select_path)

print(select.columns)

select.drop(
    columns=[
       'coords_source', 'exterior_design_height', 'leveling_catalog_name',
       'leveling_catalog_number', 'triang_catalog_name',
       'triang_catalog_number', 'status', 'status_description', 'creator',
       'object_code', 'guid', 'notes', 'coordinate_accuracy', 'surveyed',
       'point_view', 'extension_mark_height',
       'triangulation_order', 'n', 'e', 'ellip_height',
       'leveling_line_section', 'cell', 'zone',
       'catalog_name', 'number_by_catalog', 'summary_catalog_name',
       'number_by_summary_catalog', 'technical_report',
       'number_by_technical_report', 'ground_benchmark_location',
       'Unnamed: 25', 'lon', 'lat', 'unused_25', 'layer', 'path'
    ],
    inplace=True
)

gdf = source[
    (source['not_found'] != True) & \
    (source['lost'] != True)]

gdf.drop(
    columns=[
        'not_found',
        'lost',
        'ext_sign_height',
        'class',
        'x',
        'y',
        'height_tr',
        'sheet',
        'zone',
        'catalog_tr', 'num_in_cat_tr', 'catalog_lvl', 'num_in_cat_lvl',
        'teh_otchet', 'num_in_teh', 'status', 'filial', 'zone_calc', 'obj_code',
        'layer', 'notes', 'no_coordinates', 'available', 'duplicate',
        'created_by', 'created_at', 'updated_by', 'updated_at', 'f_updated_by',
        'f_updated_at', 'longitude', 'latitude', 'altitude', 'hor_accuracy',
        'confirmed', 'lost', 'not_found', 'accepted', 'work_filial',
        'team_code', 'surveyed', 'has_errors', 'checked', 'path'
    ], inplace=True)

gdf['kml'] = gdf.apply(lambda row: os.path.join('data', 'stations', f"{str(row['guid'])[:8]}.kml"), axis=1)
gdf['kml_link'] = gdf.apply(
    lambda row: f"<a href='{row['kml']}' target='_blank'>Download KML</a>",
    axis=1
)

for idx, row in gdf.iterrows():

    station_gdf = gpd.GeoDataFrame(
        row.to_frame().T,
        geometry='geometry',
        crs=gdf.crs
    )
    
    if not os.path.exists(row['kml']):
        station_gdf.to_file(row['kml'], driver='KML')

index_map = kazakhstan.explore(
    color='none',
    tiles='CartoDB positron',
    zoom_start=5,
    tooltip=False,
    style_kwds={
    "color": "black",     # Set border (edge) color to black
    "weight": 2,          # Increase border thickness
    "fillOpacity": 0.6    # Transparency of the fill
    }
)

index_map = gdf.explore(
    m=index_map,
    color='green',
    marker_kwds={'radius': 3},
    tooltip=['title'],
    popup=True
)

index_map = select.explore(
    m=index_map,
    color='red',
    marker_kwds={'radius': 3},
    tooltip=['name'],
    popup=True
)

index_map.save(os.path.join('index.html'))
