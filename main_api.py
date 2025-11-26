from flask import Flask,redirect,url_for,session,jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from models import *
from blueprints import api_users_bp,tools_bp,api_products_bp,api_sales_bp
from config import SECRET_KEY
app = Flask(__name__)
CORS(app)
app.secret_key = SECRET_KEY
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:@localhost/store_db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db2.init_app(app)

app.register_blueprint(api_users_bp)
app.register_blueprint(api_products_bp)
app.register_blueprint(api_sales_bp)
app.register_blueprint(tools_bp)

@app.route("/testapi", methods=["POST","GET"])
def test_api():
    # Return success JSON with token
    return jsonify({
        "message": "test work",
        "token": 1999
    }), 200

with app.app_context():
    db2.create_all()   # ✅ Creates all tables if they don't exist
    print("Tables created successfully!")
print(app.root_path)
app.run(host="0.0.0.0", port=5000, debug=True)