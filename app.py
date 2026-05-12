from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os

app = Flask(__name__)

def get_db():
    sav = sqlite3.connect('dati.db')
    sav.row_factory = sqlite3.Row
    return sav

@app.route('/')
def index():

    kartosana = request.args.get('kart')

    sav = get_db()

    if kartosana in ['ASC', 'DESC']:

        rezultati = sav.execute(
            f'''
            SELECT * FROM rezultati
            ORDER BY komanda_a {kartosana}
            '''
        ).fetchall()

    else:

        rezultati = sav.execute(
            '''
            SELECT * FROM rezultati
            ORDER BY datums DESC
            '''
        ).fetchall()

    skaits = sav.execute(
        'SELECT COUNT(*) FROM rezultati'
    ).fetchone()[0]

    sav.close()

    return render_template(
        'index.html',
        rezultati=rezultati,
        skaits=skaits
    )

@app.route('/pievienot', methods=['GET', 'POST'])
def pievienot():
    if request.method == 'POST':
        komanda_a = request.form['komanda_a']
        komanda_b = request.form['komanda_b']
        rezultats = request.form['rezultats']
        datums = request.form['datums']

        sav = get_db()
        sav.execute(
            'INSERT INTO rezultati (komanda_a, komanda_b, rezultats, datums) VALUES (?, ?, ?, ?)',
            (komanda_a, komanda_b, rezultats, datums)
        )
        sav.commit()
        sav.close()

        return redirect(url_for('index'))

    return render_template('pievienot.html') 

@app.route('/dzest/<int:id>')
def dzest(id):
    sav = get_db()
    sav.execute('DELETE FROM rezultati WHERE id = ?', (id,))
    sav.commit()
    sav.close()

    return redirect(url_for('index'))

@app.route('/meklet')
def meklet():

    vaicajums = request.args.get('q', '')

    sav = get_db()

    rezultati = sav.execute(
        '''
        SELECT * FROM rezultati
        WHERE komanda_a LIKE ?
        OR komanda_b LIKE ?
        OR rezultats LIKE ?
        ''',
        (
            '%' + vaicajums + '%',
            '%' + vaicajums + '%',
            '%' + vaicajums + '%'
        )
    ).fetchall()

    sav.close()
    return render_template('index.html', rezultati=rezultati, skaits=len(rezultati))


if __name__ == '__main__':

    if os.path.exists('dati.db'):
        os.remove('dati.db')

    sav = get_db()

    sav.execute('''
        CREATE TABLE rezultati (
            id INTEGER PRIMARY KEY,
            komanda_a TEXT,
            komanda_b TEXT,
            rezultats TEXT,
            datums TEXT
        )
    ''')

    sav.commit()
    sav.close()

    app.run(debug=True)
