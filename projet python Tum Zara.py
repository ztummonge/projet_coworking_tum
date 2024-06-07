import requests
import pandas as pd
from pyquery import PyQuery as pq
import re
from time import sleep
from opencage.geocoder import OpenCageGeocode

# Clé API OpenCage
opencage_key = '8edf01f98f2449b2b9f845d1a9cef634'
geocoder = OpenCageGeocode(opencage_key)

url = "https://www.leportagesalarial.com/coworking/"
response = requests.get(url)
contenu_html = response.text
doc = pq(contenu_html)

# Sélectionner les liens contenant "Paris"
links = doc('a:contains("Paris")')

# liste pour stocker les informations récupérées
data = []

for link in links:
    link_url = link.attrib['href']
    link_name = link.text

    # Récupération du contenu de la page
    rep_image = requests.get(link_url)
    page_image = rep_image.text
    page = pq(page_image)

    # du titre
    titre = page('h1').text()

    # du lien de l'image principale
    url_image_principale = page('div.inner-post-entry img').attr('src')

    # de la description
    description = page('meta[name="description"]').attr('content')

    # nettoyage de texte de la page pour que le script reconnaisse les balises
    donnees = {}
    for item in page("div.inner-post-entry ul li"):
        info = pq(item).text()
        donnees[info.split(":")[0].strip()] = (info.removeprefix(info.split(":")[0] + ":").strip()).replace('\n', '').replace('\r', '').replace('\t', '').strip()

    # récupération des données
    adresse = donnees.get("Adresse")
    telephone = donnees.get("Téléphone")
    acces = donnees.get("Accès")
    site = donnees.get("Site")
    twitter = donnees.get("Twitter")
    facebook = donnees.get("Facebook")
    linkedin = donnees.get("LinkedIn")

    # le meta title et la meta description
    meta_title = page('meta[property="og:title"]').attr('content')
    meta_description = page('meta[property="og:description"]').attr('content')

    # vérif longueur du meta title inférieure à 150 caractères ou non
    title_length_ok = len(meta_title) < 150 if meta_title else False

    # date de publication de l'article
    date_publication = page('span.posted-on time.published').attr('datetime')

    # Géocodage pour obtenir la latitude et la longitude
    if adresse:
        query = adresse + ", Paris, France"
        results = geocoder.geocode(query)
        if results:
            latitude = results[0]['geometry']['lat']
            longitude = results[0]['geometry']['lng']
        else:
            latitude = None
            longitude = None
    else:
        latitude = None
        longitude = None

    # ajout des infos récupérées à la liste
    data.append([
        link_name, link_url, url_image_principale, description,
        adresse, telephone, acces, site, twitter, facebook, linkedin,
        meta_title, meta_description, title_length_ok, date_publication,
        latitude, longitude
    ])

    # temps d'attente entre chaque requête : 2 sec
    sleep(2)
    
    print("Informations récupérées pour:", titre)

# crée un DataFrame à partir des données récupérées
df = pd.DataFrame(data, columns=[
    "Nom", "URL", "Image", "Description",
    "Adresse", "Téléphone", "Accès", "Site", "Twitter", "Facebook", "LinkedIn",
    "Meta Title", "Meta Description", "Meta Title Length Less Than 150", "Date de publication",
    "Latitude", "Longitude"
])

# écriture ds le fichier xlsx
df.to_excel("listeCoworking.xlsx", index=False)
