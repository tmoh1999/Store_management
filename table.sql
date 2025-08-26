 CREATE TABLE product_batches (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    purchase_price REAL NOT NULL, 
    date_received TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(product_id) REFERENCES products(product_id)
);