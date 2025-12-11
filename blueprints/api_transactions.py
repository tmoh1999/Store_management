import io
import os
from flask import current_app, render_template, request, jsonify,redirect, send_file,url_for,make_response,Blueprint
from datetime import date,timedelta
from flask_sqlalchemy import SQLAlchemy
from openpyxl import Workbook
from sqlalchemy.sql import func
from sqlalchemy import String, cast, desc
from weasyprint import CSS, HTML
from models import *
from decorators import token_required
api_transactions_bp = Blueprint('api_transactions', __name__, url_prefix='/api/transactions')
@api_transactions_bp.route("",methods=["GET"])
@token_required
def getTransactions(user_id):
    query=Transactions.query.filter(Transactions.user_id==user_id)

    stdate=request.args.get("start_date")
    endate=request.args.get("end_date")

    if stdate and endate :
        start_date=getDate(stdate)
        end_date=getDate(endate)
        query = query.filter(func.date(Transactions.date) >= start_date,func.date(Transactions.date) <= end_date)

    transactions=query.order_by(desc(Transactions.id)).all()
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
@api_transactions_bp.route("/export/excel", methods=["GET"])
@token_required
def export_transactions(user_id):
    
    # Create a new Excel workbook
    wb = Workbook()
    ws = wb.active
    ws.title = "Transactions"

    # Write header row
    ws.append(["Transaction ID", "Date", "Amount", "Type","Note"])


    #transactions filter
    transactions_query = Transactions.query.filter(Transactions.user_id==user_id)
    query=request.args.get("search")
    if query:
        search = f"%{query.lower()}%"
        transactions_query = transactions_query.filter(
            func.lower(
                func.concat(
                    cast(Transactions.id, String), " ",
                    cast(Transactions.date, String), " ",
                    cast(Transactions.amount, String), " ",
                    cast(Transactions.type, String), " ",
                    cast(Transactions.note, String), " ",
                )
            ).like(search)
        )


        
    
     #transactions sort
    sort_column=request.args.get("sort_column")
    
    if sort_column:
        column = getattr(Transactions, sort_column, None)

        if column:
            print("sort_column::",sort_column)
            sort_direction=request.args.get("sort_direction")
            if sort_direction == "asc":
                transactions_query = transactions_query.order_by(column.asc())
            else:
                transactions_query = transactions_query.order_by(column.desc())
        else:
            # default sort fallback
            transactions_query = transactions_query.order_by(Transactions.id.desc())
    else:
        transactions_query = transactions_query.order_by(Transactions.id.desc())
    
    transactions = transactions_query.all()

    for transaction in transactions:
        ws.append([transaction.id,transaction.date, transaction.amount, transaction.type,transaction.note])

    # Save to in-memory file
    file_stream = io.BytesIO()
    wb.save(file_stream)
    file_stream.seek(0)

    return send_file(
        file_stream,
        as_attachment=True,
        download_name="transactions.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

@api_transactions_bp.route("/export/pdf",methods=["GET"])
@token_required
def transactions_pdf(user_id):
    #transactions filter
    transactions_query = Transactions.query.filter(Transactions.user_id==user_id)
    query=request.args.get("search")
    if query:
        search = f"%{query.lower()}%"
        transactions_query = transactions_query.filter(
            func.lower(
                func.concat(
                    cast(Transactions.id, String), " ",
                    cast(Transactions.date, String), " ",
                    cast(Transactions.amount, String), " ",
                    cast(Transactions.type, String), " ",
                    func.coalesce(cast(Transactions.note, String), ""), " "
                )
            ).like(search)
        )


        
    
     #transactions sort
    sort_column=request.args.get("sort_column")
    
    if sort_column:
        column = getattr(Transactions, sort_column, None)

        if column:
            print("sort_column::",sort_column)
            sort_direction=request.args.get("sort_direction")
            if sort_direction == "asc":
                transactions_query = transactions_query.order_by(column.asc())
            else:
                transactions_query = transactions_query.order_by(column.desc())
        else:
            # default sort fallback
            transactions_query = transactions_query.order_by(Transactions.id.desc())
    else:
        transactions_query = transactions_query.order_by(Transactions.id.desc())
    
    transactions = transactions_query.all()
    print("transactions::::",len(transactions))
    columns=[
        {"Name":"ID","accessor":"id"},
        {"Name":"Date","accessor":"date"},
        {"Name":"Amount","accessor":"amount"},
        {"Name":"Type","accessor":"type"},
        {"Name":"Note","accessor":"note"},
    ]

    # render to PDF
    html = render_template("table_pdf_template.html", data=transactions,columns=columns,table_name="Transactions")
    
    css_path = os.path.join(current_app.root_path, "static", "css","bootstrap.min.css")
    pdf_bytes = HTML(string=html, base_url=current_app.root_path).write_pdf(stylesheets=[CSS(css_path)])
    pdf_file = io.BytesIO(pdf_bytes)
    return send_file(
        pdf_file,
        mimetype="application/pdf",
        as_attachment=True,          # True → download, False → open in browser
        download_name="transactions.pdf"  # filename for the browser
    )	
