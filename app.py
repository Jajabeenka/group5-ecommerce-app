import io
import base64
import qrcode
from flask import Flask, render_template,request, jsonify
from flask_socketio import SocketIO
from qrcode.constants import ERROR_CORRECT_H

from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer
from qrcode.image.styles.colormasks import RadialGradiantColorMask

# 1. Initialize the application
app = Flask(__name__)

socketio = SocketIO(app, cors_allowed_origins="*")
# 2. Define a route and its handling function
@app.route("/")

def home():

    return render_template("login.html")

@app.route("/dashboard")

def dashboard():
    return render_template("index.html")

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

# 3. Run the development server
if __name__ == "__main__":
   socketio.run(app,host='0.0.0.0',port=5000,debug=True)
