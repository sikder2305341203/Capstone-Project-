from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from datetime import date

app = Flask(__name__)
app.secret_key = 'super_secret_key' 

def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS profiles (username TEXT PRIMARY KEY, age INTEGER, weight REAL, height REAL, goal TEXT, activity TEXT, workout_location TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS progress (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, record_date TEXT, current_weight REAL, steps INTEGER, calories INTEGER)''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def home():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = c.fetchone()
    conn.close()
    if user:
        session['username'] = username
        return redirect(url_for('dashboard'))
    
    flash("Invalid Username or Password!", "error")
    return redirect(url_for('home'))

@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=?", (username,))
    if c.fetchone():
        flash("Username already exists! Try another one.", "error")
    else:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        flash("Registration Successful! Please login.", "success")
    conn.close()
    
    return redirect(url_for('home'))

@app.route('/setup_profile', methods=['GET', 'POST'])
def setup_profile():
    if 'username' not in session: return redirect(url_for('home'))
    if request.method == 'POST':
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("REPLACE INTO profiles (username, age, weight, height, goal, activity, workout_location) VALUES (?, ?, ?, ?, ?, ?, ?)", 
                  (session['username'], request.form['age'], request.form['weight'], request.form['height'], request.form['goal'], request.form['activity'], request.form['workout_location']))
        conn.commit()
        conn.close()
        return redirect(url_for('dashboard'))
    return render_template('setup_profile.html')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session: return redirect(url_for('home'))
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM profiles WHERE username=?", (session['username'],))
    profile = c.fetchone()
    c.execute("SELECT * FROM progress WHERE username=? ORDER BY record_date DESC LIMIT 5", (session['username'],))
    history = c.fetchall()
    conn.close()
    
    # Fail-safe: Jodi profile na thake ba purano database hoy jekhane location nai
    if not profile or len(profile) < 7: 
        return redirect(url_for('setup_profile'))
    
    return render_template('dashboard.html', username=session['username'], profile=profile, history=history)

@app.route('/training')
def training():
    if 'username' not in session: return redirect(url_for('home'))
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM profiles WHERE username=?", (session['username'],))
    profile = c.fetchone()
    conn.close()
    
    if not profile or len(profile) < 7: 
        return redirect(url_for('setup_profile'))
        
    return render_template('training.html', username=session['username'], profile=profile)

@app.route('/log_progress', methods=['GET', 'POST'])
def log_progress():
    if 'username' not in session: return redirect(url_for('home'))
    if request.method == 'POST':
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        today = date.today().strftime("%Y-%m-%d")
        c.execute("INSERT INTO progress (username, record_date, current_weight, steps, calories) VALUES (?, ?, ?, ?, ?)", 
                  (session['username'], today, request.form['weight'], request.form['steps'], request.form['calories']))
        conn.commit()
        conn.close()
        return redirect(url_for('dashboard'))
    return render_template('log_progress.html', username=session['username'])

@app.route('/about')
def about():
    if 'username' not in session: return redirect(url_for('home'))
    return render_template('about.html', username=session['username'])

@app.route('/contact')
def contact():
    if 'username' not in session: return redirect(url_for('home'))
    return render_template('contact.html', username=session['username'])

@app.route('/research')
def research():
    if 'username' not in session: return redirect(url_for('home'))
    return render_template('research.html', username=session['username'])

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)