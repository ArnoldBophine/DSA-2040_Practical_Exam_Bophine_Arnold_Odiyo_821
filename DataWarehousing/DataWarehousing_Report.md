# DSA 2040 Practical Exam: Section 1 - Data Warehousing Report

**Student Name:** Arnold Bophine Odiyo  
**Student ID:** 821  
**Date:** December 11, 2025  
**Course:** DSA 2040 - Data Warehousing and Data Mining  

---

## 1. Executive Summary

This report documents the successful implementation of **Section 1: Data Warehousing** for the DSA 2040 Practical Exam. The objective was to design and build a functional Data Warehouse for a retail company, enabling advanced analytics on sales, customer behavior, and product performance.

The project involved:
1.  **Schema Design**: Creating a robust Star Schema optimized for OLAP queries.
2.  **ETL Implementation**: Developing a Python-based pipeline (Extract, Transform, Load) to process raw CSV data, clean it, simulate current dates (2024-2025), and load it into an SQLite Data Warehouse.
3.  **Analysis & Visualization**: Executing multi-dimensional queries and generating visual insights.

The system is now fully operational, processing over **380,000 sales records** and providing instant analytic capabilities. The following sections detail the technical architecture, implementation logic, execution results, and analytical findings.

---

## 2. System Architecture and Design

### 2.1 Design Philosophy: Star Schema vs. Snowflake
For this retail data warehouse, a **Star Schema** was selected as the optimal design pattern. 

*   **Structure**: The schema consists of a central centralized Fact Table (`SalesFact`) surrounded by denormalized Dimension Tables (`CustomerDim`, `ProductDim`, `TimeDim`).
*   **Justification**:
    *   **Performance**: In analytical workloads, join operations are expensive. The Star Schema reduces the complexity of joins compared to a Snowflake Schema, where dimensions are normalized into sub-tables (e.g., Country table linked to City table linked to Customer table). A single join connects the Fact to the Dimension.
    *   **Usability**: The design is intuitive for business analysts writing SQL. It allows for simple "Select, Join, Group By" patterns that mirror business questions (e.g., "Show Sales by Country").
    *   **Context**: Given the dataset size (~500k rows) and the exam requirement for high-performance querying, the storage savings of a Snowflake design (normalization) were negligible compared to the read-performance benefits of the Star Schema.

### 2.2 Schema Definitions

The database `retail_dw.db` was implemented with the following structure:

#### **Fact Table: `SalesFact`**
This table holds the quantitative data (measures) and foreign keys.
*   `sale_id` (PK): Unique transaction identifier.
*   `customer_id` (FK): Links to Customer Details.
*   `product_id` (FK): Links to Product Details.
*   `time_id` (FK): Links to the specific date of sale.
*   `quantity`: The number of units sold (Measure).
*   `total_sales`: The calculated revenue (Quantity * UnitPrice) (Measure).
*   `invoice_no`: Degenerate dimension for traceability.

#### **Dimension Tables**
1.  **`CustomerDim`**: Stores customer attributes.
    *   `customer_id`: Surrogate Key.
    *   `source_customer_id`: Original Business Key.
    *   `country`: Critical for geographic analysis.
2.  **`ProductDim`**: Stores product details.
    *   `product_id`: Surrogate Key.
    *   `stock_code`: SKU.
    *   `description`: Product Name.
    *   `category`: Derived category (General).
3.  **`TimeDim`**: Facilitates time-based aggregation.
    *   `time_id`: Integer representation of date (YYYYMMDD).
    *   `full_date`, `year`, `quarter`, `month`: Attributes for Roll-up operations.

---

## 3. ETL Process Implementation

The Extract, Transform, Load (ETL) pipeline was implemented in Python using the `pandas` library for data manipulation and `sqlite3` for database interaction. The process is defined in `DataWarehousing/etl_retail.py`.

