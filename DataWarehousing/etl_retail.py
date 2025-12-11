import pandas as pd
import os
import sqlite3
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta

# Define paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Data is two levels up from Scripts/etl_retail.py (Scripts/ -> root -> copy of...)
DATA_FILE = os.path.join(BASE_DIR, '..', 'Copy of Online Retail.csv')
DB_FILE = os.path.join(BASE_DIR, '..', 'DataWarehousing', 'retail_dw.db')
SCHEMA_FILE = os.path.join(BASE_DIR, '..', 'DataWarehousing', 'warehouse_schema.sql')

def init_db():
    """Initialize the database with schema."""
    print("Initializing Database...")
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
        print("Removed existing database file.")
    try:
        with open(SCHEMA_FILE, 'r') as f:
            schema_sql = f.read()
        
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.executescript(schema_sql)
        conn.commit()
        conn.close()
        print("Database initialized successfully.")
    except Exception as e:
        print(f"Error initializing DB: {e}")

def extract_data(file_path):
    """Task 2.2: Extract Phase"""
    print(f"\n--- EXTRACT PHASE ---")
    print(f"Reading data from: {file_path}")
    try:
        try:
            df = pd.read_csv(file_path, encoding='ISO-8859-1')
        except UnicodeDecodeError:
            df = pd.read_csv(file_path, encoding='utf-8')
            
        print(f"Extracted {len(df)} rows.")
        return df
    except Exception as e:
        print(f"Error extraction: {e}")
        return None

def transform_data(df):
    """Task 2.3: Transform Phase"""
    print(f"\n--- TRANSFORM PHASE ---")
    initial_count = len(df)
    
    # 1. Drop missing CustomerID (User Instruction)
    print("Dropping rows with missing CustomerID...")
    df = df.dropna(subset=['CustomerID']).copy()
    print(f"Rows after dropping missing CustomerID: {len(df)} (Dropped {initial_count - len(df)})")
    
    # 2. Convert types
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
    df['CustomerID'] = df['CustomerID'].astype(int) # Clean ID format
    
    # 3. Calculate TotalSales (Task 2.3.1)
    df['TotalSales'] = df['Quantity'] * df['UnitPrice']
    
    # 4. Filter Data (Task 2.3.3)
    # Simulate current date as August 12, 2025.
    # The original dataset is from 2011. We will shift the data to end near Aug 2025 to make it realistic.
    print("Simulating 2025 Data: Shifting dates...")
    max_date = df['InvoiceDate'].max()
    target_date = pd.Timestamp('2025-08-12')
    # Calculate offset
    time_delta = target_date - max_date
    
    # Apply offset to all dates
    df['InvoiceDate'] = df['InvoiceDate'] + time_delta
    
    # Filter for last year (Aug 12, 2024 - Aug 12, 2025)
    start_date = target_date - pd.DateOffset(years=1)
    print(f"Filtering data between {start_date.date()} and {target_date.date()}...")
    
    df = df[(df['InvoiceDate'] >= start_date) & (df['InvoiceDate'] <= target_date)]
    
    # Remove rows with Quantity < 0 (returns) or UnitPrice <= 0
    print("Filtering invalid quantities and prices...")
    df = df[df['Quantity'] > 0]
    df = df[df['UnitPrice'] > 0]
    print(f"Rows after filtering: {len(df)}")
    
    # 5. Extract Dimensions
    
    # Customer Dimension
    # Group by CustomerID to get unique customers
    # We take the first occurrence of Country for each customer
    print("Extracting Customer Dimension...")
    customer_dim = df.groupby('CustomerID').agg({
        'Country': 'first'
    }).reset_index()
    customer_dim.columns = ['customer_id', 'country']
    customer_dim['source_customer_id'] = customer_dim['customer_id'].astype(str)
    customer_dim['name'] = 'Customer ' + customer_dim['source_customer_id'] # Placeholder
    
    # Time Dimension
    print("Extracting Time Dimension...")
    # Extract unique dates (ignoring time for the dimension, or keeping time if granulated)
    # Schema has a TimeDim. Let's create a Day-level dimension or Timestamp level?
    # Schema says: time_id, full_date, day, month, year, quarter...
    # Let's create dimensions based on the InvoiceDate (Date part)
    unique_dates = df['InvoiceDate'].dt.date.unique()
    time_dim = pd.DataFrame({'full_date': unique_dates})
    time_dim['full_date'] = pd.to_datetime(time_dim['full_date'])
    time_dim['time_id'] = time_dim['full_date'].dt.strftime('%Y%m%d').astype(int)
    time_dim['day'] = time_dim['full_date'].dt.day
    time_dim['month'] = time_dim['full_date'].dt.month
    time_dim['year'] = time_dim['full_date'].dt.year
    time_dim['quarter'] = time_dim['full_date'].dt.quarter
    time_dim['day_of_week'] = time_dim['full_date'].dt.day_name()
    
    # Product Dimension
    print("Extracting Product Dimension...")
    # Group by StockCode
    product_dim = df.groupby('StockCode').agg({
        'Description': 'first'
    }).reset_index()
    product_dim.columns = ['stock_code', 'description']
    product_dim['product_id'] = product_dim.index + 1 # Simple auto-increment surrogates
    product_dim['category'] = 'General' # Placeholder as category isn't in dataset
    
    # Prepare Sales Fact
    print("Preparing Sales Fact Table...")
    # We need to map the original data to the new Surrogate Keys
    
    # Map Product ID
    fact_table = df.merge(product_dim[['stock_code', 'product_id']], left_on='StockCode', right_on='stock_code', how='left')
    
    # Map Time ID (based on date)
    fact_table['date_key'] = fact_table['InvoiceDate'].dt.date
    # Convert date_key in fact_table to match time_dim['full_date'] type if needed, but logic below is simpler:
    # time_id construction:
    fact_table['time_id'] = fact_table['InvoiceDate'].dt.strftime('%Y%m%d').astype(int)
    
    # Customer ID is already the key (using actual ID as key or mapping? Schema has customer_id as PK)
    # Let's use the explicit CustomerID from CSV as the Link for now, assuming CustomerDim uses it as PK or we map it.
    # In my logic above: customer_dim['customer_id'] IS the CSV CustomerID.
    # So we can rename it to match schema expectation if needed. 
    # Schema: customer_id INTEGER PRIMARY KEY
    # So we can just use the CSV ID as the ID if unique.
    
    # Select final columns for Fact
    sales_fact = fact_table[[
        'CustomerID', 'product_id', 'time_id', 'InvoiceNo', 'Quantity', 'UnitPrice', 'TotalSales'
    ]].copy()
    sales_fact.columns = ['customer_id', 'product_id', 'time_id', 'invoice_no', 'quantity', 'unit_price', 'total_sales']
    
    return {
        'CustomerDim': customer_dim,
        'ProductDim': product_dim,
        'TimeDim': time_dim,
        'SalesFact': sales_fact
    }

