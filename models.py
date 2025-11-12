from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
import mysql.connector
from datetime import date,timedelta
db2 = SQLAlchemy()


class User(db2.Model):
    id = db2.Column(db2.Integer, primary_key=True)
    username = db2.Column(db2.String(100), unique=True, nullable=False)
    password = db2.Column(db2.String(200), nullable=False)
class Product(db2.Model):
    __tablename__ = "products"

    product_id = db2.Column(db2.Integer, primary_key=True)
    name = db2.Column(db2.String(255), nullable=False)
    barcode = db2.Column(db2.String(255))
    current_price = db2.Column(db2.Float)
    quantity = db2.Column(db2.Integer, server_default="0")
    quantity_float=db2.Column(db2.Float, server_default="0.0")
    user_id = db2.Column(db2.Integer, db2.ForeignKey("user.id"), nullable=False)
    def __repr__(self):
        return f"<Product {self.name}>"
class ProductBatches(db2.Model):
    __tablename__ = "product_batches"
    id= db2.Column(db2.Integer, primary_key=True)
    product_id = db2.Column(db2.Integer)
    date_received = db2.Column(db2.DateTime(timezone=True), server_default=func.now())
    purchase_price = db2.Column(db2.Float)
    quantity = db2.Column(db2.Integer, server_default="0")
    quantity_float=db2.Column(db2.Float, server_default="0.0")
    def __repr__(self):
          return f"<ProductBatches {self.id}>"

class Purchases(db2.Model):
    __tablename__ = "purchases"
    purchase_id= db2.Column(db2.Integer, primary_key=True)
    supplier_id = db2.Column(db2.Integer)
    purchase_date = db2.Column(db2.DateTime(timezone=True), server_default=func.now())
    total_amount = db2.Column(db2.Float, server_default="0.0")
    status = db2.Column(db2.Boolean, server_default="0")
    description = db2.Column(db2.String(250))
    user_id = db2.Column(db2.Integer, db2.ForeignKey("user.id"), nullable=False)
    def __repr__(self):
        return f"<Purchases {self.purchase_id}>"


class PurchaseItems(db2.Model):
    __tablename__ = "purchase_items"
    purchase_item_id = db2.Column(db2.Integer, primary_key=True)
    purchase_id = db2.Column(db2.Integer)
    product_id = db2.Column(db2.Integer)
    purchase_price = db2.Column(db2.Float)
    quantity = db2.Column(db2.Integer, server_default="0")
    quantity_float=db2.Column(db2.Float, server_default="0.0")
    remain_quantity=db2.Column(db2.Float, server_default="0.0")
    def __repr__(self):
        return f"<PurchasesItems {self.purchase_item_id}>"
class Sales(db2.Model):
    __tablename__ = "sales"
    sale_id = db2.Column(db2.Integer, primary_key=True)
    sale_date = db2.Column(db2.DateTime(timezone=True), server_default=func.now())
    total_amount = db2.Column(db2.Float)
    user_id = db2.Column(db2.Integer, db2.ForeignKey("user.id"), nullable=False)
    def __repr__(self):
        return f"<Sale {self.sale_id}>"

class SaleItems(db2.Model):
    __tablename__ = "sale_items"
    item_id = db2.Column(db2.Integer, primary_key=True)
    sale_id = db2.Column(db2.Integer)
    product_id = db2.Column(db2.Integer)
    quantity=db2.Column(db2.Integer, server_default="0")
    description = db2.Column(db2.String(255))
    unit_price = db2.Column(db2.Float)
    profit = db2.Column(db2.Float, server_default="0.0")
    quantity_float=db2.Column(db2.Float, server_default="0.0")
    def __repr__(self):
        return f"<SaleItem {self.item_id}>"
class Suppliers(db2.Model):
    __tablename__ = "suppliers"

    supplier_id = db2.Column(db2.Integer, primary_key=True)
    name = db2.Column(db2.String(64))
    email = db2.Column(db2.String(64))
    phone = db2.Column(db2.String(128))
    user_id = db2.Column(db2.Integer, db2.ForeignKey("user.id"), nullable=False)
    def __repr__(self):
        return f"<Supplier {self.name}>"  
class SalePurchaseUsage(db2.Model):
    id = db2.Column(db2.Integer, primary_key=True)
    item_id = db2.Column(db2.Integer, db2.ForeignKey('sale_items.item_id'))
    purchase_item_id = db2.Column(db2.Integer, db2.ForeignKey('purchase_items.purchase_item_id'))
    quantity_used = db2.Column(db2.Float, server_default="0.0")

    
class Transactions(db2.Model):
    __tablename__ = "transactions"

    id = db2.Column(db2.Integer, primary_key=True)
    date = db2.Column(db2.DateTime(timezone=True), server_default=func.now())
    type = db2.Column(db2.String(50))
    amount = db2.Column(db2.Float, nullable=False)
    sale_id = db2.Column(db2.Integer, db2.ForeignKey("sales.sale_id"), nullable=True)
    purchase_id = db2.Column(db2.Integer, db2.ForeignKey("purchases.purchase_id"), nullable=True)
    note = db2.Column(db2.String(255))
    user_id = db2.Column(db2.Integer, db2.ForeignKey("user.id"), nullable=False)

    def __repr__(self):
        return f"<Transaction {self.type} {self.amount}>"

def get_db():
    return mysql.connector.connect(
        host="localhost", user="root", password="", database="store_db"
    )

def getDate(filt):
        l=filt.split('-')
        year=int(l[0])
        month=int(l[1])
        day=int(l[2])
        return date(year,month,day)
def roundFive(mon):
    if mon%5!=0:
        res=(mon//5+1)*5
        return res
    return mon