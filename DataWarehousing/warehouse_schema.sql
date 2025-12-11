-- DSA 2040 FS 2025: Data Warehouse Schema
-- Task 1: Data Warehouse Design
-- Star Schema Implementation for Retail Data

-- Enable foreign key support in SQLite
PRAGMA foreign_keys = ON;

-- ==========================================
-- Dimension Tables
-- ==========================================

-- 1. Customer Dimension
CREATE TABLE IF NOT EXISTS CustomerDim (
    customer_id INTEGER PRIMARY KEY,
    source_customer_id TEXT, -- Original ID from source data
    name TEXT, -- Placeholder if name isn't available
    country TEXT,
    city TEXT -- Optional if available
);

-- 2. Product Dimension
CREATE TABLE IF NOT EXISTS ProductDim (
    product_id INTEGER PRIMARY KEY,
    stock_code TEXT, -- specific to retail dataset usually
    description TEXT,
    category TEXT -- To be derived or extracted
);

-- 3. Time Dimension
CREATE TABLE IF NOT EXISTS TimeDim (
    time_id INTEGER PRIMARY KEY,
    full_date DATE,
    day INTEGER,
    month INTEGER,
    year INTEGER,
    quarter INTEGER,
    day_of_week TEXT
);

-- ==========================================
-- Fact Table
-- ==========================================

-- Sales Fact Table
CREATE TABLE IF NOT EXISTS SalesFact (
    sale_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER,
    product_id INTEGER,
    time_id INTEGER,
    invoice_no TEXT, -- specific to online retail dataset
    quantity INTEGER,
    unit_price REAL,
    total_sales REAL,
    FOREIGN KEY (customer_id) REFERENCES CustomerDim(customer_id),
    FOREIGN KEY (product_id) REFERENCES ProductDim(product_id),
    FOREIGN KEY (time_id) REFERENCES TimeDim(time_id)
);
