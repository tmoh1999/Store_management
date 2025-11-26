from flask import render_template, request, jsonify,redirect,url_for,make_response,Blueprint
from datetime import date,timedelta
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from sqlalchemy import desc
from models import *
from decorators import token_required
api_sales_bp = Blueprint('api_sales', __name__, url_prefix='/api/sales')
@api_sales_bp.route("/add",methods=["POST","GET"])
@token_required
def addsale(user_id):
    new_sale=Sales(user_id=user_id)
    db2.session.add(new_sale)
    db2.session.commit()
    print(new_sale,new_sale.sale_id)
    return jsonify({
       "success":True,
       "sale_id":new_sale.sale_id
    })
@api_sales_bp.route("/items/add", methods=["POST"])
@token_required
def addsaleitem(user_id):
    
    sale_id=int(request.json["sale_id"])
    
    price=float(request.json["price"])
    quantity=float(request.json["quantity"])
    description=request.json["description"]
    print("fffff",description)
    new_sale_item=SaleItems(sale_id=sale_id,unit_price=price,quantity_float=quantity,description=description)
    db2.session.add(new_sale_item)
    db2.session.commit()
    print(new_sale_item,new_sale_item.description)
    
    return jsonify({
              "success": True,
              "message": "item added",
    })
    
@api_sales_bp.route("/items/list", methods=["POST"])
@token_required
def getsaleitems(user_id):
    sale_id=int(request.json["sale_id"])
    results2 = SaleItems.query.filter(SaleItems.sale_id==sale_id).all()
    result_list2=[]
    for r in results2:
       print(r.product_id)
       if r.product_id:
       	p = Product.query.filter(Product.product_id==r.product_id,Product.user_id==user_id).first()
       	x={"id": r.item_id, "name": p.name, "barcode": p.barcode, "price": r.unit_price,"quantity":r.quantity_float,"description":r.description}
       else:
           x={"id": r.item_id, "name": "", "barcode": "",  "price": r.unit_price,"quantity":r.quantity_float,"description":r.description}    
           
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