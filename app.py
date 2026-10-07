from flask import Flask, render_template, request, redirect
import os
import hashlib
import sqlite3

app = Flask(__name__)

# Create database and table
conn = sqlite3.connect('certificates.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS certificates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_name TEXT,
    roll_no TEXT,
    file_hash TEXT
)
''')

conn.commit()
conn.close()


# ---------------- HOME ----------------
@app.route('/')
def home():
    return render_template('index.html')


# ---------------- LOGIN ----------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == "admin" and password == "1234":
            return render_template('dashboard.html')
        else:
            return "Invalid Username or Password"

    return render_template('login.html')


# ---------------- UPLOAD CERTIFICATE ----------------
@app.route('/upload', methods=['POST'])
def upload():
    student_name = request.form['student_name']
    roll_no = request.form['roll_no']
    file = request.files['certificate']

    if file:
        # Save file
        filename = roll_no + "_" + file.filename
        filepath = os.path.join("certificates", filename)
        file.save(filepath)

        # Generate SHA256 hash
        with open(filepath, "rb") as f:
            file_data = f.read()
            file_hash = hashlib.sha256(file_data).hexdigest()

        print("Certificate Hash:", file_hash)

        # Save hash into database
        conn = sqlite3.connect('certificates.db')
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO certificates (student_name, roll_no, file_hash) VALUES (?, ?, ?)",
            (student_name, roll_no, file_hash)
        )

        conn.commit()
        conn.close()

        # SHOW SUCCESS PAGE
        return render_template('success.html')

    return "Upload Failed"


# ---------------- VERIFY PAGE ----------------
@app.route('/verify', methods=['GET'])
def verify_page():
    return render_template('verify.html')


# ---------------- VERIFY CERTIFICATE ----------------
@app.route('/verify', methods=['POST'])
def verify_certificate():
    file = request.files['certificate']

    if file:
        # Save temporary file
        temp_path = os.path.join("certificates", "temp_" + file.filename)
        file.save(temp_path)

        # Generate hash
        with open(temp_path, "rb") as f:
            file_data = f.read()
            file_hash = hashlib.sha256(file_data).hexdigest()

        # Check database
        conn = sqlite3.connect('certificates.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM certificates WHERE file_hash=?", (file_hash,))
        result = cursor.fetchone()
        conn.close()

        # Delete temporary file
        os.remove(temp_path)

        # SHOW RESULT PAGE
        if result:
            return render_template('result.html', valid=True)
        else:
            return render_template('result.html', valid=False)

    return "No file uploaded"


# ---------------- RUN SERVER ----------------
if __name__ == '__main__':
    app.run(debug=True)