### 3.1 Step 1: Extraction
**Objective**: Ingest raw data from the legacy system.
The script reads `Copy of Online Retail.csv`. It handles potential encoding issues (common in legacy systems) by trying varying encodings (`ISO-8859-1`, `utf-8`).

```python
# Code Snippet: Extraction
def extract_data(file_path):
    # ...
    df = pd.read_csv(file_path, encoding='ISO-8859-1')
    print(f"Extracted {len(df)} rows.")
    return df
```

### 3.2 Step 2: Transformation
**Objective**: Clean, enrich, and conform the data.
This was the most complex phase, involving several critical operations:

1.  **Data Cleaning**: Rows with missing `CustomerID` were dropped, as anonymous sales cannot be linked to customer behaviors. 
    *   *Impact*: ~135,000 incomplete rows removed to ensure high data quality.
2.  **Derived Measures**: A new column `TotalSales` was calculated:
    ```python
    df['TotalSales'] = df['Quantity'] * df['UnitPrice']
    ```
3.  **Temporal Simulation (Date Shifting)**:
    *   **Challenge**: The original dataset contains data from 2010-2011. The exam scenario requires analysis of "current" data (2024-2025).
    *   **Solution**: A dynamic date shift algorithm was implemented. The maximum date in the source was mapped to the target date (Aug 12, 2025), and the difference (delta) was added to every record.
    ```python
    # Code Snippet: Date Simulation
    max_date = df['InvoiceDate'].max()
    target_date = pd.Timestamp('2025-08-12')
    time_delta = target_date - max_date
    df['InvoiceDate'] = df['InvoiceDate'] + time_delta
    ```
4.  **Filtering**: 
    *   **Time**: Filtered to keep only the last 12 months (Aug 2024 - Aug 2025).
    *   **Logic**: Removed returns (negative Quantity) and invalid prices to ensure the Warehouse reflects only valid revenue-generating transactions.
5.  **Dimension Extraction**: 
    *   Unique customers were extracted and de-duplicated to populate `CustomerDim`.
    *   Unique products were extracted to populate `ProductDim`.
    *   Time attributes (Year, Quarter, Month) were derived from the shifted dates for `TimeDim`.

### 3.3 Step 3: Loading
**Objective**: Persist the processed data.
Data was loaded into SQLite. The pipeline uses `if_exists='append'` to populate tables. The Foreign Keys in the Fact Table were mapped using the Surrogate Keys generated during the transformation phase (or utilizing the business keys where appropriate for this scale).

---

## 4. Execution Logs and Validation

The ETL script was executed successfully. Below is the transcript of the execution, confirming the logic described above.

**Command Executed:**
```powershell
python3 DataWarehousing\etl_retail.py
```

**System Output:**
```text
Initializing Database...
Removed existing database file.
Database initialized successfully.

--- EXTRACT PHASE ---
Reading data from: C:\Users\Admin\Documents\GitHub\DSA-2040_Practical_Exam_Bophine_Arnold_Odiyo_821\DataWarehousing\..\Copy of Online Retail.csv
Extracted 541909 rows.

--- TRANSFORM PHASE ---
Dropping rows with missing CustomerID...
Rows after dropping missing CustomerID: 406829 (Dropped 135080)
Simulating 2025 Data: Shifting dates...
Filtering data between 2024-08-12 and 2025-08-12...
Filtering invalid quantities and prices...
Rows after filtering: 384529
Extracting Customer Dimension...
Extracting Time Dimension...
Extracting Product Dimension...
Preparing Sales Fact Table...

--- LOAD PHASE ---
Loading CustomerDim...
Loading ProductDim...
Loading TimeDim...
Loading SalesFact...
Data Loading Complete.

--- VISUALIZATION PHASE ---
Visualization saved to: C:\Users\Admin\Documents\GitHub\DSA-2040_Practical_Exam_Bophine_Arnold_Odiyo_821\DataWarehousing\..\sales_by_country.png

ETL Process Completed Successfully.
```

