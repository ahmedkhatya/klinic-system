from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'clinic_pro_secure_key'

def db_query(query, params=(), fetch=False):
    conn = sqlite3.connect('clinic.db')
    cursor = conn.cursor()
    cursor.execute(query, params)
    data = cursor.fetchall() if fetch else None
    conn.commit()
    conn.close()
    return data

def init_db():
    # جدول المرضى الجديد (يشمل نوع الزيارة والمبلغ)
    db_query('''CREATE TABLE IF NOT EXISTS patients 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  name TEXT, phone TEXT, age INTEGER, 
                  history TEXT, visit_type TEXT, fees REAL, visit_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    db_query('''CREATE TABLE IF NOT EXISTS users 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT, role TEXT)''')
    try:
        db_query("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", ('doctor1', '123', 'doctor'))
        db_query("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", ('nurse1', '456', 'nurse'))
    except: pass

init_db()

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form['username']
        pwd = request.form['password']
        data = db_query("SELECT * FROM users WHERE username = ? AND password = ?", (user, pwd), fetch=True)
        if data:
            session['logged_in'] = True
            session['username'] = data[0][1]
            session['role'] = data[0][3]
            return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/')
def index():
    if not session.get('logged_in'): return redirect(url_for('login'))
    search = request.args.get('search')
    if search:
        patients = db_query("SELECT * FROM patients WHERE name LIKE ? OR phone LIKE ?", (f'%{search}%', f'%{search}%'), fetch=True)
    else:
        patients = db_query("SELECT * FROM patients ORDER BY visit_date DESC", fetch=True)
    return render_template('index.html', patients=patients)

@app.route('/add', methods=['POST'])
def add_patient():
    if not session.get('logged_in'): return redirect(url_for('login'))
    # استقبال البيانات الجديدة من الفورم
    db_query("INSERT INTO patients (name, phone, age, history, visit_type, fees) VALUES (?, ?, ?, ?, ?, ?)", 
             (request.form['name'], request.form['phone'], request.form['age'], 
              request.form['history'], request.form['visit_type'], request.form['fees']))
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
