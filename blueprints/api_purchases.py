from flask import render_template, request, jsonify,redirect,url_for,make_response,Blueprint
from datetime import date,timedelta,datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from sqlalchemy import desc
from models import *
from decorators import token_required
api_purchases_bp = Blueprint('api_purchases', __name__, url_prefix='/api/purchases')

@api_purchases_bp.route("/add",methods=["POST"])
@token_required
def addpurchase(user_id):
    
    supplier=int(request.json["supplier_id"])  
    description=request.json["description"]

    new_purchase=Purchases(supplier_id=supplier,status=0,description=description,user_id=user_id)
    db2.session.add(new_purchase)
    db2.session.commit()
    print(new_purchase,new_purchase.purchase_id)
    return jsonify({
        "success":True,
        "status":"purchase created",
        "id":new_purchase.purchase_id,
    })
@api_purchases_bp.route("",methods=["GET"])
@token_required
def purchaseList(user_id):
    query=Purchases.query.filter(Purchases.user_id==user_id)
    stdate=request.args.get("start_date")
    endate=request.args.get("end_date")
    supplier_id=request.args.get("supplier_id",type=int)
    if stdate and endate :
        start_date=getDate(stdate)
        end_date=getDate(endate)
        query = query.filter(func.date(Purchases.purchase_date) >= start_date,func.date(Purchases.purchase_date) <= end_date)
    if supplier_id:
        query = query.filter(Purchases.supplier_id==supplier_id)
    purchases=query.order_by(desc(Purchases.purchase_id))
    results=[
        {
            "id":purchase.purchase_id,
            "date":purchase.purchase_date,
            "total":purchase.total_amount,
            "status":purchase.status,
            "description":purchase.description
        }
        for purchase in purchases
    ]
    return jsonify({
        "success":True,
        "results":results
    })
@api_purchases_bp.route("/<int:purchase_id>/remove", methods=["GET"])
@token_required
def remove_purchase(user_id,purchase_id):
    purchase = Purchases.query.get(purchase_id)
    if purchase:
        transaction=Transactions.query.filter(Transactions.purchase_id==purchase_id,Transactions.user_id==user_id).first()
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

        return jsonify({
            "Success":True,
            "status":"Purchase deleted",
        })
    return jsonify({
        "Success":False,
        "status":"Purchase delete failed",
    })    

@api_purchases_bp.route("/<int:purchase_id>/update", methods=["POST"])
@token_required
def update_purchase(user_id,purchase_id):
    purchase = Purchases.query.get(purchase_id)
    description=request.json["description"]
    if purchase:
        purchase.description=description
        db2.session.commit()

        return jsonify({
            "Success":True,
            "status":"Purchase updated",
        })
    return jsonify({
        "Success":False,
        "status":"Purchase update failed",
    })   
@api_purchases_bp.route("/<int:purchase_id>/confirm",methods=["GET"])
@token_required
def confirm_purchase(user_id,purchase_id):
    purchase=Purchases.query.filter(Purchases.purchase_id==purchase_id).first()
    if purchase and purchase.status==False:
        purchase.status=True
        items=PurchaseItems.query.filter(PurchaseItems.purchase_id==purchase_id).all()
        for item in items:
            product=Product.query.filter(Product.product_id==item.product_id).first()
            if product:
                product.quantity_float+=item.quantity_float
                
        transaction=Transactions(type="purchase",amount=purchase.total_amount,purchase_id=purchase_id,user_id=user_id)
        db2.session.add(transaction)
        db2.session.commit()
        return jsonify({
            "success":True,
            "message":"purchase confirmed."
        })      
    return jsonify({
        "success":False,
        "message":"confirm purchase failed."
    })