### 4.1 Log Analysis
*   **Data Volume**: The system started with **541,909 raw rows**.
*   **Quality Control**: **135,080 rows** were removed immediately due to missing Customer IDs. This is a significant finding: ~25% of the raw data was unassignable to specific customers. 
*   **Temporal Filtering**: After shifting dates and filtering for the 'Last Year' (2024-2025) and valid transactions, **384,529 rows** were loaded into the Fact Table.
*   **Environment Note**: An initial attempt failed due to a missing `matplotlib` library in the default Python environment. This was resolved by switching to the correct Python 3 environment where all data science libraries (pandas, seaborn, matplotlib) are installed.

---

## 5. OLAP Analysis and Insights

With the Warehouse populated, we performed Online Analytical Processing (OLAP) to derive business value.

### 5.1 Query Strategy
The following OLAP operations were scripted in `olap_queries.sql`:
1.  **Roll-Up**: Aggregating sales from the Day level up to the Quarter and Year level, grouped by Country. This provides the high-level strategic view for executives.
2.  **Drill-Down**: Accessing granular monthly and daily data for the **United Kingdom** to identify micro-trends within the year.
3.  **Slice**: Isolating a specific market segment (Products with 'HEART' in the description) to analyze performance in a specific niche.

### 5.2 Key Findings
1.  **Geographic Dominance**:
    The visualization (see below) clearly indicates that the **United Kingdom** is the overwhelming market leader. Its sales volume is orders of magnitude higher than the second-place country (Netherlands or EIRE depending on the slice). This suggests the company is domestic-focused or has a specific logistical advantage in the UK.
    
    *Recommendation*: Marketing efforts should focus on international expansion (cross-border trade) to reduce dependency on the UK market, given the huge disparity.

2.  **Seasonality (from Drill-Down)**:
    The drill-down analysis into monthly sales reveals strong seasonality. Peaks are observed in the months corresponding to Q4 (simulated late 2024), aligning with typical retail patterns (Black Friday, Christmas).
    
    *Recommendation*: Inventory management must ramp up stock levels 3 months prior to these peaks to prevent stockouts, which are costly given the high volume.

3.  **Niche Performance**:
    The "Heart" product slice showed that sentimental items maintain consistent sales, but are highly concentrated in specific regions. This granular visibility allows for targeted inventory distribution—sending more gift-related stock to regions with high affinity for these categories.

### 5.3 Visualization
The automated visualization script generated the following insight:

**Figure 1: Top 10 Countries by Total Sales (2024-2025)**
*(Refer to `sales_by_country.png` in the project root)*

The bar chart confirms the "Long Tail" distribution of sales: one dominant leader followed by a rapid drop-off. This visual is crucial for stakeholders to immediately grasp the geographic risk concentration.

---

## 6. Conclusion and Future Work

Section 1 of the DSA 2040 Practical Exam has been successfully delivered. A robust Data Warehouse is now in place, populated with clean, relevant, and simulated current-year data.

*   **Success Criteria Met**:
    *   Star Schema implementing 3 Dimensions and 1 Fact Table.
    *   Automated ETL Pipeline handling 380k+ records.
    *   Demonstrated OLAP capability with SQL.
    *   Visual reporting integration.

*   **Future Improvements**:
    *   **Incremental Loading**: The current ETL replaces/appends data. For a production system, implementing a "Watermarking" strategy (loading only new rows based on `last_updated` timestamp) would be more efficient.
    *   **Slowly Changing Dimensions (SCD)**: Currently, customer attributes are overwritten. Implementing SCD Type 2 would allow tracking customer changes (e.g., moving countries) over time.

This foundation is now ready for **Step 2: Data Mining**, where we will apply advanced algorithms (Clustering, Association Rules) to this structured data to uncover hidden patterns beyond what standard SQL aggregation can reveal.
