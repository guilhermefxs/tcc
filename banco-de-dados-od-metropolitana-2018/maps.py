import geopandas as gpd
import pandas as pd
import folium
from folium import Choropleth, GeoJson

# Carregar o arquivo GeoJSON
geojson_path = 'ZONAS-DE-TRAFEGO-2021-sem-pontos.geojson'
gdf = gpd.read_file(geojson_path)

# Carregar o arquivo CSV
csv_path = 'resultado.csv'
df = pd.read_csv(csv_path)

# Verificar as colunas
print(gdf.columns)
print(df.columns)

# Unir os dados do CSV com o GeoDataFrame
merged = gdf.merge(df, left_on='CODIGOZONA', right_on='ZONA')

# Verificar a união
print(merged.head())

# Criar um mapa base centrado em Recife
latitude_inicial = -8.0476
longitude_inicial = -34.8770
m = folium.Map(location=[latitude_inicial, longitude_inicial], zoom_start=12)

# Adicionar os dados ao mapa com uma coloração baseada na frequência
choropleth = Choropleth(
    geo_data=merged,
    name='choropleth',
    data=merged,
    columns=['ZONA', 'FREQUENCIA'],
    key_on='feature.properties.CODIGOZONA',
    fill_color='YlOrRd',
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name='Frequência'
).add_to(m)

# Função para criar pop-ups
def style_function(feature):
    return {
        'fillOpacity': 0,
        'color': 'transparent'
    }

def highlight_function(feature):
    return {
        'fillOpacity': 0.7,
        'weight': 2,
        'color': 'blue'
    }

# Adicionar GeoJson com pop-ups
geo_json = GeoJson(
    merged,
    style_function=style_function,
    highlight_function=highlight_function,
    tooltip=folium.features.GeoJsonTooltip(
        fields=['CODIGOZONA', 'FREQUENCIA'],
        aliases=['Zona: ', 'Frequência: '],
        localize=True
    )
).add_to(m)

# Adicionar controles de camada
folium.LayerControl().add_to(m)

# Salvar o mapa em um arquivo HTML
m.save('mapa.html')
