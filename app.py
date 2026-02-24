from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'clinic_pro_secure_key' # مفتاح تشفير الجلسات

# --- وظيفة قاعدة البيانات ---
def db_query(query, params=(), fetch=False):
    conn = sqlite3.connect('clinic.db')
    cursor = conn.cursor()
    cursor.execute(query, params)
    data = cursor.fetchall() if fetch else None
    conn.commit()
    conn.close()
    return data

# --- إنشاء الجداول (مرضى + مستخدمين) ---
def init_db():
    db_query('''CREATE TABLE IF NOT EXISTS patients 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, phone TEXT, age INTEGER, history TEXT)''')
    db_query('''CREATE TABLE IF NOT EXISTS users 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT)''')
    try:
        db_query("INSERT INTO users (username, password) VALUES (?, ?)", ('admin', '123'))
    except:
        pass

init_db()

# --- المسارات (Routes) ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form['username']
        pwd = request.form['password']
        data = db_query("SELECT * FROM users WHERE username = ? AND password = ?", (user, pwd), fetch=True)
        if data:
            session['logged_in'] = True
            return redirect(url_for('index'))
        return "<h2 style='text-align:center; color:red; margin-top:50px;'>خطأ في الدخول! <a href='/login'>ارجع وجرب تاني</a></h2>"
    return render_template('login.html')

@app.route('/')
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    search = request.args.get('search')
    if search:
        query = "SELECT * FROM patients WHERE name LIKE ? OR phone LIKE ?"
        patients = db_query(query, (f'%{search}%', f'%{search}%'), fetch=True)
    else:
        patients = db_query("SELECT * FROM patients", fetch=True)
    return render_template('index.html', patients=patients)

@app.route('/add', methods=['POST'])
def add_patient():
    if not session.get('logged_in'): return redirect(url_for('login'))
    db_query("INSERT INTO patients (name, phone, age, history) VALUES (?, ?, ?, ?)", 
             (request.form['name'], request.form['phone'], request.form['age'], request.form['history']))
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)