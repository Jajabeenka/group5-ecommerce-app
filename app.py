import io
import base64
import qrcode
from flask import Flask, render_template,request, jsonify
from flask_socketio import SocketIO

# 1. Initialize the application
app = Flask(__name__)

socketio = SocketIO(app, cors_allowed_origins="*")
# 2. Define a route and its handling function
@app.route("/")

def home():

    return render_template("login.html")

@app.route("/dashboard)

def dashboard():
    return render_template(index.html)

@app.route("/generate_qr", methods=["POST"])
def generate_qr():

    data = request.get_json()

    total_items = data["totalItems"]
    total_amount = data["totalAmount"]

    print(total_items)
    print(total_amount)

    payment_url = f"http://44.203.231.247/pay?amt={total_amount}"

    img = qrcode.make(payment_url)

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")

    qr = base64.b64encode(buffer.getvalue()).decode()

    return jsonify({
        "qr": qr
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
