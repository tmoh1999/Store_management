from flask import Flask, render_template, request, jsonify,redirect,url_for,make_response,send_file,session,flash
import mysql.connector
from datetime import datetime,date,timedelta
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from openpyxl import load_workbook,Workbook
from sqlalchemy import desc
from weasyprint import HTML,CSS
from werkzeug.security import generate_password_hash, check_password_hash
import io
import os
import webbrowser
import subprocess
app = Flask(__name__)
app.secret_key = "mohmath"
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:@localhost/store_db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db2 = SQLAlchemy(app)
def isLogin():
    print(session)
    
class User(db2.Model):
    id = db2.Column(db2.Integer, primary_key=True)
    username = db2.Column(db2.String(100), unique=True, nullable=False)
    password = db2.Column(db2.String(200), nullable=False)

@app.route("/")
def home():
    if "user" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already exists!")
            return redirect(url_for("register"))

        hashed_pw = generate_password_hash(password)
        new_user = User(username=username, password=hashed_pw)
        db2.session.add(new_user)
        db2.session.commit()
        flash("Registration successful! Please log in.")
        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session["user"] = username
            session["user_id"] = user.id
            flash("Login successful!")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid username or password")
            return redirect(url_for("login"))

    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "user" not in session: return redirect(url_for("login"))
    return render_template("index.html", username=session["user"])

@app.route("/logout")
def logout():
    session.pop("user", None)
    flash("You have been logged out.")
    return redirect(url_for("login"))
class Product(db2.Model):
    __tablename__ = "products"

    product_id = db2.Column(db2.Integer, primary_key=True)
    name = db2.Column(db2.String(255), nullable=False)
    barcode = db2.Column(db2.String(255))
    current_price = db2.Column(db2.Float)
    quantity = db2.Column(db2.Integer, server_default="0")
    quantity_float=db2.Column(db2.Float, server_default="0.0")
    user_id = db2.Column(db2.Integer, db2.ForeignKey("user.id"), nullable=False)
    def __repr__(self):
        return f"<Product {self.name}>"

class ProductBatches(db2.Model):
    __tablename__ = "product_batches"
    id= db2.Column(db2.Integer, primary_key=True)
    product_id = db2.Column(db2.Integer)
    date_received = db2.Column(db2.DateTime(timezone=True), server_default=func.now())
    purchase_price = db2.Column(db2.Float)
    quantity = db2.Column(db2.Integer, server_default="0")
    quantity_float=db2.Column(db2.Float, server_default="0.0")
    def __repr__(self):
          return f"<ProductBatches {self.id}>"

class Purchases(db2.Model):
    __tablename__ = "purchases"
    purchase_id= db2.Column(db2.Integer, primary_key=True)
    supplier_id = db2.Column(db2.Integer)
    purchase_date = db2.Column(db2.DateTime(timezone=True), server_default=func.now())
    total_amount = db2.Column(db2.Float, server_default="0.0")
    status = db2.Column(db2.Boolean, server_default="0")
    description = db2.Column(db2.String(250))
    user_id = db2.Column(db2.Integer, db2.ForeignKey("user.id"), nullable=False)
    def __repr__(self):
        return f"<Purchases {self.purchase_id}>"


class PurchaseItems(db2.Model):
    __tablename__ = "purchase_items"
    purchase_item_id = db2.Column(db2.Integer, primary_key=True)
    purchase_id = db2.Column(db2.Integer)
    product_id = db2.Column(db2.Integer)
    purchase_price = db2.Column(db2.Float)
    quantity = db2.Column(db2.Integer, server_default="0")
    quantity_float=db2.Column(db2.Float, server_default="0.0")
    remain_quantity=db2.Column(db2.Float, server_default="0.0")
    def __repr__(self):
        return f"<PurchasesItems {self.purchase_item_id}>"
class Sales(db2.Model):
    __tablename__ = "sales"
    sale_id = db2.Column(db2.Integer, primary_key=True)
    sale_date = db2.Column(db2.DateTime(timezone=True), server_default=func.now())
    total_amount = db2.Column(db2.Float)
    user_id = db2.Column(db2.Integer, db2.ForeignKey("user.id"), nullable=False)
    def __repr__(self):
        return f"<Sale {self.sale_id}>"

class SaleItems(db2.Model):
    __tablename__ = "sale_items"
    item_id = db2.Column(db2.Integer, primary_key=True)
    sale_id = db2.Column(db2.Integer)
    product_id = db2.Column(db2.Integer)
    quantity=db2.Column(db2.Integer, server_default="0")
    description = db2.Column(db2.String(255))
    unit_price = db2.Column(db2.Float)
    profit = db2.Column(db2.Float, server_default="0.0")
    quantity_float=db2.Column(db2.Float, server_default="0.0")
    def __repr__(self):
        return f"<SaleItem {self.item_id}>"
class Suppliers(db2.Model):
    __tablename__ = "suppliers"

    supplier_id = db2.Column(db2.Integer, primary_key=True)
    name = db2.Column(db2.String(64))
    email = db2.Column(db2.String(64))
    phone = db2.Column(db2.String(128))
    user_id = db2.Column(db2.Integer, db2.ForeignKey("user.id"), nullable=False)
    def __repr__(self):
        return f"<Supplier {self.name}>"  
class SalePurchaseUsage(db2.Model):
    id = db2.Column(db2.Integer, primary_key=True)
    item_id = db2.Column(db2.Integer, db2.ForeignKey('sale_items.item_id'))
    purchase_item_id = db2.Column(db2.Integer, db2.ForeignKey('purchase_items.purchase_item_id'))
    quantity_used = db2.Column(db2.Float, server_default="0.0")
def get_db():
    return mysql.connector.connect(
        host="localhost", user="root", password="", database="store_db"
    )
    
class Transactions(db2.Model):
    __tablename__ = "transactions"

    id = db2.Column(db2.Integer, primary_key=True)
    date = db2.Column(db2.DateTime(timezone=True), server_default=func.now())
    type = db2.Column(db2.String(50))
    amount = db2.Column(db2.Float, nullable=False)
    sale_id = db2.Column(db2.Integer, db2.ForeignKey("sales.sale_id"), nullable=True)
    purchase_id = db2.Column(db2.Integer, db2.ForeignKey("purchases.purchase_id"), nullable=True)
    note = db2.Column(db2.String(255))
    user_id = db2.Column(db2.Integer, db2.ForeignKey("user.id"), nullable=False)

    def __repr__(self):
        return f"<Transaction {self.type} {self.amount}>"

with app.app_context():
    db2.create_all()   # ✅ Creates all tables if they don't exist
    print("Tables created successfully!")
def getDate(filt):
        l=filt.split('-')
        year=int(l[0])
        month=int(l[1])
        day=int(l[2])
        return date(year,month,day)
