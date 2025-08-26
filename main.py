from flask import Flask, render_template, request, jsonify,redirect,url_for,make_response
import mysql.connector
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:@localhost/store_db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db2 = SQLAlchemy(app)

class Product(db2.Model):
    __tablename__ = "products"

    product_id = db2.Column(db2.Integer, primary_key=True)
    name = db2.Column(db2.String(255), nullable=False)
    barcode = db2.Column(db2.String(255))
    current_price = db2.Column(db2.Float)

    def __repr__(self):
        return f"<Product {self.name}>"
def get_db():
    return mysql.connector.connect(
        host="localhost", user="root", password="", database="store_db"
    )

@app.route("/")
def home():
    return render_template("index.html")
 
@app.route("/scanner",methods=["GET"])
def scanner():
    db = get_db(); cursor = db.cursor()
    return render_template("scanbr.html")
@app.route("/manageproducts",methods=["GET"])
def manageproducts():
    db = get_db(); cursor = db.cursor()
    return render_template("manageproducts.html")
@app.route("/addproducts",methods=["GET"])
def addproducts():
    db = get_db(); cursor = db.cursor()
    return render_template("addproduct.html")
@app.route("/insertproduct", methods=["POST"])
def insertproduct():
    product_price = float(request.json["product_price"])
    product_name=request.json["product_name"]
    product_brcode=request.json["product_brcode"]
    product = Product.query.filter_by(barcode=product_brcode).first()
    if product:
        return jsonify({
            "success": False,
            "status": "product barcode exists",
            "product_name": product_name,
            "product_price": product_price,
            "product_brcode":product_brcode
        })
    db = get_db(); cursor = db.cursor()
    cursor.execute("INSERT INTO products(name,current_price,barcode) VALUES (%s,%s,%s)", (product_name,product_price,product_brcode,))
    db.commit()
    
    return jsonify({
            "success": True,
            "status": "product added",
            "product_name": product_name,
            "product_price": product_price,
            "product_brcode":product_brcode
        })
@app.route("/productlist",methods=["GET"])
def productlist():
	db = get_db(); cursor = db.cursor()
	cursor.execute("select * from products")
	results=cursor.fetchall()
	response = make_response(render_template("products_list.html",data=results))
	response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
	response.headers["Pragma"] = "no-cache"
	response.headers["Expires"] = "0"
	return response
@app.route("/search")
def search():
    query = request.args.get("q", "")

    results = Product.query.filter(
        (Product.name.like(f"%{query}%")) |
        (Product.barcode.like(f"%{query}%"))
    ).all()
    print(results)
    return render_template("search_product.html", results=results, query=query)
@app.route("/product/<int:product_id>/edit", methods=["GET", "POST"])
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)

    if request.method == "POST":
        product.name = request.json["product_name"]
        product.current_price= float(request.json["product_price"])
        product.barcode = request.json["product_brcode"]

        db2.session.commit()

        return jsonify({
            "success": True,
            "status": "product updated",
            "product_name": product.name,
            "product_price": product.current_price,
            "product_brcode":product.barcode
        })

    return render_template("modifyproduct.html", product=product)
@app.route("/product/<int:product_id>/remove", methods=["GET", "POST"])
def remove_product(product_id):
    product = Product.query.get(product_id)
    if request.method == "POST":
        if product:
            db2.session.delete(product)
            db2.session.commit()
        return """
    <script>
        // Close current window
        // Optional: redirect parent window if opened as popup
        if (window.opener) {
             window.opener.location.reload() ;
        }
        window.close();
    </script>
    """
    return render_template("confirm_delete.html", product=product)
app.run(host="0.0.0.0", port=5000, debug=True)