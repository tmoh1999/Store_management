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
tools_bp = Blueprint('tools', __name__, url_prefix='/tools')

@tools_bp.route('/backup')
def backup():
    if "user" not in session: return redirect(url_for("users.login"))
    # Connection info
    db_user = 'root'
    db_password = ''  # empty in your case
    db_name = 'store_db'

    # Create a unique backup filename with timestamp
    backup_file = f"backup_{db_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"

    # Command to export (dump) MySQL database
    command = ['mysqldump', '-u', db_user, db_name]

    # If there’s a password, add it like: ['mysqldump', '-u', db_user, f'-p{db_password}', db_name]
    with open(backup_file, 'w') as f:
        subprocess.run(command, stdout=f)

    # Send file for download
    return send_file(backup_file, as_attachment=True)
@tools_bp.route("/test",methods=["POST","GET"])
def test():
    backup()
    return jsonify({
              "success": True,
              "test": "worked"	        
     })