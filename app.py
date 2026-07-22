import io
import base64
import qrcode
from flask import Flask, render_template,request, jsonify
# 1. Initialize the application
app = Flask(__name__)

# 2. Define a route and its handling function
@app.route("/")

def home():

    return render_template("index.html")

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

@app.route("/payment_success", methods=["POST"])
def payment_success():
    transaction_id = request.args.get("transaction_id")
    status = request.args.get("status")

    if status == "SUCCESS":
        print(f"{transaction_id} paid!")
        # Update your database here

    return jsonify({
        "message": "received",
        "transaction_id": transaction_id,
        "status": status
    })

# 3. Run the development server
if __name__ == "__main__":
    app.run(debug=True)