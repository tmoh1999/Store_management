from flask import Flask, render_template, request, jsonify,redirect,url_for,make_response,send_file,session,flash,Blueprint
from datetime import datetime,date,timedelta
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from openpyxl import load_workbook,Workbook
from sqlalchemy import desc
from weasyprint import HTML,CSS
import io
import os
import webbrowser
import subprocess
from models import *
sales_bp = Blueprint('sales', __name__, url_prefix='/sales')

#####Sales
@sales_bp.route("/managesales",methods=["GET"])
def managesales():
    if "user" not in session: return redirect(url_for("users.login"))
    return render_template("managesales.html")

@sales_bp.route("/sale/add",methods=["POST"])
def addsale():
    if "user" not in session: return redirect(url_for("users.login"))
    new_sale=Sales(user_id=int(session["user_id"]))
    db2.session.add(new_sale)
    db2.session.commit()
    print(new_sale,new_sale.sale_id)
    return render_template("sale_items.html",sale=new_sale)
@sales_bp.route("/sale/add_item", methods=["GET", "POST"])
def addsaleitem():
    if "user" not in session: return redirect(url_for("users.login"))
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
@sales_bp.route("/sale/update_item", methods=["GET", "POST"])
def updatesaleitem():
    if "user" not in session: return redirect(url_for("users.login"))
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
@sales_bp.route("/sale/refresh", methods=["GET", "POST"])
def resfreshsaleitems():
    if "user" not in session: return redirect(url_for("users.login"))
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
@sales_bp.route("/sale/remove", methods=["GET", "POST"])
def removesale():
    if "user" not in session: return redirect(url_for("users.login"))
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
	
		
@sales_bp.route("/sale/confirm", methods=["GET", "POST"])
def confirmsale():
    if "user" not in session: return redirect(url_for("users.login"))
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

@sales_bp.route("/saleslist/<string:filt>",methods=["GET"])
def saleslist(filt):
    if "user" not in session: return redirect(url_for("users.login"))
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
@sales_bp.route("/saleslist/update",methods=["POST"])
def saleslistupdate():
    if "user" not in session: return redirect(url_for("users.login"))
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
@sales_bp.route("/sales/<int:sale_id>/viewsaleitems", methods=["GET", "POST"])
def view_sales(sale_id):
    if "user" not in session: return redirect(url_for("users.login"))
    db = get_db(); cursor = db.cursor()
    cursor.execute("SELECT i.item_id,s.sale_id, s.sale_date,i.product_id,i.unit_price,i.quantity_float,i.description,i.profit FROM sale_items i INNER JOIN sales s ON i.sale_id = s.sale_id where i.sale_id=%s order by s.sale_date DESC",(sale_id,))
    results=cursor.fetchall()
    print(len(results))
    
    return render_template("sale_items_history.html",data=results)



@sales_bp.route("/saleitemslist/<string:filt>",methods=["GET"])
def saleitemslist(filt):
    if "user" not in session: return redirect(url_for("users.login"))
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
@sales_bp.route("/saleitemslist/update",methods=["POST"])
def saleitemslistupdate():
    if "user" not in session: return redirect(url_for("users.login"))
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
@sales_bp.route("/sale/statistiques",methods=["POST","GET"])
def salestatistiques():
    if "user" not in session: return redirect(url_for("users.login"))
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