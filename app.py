import io
import base64
import requests

from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash

import qrcode
from qrcode.constants import ERROR_CORRECT_H
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer
from qrcode.image.styles.colormasks import RadialGradientColorMask




# 1. Initialize the application
app = Flask(__name__)


DB_HOST="10.0.1.181"
DB_NAME="group5_ecomdb"
DB_USER="group5user"
DB_PASSWORD="group5db123"

app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)


socketio = SocketIO(app, cors_allowed_origins="*")
# 2. Define a route and its handling function
@app.route("/")

def home():

    return render_template("login.html")

@app.route("/dashboard")

def dashboard():
    return render_template("dashboard.html")

@app.route("/generate_qr", methods=["POST"])
def generate_qr():

    data = request.get_json()

    total_items = data["totalItems"]
    total_amount = data["totalAmount"]

    payment_url = f"http://34.234.163.173/pay?amt={total_amount}"

    qr = qrcode.QRCode(
        version=4,
        error_correction=ERROR_CORRECT_H,
        box_size=12,
        border=4
    )

    qr.add_data(payment_url)
    qr.make(fit=True)

    img = qr.make_image(
        image_factory=StyledPilImage,

        # Rounded dots
        module_drawer=RoundedModuleDrawer(),

        # Latte-inspired radial gradient
        color_mask=RadialGradiantColorMask(
            back_color=(247, 242, 236),      # Latte foam
            center_color=(111, 78, 55),      # Coffee brown
            edge_color=(59, 36, 23)          # Espresso
        )
    )

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")

    qr_base64 = base64.b64encode(buffer.getvalue()).decode()

    return jsonify({
        "qr": qr_base64
    })

@app.route("/payment_success")
def payment_success():

    txn = request.args.get("txn")

    socketio.emit("payment_success", {
        "transaction": txn
    })

    return "Payment marked successful."

@app.route('/login', methods=['POST'])
def login():
    # Accepts input from either JSON (JS fetch) or standard HTML form submit
    data = request.get_json(silent=True) or request.form

    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        if request.is_json:
            return jsonify({'status': 'failed', 'message': 'Username and password required'}), 400
        return "Username and password required", 400

    # Query user from MySQL database
    user = User.query.filter_by(username=username).first()

    # Verify user exists and check password hash
    if not user or not check_password_hash(user.password_hash, password):
        if request.is_json:
            return jsonify({'status': 'failed', 'message': 'Invalid credentials'}), 401
        return "Invalid username or password", 401

    # Successful login response
    if request.is_json:
        return jsonify({
            'status': 'success',
            'redirect': url_for('dashboard'),
            'user': {
                'id': user.id,
                'username': user.username
            }
        }), 200

    return redirect(url_for('dashboard'))


# 3. Run the development server
if __name__ == "__main__":
   socketio.run(app,host='0.0.0.0',port=5000,debug=True)
