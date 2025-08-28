from flask import Flask, render_template, request, jsonify,redirect,url_for,make_response
import mysql.connector
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
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
    quantity = db2.Column(db2.Integer)

    def __repr__(self):
        return f"<Product {self.name}>"
class ProductBatches(db2.Model):
    __tablename__ = "product_batches"
    id=product_id = db2.Column(db2.Integer, primary_key=True)
    product_id = db2.Column(db2.Integer)
    date_received = db2.Column(db2.DateTime(timezone=True), server_default=func.now())
    purchase_price = db2.Column(db2.Float)
    quantity = db2.Column(db2.Integer)

    def __repr__(self):
        return f"<ProductBatches {self.id}>"
class Sales(db2.Model):
    __tablename__ = "sales"
    sale_id = db2.Column(db2.Integer, primary_key=True)
    sale_date = db2.Column(db2.DateTime(timezone=True), server_default=func.now())
    def __repr__(self):
        return f"<Sale {self.sale_id}>"

class SaleItems(db2.Model):
    __tablename__ = "sale_items"
    item_id = db2.Column(db2.Integer, primary_key=True)
    sale_id = db2.Column(db2.Integer)
    product_id = db2.Column(db2.Integer)
    quantity=db2.Column(db2.Integer)
    unit_price = db2.Column(db2.Float)
    def __repr__(self):
        return f"<SaleItem {self.item_id}>"
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

@app.route("/product/<int:product_id>/addproducts",methods=["GET", "POST"])
def addproducts(product_id):
    db = get_db(); cursor = db.cursor()
    product=None
    print(product_id)
    if product_id>0:
    	
          product = Product.query.get_or_404(product_id)
    return render_template("addproduct.html",product=product)
@app.route("/insertproduct", methods=["POST"])
def insertproduct():
    db = get_db(); cursor = db.cursor()
    product_price = float(request.json["product_price"])
    product_purchase_price = float(request.json["product_purchase_price"])
    
    product_quantity= int(request.json["product_quantity"])
    product_name=request.json["product_name"]
    product_brcode=request.json["product_brcode"]
    product = Product.query.filter_by(barcode=product_brcode).first()
    if product:
    	
        print(product.quantity,product_quantity)
        product.quantity=product.quantity+product_quantity
        print(product.quantity)
        product.current_price=product_price
        db2.session.commit()
        cursor.execute("INSERT INTO product_batches(product_id,quantity,purchase_price) VALUES (%s,%s,%s)", (product.product_id,product_quantity,product_purchase_price,))
        db.commit()
        return jsonify({
            "success": False,
            "status": "product barcode exists",
            "product_name": product_name,
            "product_price": product_price,
            "product_brcode":product_brcode
        })
    else:
         
         
         
         new_product=Product(name=product_name,current_price=product_price,barcode=product_brcode,quantity=product_quantity)
         product = Product.query.filter_by(barcode=product_brcode).first()
         #print(product)
         db2.session.add(new_product)
         db2.session.commit()
         print(new_product.product_id)
         product = Product.query.filter_by(barcode=product_brcode).first()
         #print(product,product.product_id,product.name)        
         cursor.execute("INSERT INTO product_batches(product_id,quantity,purchase_price) VALUES (%s,%s,%s)", (product.product_id,product_quantity,product_purchase_price,))
         #print(product,product.product_id)        
         
         
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
@app.route("/search2",methods=["POST"])
def search2():
    query = request.json["query"]
    sale_id=int(request.json["sale_id"])
    results = Product.query.filter(
        (Product.name.like(f"%{query}%")) |
        (Product.barcode.like(f"%{query}%"))
    ).all()
    print(results)
    results_list=[
        {"id": p.product_id, "name": p.name, "barcode": p.barcode, "price": p.current_price}
        for p in results
    ]
    new_sale_item=SaleItems(sale_id=sale_id,product_id=results[0].product_id,unit_price=results[0].current_price,quantity=1)
    db2.session.add(new_sale_item)
    db2.session.commit()
    
    results2 = SaleItems.query.filter(SaleItems.sale_id==sale_id).all()
    
    print(len(results2))
    total=0
    for st in results2:
    	total+=st.unit_price*st.quantity
    print(total)
    return jsonify({
              "success": True,
              "results": results_list,
              "total":total
    })
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
            product_batches = ProductBatches.query.filter(ProductBatches.product_id==product_id).all()
            for batch in product_batches:
            	db2.session.delete(batch)
            db2.session.commit()
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
@app.route("/product/<int:product_id>/viewpurchases", methods=["GET", "POST"])
def view_purchases(product_id):
    db = get_db(); cursor = db.cursor()
    cursor.execute("SELECT o.product_id, p.barcode,p.name,p.current_price,o.purchase_price, o.quantity,o.date_received FROM product_batches o INNER JOIN products p ON o.product_id = p.product_id and o.product_id=%s order by o.date_received DESC",(product_id,))
    results=cursor.fetchall()
    print(len(results))
    return render_template("product_purchases.html",data=results)

#####Sales
@app.route("/managesales",methods=["GET"])
def managesales():
    db = get_db(); cursor = db.cursor()
    return render_template("managesales.html")

@app.route("/sale/add",methods=["POST"])
def addsale():
    db = get_db(); cursor = db.cursor()
    new_sale=Sales()
    db2.session.add(new_sale)
    db2.session.commit()
    print(new_sale,new_sale.sale_id)
    return render_template("sale_items.html",sale=new_sale)
@app.route("/sale/add_item", methods=["GET", "POST"])
def addsaleitem():
    db = get_db(); cursor = db.cursor()
    sale_id=int(request.json["sale_id"])
    price=float(request.json["price"])
    quantity=int(request.json["quantity"])
    new_sale_item=SaleItems(sale_id=sale_id,unit_price=price,quantity=quantity)
    db2.session.add(new_sale_item)
    db2.session.commit()
    print(new_sale_item,new_sale_item.unit_price)
    results2 = SaleItems.query.filter(SaleItems.sale_id==sale_id).all()
    
    print(len(results2))
    total=0
    for st in results2:
    	total+=st.unit_price*st.quantity
    print(total)
    return jsonify({
            "success": True,
            "status": "same_item added",
            "sale_id":new_sale_item.sale_id,
            "price": new_sale_item.unit_price,
            "quantity":new_sale_item.quantity,
             "total":total
    })    
app.run(host="0.0.0.0", port=5000, debug=True)