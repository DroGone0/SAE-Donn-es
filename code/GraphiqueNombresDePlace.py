import requests
import time
import os
import matplotlib.pyplot as plt

def recuperer_donnees(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de la récupération des données: {e}")
        return []

def extraire_capacite_parkings(data, type_objet):
    noms = []
    capacites = []

    for element in data:
        if type_objet == "velo" and 'totalSlotNumber' in element:
            nom = element['address']['value']['streetAddress']
            places_totales = element['totalSlotNumber']['value']
        elif type_objet == "voiture" and 'totalSpotNumber' in element:
            nom = element['name']['value']
            places_totales = element['totalSpotNumber']['value']
        else:
            continue

        noms.append(nom)
        capacites.append(places_totales)

    return noms, capacites

def tracer_diagramme_barres(noms, capacites, titre, fichier_sortie, incliner_noms=False):
    plt.figure(figsize=(10, 6))
    plt.barh(noms, capacites, color="skyblue")
    plt.xlabel("Nombre de places")
    plt.ylabel("Parkings")
    plt.title(titre)
    if incliner_noms:
        plt.yticks(rotation=5)
    plt.gca().set_yticks(plt.gca().get_yticks())  # Ajout d'espacement entre les barres
    plt.gca().set_yticklabels(noms, va="center", position=(0, 1))
    plt.tight_layout()
    plt.savefig(fichier_sortie)
    plt.close()

def generer_diagrammes_capacites():
    url_velos = "https://portail-api-data.montpellier3m.fr/bikestation?limit=1000"
    url_voitures = "https://portail-api-data.montpellier3m.fr/offstreetparking?limit=1000"

    print("Récupération des données...")

    data_velos = recuperer_donnees(url_velos)
    data_voitures = recuperer_donnees(url_voitures)

    if not data_velos or not data_voitures:
        print("Impossible de récupérer les données nécessaires pour les diagrammes.")
        return

    print("Création des diagrammes...")

    # Diagramme des parkings voitures
    noms_voitures, capacites_voitures = extraire_capacite_parkings(data_voitures, "voiture")
    dossier_graphiques = os.path.abspath("graphiques")
    fichier_voitures = os.path.join(dossier_graphiques, "parkings_voitures.png")
    tracer_diagramme_barres(noms_voitures, capacites_voitures, "Capacité des parkings voitures à Montpellier", fichier_voitures)

    # Diagramme des parkings vélos
    noms_velos, capacites_velos = extraire_capacite_parkings(data_velos, "velo")
    fichier_velos = os.path.join(dossier_graphiques, "parkings_velos.png")
    tracer_diagramme_barres(noms_velos, capacites_velos, "Capacité des parkings vélos à Montpellier", fichier_velos, incliner_noms=True)

    print(f"Diagrammes créés et enregistrés dans le dossier : {dossier_graphiques}")

if __name__ == "__main__":
    if not os.path.exists("graphiques"):
        os.makedirs("graphiques")

    generer_diagrammes_capacites()