def load_data(data_dict):
    """Task 2.4: Load Phase"""
    # Note: Using replace for dimensions to handle re-runs without duplication errors for now, 
    # but strictly ETL often uses SCD. For this exam 'replace' or 'append' with care is fine.
    # Given the schema is fresh each time via init_db, 'append' is fine.
    
    print(f"\n--- LOAD PHASE ---")
    conn = sqlite3.connect(DB_FILE)
    
    try:
        # Load Dimensions
        print("Loading CustomerDim...")
        # Schema: customer_id, source_customer_id, name, country, city
        # Our DF: customer_id, country, source_customer_id, name
        data_dict['CustomerDim'].to_sql('CustomerDim', conn, if_exists='append', index=False)
        
        print("Loading ProductDim...")
        # Schema: product_id, stock_code, description, category
        data_dict['ProductDim'].to_sql('ProductDim', conn, if_exists='append', index=False)
        
        print("Loading TimeDim...")
        # Schema: time_id, full_date, day, month, year, quarter, day_of_week
        data_dict['TimeDim'].to_sql('TimeDim', conn, if_exists='append', index=False)
        
        # Load Fact
        print("Loading SalesFact...")
        # Schema: sale_id (auto), customer_id, product_id, time_id, invoice_no, quantity, unit_price, total_sales
        # Since sale_id is AUTOINCREMENT, we don't allow it to be in the dataframe, or we don't index=False if we want pandas to help?
        # Better to just not include sale_id column and let SQLite handle it.
        # Ensure our DF column order matches what we want, or simple append works if names match.
        data_dict['SalesFact'].to_sql('SalesFact', conn, if_exists='append', index=False)
        
        print("Data Loading Complete.")
        
    except Exception as e:
        print(f"Error loading data: {e}")
    finally:
        conn.close()

def visualize_data():
    """Task 3.2: Visualize Results"""
    print(f"\n--- VISUALIZATION PHASE ---")
    conn = sqlite3.connect(DB_FILE)
    
    # Query: Total Sales by Country (Top 10)
    query = """
    SELECT 
        c.country,
        SUM(f.total_sales) as total_sales
    FROM SalesFact f
    JOIN CustomerDim c ON f.customer_id = c.customer_id
    GROUP BY c.country
    ORDER BY total_sales DESC
    LIMIT 10;
    """
    
    try:
        df_viz = pd.read_sql_query(query, conn)
        
        plt.figure(figsize=(12, 6))
        sns.barplot(data=df_viz, x='total_sales', y='country', hue='country', palette='viridis', legend=False)
        plt.title('Top 10 Countries by Total Sales (2024-2025)')
        plt.xlabel('Total Sales')
        plt.ylabel('Country')
        plt.tight_layout()
        
        output_path = os.path.join(BASE_DIR, '..', 'sales_by_country.png')
        plt.savefig(output_path)
        print(f"Visualization saved to: {output_path}")
        
    except Exception as e:
        print(f"Error visualizing data: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    # Initialize DB (Create tables)
    init_db()
    
    # ETL Pipeline
    df_raw = extract_data(DATA_FILE)
    
    if df_raw is not None:
        data_staging = transform_data(df_raw)
        load_data(data_staging)
        
        # Run Visualization
        visualize_data()
        
        print("\nETL Process Completed Successfully.")
