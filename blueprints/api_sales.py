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
    new_sale=Sales(user_id=user_id,status="incomplete")
    db2.session.add(new_sale)
    db2.session.commit()
    print(new_sale,new_sale.sale_id)
    return jsonify({
       "success":True,
       "sale_id":new_sale.sale_id,
       "sale_status":new_sale.status,
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
def validateSaleItem(r,user_id):
	
   if r.product_id:
       p = Product.query.filter(Product.product_id==r.product_id,Product.user_id==user_id).first()
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
def rollBackSaleItem(item_id,user_id):
    r=SaleItems.query.filter(SaleItems.item_id==item_id).first()
    if r and r.product_id:
        p = Product.query.filter(Product.product_id==r.product_id,Product.user_id==user_id).first()
        p.quantity_float=p.quantity_float+r.quantity_float
        items_usage=SalePurchaseUsage.query.filter(SalePurchaseUsage.item_id==item_id).all()
        for u in items_usage:
              batch=PurchaseItems.query.filter(PurchaseItems.purchase_item_id == u.purchase_item_id).order_by(PurchaseItems.purchase_item_id).first()
              batch.remain_quantity+=u.quantity_used
              db2.session.delete(u)
    db2.session.commit()
@api_sales_bp.route("/items/update", methods=["GET", "POST"])
@token_required
def updatesaleitem(user_id):
    
    
    item_id=int(request.json["item_id"])
    price=float(request.json["price"])
    quantity=float(request.json["quantity"])
    description=request.json["description"]   
    sale=Sales.query.filter(Sales.sale_id==item.sale_id,Sales.user_id==user_id).first()
    item=SaleItems.query.filter(SaleItems.item_id==item_id).first()
    if item:
       if quantity!=item.quantity_float:
           if sale.status=="complete":
               rollBackSaleItem(item_id,user_id)
               item.quantity_float=quantity
               db2.session.flush()
               validateSaleItem(item,user_id)
               db2.session.commit()
           else:
               item.quantity_float=quantity
       item.unit_price=price
       item.description=description
        
       db2.session.commit()
    
    transaction=Transactions.query.filter(Transactions.sale_id==item.sale_id,Transactions.user_id==user_id).first()
    results2 = SaleItems.query.filter(SaleItems.sale_id==item.sale_id).all()
    result_list2=[]
    total=0
    for r in results2:
        total+=r.quantity_float*r.unit_price
        if r.product_id:
            p = Product.query.filter(Product.product_id==r.product_id,Product.user_id==user_id).first()
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
              "total":total
    })
@api_sales_bp.route("/items/<int:item_id>/remove", methods=["GET"])
@token_required
def removesaleitem(user_id,item_id):
    item=SaleItems.query.filter(SaleItems.item_id==item_id).first()
    if item:
        rollBackSaleItem(item.item_id,user_id)
        db2.session.delete(item)
        db2.session.commit()
        return jsonify({
              "success": True,
              "message":"item removed"
         })
    return jsonify({
              "success": False,
              "message":"Error:item not found"
     })
@api_sales_bp.route("/<int:sale_id>/remove", methods=["GET"])
@token_required
def removesale(user_id,sale_id):
    items=SaleItems.query.filter(SaleItems.sale_id==sale_id).all()
    sale = Sales.query.filter(Sales.sale_id==sale_id,Sales.user_id==user_id).first()
    if sale.status=="complete":
        for item in items:
            rollBackSaleItem(item.item_id,user_id)
            db2.session.delete(item)
    else:
        for item in items:
            db2.session.delete(item)    	    
        
    db2.session.commit()
    
    transactions=Transactions.query.filter(Transactions.sale_id==sale_id,Transactions.user_id==user_id).all()
    for t in transactions:
          db2.session.delete(t)     
    db2.session.commit()
    if sale :
          db2.session.delete(sale)
    db2.session.commit()
    

    return jsonify({
              "success": True,
              "sale_deleted": sale_id
    })      
    	
@api_sales_bp.route("/<int:sale_id>/confirm", methods=["GET"])
@token_required
def confirmsale(user_id,sale_id):
    results2 = SaleItems.query.filter(SaleItems.sale_id==sale_id).all()
    result_list2=[]
    tot=0
    for r in results2:
       tot+=r.unit_price*r.quantity_float
       print(r.product_id)
       validateSaleItem(r,user_id)

                
    sale=Sales.query.filter(Sales.sale_id==sale_id,Sales.user_id==user_id).first()
    sale.total_amount=tot
    sale.status="complete"
    db2.session.commit()
    transaction=Transactions(sale_id=sale_id,type="sale",amount=tot,user_id=user_id)
    db2.session.add(transaction)
    db2.session.commit()
    print("sale:",sale.sale_id,"tptal_amm:",sale.total_amount,tot)
    
    return jsonify({
              "success": True,
              "sale_confirmed": sale_id,
              "sale_status":sale.status,
    })