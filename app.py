import io
import base64
import requests
import traceback

from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash

import qrcode
from qrcode.constants import ERROR_CORRECT_H
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer
from qrcode.image.styles.colormasks import RadialGradiantColorMask

# 1. Initialize the application
app = Flask(__name__)

DB_HOST = "10.0.1.181"
DB_NAME = "group5_ecomdb"
DB_USER = "group5user"
DB_PASSWORD = "group5db123"

app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'users'
    customer_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

# FIX 1: Explicitly define async_mode='threading'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# 2. Define routes
@app.route("/")
def home():
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    return render_template("index.html")

@app.route("/generate_qr", methods=["POST"])
def generate_qr():
    data = request.get_json(silent=True) or {}

    total_items = data.get("totalItems")
    total_amount = data.get("totalAmount")

    if total_amount is None:
        return jsonify({"error": "Missing totalAmount"}), 400

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
        module_drawer=RoundedModuleDrawer(),
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
    print("LOGIN ROUTE HIT")

    try:
        data = request.get_json(silent=True) or request.form

        username = data.get('username')
        password = data.get('password')

        print(f"Trying to login: {username}")

        user = User.query.filter_by(username=username).first()

        print(user)

        if not user or user.password != password:
            return jsonify({
                "status": "failed",
                "message": "Invalid credentials"
            }), 401

        return jsonify({
            "status": "success",
            "redirect": url_for("dashboard")
        })

    except Exception:
        traceback.print_exc()
        raise

# FIX 2: Set debug=False & allow_unsafe_werkzeug=True for Docker stability
if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=5000, debug=False, allow_unsafe_werkzeug=True)
