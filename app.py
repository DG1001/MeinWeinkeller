import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ihre_geheime_schluesselzeichenfolge'

def get_db_connection():
    conn = sqlite3.connect('weinkeller.db')
    conn.row_factory = sqlite3.Row
    return conn

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
    return render_template('detail.html', wein=wein)

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
        
        if not name or not jahrgang or not weingut or not rebsorte:
            flash('Name, Jahrgang, Weingut und Rebsorte sind erforderlich!', 'danger')
        else:
            conn = get_db_connection()
            conn.execute("""
                INSERT INTO weine 
                (name, jahrgang, weingut, rebsorte, region, lagerposition, 
                trinktemperatur, kaufdatum, preis, notizen, bestand) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (name, jahrgang, weingut, rebsorte, region, lagerposition, 
                  trinktemperatur, kaufdatum, preis, notizen, bestand))
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
        
        if not name or not jahrgang or not weingut or not rebsorte:
            flash('Name, Jahrgang, Weingut und Rebsorte sind erforderlich!', 'danger')
        else:
            conn = get_db_connection()
            conn.execute("""
                UPDATE weine SET 
                name = ?, jahrgang = ?, weingut = ?, rebsorte = ?, 
                region = ?, lagerposition = ?, trinktemperatur = ?, 
                kaufdatum = ?, preis = ?, notizen = ?, bestand = ?,
                aktualisiert = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (name, jahrgang, weingut, rebsorte, region, lagerposition, 
                  trinktemperatur, kaufdatum, preis, notizen, bestand, wein_id))
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

