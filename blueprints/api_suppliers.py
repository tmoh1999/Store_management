from flask import render_template, request, jsonify,redirect,url_for,make_response,Blueprint
from datetime import date,timedelta
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from sqlalchemy import desc
from models import *
from decorators import token_required
api_suppliers_bp = Blueprint('api_suppliers', __name__, url_prefix='/api/suppliers')


@api_suppliers_bp.route("/add",methods=["POST"])
@token_required
def addsupplier(user_id):
    name=request.json["name"]
    phone=request.json["phone"]
    email=request.json["email"]
    supplier=Suppliers(name=name,phone=phone,email=email,user_id=user_id)
    db2.session.add(supplier)
    db2.session.commit()
    return jsonify({
        "success":True,
        "status":"supplier added ",
    })
@api_suppliers_bp.route("/list",methods=["GET"])
@token_required
def getSuppliersList(user_id):
    suppliers=Suppliers.query.filter(Suppliers.user_id==user_id).order_by(desc(Suppliers.supplier_id)).all()
    results=[
        {
            "id":supplier.supplier_id,
            "name":supplier.name,
            "phone":supplier.phone,
            "email":supplier.email
        }
        for supplier in suppliers
    ]
    return jsonify({
        "success":True,
        "results":results,
    })
@api_suppliers_bp.route("/<int:supplier_id>/remove", methods=["GET"])
@token_required
def removesupplier(user_id,supplier_id):
    supplier=Suppliers.query.filter(Suppliers.supplier_id==supplier_id).first()
    if supplier:
        db2.session.delete(supplier)
        db2.session.commit()
        return jsonify({
              "success": True,
              "message":"item removed"
         })
    return jsonify({
              "success": False,
              "message":"Error:item not found"
     })

@api_suppliers_bp.route("/<int:supplier_id>/update", methods=["GET", "POST"])
@token_required
def edit_transaction(user_id,supplier_id):
    
    supplier = Suppliers.query.get_or_404(supplier_id)

    if request.method == "POST":
       if supplier:
           supplier.name = request.json["name"]
           supplier.email = request.json["email"]
           supplier.phone = request.json["phone"]
           db2.session.commit()
       return jsonify({
            "success": True,
            "status": "supplier data updated",
        })

    return jsonify({
            "success": False,
            "status": "Data missing"
        })