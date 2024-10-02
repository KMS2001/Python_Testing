import json
from flask import Flask, render_template, request, redirect, flash, url_for

# Chargement des données depuis les fichiers JSON
def loadClubs():
    with open('clubs.json') as c:
        return json.load(c)['clubs']

def loadCompetitions():
    with open('competitions.json') as comps:
        return json.load(comps)['competitions']

app = Flask(__name__)
app.secret_key = 'something_special'

competitions = loadCompetitions()
clubs = loadClubs()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/showSummary', methods=['POST'])
def showSummary():
    email = request.form.get('email', '').strip()
    club = next((club for club in clubs if club['email'].lower() == email.lower()), None)

    if club:
        return render_template('welcome.html', club=club, competitions=competitions)
    else:
        flash("Erreur : Le club correspondant à l'email n'a pas été trouvé.")
        return redirect(url_for('index'))

@app.route('/book/<competition>/<club>')
def book(competition, club):
    foundClub = next((c for c in clubs if c['name'].lower() == club.lower()), None)
    foundCompetition = next((c for c in competitions if c['name'].lower() == competition.lower()), None)

    if foundClub and foundCompetition:
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
        flash("Erreur : Nombre de places invalide.")
        return redirect(url_for('index'))

    competition = next((c for c in competitions if c['name'].lower() == competition_name.lower()), None)
    club = next((c for c in clubs if c['name'].lower() == club_name.lower()), None)

    if not competition or not club:
        flash("Erreur : Club ou compétition introuvable.")
        return redirect(url_for('index'))

    if placesRequired <= 0:
        flash("Erreur : Le nombre de places doit être supérieur à zéro.")
    elif placesRequired > 12:
        flash('Erreur : Vous ne pouvez pas réserver plus de 12 places.')
    elif placesRequired > int(competition['numberOfPlaces']):
        flash("Erreur : Pas assez de places disponibles.")
    elif placesRequired > int(club['points']):
        flash("Erreur : Vous n'avez pas assez de points pour cette réservation.")
    else:
        competition['numberOfPlaces'] = int(competition['numberOfPlaces']) - placesRequired
        club['points'] = int(club['points']) - placesRequired
        flash('Réservation réussie !')

    return render_template('welcome.html', club=club, competitions=competitions)

@app.route('/logout')
def logout():
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
