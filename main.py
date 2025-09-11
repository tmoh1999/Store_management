from flask import Flask, render_template, request, jsonify,redirect,url_for,make_response,send_file
import mysql.connector
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from openpyxl import load_workbook,Workbook
from sqlalchemy import desc
from weasyprint import HTML,CSS
import io
import os
import webbrowser
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
    id= db2.Column(db2.Integer, primary_key=True)
    product_id = db2.Column(db2.Integer)
    date_received = db2.Column(db2.DateTime(timezone=True), server_default=func.now())
    purchase_price = db2.Column(db2.Float)
    quantity = db2.Column(db2.Integer)
    
    def __repr__(self):
          return f"<ProductBatches {self.id}>"

class Purchases(db2.Model):
    __tablename__ = "purchases"
    purchase_id= db2.Column(db2.Integer, primary_key=True)
    supplier_id = db2.Column(db2.Integer)
    purchase_date = db2.Column(db2.DateTime(timezone=True), server_default=func.now())
    total_amount = db2.Column(db2.Float, server_default="0.0")
   
    
    def __repr__(self):
        return f"<Purchases {self.purchase_id}>"


class PurchaseItems(db2.Model):
    __tablename__ = "purchase_items"
    purchase_item_id = db2.Column(db2.Integer, primary_key=True)
    purchase_id = db2.Column(db2.Integer)
    product_id = db2.Column(db2.Integer)
    purchase_price = db2.Column(db2.Float)
    quantity = db2.Column(db2.Integer)
    
    def __repr__(self):
        return f"<PurchasesItems {self.purchase_item_id}>"
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
class Suppliers(db2.Model):
    __tablename__ = "suppliers"

    supplier_id = db2.Column(db2.Integer, primary_key=True)
    name = db2.Column(db2.String(64))
    email = db2.Column(db2.String(64))
    phone = db2.Column(db2.String(128))
    def __repr__(self):
        return f"<Supplier {self.name}>"  

def get_db():
    return mysql.connector.connect(
        host="localhost", user="root", password="", database="store_db"
    )

@app.route("/")
def home():
    return render_template("index.html")
 
@app.route("/scanner",methods=["GET"])
def scanner():
    return render_template("scanbr.html")
@app.route("/manageproducts",methods=["GET"])
def manageproducts():
    return render_template("manageproducts.html")

@app.route("/product/<int:product_id>/addproducts",methods=["GET", "POST"])
def addproducts(product_id):
 
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
    purchase_id=request.json["purchase_id"]
    product = Product.query.filter_by(barcode=product_brcode).first()
    if product:
    	
        print(product.quantity,product_quantity)
        product.quantity=product.quantity+product_quantity
        print(product.quantity)
        product.current_price=product_price
        db2.session.commit()
        cursor.execute("INSERT INTO product_batches(product_id,quantity,purchase_price) VALUES (%s,%s,%s)", (product.product_id,product_quantity,product_purchase_price,))
        db.commit()
        purchase=PurchaseItems(purchase_id=purchase_id,product_id=product.product_id,purchase_price=product_purchase_price,quantity=product_quantity)
        db2.session.add(purchase)
        db2.session.commit()
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
         purchase=PurchaseItems(purchase_id=purchase_id,product_id=product.product_id,purchase_price=product_purchase_price,quantity=product_quantity)
         db2.session.add(purchase)
         db2.session.commit()
         
         db.commit()
         return jsonify({
              "success": True,
              "status": "product added",
              "product_name": product_name,
              "product_price": product_price,
              "product_brcode":product_brcode
          })
    
@app.route("/insertemptyproduct", methods=["POST"])
def insertemptyproduct():
    db = get_db(); cursor = db.cursor()
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
    else:
         
         
         
         new_product=Product(name=product_name,current_price=product_price,barcode=product_brcode)
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
    


