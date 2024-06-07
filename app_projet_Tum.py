import pandas as pd
import folium
from streamlit_folium import folium_static
import streamlit as st

st.title("Coworkings à Paris")

@st.cache
def load_data():
    df = pd.read_excel("coworkings_paris.xlsx")
    return df

df = load_data()

map_center = [48.8566, 2.3522]  # Coordonnées de Paris
coworking_map = folium.Map(location=map_center, zoom_start=12)

for index, row in df.iterrows():
    if pd.notnull(row['Latitude']) and pd.notnull(row['Longitude']):
        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            popup=f"{row['Nom du Coworking']}<br>{row['Adresse']}",
            tooltip=row['Nom du Coworking']
        ).add_to(coworking_map)

folium_static(coworking_map)

st.dataframe(df)
