import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash, session
from datetime import datetime
import os
import base64
from werkzeug.utils import secure_filename
import openai # Import the OpenAI library
import markdown2 # Import markdown2

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
if not app.config['SECRET_KEY']:
    print("WARNUNG: SECRET_KEY nicht über Umgebungsvariable gesetzt. Verwende unsicheren Default-Key für Entwicklung.")
    app.config['SECRET_KEY'] = 'dev_secret_key_bitte_in_production_aendern' # Default für Entwicklung
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
app.config['OPENAI_API_KEY'] = os.environ.get('OPENAI_API_KEY')
app.config['APP_PASSWORD'] = os.environ.get('APP_PASSWORD') # Passwort für die App

# Initialize OpenAI client
if app.config['OPENAI_API_KEY']:
    client = openai.OpenAI(api_key=app.config['OPENAI_API_KEY'])
else:
    client = None
    print("WARNUNG: OPENAI_API_KEY nicht gesetzt. AI-Funktionen sind deaktiviert.")

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def get_db_connection():
    conn = sqlite3.connect('weinkeller.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password and app.config['APP_PASSWORD'] and password == app.config['APP_PASSWORD']:
            session['logged_in'] = True
            session.permanent = True # Session bleibt über Browser-Schließung hinaus bestehen (abhängig von app.permanent_session_lifetime)
            flash('Erfolgreich angemeldet!', 'success')
            next_url = request.args.get('next')
            return redirect(next_url or url_for('index'))
        else:
            flash('Falsches Passwort.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('Erfolgreich abgemeldet.', 'info')
    return redirect(url_for('login'))

@app.before_request
def require_login():
    if not session.get('logged_in') and \
       request.endpoint not in ['login', 'static']:
        return redirect(url_for('login', next=request.url))

@app.context_processor
def inject_now():
    return {'now': datetime.utcnow()}

@app.route('/')
def index():
    conn = get_db_connection()
    weine = conn.execute('SELECT * FROM weine ORDER BY erstellt DESC').fetchall()
    conn.close()
    return render_template('index.html', weine=weine)

@app.route('/wein/<int:wein_id>')
def wein_detail(wein_id):
    conn = get_db_connection()
    wein = conn.execute('SELECT * FROM weine WHERE id = ?', (wein_id,)).fetchone()
    conn.close()
    if wein is None:
        flash('Wein nicht gefunden!', 'danger')
        return redirect(url_for('index'))
    
    ai_html_beschreibung = None
    if wein['ai_beschreibung']:
        ai_html_beschreibung = markdown2.markdown(wein['ai_beschreibung'])
        
    return render_template('detail.html', wein=wein, ai_html_beschreibung=ai_html_beschreibung)

@app.route('/wein/neu', methods=('GET', 'POST'))
def wein_neu():
    if request.method == 'POST':
        name = request.form['name']
        jahrgang = request.form['jahrgang']
        weingut = request.form['weingut']
        rebsorte = request.form['rebsorte']
        region = request.form.get('region', '')
        lagerposition = request.form.get('lagerposition', '')
        trinktemperatur = request.form.get('trinktemperatur', '')
        kaufdatum = request.form.get('kaufdatum', '')
        preis = request.form.get('preis', 0)
        notizen = request.form.get('notizen', '')
        bestand = request.form.get('bestand', 1)

        bild_pfade_list = []
        uploaded_files = request.files.getlist("bilder")

        # Create upload folder if it doesn't exist
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

        for file in uploaded_files:
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                bild_pfade_list.append(filename)
            elif file and file.filename != '' and not allowed_file(file.filename):
                flash(f'Ungültiger Dateityp für Datei: {file.filename}. Erlaubt sind: {", ".join(app.config["ALLOWED_EXTENSIONS"])}', 'warning')
        
        bild_pfade_str = ",".join(bild_pfade_list)
        
        if not name or not jahrgang or not weingut or not rebsorte:
            flash('Name, Jahrgang, Weingut und Rebsorte sind erforderlich!', 'danger')
        else:
            conn = get_db_connection()
            conn.execute("""
                INSERT INTO weine 
                (name, jahrgang, weingut, rebsorte, region, lagerposition, 
                trinktemperatur, kaufdatum, preis, notizen, bestand, bild_pfade) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (name, jahrgang, weingut, rebsorte, region, lagerposition, 
                  trinktemperatur, kaufdatum, preis, notizen, bestand, bild_pfade_str))
            conn.commit()
            conn.close()
            flash('Wein erfolgreich hinzugefügt!', 'success')
            return redirect(url_for('index'))
            
    return render_template('formular.html', wein={}, titel="Neuen Wein hinzufügen")

@app.route('/wein/<int:wein_id>/bearbeiten', methods=('GET', 'POST'))
def wein_bearbeiten(wein_id):
    conn = get_db_connection()
    wein = conn.execute('SELECT * FROM weine WHERE id = ?', (wein_id,)).fetchone()
    conn.close()
    
    if wein is None:
        flash('Wein nicht gefunden!', 'danger')
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        name = request.form['name']
        jahrgang = request.form['jahrgang']
        weingut = request.form['weingut']
        rebsorte = request.form['rebsorte']
        region = request.form.get('region', '')
        lagerposition = request.form.get('lagerposition', '')
        trinktemperatur = request.form.get('trinktemperatur', '')
        kaufdatum = request.form.get('kaufdatum', '')
        preis = request.form.get('preis', 0)
        notizen = request.form.get('notizen', '')
        bestand = request.form.get('bestand', 1)

        bilder_zu_loeschen = request.form.getlist('delete_bild') # Liste der zu löschenden Bilddateinamen

        # Beginne mit den aktuellen Bildern aus der Datenbank
        aktuelle_bilder_im_db = [p for p in (wein['bild_pfade'] or '').split(',') if p]
        
        verbleibende_bilder = []
        for bild_pfad in aktuelle_bilder_im_db:
            if bild_pfad in bilder_zu_loeschen:
                # Bild ist zum Löschen markiert
                try:
                    file_path_to_delete = os.path.join(app.config['UPLOAD_FOLDER'], bild_pfad)
                    if os.path.exists(file_path_to_delete):
                        os.remove(file_path_to_delete)
                        # flash(f'Bild "{bild_pfad}" erfolgreich vom Server gelöscht.', 'info') # Optional, kann bei vielen Bildern störend sein
                    # else:
                        # flash(f'Zu löschende Bilddatei "{bild_pfad}" nicht auf dem Server gefunden.', 'warning')
                except OSError as e:
                    flash(f'Fehler beim Löschen der Datei "{bild_pfad}" vom Server: {e}', 'danger')
                # Füge es nicht zur Liste der verbleibenden Bilder hinzu
            else:
                # Behalte dieses Bild
                verbleibende_bilder.append(bild_pfad)
        
        # Verarbeite neu hochgeladene Dateien
        uploaded_files = request.files.getlist("bilder")
        newly_uploaded_filenames = []

        if uploaded_files and any(f.filename for f in uploaded_files): # Prüfen, ob neue Dateien hochgeladen wurden
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True) # Sicherstellen, dass der Upload-Ordner existiert
            for file in uploaded_files:
                if file and file.filename != '' and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    # Speichere die Datei
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    if filename not in newly_uploaded_filenames: # Nur einmal pro Upload-Vorgang hinzufügen
                        newly_uploaded_filenames.append(filename)
                elif file and file.filename != '' and not allowed_file(file.filename):
                    flash(f'Ungültiger Dateityp für Datei: {file.filename}. Erlaubt sind: {", ".join(app.config["ALLOWED_EXTENSIONS"])}', 'warning')
        
        # Kombiniere verbleibende Bilder mit neu hochgeladenen
        # Füge neue Dateien hinzu, wenn sie nicht bereits in der Liste der verbleibenden Bilder sind
        final_bild_pfade_list = list(verbleibende_bilder) # Starte mit Bildern, die nicht gelöscht wurden
        for fn in newly_uploaded_filenames:
            if fn not in final_bild_pfade_list:
                 final_bild_pfade_list.append(fn)
        
        # Erstelle den String für die Datenbank, filtere leere Einträge heraus
        bild_pfade_str = ",".join(fn for fn in final_bild_pfade_list if fn)
        
        if not name or not jahrgang or not weingut or not rebsorte:
            flash('Name, Jahrgang, Weingut und Rebsorte sind erforderlich!', 'danger')
        else:
            conn = get_db_connection()
            conn.execute("""
                UPDATE weine SET 
                name = ?, jahrgang = ?, weingut = ?, rebsorte = ?, 
                region = ?, lagerposition = ?, trinktemperatur = ?, 
                kaufdatum = ?, preis = ?, notizen = ?, bestand = ?, bild_pfade = ?,
                aktualisiert = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (name, jahrgang, weingut, rebsorte, region, lagerposition, 
                  trinktemperatur, kaufdatum, preis, notizen, bestand, bild_pfade_str, wein_id))
            conn.commit()
            conn.close()
            flash('Wein erfolgreich aktualisiert!', 'success')
            return redirect(url_for('wein_detail', wein_id=wein_id))
    
    return render_template('formular.html', wein=wein, titel="Wein bearbeiten")

@app.route('/wein/<int:wein_id>/loeschen', methods=('POST',))
def wein_loeschen(wein_id):
    conn = get_db_connection()
    wein = conn.execute('SELECT * FROM weine WHERE id = ?', (wein_id,)).fetchone()
    
    if wein is None:
        flash('Wein nicht gefunden!', 'danger')
    else:
        conn.execute('DELETE FROM weine WHERE id = ?', (wein_id,))
        conn.commit()
        flash('Wein erfolgreich gelöscht!', 'success')
    
    conn.close()
    return redirect(url_for('index'))

def get_image_base64(image_path):
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except Exception as e:
        print(f"Error encoding image {image_path}: {e}")
        return None

@app.route('/wein/<int:wein_id>/generate_ai_description', methods=('POST',))
def generate_ai_description(wein_id):
    if not client:
        flash('OpenAI API Key nicht konfiguriert. AI-Funktion ist deaktiviert.', 'danger')
        return redirect(url_for('wein_detail', wein_id=wein_id))

    conn = get_db_connection()
    wein = conn.execute('SELECT * FROM weine WHERE id = ?', (wein_id,)).fetchone()
    
    if wein is None:
        flash('Wein nicht gefunden!', 'danger')
        conn.close()
        return redirect(url_for('index'))

    image_analysis_results = []
    if wein['bild_pfade']:
        image_paths = [p for p in wein['bild_pfade'].split(',') if p]
        for img_filename in image_paths:
            full_image_path = os.path.join(app.config['UPLOAD_FOLDER'], img_filename)
            if os.path.exists(full_image_path):
                base64_image = get_image_base64(full_image_path)
                if base64_image:
                    try:
                        response = client.chat.completions.create(
                            model="gpt-4o", # Use gpt-4o for vision
                            messages=[
                                {
                                    "role": "user",
                                    "content": [
                                        {"type": "text", "text": "Beschreibe das Weinetikett und die Flasche auf diesem Bild. Konzentriere dich auf sichtbare Informationen wie Name, Jahrgang, Weingut, Rebsorte, Herkunft, Alkoholgehalt und besondere Merkmale des Etiketts."},
                                        {
                                            "type": "image_url",
                                            "image_url": {
                                                "url": f"data:image/jpeg;base64,{base64_image}"
                                            }
                                        }
                                    ]
                                }
                            ],
                            max_tokens=300
                        )
                        image_analysis_results.append(response.choices[0].message.content)
                    except Exception as e:
                        flash(f'Fehler bei der Analyse von Bild {img_filename} mit OpenAI: {e}', 'danger')
            else:
                flash(f'Bilddatei {img_filename} nicht gefunden.', 'warning')
    
    # Prepare data for text generation
    wine_data_text = f"Name: {wein['name']}\nJahrgang: {wein['jahrgang']}\nWeingut: {wein['weingut']}\nRebsorte: {wein['rebsorte']}\nRegion: {wein['region'] or 'N/A'}\nPreis: {wein['preis'] or 'N/A'}\nNotizen: {wein['notizen'] or 'N/A'}"
    
    image_summary = "Keine Bilder analysiert."
    if image_analysis_results:
        image_summary = "\n\nAnalyse der Bilder:\n" + "\n---\n".join(image_analysis_results)

    final_prompt = f"""Basierend auf den folgenden Informationen und Bildanalysen, erstelle eine ansprechende und informative Markdown-Beschreibung für den Wein.
Die Beschreibung sollte Details zum Wein, mögliche Verkostungsnotizen (basierend auf typischen Eigenschaften der Rebsorte/Region, falls nicht anders gegeben), und interessante Fakten enthalten.
Strukturiere den Text gut mit Markdown (Überschriften, Listen, Fett-/Kursivschrift).
WICHTIG: Füge keine Bilder oder Bild-Tags (z.B. `![alt text](url)`) in die Markdown-Beschreibung ein. Die Beschreibung soll rein textuell sein.

Weindaten:
{wine_data_text}

{image_summary}

Erstelle nun die Markdown-Beschreibung:
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini", # Use gpt-4o-mini for text generation
            messages=[
                {"role": "system", "content": "Du bist ein Weinexperte und Sommelier, der detaillierte und ansprechende Weinbeschreibungen im Markdown-Format erstellt."},
                {"role": "user", "content": final_prompt}
            ]
        )
        ai_text = response.choices[0].message.content
        
        conn.execute('UPDATE weine SET ai_beschreibung = ?, aktualisiert = CURRENT_TIMESTAMP WHERE id = ?', (ai_text, wein_id))
        conn.commit()
        flash('AI Weinbeschreibung erfolgreich generiert und gespeichert!', 'success')
    except Exception as e:
        flash(f'Fehler bei der Generierung der Weinbeschreibung mit OpenAI: {e}', 'danger')
    
    conn.close()
    return redirect(url_for('wein_detail', wein_id=wein_id))

@app.route('/suche')
def suche():
    suchbegriff = request.args.get('q', '')
    rebsorte = request.args.get('rebsorte', '')
    weingut = request.args.get('weingut', '')
    jahrgang = request.args.get('jahrgang', '')
    
    conn = get_db_connection()
    query = 'SELECT * FROM weine WHERE 1=1'
    params = []
    
    if suchbegriff:
        query += ' AND (name LIKE ? OR weingut LIKE ? OR rebsorte LIKE ? OR region LIKE ?)'
        suchterm = f'%{suchbegriff}%'
        params.extend([suchterm, suchterm, suchterm, suchterm])
    
    if rebsorte:
        query += ' AND rebsorte = ?'
        params.append(rebsorte)
    
    if weingut:
        query += ' AND weingut = ?'
        params.append(weingut)
    
    if jahrgang:
        query += ' AND jahrgang = ?'
        params.append(jahrgang)
    
    weine = conn.execute(query, params).fetchall()
    
    # Für Filter-Dropdowns
    rebsorten = conn.execute('SELECT DISTINCT rebsorte FROM weine ORDER BY rebsorte').fetchall()
    weingueter = conn.execute('SELECT DISTINCT weingut FROM weine ORDER BY weingut').fetchall()
    jahrgaenge = conn.execute('SELECT DISTINCT jahrgang FROM weine ORDER BY jahrgang DESC').fetchall()
    
    conn.close()
    return render_template('suche.html', weine=weine, suchbegriff=suchbegriff, 
                          rebsorten=rebsorten, weingueter=weingueter, jahrgaenge=jahrgaenge,
                          ausgewaehlte_rebsorte=rebsorte, ausgewaehltes_weingut=weingut, 
                          ausgewaehlter_jahrgang=jahrgang)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)