@app.route("/productlist",methods=["GET"])
def productlist():
	products = Product.query.order_by(desc(Product.product_id)).all()
	response = make_response(render_template("products_list.html",data=products))
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
    	rs.quantity+=1
    else:
        new_sale_item=SaleItems(sale_id=sale_id,product_id=results[0].product_id,unit_price=results[0].current_price,quantity=1)
        db2.session.add(new_sale_item)
    db2.session.commit()
    
    results2 = SaleItems.query.filter(SaleItems.sale_id==sale_id).all()
    result_list2=[]
    for r in results2:
       print(r.product_id)
       if r.product_id:
       	p = Product.query.filter(Product.product_id==r.product_id).first()
       	x={"item_id": r.item_id, "name": p.name, "barcode": p.barcode, "price": r.unit_price,"quantity":r.quantity}
       else:
           x={"item_id": r.item_id, "name": "", "barcode": "",  "price": r.unit_price,"quantity":r.quantity}    
           
       result_list2.append(x)
    print(len(results2))
    total=0
    for st in results2:
    	total+=st.unit_price*st.quantity
    print(total)
    
    return jsonify({
              "success": True,
              "results": result_list2,
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
    cursor.execute("""
SELECT p.product_id, p.barcode,
p.name,p.current_price,
it.purchase_price, it.quantity,pu.purchase_date 
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
    result_list2=[]
    for r in results2:
       print(r.product_id)
       if r.product_id:
       	p = Product.query.filter(Product.product_id==r.product_id).first()
       	x={"item_id": r.item_id, "name": p.name, "barcode": p.barcode, "price": r.unit_price,"quantity":r.quantity}
       else:
           x={"item_id": r.item_id, "name": "", "barcode": "",  "price": r.unit_price,"quantity":r.quantity}    
           
       result_list2.append(x)
    print(len(results2))
    total=0
    for st in results2:
    	total+=st.unit_price*st.quantity
    print(total)
    
    return jsonify({
              "success": True,
              "results": result_list2,
              "total":total
    })
@app.route("/sale/update_item", methods=["GET", "POST"])
def updatesaleitem():
    db = get_db(); cursor = db.cursor()
    sale_id=int(request.json["sale_id"])
    item_id=int(request.json["item_id"])
    target=request.json["target"]
    new_value=request.json["new_value"]
    
    item=SaleItems.query.filter(SaleItems.sale_id==sale_id,SaleItems.item_id==item_id).first()
    if item:
       print(target,item_id)
       if target=="quantity":
    	    item.quantity=int(new_value)
       else:
        	item.unit_price=float(new_value)
       db2.session.commit()
    results2 = SaleItems.query.filter(SaleItems.sale_id==sale_id).all()
    result_list2=[]
    for r in results2:
       if r.product_id:
       	p = Product.query.filter(Product.product_id==r.product_id).first()
       	x={"item_id": r.item_id, "name": p.name, "barcode": p.barcode, "price": r.unit_price,"quantity":r.quantity}
       else:
           x={"item_id": r.item_id, "name": "", "barcode": "",  "price": r.unit_price,"quantity":r.quantity}    
           
       result_list2.append(x)
    print(len(results2))
    total=0
    for st in results2:
    	total+=st.unit_price*st.quantity
    print(total)
    
    return jsonify({
              "success": True,
              "results": result_list2,
              "total":total
    })
@app.route("/sale/remove", methods=["GET", "POST"])
def removesale():
    db = get_db(); cursor = db.cursor()
    sale_id=int(request.json["sale_id"])


    items=SaleItems.query.filter(SaleItems.sale_id==sale_id).all()
    for item in items:
    	db2.session.delete(item)
    db2.session.commit()
    sales = Sales.query.filter(Sales.sale_id==sale_id).all()
    
    for r in sales:
          db2.session.delete(r)
    db2.session.commit()

    return jsonify({
              "success": True,
              "id deleted": sale_id
    })
@app.route("/sale/confirm", methods=["GET", "POST"])
def confirmsale():
    
    sale_id=int(request.json["sale_id"])

    results2 = SaleItems.query.filter(SaleItems.sale_id==sale_id).all()
    result_list2=[]
    for r in results2:
       print(r.product_id)
       if r.product_id:
            p = Product.query.filter(Product.product_id==r.product_id).first()
            p.quantity=max(p.quantity-r.quantity,0)
            product_batches = ProductBatches.query.filter(ProductBatches.product_id == r.product_id).order_by(ProductBatches.date_received).all()
            g=r.quantity
            for batch in product_batches:
                if batch.quantity>=g:
                   batch.quantity-=g
                   break
                else:
                   g-=batch.quantity
                   batch.quantity=0
                print(batch.date_received,batch.quantity)
    db2.session.commit()
    return jsonify({
              "success": True,
              "id deleted": sale_id
    })

@app.route("/saleslist",methods=["GET"])
def saleslist():
    sales=Sales.query.order_by(desc(Sales.sale_date)).all()
    retdict=[]
    for sale in sales:
    	#nb products
        items=SaleItems.query.filter(SaleItems.sale_id==sale.sale_id).all()
        total=0;quantity=0
        for item in items:
        	quantity+=item.quantity
        	total+=item.unit_price*item.quantity
        x={"sale_id":sale.sale_id , "date": sale.sale_date, "total": total,  "quantity": quantity}
        retdict.append(x)
    response = make_response(render_template("sales_list.html",data=retdict))
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response
@app.route("/sales/<int:sale_id>/viewsaleitems", methods=["GET", "POST"])
def view_sales(sale_id):
    db = get_db(); cursor = db.cursor()
    cursor.execute("SELECT s.sale_id, s.sale_date,i.product_id,i.unit_price,i.quantity FROM sale_items i INNER JOIN sales s ON i.sale_id = s.sale_id where i.sale_id=%s order by s.sale_date DESC",(sale_id,))
    results=cursor.fetchall()
    print(len(results))
    
    return render_template("sale_items_history.html",data=results)




@app.route("/product/import", methods=["GET", "POST"])
def upload_products():
    if request.method == "POST":
        file = request.files["file"]
        if not file:
            return "No file uploaded", 400
        
    
        # Load the Excel file
        wb = load_workbook(file)
        ws = wb.active   # first sheet
        name="Opening_"+datetime.now().strftime("%Y%m%d_%H%M")
        
        supplier=Suppliers(name=name,email="",phone="")
        db2.session.add(supplier)
        db2.session.flush()
        purchase=Purchases(supplier_id=supplier.supplier_id)
        db2.session.add(purchase)
        db2.session.flush()
        # Skip headers (row 1)
        total=0
        for row in ws.iter_rows(min_row=2, values_only=True):
              print("  ..... ,  ",row)
              name,barcode,quantity,price,purchase_price=row
              quantity=int(quantity)
              purchase_price=float(purchase_price)
              price=float(price)
              pd=Product.query.filter(Product.barcode==barcode).first()
              if pd:
                    print("barcode exists")
                    pd.quantity += quantity
                    pd.current_price = price  # if you want latest price
              else:
                   pd=Product(name=name,barcode=barcode,quantity=quantity,current_price=price)
                   db2.session.add(pd)
                   db2.session.flush()
              total+=quantity*purchase_price
              new_prod_batch=ProductBatches(product_id=pd.product_id,purchase_price=purchase_price,quantity=quantity)
              db2.session.add(new_prod_batch)
                  
              
              new_purchase_item=PurchaseItems(product_id=pd.product_id,purchase_price=purchase_price,purchase_id=purchase.purchase_id,quantity=quantity)
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
    # Create a new Excel workbook
    wb = Workbook()
    ws = wb.active
    ws.title = "Products"

    # Write header row
    ws.append(["Name", "Barcode", "Quantity", "Price", "Purchase Price"])

    # Fetch all products
    products = Product.query.all()

    for p in products:
        # Get latest batch purchase price (or None if no batch exists)
        item = PurchaseItems.query.filter_by(product_id=p.product_id).order_by(PurchaseItems.purchase_id.desc()).first()
        purchase_price = item.purchase_price if item else None

        ws.append([p.name, p.barcode, p.quantity, p.current_price, purchase_price])

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


@app.route("/products.pdf")
def products_pdf():
    # 🔹 directly reuse the same query
    products = Product.query.all()
 
    # render to PDF
    html = render_template("products_list_pdf_template.html", data=products)
    print(html)
    css_path = os.path.join(app.root_path, "static", "css","product_list.css")
    
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
    db = get_db(); cursor = db.cursor()
    return render_template("manage_suppliers.html")
@app.route("/suppliers/add",methods=["GET"])
def addsupplier():
    db = get_db(); cursor = db.cursor()
    return render_template("addsuplier.html")
@app.route("/suppliers/insert", methods=["POST"])
def insertsupplier():
    
    
    
    
    supplier_name=request.json["supplier_name"]
    supplier_email=request.json["supplier_email"]
    supplier_phone=request.json["supplier_phone"]
    supplier = Suppliers(name=supplier_name,email=supplier_email,phone=supplier_phone)
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
     suppliers=Suppliers.query.all()
     response = make_response(render_template("suppliers_list.html",data=suppliers))
     response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
     response.headers["Pragma"] = "no-cache"
     response.headers["Expires"] = "0"
     return response


@app.route("/supplier/<int:supplier_id>/viewpurchases", methods=["GET", "POST"])
def view_supplier_purchases(supplier_id):
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
    # 🔹 directly reuse the same query
    suppliers = Suppliers.query.all()
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
    return render_template("managepurchases.html")
@app.route("/purchase/new",methods=["POST"])
def purchaseaddsupplier():
    return render_template("purchase_add_supplier.html")
@app.route("/purchase/add",methods=["POST"])
def addpurchase():
    supplier=request.form.get("supplier")
    print(supplier)
    new_purchase=Purchases(supplier_id=supplier)
    db2.session.add(new_purchase)
    db2.session.commit()
    print(new_purchase,new_purchase.purchase_id)
    return render_template("purchases_items.html",purchase=new_purchase)
 
@app.route("/purchase/<int:purchase_id>/additems",methods=["GET", "POST"])
def additems(purchase_id):
 
    purchase=None
    print(purchase_id)
    if purchase_id>0:
    	
          purchase = Purchases.query.get_or_404(purchase_id)
    return render_template("purchases_items.html",purchase=purchase)
@app.route("/purchase/<int:purchase_id>/remove", methods=["GET", "POST"])
def remove_purchase(purchase_id):
    purchase = Purchases.query.get(purchase_id)
    print("purchase to delete:",purchase.purchase_id)
    if request.method == "POST":
        if purchase:
            purchase_items = PurchaseItems.query.filter(PurchaseItems.purchase_id==purchase_id).all()
            for item in purchase_items:
            	db2.session.delete(item)
            db2.session.commit()
            db2.session.delete(purchase)
            db2.session.commit()
        return render_template("managepurchases.html")
    return render_template("confirm_delete_purchase.html", purchase=purchase)
@app.route("/purchase/<int:purchase_id>/confirm", methods=["GET"])
def save_purchase(purchase_id):
    
    purchase = Purchases.query.get(purchase_id)
    print("purchase to confirm:",purchase.purchase_id)
    total=0
    if purchase:
        purchase_items = PurchaseItems.query.filter(PurchaseItems.purchase_id==purchase_id).all()
        for item in purchase_items:
           total+=item.purchase_price*item.quantity
        purchase.total_amount=total
        db2.session.commit()
    return render_template("managepurchases.html")
@app.route("/purchaseslist",methods=["GET"])
def purchaseslist():
	purchases = Purchases.query.order_by(desc(Purchases.purchase_date)).all()
	response = make_response(render_template("purchases_list.html",data=purchases))
	response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
	response.headers["Pragma"] = "no-cache"
	response.headers["Expires"] = "0"
	return response
@app.route("/purchase/<int:purchase_id>/viewitems", methods=["GET", "POST"])
def view_items(purchase_id):
    db = get_db(); cursor = db.cursor()
    cursor.execute("SELECT p.purchase_id,p.purchase_date,p.supplier_id,it.product_id,it.purchase_price, it.quantity FROM purchases p INNER JOIN purchase_items it ON p.purchase_id = it.purchase_id where p.purchase_id=%s order by p.purchase_date DESC",(purchase_id,))
    results=cursor.fetchall()
    print(len(results))
    return render_template("purchase_items_view.html",data=results)
app.run(host="0.0.0.0", port=5000, debug=True)