from flask import Flask, render_template, request, jsonify,redirect,url_for,make_response,send_file,session,flash,Blueprint
from datetime import datetime,date,timedelta
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from openpyxl import load_workbook,Workbook
from sqlalchemy import desc
from weasyprint import HTML,CSS
from decorators import token_required
import io
import os
import webbrowser
import subprocess
tools_bp = Blueprint('tools', __name__, url_prefix='/tools')

@tools_bp.route('/backup')
@token_required
def backup(user_id):
    
    # Connection info
    db_user = 'root'
    db_password = 'mohamed'  # empty in your case
    db_name = 'store_db'

    # Create a unique backup filename with timestamp
    backup_file = f"backup_{db_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"

    # Command to export (dump) MySQL database
    command = ['mysqldump', '-u', db_user, f'-p{db_password}', db_name]

    # If there’s a password, add it like: ['mysqldump', '-u', db_user, f'-p{db_password}', db_name]
    with open(backup_file, 'w') as f:
        subprocess.run(command, stdout=f)

    # Send file for download
    return send_file(backup_file, as_attachment=True)


@tools_bp.route('/restore', methods=['POST'])
@token_required
def restore(user_id):
    db_user = 'root'
    db_password = 'mohamed'
    db_name = 'store_db'

    if 'file' not in request.files:
        return {"error": "No file uploaded"}, 400

    file = request.files['file']

    if not file.filename.endswith('.sql'):
        return {"error": "Only .sql files are allowed"}, 400

    temp_path = "uploaded_restore.sql"
    file.save(temp_path)

    # Read the SQL file as UTF-8
    with open(temp_path, 'r', encoding='utf-8', errors='ignore') as f:
        sql = f.read()

    # Fix new MySQL collations for older MySQL versions
    replacements = [
        ("utf8mb4_uca1400_ai_ci", "utf8mb4_unicode_ci"),
        ("utf8mb4_uca1400_as_ci", "utf8mb4_unicode_ci"),
        ("utf8mb4_uca1400_ci", "utf8mb4_unicode_ci"),
        ("utf8mb4_uca1400", "utf8mb4_unicode_ci"),
    ]
    for old, new in replacements:
        sql = sql.replace(old, new)

    fixed_path = "fixed_restore.sql"
    with open(fixed_path, "w", encoding='utf-8') as f:
        f.write(sql)

    command = ['mysql', '-u', db_user, f'-p{db_password}', db_name]

    with open(fixed_path, 'r', encoding='utf-8') as f:
        subprocess.run(command, stdin=f)

    os.remove(temp_path)
    os.remove(fixed_path)

    return {"status": "Database restored successfully"}



@tools_bp.route("/test",methods=["POST","GET"])
def test():
    backup()
    return jsonify({
              "success": True,
              "test": "worked"	        
     })