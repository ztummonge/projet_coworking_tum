import requests
import pandas as pd
from pyquery import PyQuery as pq
import re
from time import sleep
from opencage.geocoder import OpenCageGeocode
import folium
from streamlit_folium import folium_static
import streamlit as st

def main():
    # Clé API OpenCage
    api_key = '8edf01f98f2449b2b9f845d1a9cef634'
    geocoder = OpenCageGeocode(api_key)

    url = "https://www.leportagesalarial.com/coworking/"
    response = requests.get(url)
    contenu_html = response.text
    doc = pq(contenu_html)

    # Sélectionner les liens contenant "Paris"
    links = doc('a:contains("Paris")')

    # Liste pour stocker les informations récupérées
    data = []

    for link in links:
        link_url = link.attrib['href']
        link_name = link.text

        # Récupération du contenu de la page
        rep_image = requests.get(link_url)
        page_image = rep_image.text
        page = pq(page_image)

        # Titre
        titre = page('h1').text()

        # Lien de l'image principale
        url_image_principale = page('div.inner-post-entry img').attr('src')

        # Description
        description = page('meta[name="description"]').attr('content')

        # Nettoyage de texte de la page pour que le script reconnaisse les balises
        donnees = {}
        for item in page("div.inner-post-entry ul li"):
            info = pq(item).text()
            donnees[info.split(":")[0].strip()] = (info.removeprefix(info.split(":")[0] + ":").strip()).replace('\n', '').replace('\r', '').replace('\t', '').strip()

        # Récupération des données
        adresse = donnees.get("Adresse")
        telephone = donnees.get("Téléphone")
        acces = donnees.get("Accès")
        site = donnees.get("Site")
        twitter = donnees.get("Twitter")
        facebook = donnees.get("Facebook")
        linkedin = donnees.get("LinkedIn")

        # Meta title et meta description
        meta_title = page('meta[property="og:title"]').attr('content')
        meta_description = page('meta[property="og:description"]').attr('content')

        # Vérif longueur du meta title inférieure à 150 caractères ou non
        title_length_ok = len(meta_title) < 150 if meta_title else False

        # Date de publication de l'article
        date_publication = page('span.posted-on time.published').attr('datetime')

        # Ajout des infos récupérées à la liste
        data.append([
            link_name, link_url, url_image_principale, description,
            adresse, telephone, acces, site, twitter, facebook, linkedin,
            meta_title, meta_description, title_length_ok, date_publication
        ])

        # Temps d'attente entre chaque requête : 2 sec
        sleep(2)
        
        print("Informations récupérées pour:", titre)

    # Crée un DataFrame à partir des données récupérées
    df = pd.DataFrame(data, columns=[
        "Nom", "URL", "image", "Description",
        "Adresse", "Téléphone", "Accès", "Site", "Twitter", "Facebook", "LinkedIn",
        "Meta Title", "Meta Description", "Meta Title Length Less Than 150", "Date de publication"
    ])

    # Ajout de coordonnées GPS avec OpenCage
    df['Latitude'] = None
    df['Longitude'] = None

    for index, row in df.iterrows():
        if row['Adresse']:
            query = row['Adresse']
            result = geocoder.geocode(query)
            if result and len(result) > 0:
                row['Latitude'] = result[0]['geometry']['lat']
                row['Longitude'] = result[0]['geometry']['lng']

    # Filtrer les lignes avec des coordonnées valides
    df = df.dropna(subset=['Latitude', 'Longitude'])

    # Création de la carte Folium
    map = folium.Map(location=[48.8566, 2.3522], zoom_start=12)

    # Ajout des points sur la carte
    for index, row in df.iterrows():
        if pd.notnull(row['Latitude']) and pd.notnull(row['Longitude']):
            folium.Marker(
                location=[row['Latitude'], row['Longitude']],
                popup=f"{row['Nom']}<br>{row['Adresse']}",
                tooltip=row['Nom']
            ).add_to(map)

    # Affichage avec Streamlit
    st.title("Carte des Coworkings à Paris")
    folium_static(map)

    # Écriture ds le fichier xlsx
    df.to_excel("listeCoworking.xlsx", index=False)

if __name__ == "__main__":
    main()
