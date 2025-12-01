from flask import render_template, request, jsonify,redirect,url_for,make_response,Blueprint
from datetime import date,timedelta
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from sqlalchemy import desc
from models import *
from decorators import token_required
api_transactions_bp = Blueprint('api_transactions', __name__, url_prefix='/api/transactions')
@api_transactions_bp.route("/list",methods=["GET"])
@token_required
def getTransactionsList(user_id):
    transactions=Transactions.query.filter(Transactions.user_id==user_id).order_by(desc(Transactions.id)).all()
    results=[
        {
            "id":transaction.id,
            "date":transaction.date,
            "type":transaction.type,
            "amount":transaction.amount,
            "note":transaction.note,

        }
        for transaction in transactions
    ]
    return jsonify({
        "success":True,
        "results":results,
    })
@api_transactions_bp.route("/<int:transaction_id>/remove", methods=["GET"])
@token_required
def remove_transaction(user_id,transaction_id):
    transaction = Transactions.query.get(transaction_id)
    if transaction:
        db2.session.delete(transaction)
        db2.session.commit()
        return jsonify({
            "success":True,
            "message":"Transaction deleted",
        })        
    return jsonify({
        "success":False,
        "message":"Transaction delete failed",
    })
@api_transactions_bp.route("/<int:transaction_id>/update", methods=["GET", "POST"])
@token_required
def edit_transaction(user_id,transaction_id):
    
    transaction = Transactions.query.get_or_404(transaction_id)

    if request.method == "POST":
       if transaction:
           transaction.note = request.json["note"]
           db2.session.commit()
       return jsonify({
            "success": True,
            "status": "transaction updated",
            "note": transaction.note,
        })

    return jsonify({
            "success": False,
            "status": "Data missing"
        })