def roundFive(mon):
    if mon%5!=0:
        res=(mon//5+1)*5
        return res
    return mon
    

 
@app.route("/scanner",methods=["GET"])
def scanner():
    if "user" not in session: return redirect(url_for("login"))
    return render_template("scanbr.html")
@app.route("/manageproducts",methods=["GET"])
def manageproducts():
    if "user" not in session: return redirect(url_for("login"))
    return render_template("manageproducts.html")

@app.route("/product/<int:product_id>/addproducts",methods=["GET", "POST"])
def addproducts(product_id):
    if "user" not in session: return redirect(url_for("login"))
    product=None
    print(product_id)
    if product_id>0:
    	
          product = Product.query.get_or_404(product_id)
    return render_template("addproduct.html",product=product)

@app.route("/insertproductpurchase", methods=["POST"])
def insertproductpurchase():
    if "user" not in session: return redirect(url_for("login"))
    product_price = float(request.json["product_price"])
    product_purchase_price = float(request.json["product_purchase_price"])
    
    product_quantity= float(request.json["product_quantity"])
    
    product_name=request.json["product_name"]
    product_brcode=request.json["product_brcode"]
    purchase_id=request.json["purchase_id"]
    purchase=Purchases.query.filter(Purchases.purchase_id==purchase_id).first()
    if product_brcode=="":
       product_brcode=datetime.now().strftime("%Y%m%d%H%M%S%f")
    product = Product.query.filter_by(barcode=product_brcode).first()
    if product:
        if purchase and purchase.status:
              product.quantity_float=product.quantity_float+product_quantity
        product.current_price=product_price
        db2.session.commit()
        ##batch=ProductBatches(product_id=product.product_id,purchase_price=product_purchase_price,quantity_float=product_quantity)
        ##db2.session.add(batch)
        ##db2.session.commit()
        
        if  purchase:
               purchase_item=PurchaseItems(purchase_id=purchase_id,product_id=product.product_id,purchase_price=product_purchase_price,quantity_float=product_quantity,remain_quantity=product_quantity)
               db2.session.add(purchase_item)
               purchase.total_amount+=product_purchase_price*product_quantity
        db2.session.commit()
        return jsonify({
            "success": True,
            "status": "product updated",
            "product_name": product_name,
            "product_price": product_price,
            "product_brcode":product_brcode
        })
    else:
         
         
         
         new_product=Product(name=product_name,current_price=product_price,barcode=product_brcode,user_id=int(session["user_id"]))
         product = Product.query.filter_by(barcode=product_brcode).first()
         #print(product)
         db2.session.add(new_product)
         db2.session.commit()
         print(new_product.product_id)
         product = Product.query.filter_by(barcode=product_brcode).first()
         #print(product,product.product_id,product.name)        
         ##batch=ProductBatches(product_id=product.product_id,purchase_price=product_purchase_price,quantity_float=product_quantity)
         ##db2.session.add(batch)
         ##db2.session.commit()
         #print(product,product.product_id)
         #purchase=Purchases.query.filter(Purchases.purchase_id==purchase_id).first()
         if  purchase:
               purchase_item=PurchaseItems(purchase_id=purchase_id,product_id=product.product_id,purchase_price=product_purchase_price,quantity_float=product_quantity,remain_quantity=product_quantity)
               db2.session.add(purchase_item)
               purchase.total_amount+=product_purchase_price*product_quantity
         db2.session.commit()
         
         
         return jsonify({
              "success": True,
              "status": "product added",
              "product_name": product_name,
              "product_price": product_price,
              "product_brcode":product_brcode
          })
    
@app.route("/insertemptyproduct", methods=["POST"])
def insertemptyproduct():
    if "user" not in session: return redirect(url_for("login"))
    product_price = float(request.json["product_price"])
    product_name=request.json["product_name"]
    product_brcode=request.json["product_brcode"]
    if product_brcode=="":
       product_brcode=datetime.now().strftime("%Y%m%d%H%M%S%f")
    product = Product.query.filter_by(barcode=product_brcode).first()
    
    if product:
        return jsonify({
            "success": True,
            "status": "product updated",
            "product_name": product_name,
            "product_price": product_price,
            "product_brcode":product_brcode
        })
    else:
         
         
         
         new_product=Product(name=product_name,current_price=product_price,barcode=product_brcode,user_id=int(session["user_id"]))
         product = Product.query.filter_by(barcode=product_brcode).first()
         #print(product)
         db2.session.add(new_product)
         db2.session.commit()
         print(new_product.product_id)
         return jsonify({
              "success": True,
              "status": "product added",
              "product_name": product_name,
              "product_price": product_price,
              "product_brcode":product_brcode
          })
    


@app.route("/productlist",methods=["GET","POST"])
def productlist():
    if "user" not in session: return redirect(url_for("login"))
    products = Product.query.filter(Product.user_id==int(session["user_id"])).order_by(desc(Product.product_id)).all()
    if request.method=="POST":
        query = request.json["search_q"]
        products_filter = int(request.json["products_filter"])
        if query:
            products = Product.query.filter(
            ((Product.name.like(f"%{query}%")) |
            (Product.barcode.like(f"%{query}%"))) & (Product.user_id==int(session["user_id"]))).order_by(desc(Product.product_id)).all()
        
        if products_filter==1:
           products = Product.query.filter(Product.quantity_float==0.0,Product.user_id==int(session["user_id"])).order_by(desc(Product.product_id)).all()
        elif products_filter==2:
        	products = Product.query.filter(Product.quantity_float>0.0,Product.user_id==int(session["user_id"])).order_by(desc(Product.product_id)).all()
        results_list=[
        {"id": p.product_id, "name": p.name, "barcode": p.barcode, "price": p.current_price,"quantity":p.quantity_float} for p in products]
        return jsonify({
              "success": True,
              "results": results_list
        })
    response = make_response(render_template("products_list.html",data=products,mode="manage"))
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response
@app.route("/search")
def search():
    if "user" not in session: return redirect(url_for("login"))
    query = request.args.get("q", "")

    results = Product.query.filter(
        ((Product.name.like(f"%{query}%")) |
        (Product.barcode.like(f"%{query}%"))) &(Product.user_id==int(session["user_id"]))
    ).all()
    print(results)
    return render_template("search_product.html", results=results, query=query)
@app.route("/search2",methods=["POST"])
def search2():
    if "user" not in session: return redirect(url_for("login"))
    query = request.json["query"]
    sale_id=int(request.json["sale_id"])
    results = Product.query.filter(
        ((Product.name.like(f"%{query}%")) |
        (Product.barcode.like(f"%{query}%"))) &(Product.user_id==int(session["user_id"]))
    ).all()
    print(results)
    if len(results)==0:
       return jsonify({
              "success": False,
              "results": [],
              "total":0
       })
    results_list=[
        {"id": p.product_id, "name": p.name, "barcode": p.barcode, "price": p.current_price}
        for p in results
    ]
    rs=SaleItems.query.filter(SaleItems.sale_id==sale_id,SaleItems.product_id==results[0].product_id).first()
    if rs:
    	rs.quantity_float+=1
    else:
        new_sale_item=SaleItems(sale_id=sale_id,product_id=results[0].product_id,unit_price=results[0].current_price,quantity_float=1)
        db2.session.add(new_sale_item)
    db2.session.commit()
    
    results2 = SaleItems.query.filter(SaleItems.sale_id==sale_id).all()
    result_list2=[]
    for r in results2:
       print(r.product_id)
       if r.product_id:
       	p = Product.query.filter(Product.product_id==r.product_id,Product.user_id==int(session["user_id"])).first()
       	x={"item_id": r.item_id, "name": p.name, "barcode": p.barcode, "price": r.unit_price,"quantity":r.quantity_float}
       else:
           x={"item_id": r.item_id, "name": "", "barcode": "",  "price": r.unit_price,"quantity":r.quantity_float}    
           
       result_list2.append(x)
    print(len(results2))
    total=0
    for st in results2:
    	total+=st.unit_price*st.quantity_float
    print(total)
    
    return jsonify({
              "success": True,
              "results": result_list2,
              "total":total
    })
@app.route("/product/<int:product_id>/edit", methods=["GET", "POST"])
def edit_product(product_id):
    if "user" not in session: return redirect(url_for("login"))
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
    if "user" not in session: return redirect(url_for("login"))
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
@app.route("/product/<int:product_id>/viewpurchases", methods=["GET", "POST"])
def view_purchases(product_id):
    if "user" not in session: return redirect(url_for("login"))
    db = get_db(); cursor = db.cursor()
    cursor.execute("""
SELECT p.product_id, p.barcode,
p.name,p.current_price,
it.purchase_price, it.quantity_float,pu.purchase_date 
FROM purchases pu
JOIN purchase_items it
ON pu.purchase_id = it.purchase_id 
JOIN products p
ON it.product_id = p.product_id 
where it.product_id=%s 
order by pu.purchase_date DESC
""",(product_id,))
    results=cursor.fetchall()
    print(len(results))
    return render_template("product_purchases.html",data=results)
@app.route("/product/<int:product_id>/viewsales", methods=["GET", "POST"])
def view_product_sales(product_id):
    if "user" not in session: return redirect(url_for("login"))
    db = get_db(); cursor = db.cursor()
    cursor.execute("""
SELECT p.product_id, p.barcode,
p.name,p.current_price,
it.unit_price, it.quantity_float,sa.sale_date 
FROM sales sa
JOIN sale_items it
ON sa.sale_id = it.sale_id 
JOIN products p
ON it.product_id = p.product_id 
where it.product_id=%s 
order by it.item_id DESC
""",(product_id,))
    results=cursor.fetchall()
    print(len(results))
    return render_template("product_sales.html",data=results)
@app.route("/product/select/<string:type>/<int:row_id>", methods=["GET", "POST"])
def selectproduct(type,row_id):
    if "user" not in session: return redirect(url_for("login"))
    products = Product.query.filter(Product.user_id==int(session["user_id"])).order_by(desc(Product.product_id)).all()
    response = make_response(render_template("products_list.html",data=products,mode="select",type=type,row_id=row_id))
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response
@app.route("/product/selected", methods=["GET", "POST"])
def selectedproduct():
    if "user" not in session: return redirect(url_for("login"))
    product_id=int(request.json["product_id"])
    row_id=int(request.json["row_id"])
    type=request.json["type"]	
    print("       type:",type)
    print("       row_id:",row_id)
    print("       product_id:",product_id)
    product = Product.query.filter(Product.product_id==product_id).first()
    if product:
        if "sale_items" in type:
            item=SaleItems.query.filter(SaleItems.item_id==row_id).first()
            if item:
               item.product_id=product.product_id
               item.description=product.name
               print("            product.quantity_float:",product.quantity_float)
               print("            item.quantity_float:",item.quantity_float)
               if type!="sale_items_before":
                    product.quantity_float-=item.quantity_float
               print("            product.quantity_float:",product.quantity_float)
               purchase_item=PurchaseItems.query.filter(PurchaseItems.product_id==item.product_id).order_by(desc(PurchaseItems.purchase_item_id)).first()
               if purchase_item:
                  item.profit=item.unit_price-purchase_item.purchase_price
        elif type=="purchase_items":
            purchase=Purchases.query.filter(Purchases.purchase_id==row_id,Purchases.user_id==int(session["user_id"])).first()
            if purchase:
            	print("&&&&&&&&&&&")
            	x={"product_id": product.product_id, "name": product.name, "barcode": product.barcode, "price": product.current_price}
            	return jsonify({
                 "success": True,
                 "results":x
                })			
        db2.session.commit()
    return jsonify({
              "success": True
    })			
#####Sales
@app.route("/managesales",methods=["GET"])
def managesales():
    if "user" not in session: return redirect(url_for("login"))
    return render_template("managesales.html")

@app.route("/sale/add",methods=["POST"])
def addsale():
    if "user" not in session: return redirect(url_for("login"))
    new_sale=Sales(user_id=int(session["user_id"]))
    db2.session.add(new_sale)
    db2.session.commit()
    print(new_sale,new_sale.sale_id)
    return render_template("sale_items.html",sale=new_sale)
@app.route("/sale/add_item", methods=["GET", "POST"])
def addsaleitem():
    if "user" not in session: return redirect(url_for("login"))
    sale_id=int(request.json["sale_id"])
    price=float(request.json["price"])
    quantity=float(request.json["quantity"])
    description=request.json["description"]
    new_sale_item=SaleItems(sale_id=sale_id,unit_price=price,quantity_float=quantity,description=description)
    db2.session.add(new_sale_item)
    db2.session.commit()
    print(new_sale_item,new_sale_item.unit_price)
    results2 = SaleItems.query.filter(SaleItems.sale_id==sale_id).all()
    result_list2=[]
    for r in results2:
       print(r.product_id)
       if r.product_id:
       	p = Product.query.filter(Product.product_id==r.product_id,Product.user_id==int(session["user_id"])).first()
       	x={"item_id": r.item_id, "name": p.name, "barcode": p.barcode, "price": r.unit_price,"quantity":r.quantity_float,"description":r.description}
       else:
           x={"item_id": r.item_id, "name": "", "barcode": "",  "price": r.unit_price,"quantity":r.quantity_float,"description":r.description}    
           
       result_list2.append(x)
    print(len(results2))
    total=0
    for st in results2:
    	total+=st.unit_price*st.quantity_float
    print(total)
    
    return jsonify({
              "success": True,
              "results": result_list2,
              "total":total
    })
@app.route("/sale/update_item", methods=["GET", "POST"])
def updatesaleitem():
    if "user" not in session: return redirect(url_for("login"))
    sale_id=int(request.json["sale_id"])
    item_id=int(request.json["item_id"])
    target=request.json["target"]
    new_value=request.json["new_value"]
    
    item=SaleItems.query.filter(SaleItems.sale_id==sale_id,SaleItems.item_id==item_id).first()
    if item:
       print(target,item_id)
       if target=="quantity":
          rollBackSaleItem(item_id)
          item.quantity_float=float(new_value)
          db2.session.flush()
          validateSaleItem(item)
          db2.session.commit()
       elif target=="price":
        	item.unit_price=float(new_value)
       elif target=="profit":
        	item.profit=float(new_value)
       else:
            item.description=new_value
       db2.session.commit()
    sale=Sales.query.filter(Sales.sale_id==sale_id,Sales.user_id==int(session["user_id"])).first()
    transaction=Transactions.query.filter(Transactions.sale_id==sale_id,Transactions.user_id==int(session["user_id"])).first()
    results2 = SaleItems.query.filter(SaleItems.sale_id==sale_id).all()
    result_list2=[]
    total=0
    for r in results2:
       total+=r.quantity_float*r.unit_price
       if r.product_id:
       	p = Product.query.filter(Product.product_id==r.product_id,Product.user_id==int(session["user_id"])).first()
       	x={"item_id": r.item_id, "name": p.name, "barcode": p.barcode, "price": r.unit_price,"quantity":r.quantity_float,"description":r.description,"profit":r.profit}
       else:
           x={"item_id": r.item_id, "name": "", "barcode": "",  "price": r.unit_price,"quantity":r.quantity_float,"description":r.description,"profit":r.profit}    
           
       result_list2.append(x)
    sale.total_amount=total
    
    print(len(results2))
    if transaction:
       transaction.amount=total;
    db2.session.commit()
    return jsonify({
              "success": True,
              "results": result_list2,
              "total":total
    })
@app.route("/sale/refresh", methods=["GET", "POST"])
def resfreshsaleitems():
    if "user" not in session: return redirect(url_for("login"))
    sale_id=int(request.json["sale_id"])
    
    
    
    sale=Sales.query.filter(Sales.sale_id==sale_id,Sales.user_id==int(session["user_id"])).first()
    transaction=Transactions.query.filter(Transactions.sale_id==sale_id,Transactions.user_id==int(session["user_id"])).first()
    results2 = SaleItems.query.filter(SaleItems.sale_id==sale_id).all()
    result_list2=[]
    total=0
    for r in results2:
       total+=r.quantity_float*r.unit_price
       if r.product_id:
       	p = Product.query.filter(Product.product_id==r.product_id,Product.user_id==int(session["user_id"])).first()
       	x={"item_id": r.item_id, "name": p.name, "barcode": p.barcode, "price": r.unit_price,"quantity":r.quantity_float,"description":r.description,"profit":r.profit}
       else:
           x={"item_id": r.item_id, "name": "", "barcode": "",  "price": r.unit_price,"quantity":r.quantity_float,"description":r.description,"profit":r.profit}    
           
       result_list2.append(x)
    
    
    
    
    
    return jsonify({
              "success": True,
              "results": result_list2,
              "total":total
    })
@app.route("/sale/remove", methods=["GET", "POST"])
def removesale():
    if "user" not in session: return redirect(url_for("login"))
    sale_id=int(request.json["sale_id"])


    items=SaleItems.query.filter(SaleItems.sale_id==sale_id).all()
    for item in items:
        rollBackSaleItem(item.item_id)
        db2.session.delete(item)
        
    db2.session.commit()
    sales = Sales.query.filter(Sales.sale_id==sale_id,Sales.user_id==int(session["user_id"])).all()
    transactions=Transactions.query.filter(Transactions.sale_id==sale_id,Transactions.user_id==int(session["user_id"])).all()
    for t in transactions:
          db2.session.delete(t)     
    db2.session.commit()
    for r in sales:
          db2.session.delete(r)
    db2.session.commit()
    

    return jsonify({
              "success": True,
              "sale deleted": sale_id
    })
def validateSaleItem(r):
	
   if r.product_id:
       p = Product.query.filter(Product.product_id==r.product_id,Product.user_id==int(session["user_id"])).first()
       p.quantity_float=max(p.quantity_float-r.quantity_float,0)
       ####for each item save reduced pjrchaseitem 
       purchase_items = PurchaseItems.query.filter(PurchaseItems.product_id == r.product_id).order_by(PurchaseItems.purchase_item_id).all()
       g=r.quantity_float
       for batch in purchase_items:
           if batch.remain_quantity>=g:
              batch.remain_quantity-=g
              sale_purchase_usage=SalePurchaseUsage(item_id=r.item_id,purchase_item_id=batch.purchase_item_id,quantity_used=g)
              db2.session.add(sale_purchase_usage)
              break
           else:
              g-=batch.remain_quantity
              sale_purchase_usage=SalePurchaseUsage(item_id=r.item_id,purchase_item_id=batch.purchase_item_id,quantity_used=batch.remain_quantity)
              db2.session.add(sale_purchase_usage)
              batch.remain_quantity=0
       db2.session.commit()
def rollBackSaleItem(item_id):
    r=SaleItems.query.filter(SaleItems.item_id==item_id).first()
    if r and r.product_id:
        p = Product.query.filter(Product.product_id==r.product_id,Product.user_id==int(session["user_id"])).first()
        p.quantity_float=p.quantity_float+r.quantity_float
        items_usage=SalePurchaseUsage.query.filter(SalePurchaseUsage.item_id==item_id).all()
        for u in items_usage:
              batch=PurchaseItems.query.filter(PurchaseItems.purchase_item_id == u.purchase_item_id).order_by(PurchaseItems.purchase_item_id).first()
              batch.remain_quantity+=u.quantity_used
              db2.session.delete(u)
    db2.session.commit()
	
		
@app.route("/sale/confirm", methods=["GET", "POST"])
def confirmsale():
    if "user" not in session: return redirect(url_for("login"))
    sale_id=int(request.json["sale_id"])

    results2 = SaleItems.query.filter(SaleItems.sale_id==sale_id).all()
    result_list2=[]
    tot=0
    for r in results2:
       tot+=r.unit_price*r.quantity_float
       print(r.product_id)
       validateSaleItem(r)

                
    sale=Sales.query.filter(Sales.sale_id==sale_id,Sales.user_id==int(session["user_id"])).first()
    sale.total_amount=tot
    db2.session.commit()
    transaction=Transactions(sale_id=sale_id,type="sale",amount=tot,user_id=int(session["user_id"]))
    db2.session.add(transaction)
    db2.session.commit()
    print("sale:",sale.sale_id,"tptal_amm:",sale.total_amount,tot)
    
    return jsonify({
              "success": True,
              "id deleted": sale_id
    })

@app.route("/saleslist/<string:filt>",methods=["GET"])
def saleslist(filt):
    if "user" not in session: return redirect(url_for("login"))
    if filt=="ALL":
       sales=Sales.query.filter(Sales.user_id==int(session["user_id"])).order_by(desc(Sales.sale_date)).all()
    if filt=="Today":
       sales = Sales.query.filter(func.date(Sales.sale_date) == date.today(),Sales.user_id==int(session["user_id"])).order_by(desc(Sales.sale_date)).all()
    print(date.today())
    retdict=[]
    for sale in sales:
    	#nb products
        items=SaleItems.query.filter(SaleItems.sale_id==sale.sale_id).all()
        total=0;tquantity=0
        for item in items:
        	tquantity+=item.quantity_float
        	total+=item.unit_price*item.quantity_float
        x={"sale_id":sale.sale_id , "date": sale.sale_date, "total": total,  "quantity": tquantity,  "total_amount": sale.total_amount}
        retdict.append(x)
    response = make_response(render_template("sales_list.html",data=retdict))
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response
@app.route("/saleslist/update",methods=["POST"])
def saleslistupdate():
    if "user" not in session: return redirect(url_for("login"))
    filt=request.json["filter"]
    if filt=="ALL":
       sales=Sales.query.filter(Sales.user_id==int(session["user_id"])).order_by(desc(Sales.sale_date)).all()
    elif filt=="Today":
       sales = Sales.query.filter(func.date(Sales.sale_date) == date.today(),Sales.user_id==int(session["user_id"])).order_by(desc(Sales.sale_date)).all()
    else:
        sales = Sales.query.filter(func.date(Sales.sale_date) == date.today(),Sales.user_id==int(session["user_id"])).order_by(desc(Sales.sale_date)).all()
        
        l=filt.split('-')
        
        year=int(l[0])
        month=int(l[1])
        day=int(l[2])
        xdate=date(year,month,day)
        
        sales = Sales.query.filter(func.date(Sales.sale_date) == xdate,Sales.user_id==int(session["user_id"])).order_by(desc(Sales.sale_date)).all()
    retdict=[]
    for sale in sales:
    	#nb products
        items=SaleItems.query.filter(SaleItems.sale_id==sale.sale_id).all()
        total=0;tquantity=0
        for item in items:
        	tquantity+=item.quantity_float
        	total+=item.unit_price*item.quantity_float
        x={"sale_id":sale.sale_id , "sale_date": sale.sale_date, "total": total,  "quantity": tquantity,  "total_amount": sale.total_amount}
        retdict.append(x)
    return jsonify({
              "success": True,
              "results": retdict
     })
@app.route("/sales/<int:sale_id>/viewsaleitems", methods=["GET", "POST"])
def view_sales(sale_id):
    if "user" not in session: return redirect(url_for("login"))
    db = get_db(); cursor = db.cursor()
    cursor.execute("SELECT i.item_id,s.sale_id, s.sale_date,i.product_id,i.unit_price,i.quantity_float,i.description,i.profit FROM sale_items i INNER JOIN sales s ON i.sale_id = s.sale_id where i.sale_id=%s order by s.sale_date DESC",(sale_id,))
    results=cursor.fetchall()
    print(len(results))
    
    return render_template("sale_items_history.html",data=results)



@app.route("/saleitemslist/<string:filt>",methods=["GET"])
def saleitemslist(filt):
    if "user" not in session: return redirect(url_for("login"))
    if filt=="ALL":
       sales=Sales.query.filter(Sales.user_id==int(session["user_id"])).order_by(desc(Sales.sale_date)).all()
    if filt=="Today":
       sales = Sales.query.filter(func.date(Sales.sale_date) == date.today(),Sales.user_id==int(session["user_id"])).order_by(desc(Sales.sale_date)).all()
    print(date.today())
    retdict=[]
    for sale in sales:
    	#nb products
        items=SaleItems.query.filter(SaleItems.sale_id==sale.sale_id).all()
        
        for item in items:
            total=item.unit_price*item.quantity_float
            x={"sale_id":sale.sale_id , "date": sale.sale_date, "total": total,  "quantity": item.quantity_float,  "unit_price": item.unit_price,"description": item.description,"profit":item.profit,"product":item.product_id}
            retdict.append(x)
    response = make_response(render_template("saleitems_list.html",data=retdict))
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response
@app.route("/saleitemslist/update",methods=["POST"])
def saleitemslistupdate():
    if "user" not in session: return redirect(url_for("login"))
    date_start=request.json["date_start"]
    date_end=request.json["date_end"]
    filt2=request.json["filter2"]
    stdate=getDate(date_start)
    endate=getDate(date_end)
        
    sales = Sales.query.filter(func.date(Sales.sale_date) >= stdate,func.date(Sales.sale_date) <= endate,Sales.user_id==int(session["user_id"])).order_by(desc(Sales.sale_date)).all()
    retdict=[]
    for sale in sales:
    	#nb products
        items=SaleItems.query.filter(SaleItems.sale_id==sale.sale_id).all()
        if filt2:
            items=SaleItems.query.filter((SaleItems.sale_id==sale.sale_id )& (SaleItems.description.like(f"%{filt2}%"))).all()
            
        for item in items:
            total=item.unit_price*item.quantity_float
            print(item.unit_price)
            x={"sale_id":sale.sale_id , "date": sale.sale_date, "total": total,  "quantity": item.quantity_float,  "unit_price": item.unit_price,"description": item.description,"profit":item.profit,"product":item.product_id}
            retdict.append(x)
    
    return jsonify({
              "success": True,
              "results": retdict
     })
@app.route("/sale/statistiques",methods=["POST","GET"])
def salestatistiques():
    if "user" not in session: return redirect(url_for("login"))
    print()
    print("method:::::",request.method)
    if request.method=="POST":
        date_start=request.json["date_start"]
        date_end=request.json["date_end"]
        stdate=getDate(date_start)
        endate=getDate(date_end) 
    else:
        xdate=date.today()
        stdate=date(xdate.year,xdate.month,xdate.day)
        endate=date(xdate.year,xdate.month,xdate.day)
    current=stdate
    retdict=[]
    while current<=endate:
       print(current)
       sales = Sales.query.filter(func.date(Sales.sale_date) == current,Sales.user_id==int(session["user_id"])).order_by(desc(Sales.sale_date)).all()
       total=0;nbit=0
       for sale in sales:
          items=SaleItems.query.filter(SaleItems.sale_id==sale.sale_id).all()
          for item in items:
               nbit+=1
               total+=item.unit_price*item.quantity_float
       x={"date": current.strftime("%a, %d -%b -%Y"), "nbsales": len(sales),  "nbitems": nbit,  "total": total}
       retdict.insert(0,x)
       current+=timedelta(days=1)
    print(len(retdict))
    if request.method=="POST":
        return jsonify({
              "success": True,
              "results": retdict
         })
    
    response = make_response(render_template("sale_statistiques.html",data=retdict))
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response
@app.route("/product/import", methods=["GET", "POST"])
def upload_products():
    if "user" not in session: return redirect(url_for("login"))
    if request.method == "POST":
        file = request.files["file"]
        if not file:
            return "No file uploaded", 400
        
    
        # Load the Excel file
        wb = load_workbook(file)
        ws = wb.active   # first sheet
        name="Opening_"+datetime.now().strftime("%Y%m%d_%H%M")
        
        supplier=Suppliers(name=name,email="",phone="",user_id=int(session["user_id"]))
        db2.session.add(supplier)
        db2.session.flush()
        purchase=Purchases(supplier_id=supplier.supplier_id,user_id=int(session["user_id"]))
        db2.session.add(purchase)
        db2.session.flush()
        # Skip headers (row 1)
        total=0
        for row in ws.iter_rows(min_row=2, values_only=True):
              print("  ..... ,  ",row)
              name,barcode,quantity,price,purchase_price=row
              quantity=float(quantity)
              purchase_price=float(purchase_price)
              price=float(price)
              pd=Product.query.filter(Product.barcode==barcode).first()
              if pd:
                    print("barcode exists")
                    pd.quantity_float += quantity
                    pd.current_price = price  # if you want latest price
              else:
                   pd=Product(name=name,barcode=barcode,quantity_float=quantity,current_price=price,user_id=int(session["user_id"]))
                   db2.session.add(pd)
                   db2.session.flush()
              total+=quantity*purchase_price
              new_prod_batch=ProductBatches(product_id=pd.product_id,purchase_price=purchase_price,quantity_float=quantity)
              db2.session.add(new_prod_batch)
                  
              
              new_purchase_item=PurchaseItems(product_id=pd.product_id,purchase_price=purchase_price,purchase_id=purchase.purchase_id,quantity_float=quantity,remain_quantity=product_quantity)
              db2.session.add(new_purchase_item)
                  
        purchase.total_amount=total   
        db2.session.commit()
        return """
    <script>
        history.go(-2)
    </script>
    """

    return render_template("upload.html")


@app.route("/product/export", methods=["GET"])
def export_products():
    if "user" not in session: return redirect(url_for("login"))
    # Create a new Excel workbook
    wb = Workbook()
    ws = wb.active
    ws.title = "Products"

    # Write header row
    ws.append(["Name", "Barcode", "Quantity", "Price", "Purchase Price"])

    # Fetch all products
    products = Product.query.filter(Product.user_id==int(session["user_id"])).all()

    for p in products:
        # Get latest batch purchase price (or None if no batch exists)
        item = PurchaseItems.query.filter_by(product_id=p.product_id).order_by(PurchaseItems.purchase_id.desc()).first()
        purchase_price = item.purchase_price if item else None

        ws.append([p.name, p.barcode, p.quantity_float, p.current_price, purchase_price])

    # Save to in-memory file
    file_stream = io.BytesIO()
    wb.save(file_stream)
    file_stream.seek(0)

    return send_file(
        file_stream,
        as_attachment=True,
        download_name="products.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

@app.route("/products.pdf/<string:filt>/", defaults={"query": ""})
@app.route("/products.pdf/<string:filt>/<string:query>/")
def products_pdf(filt,query=""):
    if "user" not in session: return redirect(url_for("login"))
    # 🔹 directly reuse the same query
    products = Product.query.filter(Product.user_id==int(session["user_id"])).order_by(desc(Product.product_id)).all()
    if query:
        products = Product.query.filter(
          ((Product.name.like(f"%{query}%")) |
          (Product.barcode.like(f"%{query}%"))) & (Product.user_id==int(session["user_id"]))
          ).order_by(desc(Product.product_id)).all()
    products_filte=int(filt)      
    if products_filte==1:
           products = Product.query.filter(Product.quantity_float==0.0,Product.user_id==int(session["user_id"])).order_by(desc(Product.product_id)).all()
    elif products_filte==2:
           products = Product.query.filter(Product.quantity_float>0.0,Product.user_id==int(session["user_id"])).order_by(desc(Product.product_id)).all()
    
 
    # render to PDF
    html = render_template("products_list_pdf_template.html", data=products)
    
    css_path = os.path.join(app.root_path, "static", "css","bootstrap.min.css")
    
    pdf = HTML(string=html,base_url=app.root_path).write_pdf()
    #pdf_bytes = HTML(string=html, base_url=app.root_path).write_pdf()
    pdf_bytes = HTML(string=html, base_url=app.root_path).write_pdf(stylesheets=[CSS(css_path)])
    pdf_file = io.BytesIO(pdf_bytes)
    return send_file(
        pdf_file,
        mimetype="application/pdf",
        as_attachment=True,          # True → download, False → open in browser
        download_name="products.pdf"  # filename for the browser
    )
##suppliers
@app.route("/managesuppliers",methods=["GET"])
def managesuppliers():
    if "user" not in session: return redirect(url_for("login"))
    return render_template("manage_suppliers.html")
@app.route("/suppliers/add",methods=["GET"])
def addsupplier():
    if "user" not in session: return redirect(url_for("login"))
    return render_template("addsuplier.html")
@app.route("/suppliers/insert", methods=["POST"])
def insertsupplier():
    if "user" not in session: return redirect(url_for("login"))
    
    
    
    supplier_name=request.json["supplier_name"]
    supplier_email=request.json["supplier_email"]
    supplier_phone=request.json["supplier_phone"]
    supplier = Suppliers(name=supplier_name,email=supplier_email,phone=supplier_phone,user_id=int(session["user_id"]))
    db2.session.add(supplier)
    db2.session.commit()
    print(supplier)
         
    return jsonify({
              "success": True,
              "status": "supplier added",
              "supplier_name": supplier_name,
              "supplier_phone": supplier_phone,
              "supplier_email":supplier_email
    })
@app.route("/suppliers/list", methods=["GET"])
def supplierslist():
     if "user" not in session: return redirect(url_for("login"))
     suppliers=Suppliers.query.filter(Suppliers.user_id==int(session["user_id"])).all()
     response = make_response(render_template("suppliers_list.html",data=suppliers))
     response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
     response.headers["Pragma"] = "no-cache"
     response.headers["Expires"] = "0"
     return response


@app.route("/supplier/<int:supplier_id>/viewpurchases", methods=["GET", "POST"])
def view_supplier_purchases(supplier_id):
    if "user" not in session: return redirect(url_for("login"))
    db = get_db(); cursor = db.cursor()
    cursor.execute("""SELECT 
        s.supplier_id,s.name,
      p.purchase_date,p.purchase_id,p.total_amount
     FROM purchases p
     INNER JOIN suppliers s 
    ON p.supplier_id = s.supplier_id 
   where s.supplier_id=%s 
     order by p.purchase_date DESC""",(supplier_id,))
    results=cursor.fetchall()
    print(len(results))
    return render_template("supplier_purchases.html",data=results)
@app.route("/supplier/<int:supplier_id>/edit", methods=["GET", "POST"])
def edit_supplier(supplier_id):
    if "user" not in session: return redirect(url_for("login"))
    supplier = Suppliers.query.get_or_404(supplier_id)

    if request.method == "POST":
        supplier.name = request.json["supplier_name"]
        supplier.email= request.json["supplier_email"]
        supplier.phone = request.json["supplier_phone"]

        db2.session.commit()

        return jsonify({
            "success": True,
            "status": "supplier updated",
            "product_name": supplier.name,
            "product_price": supplier.email,
            "product_brcode":supplier.phone
        })

    return render_template("update_supplier.html", supplier=supplier)
@app.route("/suppliers/select_list", methods=[ "POST"])
def supliersselectlist():
    if "user" not in session: return redirect(url_for("login"))
    # 🔹 directly reuse the same query
    suppliers = Suppliers.query.filter(Suppliers.user_id==int(session["user_id"])).all()
    list1=[]
    for supplier in suppliers:
       x={"supplier_id":supplier.supplier_id , "name": supplier.name}
       list1.append(x)
    return jsonify({
              "success": True,
              "suppliers": list1
    })
###puchases
@app.route("/managepurchases",methods=["GET"])
def managepurchases():
    if "user" not in session: return redirect(url_for("login"))
    return render_template("managepurchases.html")
@app.route("/purchase/new",methods=["POST"])
def purchaseaddsupplier():
    if "user" not in session: return redirect(url_for("login"))
    return render_template("purchase_add_supplier.html")
@app.route("/purchase/add",methods=["POST"])
def addpurchase():
    if "user" not in session: return redirect(url_for("login"))
    supplier=request.form.get("supplier")
    status=int(request.form.get("status"))
    description=request.form.get("description")
    print(status)
    new_purchase=Purchases(supplier_id=supplier,status=status,description=description,user_id=int(session["user_id"]))
    db2.session.add(new_purchase)
    db2.session.commit()
    print(new_purchase,new_purchase.purchase_id)
    return render_template("purchases_items.html",purchase=new_purchase,pcase=0)
 
@app.route("/purchase/<int:purchase_id>/additems",methods=["GET", "POST"])
def additems(purchase_id):
    if "user" not in session: return redirect(url_for("login"))
    purchase=None
    print(purchase_id)
    
    if purchase_id>0:
    	
          purchase = Purchases.query.get_or_404(purchase_id)
    return render_template("purchases_items.html",purchase=purchase,pcase=1)
@app.route("/purchase/<int:purchase_id>/remove", methods=["GET", "POST"])
def remove_purchase(purchase_id):
    if "user" not in session: return redirect(url_for("login"))
    purchase = Purchases.query.get(purchase_id)
    print("purchase to delete:",purchase.purchase_id)
    if request.method == "POST":
        if purchase:
            transaction=Transactions.query.filter(Transactions.purchase_id==purchase_id,Transactions.user_id==int(session["user_id"])).first()
            purchase_items = PurchaseItems.query.filter(PurchaseItems.purchase_id==purchase_id).all()
            for item in purchase_items:
                 items_usage=SalePurchaseUsage.query.filter(SalePurchaseUsage.purchase_item_id==item.purchase_item_id).all()
                 for u in items_usage:
        	           db2.session.delete(u)
                 db2.session.flush()
                 db2.session.delete(item)
            if transaction:
                db2.session.delete(transaction)
            db2.session.commit()
            db2.session.delete(purchase)
            
            db2.session.commit()
        return render_template("managepurchases.html")
    return render_template("confirm_delete_purchase.html", purchase=purchase)
@app.route("/purchase/<int:purchase_id>/confirm", methods=["GET"])
def save_purchase(purchase_id):
    if "user" not in session: return redirect(url_for("login"))
    purchase = Purchases.query.get(purchase_id)
    print("purchase to confirm:",purchase.purchase_id)
    total=0
    if purchase:
        purchase_items = PurchaseItems.query.filter(PurchaseItems.purchase_id==purchase_id).all()
        for item in purchase_items:
           total+=item.purchase_price*item.quantity_float
        purchase.total_amount=total
        if purchase.status:
              transaction=Transactions(purchase_id=purchase_id,type="purchase",amount=total,user_id=int(session["user_id"]))
              db2.session.add(transaction)
        db2.session.commit()
    return render_template("managepurchases.html")
@app.route("/purchase/<int:purchase_id>/complete", methods=["GET"])
def complete_purchase(purchase_id):
    if "user" not in session: return redirect(url_for("login"))
    purchase = Purchases.query.get(purchase_id)
    print("purchase to confirm:",purchase.purchase_id)
    if purchase and not purchase.status:
        purchase.status=1
        transaction=Transactions(purchase_id=purchase_id,type="purchase",amount=purchase.total_amount,user_id=int(session["user_id"]))
        db2.session.add(transaction)
        items=PurchaseItems.query.filter(PurchaseItems.purchase_id==purchase.purchase_id).all()
        for item in items:
            product=Product.query.filter(Product.product_id==item.product_id,Product.user_id==int(session["user_id"])).first()
            if product:
                product.quantity_float+=item.quantity_float
                batch=ProductBatches(product_id=product.product_id,purchase_price=item.purchase_price,quantity_float=product.quantity_float)
                db2.session.add(batch)
        db2.session.commit()
    return render_template("managepurchases.html")
@app.route("/purchaseslist",methods=["GET"])
def purchaseslist():
    if "user" not in session: return redirect(url_for("login"))
    purchases = Purchases.query.filter(Purchases.user_id==int(session["user_id"])).order_by(desc(Purchases.purchase_date)).all()
    response = make_response(render_template("purchases_list.html",data=purchases))
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response
@app.route("/purchase/<int:purchase_id>/viewitems", methods=["GET", "POST"])
def view_items(purchase_id):
    db = get_db(); cursor = db.cursor()
    cursor.execute("""
SELECT p.purchase_id,p.purchase_date,
p.supplier_id,pd.name,it.purchase_price,pd.current_price,it.quantity_float,it.purchase_item_id,it.product_id,it.purchase_id
FROM purchases p 
INNER JOIN purchase_items it 
ON p.purchase_id = it.purchase_id 
LEFT JOIN products pd
ON pd.product_id = it.product_id 
where p.purchase_id=%s 
order by p.purchase_date DESC""",(purchase_id,))
    results=cursor.fetchall()
    print(len(results))
    return render_template("purchase_items_view.html",data=results,purchase_id=purchase_id)
@app.route("/purchase/update", methods=["GET", "POST"])
def updatepurchase():
    if "user" not in session: return redirect(url_for("login"))
    purchase_id=int(request.json["purchase_id"])
    target=request.json["target"]
    new_value=request.json["new_value"]
    
    purchase=Purchases.query.filter(Purchases.purchase_id==purchase_id,Purchases.user_id==int(session["user_id"])).first()
    if purchase:
       
       if target=="description":
    	    purchase.description=new_value
       db2.session.commit()
    return jsonify({
              "success": True,
              "target":target
    })
@app.route("/purchase/update_item", methods=["GET", "POST"])
def updatepurchaseitem():
    if "user" not in session: return redirect(url_for("login"))
    purchase_item_id=int(request.json["purchase_item_id"])
    product_id=int(request.json["product_id"])
    purchase_id=int(request.json["purchase_id"])
    target=request.json["target"]
    new_value=request.json["new_value"]
    
    item=PurchaseItems.query.filter(PurchaseItems.purchase_item_id==purchase_item_id).first()
    if item:
       
       if target=="quantity":
    	    item.quantity_float=float(new_value)
       elif target=="purchaseprice":
        	item.purchase_price=float(new_value)
       else:
            product=Product.query.filter(Product.product_id==product_id,Product.user_id==int(session["user_id"])).first()
            if product:
                product.current_price=float(new_value)
       db2.session.commit()
    purchase=Purchases.query.filter(Purchases.purchase_id==purchase_id,Purchases.user_id==int(session["user_id"])).first()
    transaction=Transactions.query.filter(Transactions.purchase_id==purchase_id,Transactions.user_id==int(session["user_id"])).first()
    results2 = PurchaseItems.query.filter(PurchaseItems.purchase_id==purchase_id).all()
    
    total=0
    for r in results2:
       total+=r.quantity_float*r.purchase_price
    purchase.total_amount=total
    
    print(len(results2))
    if transaction:
       transaction.amount=total;
    db2.session.commit()
    return jsonify({
              "success": True,
              "total":total
    })
###transactions
@app.route("/managetransactions",methods=["GET"])
def managetransactions():
    if "user" not in session: return redirect(url_for("login"))
    return render_template("manage_transactions.html")
@app.route("/transaction/new",methods=["GET"])
def newtransaction():
    if "user" not in session: return redirect(url_for("login"))
    return render_template("addtransaction.html")
@app.route("/transaction/add",methods=["POST"])
def addtransaction():
    if "user" not in session: return redirect(url_for("login"))
    transaction_type = request.json["transaction_type"]
    transaction_amount = float(request.json["transaction_amount"])
    transaction_date = request.json["transaction_date"]
    
    if transaction_date:
        l=transaction_date.split('-')
        year,month,day=int(l[0]),int(l[1]),int(l[2])
        print()
        print(transaction_date.split('-')[0])
        xd=datetime(year,month,day)
        transaction=Transactions(type=transaction_type,amount=transaction_amount,date=xd,user_id=int(session["user_id"]))
        
    else:
        transaction=Transactions(type=transaction_type,amount=transaction_amount,user_id=int(session["user_id"]))
    db2.session.add(transaction)
    db2.session.commit()
    
    return jsonify({
              "success": True,
              "transaction added": transaction.id,
              "amount":transaction.amount,
               "type":transaction.type
    })
    return render_template("addtransaction.html")
@app.route("/transaction/<int:transaction_id>/remove", methods=["GET", "POST"])
def remove_transaction(transaction_id):
    if "user" not in session: return redirect(url_for("login"))
    transaction = Transactions.query.get(transaction_id)
    if request.method == "POST":
        db2.session.delete(transaction)
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
    return render_template("confirm_delete_transaction.html",transaction=transaction)
        
@app.route("/transactions/list/<string:filt>",methods=["GET"])
def transactionslist(filt):
    if "user" not in session: return redirect(url_for("login"))
    if filt=="Today":
       transactions = Transactions.query.filter(func.date(Transactions.date) == date.today(),Transactions.user_id==int(session["user_id"])).order_by(desc(Transactions.date)).all()
    else:
       transactions=Transactions.query.filter(Transactions.user_id==int(session["user_id"])).order_by(desc(Transactions.date)).all()
    print(date.today())
    retdict=[]
    balance=0
    for tr in transactions:
        x={"id":tr.id , "date": tr.date, "type": tr.type,  "amount": roundFive(tr.amount)}
        if tr.type=="withdraw" or tr.type=="expense" or tr.type=="purchase"  or tr.type=="forgive":
        	balance-=roundFive(tr.amount)
        else:
        	balance+=roundFive(tr.amount)
        retdict.append(x)
    response = make_response(render_template("transactions_list.html",data=retdict,balance=balance))
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response
@app.route("/transactions/list/update",methods=["POST"])
def transactionslistupdate():
    if "user" not in session: return redirect(url_for("login"))
    filt=request.json["filter"]
    
    
    print("filt",filt)
    if filt=="Today":
    	
       transactions = Transactions.query.filter(func.date(Transactions.date) == date.today(),Transactions.user_id==int(session["user_id"])).order_by(desc(Transactions.date)).all()
    else:
        
        
        l=filt.split('-')
        
        year=int(l[0])
        month=int(l[1])
        day=int(l[2])
        xdate=date(year,month,day)
        print("xdate",xdate)
        transactions = Transactions.query.filter(func.date(Transactions.date) == xdate,Transactions.user_id==int(session["user_id"])).order_by(desc(Transactions.date)).all()
    retdict=[]
    balance=0
    for tr in transactions:
        x={"id":tr.id , "date": tr.date, "type": tr.type,  "amount": roundFive(tr.amount)}
        if tr.type=="withdraw" or tr.type=="expense" or tr.type=="purchase" or tr.type=="forgive":
        	balance-=roundFive(tr.amount)
        else:
        	balance+=roundFive(tr.amount)
        retdict.append(x)
    return jsonify({
              "success": True,
              "results": retdict,
              "balance":balance
     })
@app.route('/backup')
def backup():
    if "user" not in session: return redirect(url_for("login"))
    # Connection info
    db_user = 'root'
    db_password = ''  # empty in your case
    db_name = 'store_db'

    # Create a unique backup filename with timestamp
    backup_file = f"backup_{db_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"

    # Command to export (dump) MySQL database
    command = ['mysqldump', '-u', db_user, db_name]

    # If there’s a password, add it like: ['mysqldump', '-u', db_user, f'-p{db_password}', db_name]
    with open(backup_file, 'w') as f:
        subprocess.run(command, stdout=f)

    # Send file for download
    return send_file(backup_file, as_attachment=True)
@app.route("/test",methods=["POST","GET"])
def test():
    sales = Sales.query.filter(func.date(Sales.sale_date) == date.today()).order_by(desc(Sales.sale_date))
    for sale in sales:
        transaction=Transactions.query.filter(Transactions.sale_id==sale.sale_id).first()
        if not transaction:
            print(sale.sale_id)
    x=date(2025,5,13)
    xt= datetime.combine(x, datetime.min.time())
    print("xdate:,,",xt)
    backup()
    return jsonify({
              "success": True,
              "test": "worked"	        
     })
app.run(host="0.0.0.0", port=5000, debug=True)