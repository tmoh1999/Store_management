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
@api_suppliers_bp.route("/search",methods=["GET"])
@token_required
def search_supplier(user_id):
    supplier_id=request.args.get("supplier_id",type=int) 
    supplier_query=Suppliers.query
    if supplier_id:    
        supplier_query=supplier_query.filter(Suppliers.supplier_id==supplier_id)  
    supplier:Suppliers=supplier_query.first()
    if supplier:
        return jsonify({
            "success":True,
            "message":"supplier found",
            "supplier_id":supplier.supplier_id,
            "name":supplier.name,
            "email":supplier.email,
            "phone":supplier.phone,
        })
    else:
        return jsonify({
            "success":False,
            "message":"supplier not found"
        })        

@api_suppliers_bp.route("",methods=["GET"])
@token_required
def getSuppliers(user_id):
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
@api_suppliers_bp.route("/export/excel", methods=["GET"])
@token_required
def export_suppliers(user_id):
    
    # Create a new Excel workbook
    wb = Workbook()
    ws = wb.active
    ws.title = "Suppliers"

    # Write header row
    ws.append(["Supplier ID", "Name", "Email", "Phone"])


    #Suppliers filter
    suppliers_query = Suppliers.query.filter(Suppliers.user_id==user_id)
    query=request.args.get("search")
    if query:
        search = f"%{query.lower()}%"
        suppliers_query = suppliers_query.filter(
            func.lower(
                func.concat(
                    cast(Suppliers.supplier_id, String), " ",
                    cast(Suppliers.name, String), " ",
                    cast(Suppliers.email, String), " ",
                    cast(Suppliers.phone, String), " ",
                )
            ).like(search)
        )


        
    
     #suppliers sort
    sort_column=request.args.get("sort_column")
    
    if sort_column:
        column = getattr(Suppliers, sort_column, None)

        if column:
            print("sort_column::",sort_column)
            sort_direction=request.args.get("sort_direction")
            if sort_direction == "asc":
                suppliers_query = suppliers_query.order_by(column.asc())
            else:
                suppliers_query = suppliers_query.order_by(column.desc())
        else:
            # default sort fallback
            suppliers_query = suppliers_query.order_by(Suppliers.supplier_id.desc())
    else:
        suppliers_query = suppliers_query.order_by(Suppliers.supplier_id.desc())
    
    suppliers = suppliers_query.all()

    for supplier in suppliers:
        ws.append([supplier.supplier_id,supplier.name, supplier.email, supplier.phone])

    # Save to in-memory file
    file_stream = io.BytesIO()
    wb.save(file_stream)
    file_stream.seek(0)

    return send_file(
        file_stream,
        as_attachment=True,
        download_name="suppliers.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

@api_suppliers_bp.route("/export/pdf",methods=["GET"])
@token_required
def suppliers_pdf(user_id):
    #Suppliers filter
    suppliers_query = Suppliers.query.filter(Suppliers.user_id==user_id)
    query=request.args.get("search")
    if query:
        search = f"%{query.lower()}%"
        suppliers_query = suppliers_query.filter(
            func.lower(
                func.concat(
                    cast(Suppliers.supplier_id, String), " ",
                    cast(Suppliers.name, String), " ",
                    cast(Suppliers.email, String), " ",
                    cast(Suppliers.phone, String), " ",
                )
            ).like(search)
        )


        
    
     #suppliers sort
    sort_column=request.args.get("sort_column")
    
    if sort_column:
        column = getattr(Suppliers, sort_column, None)

        if column:
            print("sort_column::",sort_column)
            sort_direction=request.args.get("sort_direction")
            if sort_direction == "asc":
                suppliers_query = suppliers_query.order_by(column.asc())
            else:
                suppliers_query = suppliers_query.order_by(column.desc())
        else:
            # default sort fallback
            suppliers_query = suppliers_query.order_by(Suppliers.supplier_id.desc())
    else:
        suppliers_query = suppliers_query.order_by(Suppliers.supplier_id.desc())
    
    suppliers = suppliers_query.all()

    columns=[
        {"Name":"ID","accessor":"supplier_id"},
        {"Name":"Name","accessor":"name"},
        {"Name":"Email","accessor":"email"},
        {"Name":"Phone","accessor":"phone"},
    ]

    # render to PDF
    html = render_template("table_pdf_template.html", data=suppliers,columns=columns,table_name="SUppliers")
    
    css_path = os.path.join(current_app.root_path, "static", "css","bootstrap.min.css")
    pdf_bytes = HTML(string=html, base_url=current_app.root_path).write_pdf(stylesheets=[CSS(css_path)])
    pdf_file = io.BytesIO(pdf_bytes)
    return send_file(
        pdf_file,
        mimetype="application/pdf",
        as_attachment=True,          # True → download, False → open in browser
        download_name="suppliers.pdf"  # filename for the browser
    )	
