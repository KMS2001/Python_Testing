import json
from flask import Flask, render_template, request, redirect, flash, url_for
from datetime import datetime

# Chargement des données depuis les fichiers JSON
def loadClubs():
    with open('clubs.json') as c:
        return json.load(c)['clubs']

def loadCompetitions():
    with open('competitions.json') as comps:
        listOfCompetitions = json.load(comps)['competitions']
        # Convertir la date de chaque compétition en objet datetime
        for comp in listOfCompetitions:
            comp['date'] = datetime.strptime(comp['date'], '%Y-%m-%d %H:%M:%S')
        return listOfCompetitions

app = Flask(__name__)
app.secret_key = 'something_special'

# Charger les données
competitions = loadCompetitions()
clubs = loadClubs()
current_date = datetime.now()

@app.route('/')
def index():
    return render_template('index.html', clubs=clubs)

@app.route('/showSummary', methods=['POST'])
def showSummary():
    email = request.form.get('email', '').strip()
    club = next((club for club in clubs if club['email'].lower() == email.lower()), None)

    if club:
        return render_template('welcome.html', club=club, competitions=competitions, current_date=current_date)
    else:
        flash("Erreur : Le club correspondant à l'email n'a pas été trouvé.")
        return redirect(url_for('index'))

@app.route('/book/<competition>/<club>')
def book(competition, club):
    foundClub = next((c for c in clubs if c['name'].lower() == club.lower()), None)
    foundCompetition = next((c for c in competitions if c['name'].lower() == competition.lower()), None)

    if foundClub and foundCompetition:
        # Vérifier si la compétition est déjà passée
        if foundCompetition['date'] < current_date:
            flash("Erreur : Cette compétition est déjà passée.")
            return redirect(url_for('index'))
        return render_template('booking.html', club=foundClub, competition=foundCompetition)
    else:
        flash("Erreur : Club ou compétition introuvable.")
        return redirect(url_for('index'))

@app.route('/purchasePlaces', methods=['POST'])
def purchasePlaces():
    competition_name = request.form.get('competition', '').strip()
    club_name = request.form.get('club', '').strip()

    try:
        placesRequired = int(request.form.get('places', 0))
    except ValueError:
        flash("Erreur : Vous devez entrer un entier.")
        return render_template('welcome.html', club=next((c for c in clubs if c['name'].lower() == club_name.lower()), None), competitions=competitions, current_date=current_date)

    competition = next((c for c in competitions if c['name'].lower() == competition_name.lower()), None)
    club = next((c for c in clubs if c['name'].lower() == club_name.lower()), None)

    if not competition or not club:
        flash("Erreur : Club ou compétition introuvable.")
        return redirect(url_for('index'))

    if competition['date'] < current_date:
        flash("Erreur : Cette compétition est déjà passée.")
    elif placesRequired <= 0:
        flash("Erreur : Vous avez entré un nombre négatif ou nul.")
    elif placesRequired > 12:
        flash("Erreur : Vous ne pouvez pas réserver plus de 12 places.")
    elif placesRequired > int(competition['numberOfPlaces']):
        flash("Erreur : Pas assez de places disponibles.")
    elif placesRequired > int(club['points']):
        flash("Erreur : Vous n'avez pas assez de points pour cette réservation.")
    else:
        competition['numberOfPlaces'] = int(competition['numberOfPlaces']) - placesRequired
        club['points'] = int(club['points']) - placesRequired
        flash("Réservation réussie !")

    return render_template('welcome.html', club=club, competitions=competitions, current_date=current_date)

@app.route('/logout')
def logout():
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)  # Ajout du mode debug pour un développement plus facile.
