from flask import Flask, render_template, request, jsonify,redirect,url_for,make_response,send_file
import mysql.connector
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from openpyxl import load_workbook,Workbook
from sqlalchemy import desc
from weasyprint import HTML
import io
import os
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
	products = Product.query.all()
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
    cursor.execute("SELECT s.sale_id, s.sale_date,i.product_id,i.unit_price,i.quantity FROM sale_items i INNER JOIN sales s ON i.sale_id = s.sale_id and i.sale_id=%s order by s.sale_date DESC",(sale_id,))
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

        # Skip headers (row 1)
        for row in ws.iter_rows(min_row=2, values_only=True):
              print("  ..... ,  ",row)
              name,barcode,quantity,price,purchase_price=row
              pd=Product.query.filter(Product.barcode==barcode).first()
              if pd:
              	 print("barcode exists")
              else:
                   new_prod=Product(name=name,barcode=barcode,quantity=quantity,current_price=price)
                   db2.session.add(new_prod)
                   db2.session.commit()
                   new_prod_batch=ProductBatches(product_id=new_prod.product_id,purchase_price=purchase_price,quantity=quantity)
                   db2.session.add(new_prod_batch)
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
        batch = ProductBatches.query.filter_by(product_id=p.product_id).order_by(ProductBatches.id.desc()).first()
        purchase_price = batch.purchase_price if batch else None

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
    pdf = HTML(string=html,base_url=app.root_path).write_pdf()
    pdf_bytes = HTML(string=html, base_url=app.root_path).write_pdf()
    pdf_file = io.BytesIO(pdf_bytes)
    return send_file(
        pdf_file,
        mimetype="application/pdf",
        as_attachment=True,          # True → download, False → open in browser
        download_name="products.pdf"  # filename for the browser
    )
@app.route("/testpdf")
def testpdf():
    html = """<!DOCTYPE html>
    <html><body>
    <h1>Hello PDF</h1>
    <table border="1">
        <tr><td>1</td><td>2</td></tr>
    </table>
    </body></html>"""
    pdf = HTML(string=html).write_pdf("test.pdf")
    return "PDF generated"
app.run(host="0.0.0.0", port=5000, debug=True)
