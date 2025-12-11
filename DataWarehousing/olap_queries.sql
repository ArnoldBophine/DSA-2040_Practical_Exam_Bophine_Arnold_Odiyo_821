-- OLAP Queries for Data Warehousing Task 3
-- 3.1.1 Roll-Up Query
-- Goal: Total sales by Country and Quarter (Aggregating up from Time/Customer dims)
-- Note: SQLite doesn't support CUBE/ROLLUP standard syntax perfectly, using GROUP BY
SELECT 
    c.country,
    t.year,
    t.quarter,
    SUM(f.total_sales) as total_sales
FROM SalesFact f
JOIN CustomerDim c ON f.customer_id = c.customer_id
JOIN TimeDim t ON f.time_id = t.time_id
GROUP BY c.country, t.year, t.quarter
ORDER BY c.country, t.year, t.quarter;

-- 3.1.2 Drill-Down Query
-- Goal: Sales details for specific country (United Kingdom) by Month for a specific Year (to go deeper than quarter)
SELECT 
    t.month,
    t.day,
    p.description,
    SUM(f.quantity) as total_quantity,
    SUM(f.total_sales) as monthly_sales
FROM SalesFact f
JOIN CustomerDim c ON f.customer_id = c.customer_id
JOIN TimeDim t ON f.time_id = t.time_id
JOIN ProductDim p ON f.product_id = p.product_id
WHERE c.country = 'United Kingdom' AND t.year = 2011
GROUP BY t.month, t.day, p.description
ORDER BY t.month, t.day, total_quantity DESC
LIMIT 50; -- Limit results for readability

-- 3.1.3 Slice Query
-- Goal: Total sales for specific product category (Simulated by filtering Description)
-- Slicing the cube by Product = 'HEART' related items
SELECT 
    c.country,
    SUM(f.total_sales) as heart_items_sales
FROM SalesFact f
JOIN ProductDim p ON f.product_id = p.product_id
JOIN CustomerDim c ON f.customer_id = c.customer_id
WHERE p.description LIKE '%HEART%'
GROUP BY c.country
ORDER BY heart_items_sales DESC;
