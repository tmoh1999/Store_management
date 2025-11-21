from flask import  render_template, request, jsonify,redirect,url_for,make_response,send_file,session,Blueprint
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from openpyxl import load_workbook,Workbook
from sqlalchemy import desc
from weasyprint import HTML,CSS
from decorators import token_required
import io
import os

from models import *
api_products_bp = Blueprint('api_products', __name__, url_prefix='/api/products')


@api_products_bp.route("/insertproductpurchase", methods=["POST"])
def insertproductpurchase():
    #if "user" not in session: return redirect(url_for("users.login"))
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
@api_products_bp.route("/productlist",methods=["GET","POST"])
@token_required
def productlist(user_id):
    #if "user" not in session: return redirect(url_for("users.login"))
    
    products_query = Product.query.filter(Product.user_id==user_id)
    
    if request.method=="POST":
        query = request.json["search_q"]
        products_filter = int(request.json["products_filter"])
        if query:
            products_query = products_query.filter(
            (Product.name.like(f"%{query}%")) |
            (Product.barcode.like(f"%{query}%")))
        
        if products_filter==1:
           products_query = products_query.filter(Product.quantity_float==0.0)
        elif products_filter==2:
        	products_query = products_query.filter(Product.quantity_float>0.0)
        products=products_query.order_by(desc(Product.product_id)).all()
        
    products=products_query.order_by(desc(Product.product_id)).all()
    #response = make_response(render_template("products_list.html",data=products,mode="manage"))
    results_list=[
        {"id": p.product_id, "name": p.name, "barcode": p.barcode, "price": p.current_price,"quantity":p.quantity_float} for p in products]
    return jsonify({
              "success": True,
              "results": results_list
     })
@api_products_bp.route("/insertemptyproduct", methods=["POST"])
@token_required
def insertemptyproduct(user_id):
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
         
         
         
         new_product=Product(name=product_name,current_price=product_price,barcode=product_brcode,user_id=user_id)
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
@api_products_bp.route("/<int:product_id>/update", methods=["GET", "POST"])
@token_required
def edit_product(user_id,product_id):
    
    product = Product.query.get_or_404(product_id)

    if request.method == "POST":
       if product:
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

    return jsonify({
            "success": False,
            "status": "Data missing"
        })
@api_products_bp.route("/<int:product_id>/remove", methods=["GET"])
@token_required
def remove_product(user_id,product_id):
    
    product = Product.query.get_or_404(product_id)
    if product:
           db2.session.delete(product)
           db2.session.commit()
           return jsonify({
            "success": True,
            "status": "product deleted"
           })

    return jsonify({
            "success": False,
            "status": "Data missing"
        })
