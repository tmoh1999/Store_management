from flask import Flask, render_template, request, jsonify,redirect,url_for,make_response,send_file,session,flash
from datetime import datetime,date,timedelta
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from openpyxl import load_workbook,Workbook
from sqlalchemy import desc
from weasyprint import HTML,CSS
import io
import os
import webbrowser
import subprocess
from models import *
from blueprints import users_bp,products_bp,sales_bp,suppliers_bp,purchases_bp,transactions_bp,tools_bp
app = Flask(__name__)
app.secret_key = "mohmath"
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:@localhost/store_db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db2.init_app(app)

app.register_blueprint(users_bp)
app.register_blueprint(products_bp)
app.register_blueprint(sales_bp)
app.register_blueprint(suppliers_bp)
app.register_blueprint(purchases_bp)
app.register_blueprint(transactions_bp)
app.register_blueprint(tools_bp)

@app.route("/")
def home():
    if "user" in session:
        return redirect(url_for("users.dashboard"))
    return redirect(url_for("users.login"))


with app.app_context():
    db2.create_all()   # ✅ Creates all tables if they don't exist
    print("Tables created successfully!")
print(app.root_path)
app.run(host="0.0.0.0", port=5000, debug=True)