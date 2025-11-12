from flask import render_template, request, jsonify,redirect,url_for,make_response,session,Blueprint
from datetime import datetime,date,timedelta
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from sqlalchemy import desc
from models import *
transactions_bp = Blueprint('transactions', __name__, url_prefix='/transactions')###transactions
@transactions_bp.route("/managetransactions",methods=["GET"])
def managetransactions():
    if "user" not in session: return redirect(url_for("users.login"))
    return render_template("manage_transactions.html")
@transactions_bp.route("/transaction/new",methods=["GET"])
def newtransaction():
    if "user" not in session: return redirect(url_for("users.login"))
    return render_template("addtransaction.html")
@transactions_bp.route("/transaction/add",methods=["POST"])
def addtransaction():
    if "user" not in session: return redirect(url_for("users.login"))
    transaction_type = request.json["transaction_type"]
    transaction_amount = float(request.json["transaction_amount"])
    transaction_date = request.json["transaction_date"]
    
    if transaction_date:
        l=transaction_date.split('-')
        year,month,day=int(l[0]),int(l[1]),int(l[2])
        print()
        print(transaction_date.split('-')[0])
        xd=datetime(year,month,day)
        transaction=Transactions(type=transaction_type,amount=transaction_amount,date=xd,user_id=int(session["user_id"]))
        
    else:
        transaction=Transactions(type=transaction_type,amount=transaction_amount,user_id=int(session["user_id"]))
    db2.session.add(transaction)
    db2.session.commit()
    
    return jsonify({
              "success": True,
              "transaction added": transaction.id,
              "amount":transaction.amount,
               "type":transaction.type
    })
    return render_template("addtransaction.html")
@transactions_bp.route("/transaction/<int:transaction_id>/remove", methods=["GET", "POST"])
def remove_transaction(transaction_id):
    if "user" not in session: return redirect(url_for("users.login"))
    transaction = Transactions.query.get(transaction_id)
    if request.method == "POST":
        db2.session.delete(transaction)
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
    return render_template("confirm_delete_transaction.html",transaction=transaction)
        
@transactions_bp.route("/transactions/list/<string:filt>",methods=["GET"])
def transactionslist(filt):
    if "user" not in session: return redirect(url_for("users.login"))
    if filt=="Today":
       transactions = Transactions.query.filter(func.date(Transactions.date) == date.today(),Transactions.user_id==int(session["user_id"])).order_by(desc(Transactions.date)).all()
    else:
       transactions=Transactions.query.filter(Transactions.user_id==int(session["user_id"])).order_by(desc(Transactions.date)).all()
    print(date.today())
    retdict=[]
    balance=0
    for tr in transactions:
        x={"id":tr.id , "date": tr.date, "type": tr.type,  "amount": roundFive(tr.amount)}
        if tr.type=="withdraw" or tr.type=="expense" or tr.type=="purchase"  or tr.type=="forgive":
        	balance-=roundFive(tr.amount)
        else:
        	balance+=roundFive(tr.amount)
        retdict.append(x)
    response = make_response(render_template("transactions_list.html",data=retdict,balance=balance))
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response
@transactions_bp.route("/transactions/list/update",methods=["POST"])
def transactionslistupdate():
    if "user" not in session: return redirect(url_for("users.login"))
    filt=request.json["filter"]
    
    
    print("filt",filt)
    if filt=="Today":
    	
       transactions = Transactions.query.filter(func.date(Transactions.date) == date.today(),Transactions.user_id==int(session["user_id"])).order_by(desc(Transactions.date)).all()
    else:
        
        
        l=filt.split('-')
        
        year=int(l[0])
        month=int(l[1])
        day=int(l[2])
        xdate=date(year,month,day)
        print("xdate",xdate)
        transactions = Transactions.query.filter(func.date(Transactions.date) == xdate,Transactions.user_id==int(session["user_id"])).order_by(desc(Transactions.date)).all()
    retdict=[]
    balance=0
    for tr in transactions:
        x={"id":tr.id , "date": tr.date, "type": tr.type,  "amount": roundFive(tr.amount)}
        if tr.type=="withdraw" or tr.type=="expense" or tr.type=="purchase" or tr.type=="forgive":
        	balance-=roundFive(tr.amount)
        else:
        	balance+=roundFive(tr.amount)
        retdict.append(x)
    return jsonify({
              "success": True,
              "results": retdict,
              "balance":balance
     })