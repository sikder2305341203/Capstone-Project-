from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'rifat_capstone_secret'

def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    # Login er jonno table
    c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)''')
    # Profile ar Goal er jonno notun table
    c.execute('''CREATE TABLE IF NOT EXISTS profiles (username TEXT PRIMARY KEY, age INTEGER, weight REAL, height REAL, goal TEXT, activity TEXT)''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def home():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']
    
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=?", (username,))
    if c.fetchone():
        return "User already exists! <a href='/'>Go back</a>"
        
    c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
    conn.commit()
    conn.close()
    # Register korar por profile setup e pathabo
    session['username'] = username
    return redirect(url_for('setup_profile'))

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
    else:
        return "Invalid Credentials! <a href='/'>Try again</a>"

@app.route('/setup_profile', methods=['GET', 'POST'])
def setup_profile():
    if 'username' not in session:
        return redirect(url_for('home'))
        
    if request.method == 'POST':
        age = request.form['age']
        weight = request.form['weight']
        height = request.form['height']
        goal = request.form['goal']
        activity = request.form['activity']
        
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("REPLACE INTO profiles (username, age, weight, height, goal, activity) VALUES (?, ?, ?, ?, ?, ?)", 
                  (session['username'], age, weight, height, goal, activity))
        conn.commit()
        conn.close()
        return redirect(url_for('dashboard'))
        
    return render_template('setup_profile.html')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('home'))
        
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM profiles WHERE username=?", (session['username'],))
    profile = c.fetchone()
    conn.close()
    
    if not profile:
        return redirect(url_for('setup_profile'))
        
    # Profile data unpack korchi
    age, weight, height, goal, activity = profile[1], profile[2], profile[3], profile[4], profile[5]
    
    return render_template('dashboard.html', username=session['username'], weight=weight, height=height, goal=goal, activity=activity)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)