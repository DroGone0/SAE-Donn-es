import requests
import time
import os
import matplotlib.pyplot as plt
from collections import defaultdict

def recuperer_donnees(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de la récupération des données: {e}")
        return []

def calculer_statistiques(data, type_objet):
    statistiques = []
    total_places = 0
    total_utilisees = 0

    for element in data:
        if type_objet == "velo" and 'availableBikeNumber' in element and 'totalSlotNumber' in element:
            nom = element['address']['value']['streetAddress']
            places_libres = element['availableBikeNumber']['value']
            places_totales = element['totalSlotNumber']['value']
        elif type_objet == "voiture" and 'availableSpotNumber' in element and 'totalSpotNumber' in element:
            nom = element['name']['value']
            places_libres = element['availableSpotNumber']['value']
            places_totales = element['totalSpotNumber']['value']
        else:
            continue

        places_utilisees = places_totales - places_libres
        pourcentage_utilise = (places_utilisees / places_totales) * 100 if places_totales > 0 else 0
        statut = element['status']['value'] if 'status' in element else "inconnu"

        statistiques.append({
            "nom": nom,
            "places_totales": places_totales,
            "places_utilisees": places_utilisees,
            "pourcentage_utilise": pourcentage_utilise,
            "statut": statut
        })

        total_places += places_totales
        total_utilisees += places_utilisees

    moyenne_utilisees = (total_utilisees / total_places) * 100 if total_places > 0 else 0
    return statistiques, moyenne_utilisees

def tracer_graphiques_horaires(moyennes_velos, moyennes_voitures, timestamp):
    plt.figure()
    plt.plot(range(len(moyennes_velos)), moyennes_velos, label="Vélos", marker="o")
    plt.plot(range(len(moyennes_voitures)), moyennes_voitures, label="Voitures", marker="s")
    plt.xlabel("Minutes (échantillons horaires)")
    plt.ylabel("Pourcentage d'occupation moyen (%)")
    plt.title(f"Moyennes d'occupation pour l'heure {timestamp}")
    plt.legend()
    plt.grid()
    plt.savefig(f"graphiques/moyennes_horaires_{timestamp}.png")
    plt.close()

def tracer_graphiques_final(moyennes_horaires_velos, moyennes_horaires_voitures, heures):
    plt.figure()
    plt.plot(heures, moyennes_horaires_velos, label="Vélos", marker="o")
    plt.plot(heures, moyennes_horaires_voitures, label="Voitures", marker="s")
    plt.xlabel("Heures")
    plt.ylabel("Pourcentage d'occupation moyen (%)")
    plt.title("Moyennes d'occupation par heure (24h)")
    plt.legend()
    plt.grid()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("graphiques/moyennes_24h.png")
    plt.close()

def suivi_combiner_statistiques(fichier_sortie):
    url_velos = "https://portail-api-data.montpellier3m.fr/bikestation?limit=1000"
    url_voitures = "https://portail-api-data.montpellier3m.fr/offstreetparking?limit=1000"

    print("\nDébut du suivi des parkings pour 24 heures...")

    duree = 86400  # 24 heures
    periode = 600  # 10 minutes
    debut = time.time()
    moyennes_velos = []
    moyennes_voitures = []
    moyennes_horaires_velos = []
    moyennes_horaires_voitures = []
    heures = []
    echantillons_horaires_velos = []
    echantillons_horaires_voitures = []

    while time.time() - debut < duree:
        data_velos = recuperer_donnees(url_velos)
        data_voitures = recuperer_donnees(url_voitures)

        if not data_velos or not data_voitures:
            print("Impossible de récupérer les données nécessaires.")
            time.sleep(periode)
            continue

        _, moyenne_velos = calculer_statistiques(data_velos, "velo")
        _, moyenne_voitures = calculer_statistiques(data_voitures, "voiture")

        moyennes_velos.append(moyenne_velos)
        moyennes_voitures.append(moyenne_voitures)
        echantillons_horaires_velos.append(moyenne_velos)
        echantillons_horaires_voitures.append(moyenne_voitures)

        heure_actuelle = time.strftime('%H:%M')
        if len(echantillons_horaires_velos) == 6:  # Une heure complète (6 échantillons de 10 min)
            moyennes_horaires_velos.append(sum(echantillons_horaires_velos) / len(echantillons_horaires_velos))
            moyennes_horaires_voitures.append(sum(echantillons_horaires_voitures) / len(echantillons_horaires_voitures))
            heures.append(heure_actuelle)

            tracer_graphiques_horaires(echantillons_horaires_velos, echantillons_horaires_voitures, heure_actuelle)
            echantillons_horaires_velos.clear()
            echantillons_horaires_voitures.clear()

        time.sleep(periode)

    tracer_graphiques_final(moyennes_horaires_velos, moyennes_horaires_voitures, heures)
    print("\nSuivi terminé. Les données ont été enregistrées dans les fichiers de sortie.")

if __name__ == "__main__":
    fichier_sortie = "statistiques_parkings.txt"
    if not os.path.exists("graphiques"):
        os.makedirs("graphiques")

    suivi_combiner_statistiques(fichier_sortie)
