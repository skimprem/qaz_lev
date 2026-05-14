import os
import pandas as pd
import geopandas as gpd
import requests
import folium
import json
from folium.plugins import MeasureControl, MousePosition, LocateControl
from transliterate import translit 
import uuid
import zipfile


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

unchecked_path = os.path.join('data', 'source', 'unchecked.gpkg')
unchecked_gdf = gpd.read_file(unchecked_path, layer='unchecked')
# unchecked_gdf['guid'] = unchecked_gdf.apply(lambda x: uuid.uuid4(), axis=1)
# unchecked_gdf.to_file(os.path.join('data', 'source', 'unchecked.gpkg'), driver='GPKG', layer='unchecked')

unchecked_gdf.drop(
    columns=[
       'sign_height', 'triangulation_order',
       'northing', 'easting', 'geodetic_height',
       'nomenclature', 'zone',
       'coordinate_catalog_name', 'coordinate_catalog_number',
       'summary_catalog_name', 'summary_catalog_number',
       'technical_report_name', 'technical_report_number',
       'technical_report_name_1', 'technical_report_number_1', 'lon',
       'lat', 'unknown_25', 'ground_location',
       'Месторасположения контрольного репера',
       'Название сводного каталога высот пункта нивелирования, инв. №, год издания',
       'Unnamed: 26', 'Unnamed: 27', 'Unnamed: 28', 'Unnamed: 29',
       'Unnamed: 30', 'Unnamed: 31', 'Unnamed: 32', 'Unnamed: 33',
       'Unnamed: 34', 'Unnamed: 35', 'Unnamed: 36', 'Unnamed: 37',
       'Unnamed: 38', 'Unnamed: 39', 'Unnamed: 40', 'Unnamed: 41',
       'Unnamed: 42', 'Unnamed: 43', 'Unnamed: 44', 'Unnamed: 45',
       'Unnamed: 46', 'Unnamed: 47', 'Unnamed: 48', 'Unnamed: 49',
       'Unnamed: 50', 'Unnamed: 51', 'Unnamed: 52', 'Unnamed: 53',
       'Unnamed: 54', 'Unnamed: 55'
    ], inplace=True)
 
checked_path = os.path.join('data', 'source', 'gns_1_2.gpkg')
checked_gdf = gpd.read_file(checked_path, layer='gns_1_2')

select_path = os.path.join('data', 'source', 'selected.geojson')
select_gdf = gpd.read_file(select_path)