@api_purchases_bp.route("/items/add", methods=["POST"])
@token_required
def add_purchase_item(user_id):
    
    purchase_id=int(request.json["purchase_id"])
    product_id=int(request.json["product_id"])
    purchase_price=float(request.json["purchase_price"])
    quantity=float(request.json["quantity"])

    purchase=Purchases.query.filter(Purchases.purchase_id==purchase_id).first()

    product = Product.query.filter(Product.product_id==product_id).first()
    if product:
        # if purchase and purchase.status:
        #       product.quantity_float=product.quantity_float+quantity
        # #product.current_price=product_price
        # db2.session.commit()      
        if  purchase:
            purchase_item=PurchaseItems(purchase_id=purchase_id,product_id=product.product_id,purchase_price=purchase_price,quantity_float=quantity,remain_quantity=quantity)
            db2.session.add(purchase_item)
            db2.session.commit()
            recalcultePurchaseTotal(purchase_id,user_id)

        return jsonify({
            "success": True,
            "status": "purchase item added",
            "product_name": product.name,
            "product_price": product.current_price,
            "product_brcode":product.barcode
        })
    return jsonify({
        "success": False,
        "status": "purchase item adding failed",
    })
@api_purchases_bp.route("/items", methods=["GET"])
@token_required
def getpurchaseitems(user_id):
    purchase_id=request.args.get("purchase_id",type=int)
    product_id=request.args.get("product_id",type=int)
    query=PurchaseItems.query

    print("test: ",product_id,"  .   ",purchase_id)
    if purchase_id:
        query=query.filter(PurchaseItems.purchase_id==purchase_id)

    if product_id:
        query=query.filter(PurchaseItems.product_id==product_id)

    results2 = query.order_by(desc(PurchaseItems.purchase_item_id)).all()
    result_list2=[]
    for r in results2:
        print(r.product_id)
        if r.product_id:
            p = Product.query.filter(Product.product_id==r.product_id,Product.user_id==user_id).first()
            x={"id": r.purchase_item_id, "name": p.name, "barcode": p.barcode, "price": r.purchase_price,"quantity":r.quantity_float}
        else:
            x={"id": r.purchase_item_id, "name": "", "barcode": "",  "price": r.purchase_price,"quantity":r.quantity_float}    
           
        result_list2.append(x)
    print(len(results2))
    total=0
    for st in results2:
        total+=st.purchase_price*st.quantity_float
    print(total)
    
    return jsonify({
              "success": True,
              "results": result_list2,
              "total":total
    })

@api_purchases_bp.route("/items/<int:item_id>/remove", methods=["GET"])
@token_required
def removepurchaseitem(user_id,item_id):
    item=PurchaseItems.query.filter(PurchaseItems.purchase_item_id==item_id).first()
    if item:
        purchase=Purchases.query.filter(Purchases.purchase_id==item.purchase_id).first()
        if purchase:
            if purchase.status==False:
                db2.session.delete(item)
                db2.session.commit()
                recalcultePurchaseTotal(item.purchase_id,user_id)
                return jsonify({
                    "success": True,
                    "message":"item removed"
                })
            else:
                return jsonify({
                    "success": False,
                    "message":"cannot modify in confirmed purchase"
                })                
    return jsonify({
              "success": False,
              "message":"Error:item not found"
     })
def recalcultePurchaseTotal(purchase_id,user_id):
    purchase=Purchases.query.filter(Purchases.purchase_id==purchase_id).first()
    if purchase:
        total=0
        items=PurchaseItems.query.filter(PurchaseItems.purchase_id==purchase_id).all()
        for item in items:
            total+=item.quantity_float*item.purchase_price
        
        purchase.total_amount=total
        transaction=Transactions.query.filter(Transactions.purchase_id==purchase.purchase_id,Transactions.user_id==user_id)
        if transaction:
            transaction.amount=total
        db2.session.commit()
        return total
    return 0

@api_purchases_bp.route("/items/update",methods=["POST"])
@token_required
def updatepurchaseitem(user_id):
    quantity=float(request.json["quantity"])
    purchase_price=float(request.json["purchase_price"])
    item_id=int(request.json["item_id"])

    item=PurchaseItems.query.filter(PurchaseItems.purchase_item_id==item_id).first()
    if item:
        purchase=Purchases.query.filter(Purchases.purchase_id==item.purchase_id).first()
        print("Status:",purchase.status)
        if purchase.status==False:
            item.quantity_float=quantity
            item.remain_quantity=quantity
            item.purchase_price=purchase_price
            db2.session.commit()
            recalcultePurchaseTotal(purchase.purchase_id,user_id)
            return jsonify({
                "success":True,
                "message":"item updated",
            })    
        else:
            return jsonify({
                "success": False,
                "message":"cannot modify in confirmed purchase"
            })                  
    return jsonify({
        "success":False,
        "message":"item update failed",
    })
