from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
import os
import cv2

app = Flask(__name__)
app.secret_key = 'super_secret_key'
app.config['UPLOAD_FOLDER'] = 'uploads'

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# Mock user store (no DB)
users = {}

# Helper Functions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_image(filename, operation):
    img = cv2.imread(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    new_filename = f"{filename.rsplit('.', 1)[0]}.{operation[1:] if operation.startswith('c') else operation}"
    output_path = os.path.join('static', new_filename)

    match operation:
        case 'cgray':
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            cv2.imwrite(output_path, gray)
        case 'cpng' | 'cjpg' | 'cwebp':
            cv2.imwrite(output_path, img)
        case _:
            return None

    return output_path

# Routes
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/edit", methods=["POST"])
def edit():
    if 'file' not in request.files or request.files['file'].filename == '':
        flash("No file selected", "danger")
        return redirect(url_for("home"))

    file = request.files['file']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        operation = request.form.get("operation")
        output_path = process_image(filename, operation)

        if output_path:
            flash(f"Image processed successfully! <a href='/{output_path}' target='_blank'>View Result</a>", "success")
        else:
            flash("Invalid operation selected", "danger")

    else:
        flash("Invalid file format", "danger")

    return redirect(url_for("home"))

@app.route("/signup", methods=["POST"])
def signup():
    email = request.form.get("email")
    password = request.form.get("password")
    confirm = request.form.get("confirm_password")

    if not email or not password:
        flash("Email and password are required", "danger")
    elif password != confirm:
        flash("Passwords do not match", "danger")
    elif email in users:
        flash("User already exists", "danger")
    else:
        users[email] = password
        session['user'] = email  # ✅ Automatically log in
        flash("Signup successful! You are now logged in.", "success")

    return redirect(url_for("home"))

@app.route("/login", methods=["POST"])
def login():
    email = request.form.get("email")
    password = request.form.get("password")

    if email in users and users[email] == password:
        session['user'] = email
        flash("Login successful", "success")
    else:
        flash("Invalid email or password", "danger")

    return redirect(url_for("home"))

@app.route("/logout")
def logout():
    session.pop('user', None)
    flash("Logged out successfully", "success")
    return redirect(url_for("home"))

# Create folders if they don't exist
os.makedirs('uploads', exist_ok=True)
os.makedirs('static', exist_ok=True)

if __name__ == "__main__":
    app.run(debug=True, port=5001)
