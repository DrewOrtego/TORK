"""
Application for Online Analysis UI Testing reporting site
"""

import sqlite3

from flask import Flask, render_template

DATABASE = r'SQLite_database_path_goes_here'
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'many random bytes'


def connect_db():
    connection = sqlite3.connect(DATABASE)
    return connection.cursor()


@app.route('/')
def index():
    cur = connect_db()
    query = 'SELECT * FROM testsession ORDER BY start_time DESC'
    cur.execute(query)
    results = cur.fetchall()
    return render_template('index.html', results=results)


@app.route('/tests/<session_id>')
def tests(session_id):
    cur = connect_db()
    cur.execute('SELECT * FROM tests WHERE tests.session_id = ? ORDER BY tests.test_passed', (session_id,))
    results = cur.fetchall()
    # Append the URL to print at the top of the tests.html page
    cur.execute('SELECT endpoint, assertion_level, username FROM testsession WHERE id = ?', (session_id,))
    results.append(cur.fetchall())
    return render_template('tests.html', results=results)


if __name__ == '__main__':
    # app.run(debug=True, host='0.0.0.0', port=80, threaded=True)
    app.run(host='0.0.0.0', debug=True, port=5002, threaded=True)
    # app.run(debug=True)
