from flask import render_template, request, jsonify,redirect,url_for,make_response,session,Blueprint
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from models import *
suppliers_bp = Blueprint('suppliers', __name__, url_prefix='/suppliers')

##suppliers
@suppliers_bp.route("/managesuppliers",methods=["GET"])
def managesuppliers():
    if "user" not in session: return redirect(url_for("users.login"))
    return render_template("manage_suppliers.html")
@suppliers_bp.route("/suppliers/add",methods=["GET"])
def addsupplier():
    if "user" not in session: return redirect(url_for("users.login"))
    return render_template("addsuplier.html")
@suppliers_bp.route("/suppliers/insert", methods=["POST"])
def insertsupplier():
    if "user" not in session: return redirect(url_for("users.login"))
    
    
    
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
@suppliers_bp.route("/suppliers/list", methods=["GET"])
def supplierslist():
     if "user" not in session: return redirect(url_for("users.login"))
     suppliers=Suppliers.query.filter(Suppliers.user_id==int(session["user_id"])).all()
     response = make_response(render_template("suppliers_list.html",data=suppliers))
     response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
     response.headers["Pragma"] = "no-cache"
     response.headers["Expires"] = "0"
     return response


@suppliers_bp.route("/supplier/<int:supplier_id>/viewpurchases", methods=["GET", "POST"])
def view_supplier_purchases(supplier_id):
    if "user" not in session: return redirect(url_for("users.login"))
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
@suppliers_bp.route("/supplier/<int:supplier_id>/edit", methods=["GET", "POST"])
def edit_supplier(supplier_id):
    if "user" not in session: return redirect(url_for("users.login"))
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
@suppliers_bp.route("/suppliers/select_list", methods=[ "POST"])
def supliersselectlist():
    if "user" not in session: return redirect(url_for("users.login"))
    # ðŸ”¹ directly reuse the same query
    suppliers = Suppliers.query.filter(Suppliers.user_id==int(session["user_id"])).all()
    list1=[]
    for supplier in suppliers:
       x={"supplier_id":supplier.supplier_id , "name": supplier.name}
       list1.append(x)
    return jsonify({
              "success": True,
              "suppliers": list1
    })