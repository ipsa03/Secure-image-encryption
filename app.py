from flask import Flask, render_template, request, redirect, session, send_file
from encryption.aes import decrypt_image, encrypt_image
import os
import sqlite3
import bcrypt

app = Flask(__name__)
app.secret_key = "mysecretkey123"

UPLOAD_FOLDER = "static/uploads/"
ENCRYPTED_FOLDER = "static/encrypted/"
DECRYPTED_FOLDER = "static/decrypted/"

# ---------------- REGISTER ----------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

        conn = sqlite3.connect('database.db')
        conn.execute("INSERT INTO users VALUES (?, ?)", (username, hashed))
        conn.commit()
        conn.close()

        return redirect('/')

    return render_template('register.html')


# ---------------- LOGIN ----------------
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password'].encode()

        conn = sqlite3.connect('database.db')
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username=?", (username,))
        user = cur.fetchone()
        conn.close()

        if user and bcrypt.checkpw(password, user[1]):
            session['user'] = username
            return redirect('/dashboard')
        else:
            return "Invalid Username or Password"

    return render_template('login.html')


# ---------------- DASHBOARD ----------------
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user' not in session:
        return redirect('/')

    if request.method == 'POST':
        file = request.files['file']

        # Create folders if not exist
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(ENCRYPTED_FOLDER, exist_ok=True)

        upload_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(upload_path)

        encrypted_path = os.path.join(ENCRYPTED_FOLDER, file.filename + ".bin")

        key = encrypt_image(upload_path, encrypted_path)

        session['key'] = key.hex()
        session['file'] = file.filename

        return "✅ Image Encrypted Successfully!"

    return render_template('dashboard.html')


# ---------------- DECRYPT ----------------
@app.route('/decrypt')
def decrypt():
    if 'user' not in session:
        return redirect('/')

    if not session.get('key') or not session.get('file'):
        return "⚠️ Please encrypt an image first."

    filename = session['file']
    key = bytes.fromhex(session['key'])

    os.makedirs(DECRYPTED_FOLDER, exist_ok=True)

    enc_path = os.path.join(ENCRYPTED_FOLDER, filename + ".bin")
    dec_path = os.path.join(DECRYPTED_FOLDER, filename)

    decrypt_image(enc_path, dec_path, key)

    return send_file(dec_path, as_attachment=True)


# ---------------- LOGOUT ----------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


# ---------------- RUN APP ----------------
if __name__ == "__main__":
    app.run(debug=True)