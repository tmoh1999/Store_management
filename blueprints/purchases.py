from flask import render_template, request, jsonify,redirect,url_for,make_response,session,Blueprint
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from models import *
purchases_bp = Blueprint('purchases', __name__, url_prefix='/purchases')

###puchases
@purchases_bp.route("/managepurchases",methods=["GET"])
def managepurchases():
    if "user" not in session: return redirect(url_for("users.login"))
    return render_template("managepurchases.html")
@purchases_bp.route("/purchase/new",methods=["POST"])
def purchaseaddsupplier():
    if "user" not in session: return redirect(url_for("users.login"))
    return render_template("purchase_add_supplier.html")
@purchases_bp.route("/purchase/add",methods=["POST"])
def addpurchase():
    if "user" not in session: return redirect(url_for("users.login"))
    supplier=request.form.get("supplier")
    status=int(request.form.get("status"))
    description=request.form.get("description")
    print(status)
    new_purchase=Purchases(supplier_id=supplier,status=status,description=description,user_id=int(session["user_id"]))
    db2.session.add(new_purchase)
    db2.session.commit()
    print(new_purchase,new_purchase.purchase_id)
    return render_template("purchases_items.html",purchase=new_purchase,pcase=0)
 
@purchases_bp.route("/purchase/<int:purchase_id>/additems",methods=["GET", "POST"])
def additems(purchase_id):
    if "user" not in session: return redirect(url_for("users.login"))
    purchase=None
    print(purchase_id)
    
    if purchase_id>0:
    	
          purchase = Purchases.query.get_or_404(purchase_id)
    return render_template("purchases_items.html",purchase=purchase,pcase=1)
@purchases_bp.route("/purchase/<int:purchase_id>/remove", methods=["GET", "POST"])
def remove_purchase(purchase_id):
    if "user" not in session: return redirect(url_for("users.login"))
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
@purchases_bp.route("/purchase/<int:purchase_id>/confirm", methods=["GET"])
def save_purchase(purchase_id):
    if "user" not in session: return redirect(url_for("users.login"))
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
@purchases_bp.route("/purchase/<int:purchase_id>/complete", methods=["GET"])
def complete_purchase(purchase_id):
    if "user" not in session: return redirect(url_for("users.login"))
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
@purchases_bp.route("/purchaseslist",methods=["GET"])
def purchaseslist():
    if "user" not in session: return redirect(url_for("users.login"))
    purchases = Purchases.query.filter(Purchases.user_id==int(session["user_id"])).order_by(desc(Purchases.purchase_date)).all()
    response = make_response(render_template("purchases_list.html",data=purchases))
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response
@purchases_bp.route("/purchase/<int:purchase_id>/viewitems", methods=["GET", "POST"])
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
@purchases_bp.route("/purchase/update", methods=["GET", "POST"])
def updatepurchase():
    if "user" not in session: return redirect(url_for("users.login"))
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
@purchases_bp.route("/purchase/update_item", methods=["GET", "POST"])
def updatepurchaseitem():
    if "user" not in session: return redirect(url_for("users.login"))
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