select_gdf.drop(
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

checked_gdf = checked_gdf[
    (checked_gdf['not_found'] != True) & \
    (checked_gdf['lost'] != True)]

checked_gdf.drop(
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

checked_gdf['kml'] = checked_gdf.apply(lambda row: os.path.join('data', 'stations', f"{str(row['guid'])[:8]}.kml"), axis=1)
checked_gdf['kml_link'] = checked_gdf.apply(
    lambda row: f"<a href='{row['kml']}' target='_blank'>Download KML</a>",
    axis=1
)

# for idx, row in checked_gdf.iterrows():

#     station_gdf = gpd.GeoDataFrame(
#         row.to_frame().T,
#         geometry='geometry',
#         crs=checked_gdf.crs
#     )
    
#     if not os.path.exists(row['kml']):
#         station_gdf.to_file(row['kml'], driver='KML')

unchecked_gdf['kml'] = unchecked_gdf.apply(lambda row: os.path.join('data', 'stations', f"{str(row['guid'])[:8]}.kml"), axis=1)
unchecked_gdf['kml_link'] = unchecked_gdf.apply(
    lambda row: f"<a href='{row['kml']}' target='_blank'>Download KML</a>",
    axis=1
)

# for idx, row in unchecked_gdf.iterrows():

#     station_gdf = gpd.GeoDataFrame(
#         row.to_frame().T,
#         geometry='geometry',
#         crs=unchecked_gdf.crs
#     )
    
#     if not os.path.exists(row['kml']):
#         station_gdf.to_file(row['kml'], driver='KML')

index_map = folium.Map(
    location=[48.0, 68.0],  # Центр Казахстана
    zoom_start=5,
    tiles=None
)

# Добавить CartoDB Positron с правильным названием
folium.TileLayer(
    tiles='CartoDB positron',
    name='CartoDB Positron',
    overlay=False,
    control=True
).add_to(index_map)

# Опционально: добавить другие варианты
folium.TileLayer(
    tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
    attr='Google',
    name='Google Satellite',
    overlay=False,
    control=True
).add_to(index_map)

kazakhstan.explore(
    m=index_map,
    name='Kazakhstan Border',
    zoom_start=5,
    tooltip=False,
    popup=False,
    style_kwds={
        'color': 'black',
        'weight': 2,
        'fillOpacity': 0.0,
        'fill': False
    },
    highlight_kwds={
        'fillOpacity': 0.0,
        'fill': False
    }
)

unchecked_gdf[unchecked_gdf.geometry.notna() & ~unchecked_gdf.geometry.is_empty].explore(
    m=index_map,
    name='Unchecked Stations',
    color='blue',
    marker_kwds={'radius': 3},
    tooltip='name',
    popup=True
)

checked_gdf[checked_gdf.geometry.notna() & ~checked_gdf.geometry.is_empty].explore(
    m=index_map,
    name='Checked Stations',
    color='green',
    marker_kwds={'radius': 3},
    tooltip='title',
    popup=True
)

selected_data = select_gdf[select_gdf.geometry.notna() & ~select_gdf.geometry.is_empty]
selected_fg = folium.FeatureGroup(name='Selected Stations')
selected_geojson = folium.GeoJson(
    selected_data,
    marker=folium.CircleMarker(
        radius=3, fill=True,
        fill_color='red', color='red', fill_opacity=0.5
    ),
    tooltip=folium.GeoJsonTooltip(fields=['name']),
    popup=folium.GeoJsonPopup(fields=[
        'longitude', 'latitude', 'name', 'point_type', 'exterior_design',
        'leveling_order', 'height', 'height_type',
        'control_benchmark_height', 'control_benchmark_location',
        'benchmark_number', 'benchmark_type', 'leveling_line',
        'location_description', 'point_name', 'normal_height',
        'mark_number', 'center_type'
    ])
)
selected_geojson.add_to(selected_fg)
selected_fg.add_to(index_map)

folium.LayerControl().add_to(index_map)

MeasureControl(
    position='topleft',
    primary_length_unit='meters',
    secondary_length_unit='kilometers',
    primary_area_unit='sqmeters',
    secondary_area_unit='sqkilometers'
).add_to(index_map)

# Комбинированный поисковый индекс по всем слоям (без дополнительных Leaflet-слоёв)
def build_search_index(unchecked, checked, selected):
    data = []
    for gdf, name_col, desc_col in [
        (unchecked, 'name', 'location_description'),
        (checked, 'title', 'description'),
        (selected, 'name', 'location_description')
    ]:
        mask = gdf.geometry.notna() & ~gdf.geometry.is_empty
        for _, row in gdf[mask].iterrows():
            n = row.get(name_col)
            if n and str(n).strip():
                desc = row.get(desc_col)
                data.append({
                    'name': str(n),
                    'desc': str(desc) if desc and str(desc) not in ('None', 'nan', '') else '',
                    'lat': round(row.geometry.y, 6),
                    'lng': round(row.geometry.x, 6)
                })
    return data

search_index = build_search_index(
    unchecked_gdf, checked_gdf, selected_data
)
search_json = json.dumps(search_index, ensure_ascii=False)
map_var = index_map.get_name()

custom_search = f'''
<style>
.custom-search-wrap {{
    position: absolute;
    top: 10px;
    left: 45px;
    z-index: 1000;
    background: white;
    border-radius: 4px;
    padding: 6px 8px;
    box-shadow: 0 1px 5px rgba(0,0,0,0.4);
    font-family: sans-serif;
    font-size: 13px;
    width: 240px;
}}
.custom-search-wrap input {{
    width: 100%;
    box-sizing: border-box;
    border: 1px solid #ccc;
    border-radius: 3px;
    padding: 4px 6px;
    font-size: 13px;
    outline: none;
}}
.custom-search-results {{
    max-height: 180px;
    overflow-y: auto;
    margin-top: 4px;
}}
.custom-search-results div {{
    padding: 4px 6px;
    cursor: pointer;
    border-radius: 3px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}}
.custom-search-results div:hover {{
    background: #e8f4f8;
}}
</style>
<div class="custom-search-wrap leaflet-control">
    <input id="cs-input" type="text" placeholder="Поиск по названию...">
    <div class="custom-search-results" id="cs-results"></div>
</div>
<script>
(function() {{
    var searchData = {search_json};
    var input = document.getElementById('cs-input');
    var results = document.getElementById('cs-results');

    input.addEventListener('input', function() {{
        var q = this.value.trim().toLowerCase();
        results.innerHTML = '';
        if (q.length < 2) return;
        var matches = searchData.filter(function(d) {{
            return d.name.toLowerCase().indexOf(q) !== -1;
        }}).slice(0, 20);
        matches.forEach(function(d) {{
            var el = document.createElement('div');
            var nameSpan = document.createElement('span');
            nameSpan.textContent = d.name;
            el.appendChild(nameSpan);
            if (d.desc) {{
                var descSpan = document.createElement('span');
                descSpan.textContent = '  ' + d.desc;
                descSpan.style.cssText = 'color:#aaa; font-size:11px; margin-left:6px;';
                el.appendChild(descSpan);
            }}
            el.title = d.name + (d.desc ? ' — ' + d.desc : '');
            el.addEventListener('click', function() {{
                var mapObj = window["{map_var}"];
                if (mapObj) mapObj.setView([d.lat, d.lng], 14);
                input.value = d.name;
                results.innerHTML = '';
            }});
            results.appendChild(el);
        }});
    }});

    document.addEventListener('click', function(e) {{
        if (!e.target.closest('.custom-search-wrap')) {{
            results.innerHTML = '';
        }}
    }});
}})();
</script>
'''

index_map.get_root().html.add_child(folium.Element(custom_search))


MousePosition(
    position='bottomleft',
    separator=' | ',
    prefix='Координаты:'
).add_to(index_map)

LocateControl(
    position='topleft',
    strings={'title': 'Моё местоположение'}
).add_to(index_map)

index_map.save(os.path.join('index.html'))
