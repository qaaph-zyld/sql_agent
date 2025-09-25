# Sample Query Documentation

*Last updated: 2025-06-04*

## Overview

This document provides a comprehensive collection of sample queries for the SQL Agent system. These examples demonstrate various capabilities of the system and serve as a reference for users to create their own queries.

## Basic Queries

### Simple Selection

**Natural Language Query:**
```
Show me all employees in the Sales department.
```

**Generated SQL:**
```sql
SELECT * 
FROM employees 
WHERE department = 'Sales';
```

**Description:**
This query retrieves all columns for employees who belong to the Sales department.

### Filtered Selection

**Natural Language Query:**
```
List the names and salaries of employees who earn more than $75,000.
```

**Generated SQL:**
```sql
SELECT employee_name, salary 
FROM employees 
WHERE salary > 75000;
```

**Description:**
This query retrieves only the name and salary columns for employees with salaries exceeding $75,000.

### Sorting Results

**Natural Language Query:**
```
Show me all products sorted by price from highest to lowest.
```

**Generated SQL:**
```sql
SELECT * 
FROM products 
ORDER BY price DESC;
```

**Description:**
This query retrieves all product information and sorts the results by price in descending order.

## Intermediate Queries

### Aggregation

**Natural Language Query:**
```
What is the average salary by department?
```

**Generated SQL:**
```sql
SELECT department, AVG(salary) as average_salary 
FROM employees 
GROUP BY department;
```

**Description:**
This query calculates the average salary for each department and groups the results by department.

### Joining Tables

**Natural Language Query:**
```
Show me customer names and their order dates.
```

**Generated SQL:**
```sql
SELECT c.customer_name, o.order_date 
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id;
```

**Description:**
This query joins the customers and orders tables to display customer names alongside their order dates.

### Subqueries

**Natural Language Query:**
```
Find employees who earn more than the average salary.
```

**Generated SQL:**
```sql
SELECT employee_name, salary 
FROM employees 
WHERE salary > (SELECT AVG(salary) FROM employees);
```

**Description:**
This query uses a subquery to calculate the average salary and then finds employees whose salaries exceed that average.

## Advanced Queries

### Complex Joins

**Natural Language Query:**
```
Show me customers who have placed orders for products in the 'Electronics' category.
```

**Generated SQL:**
```sql
SELECT DISTINCT c.customer_id, c.customer_name 
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id
WHERE p.category = 'Electronics';
```

**Description:**
This query joins multiple tables to find customers who have ordered products in the Electronics category.

### Window Functions

**Natural Language Query:**
```
Rank employees by salary within each department.
```

**Generated SQL:**
```sql
SELECT 
    employee_name, 
    department, 
    salary,
    RANK() OVER (PARTITION BY department ORDER BY salary DESC) as salary_rank
FROM employees;
```

**Description:**
This query uses window functions to rank employees within their departments based on salary.

### Common Table Expressions (CTEs)

**Natural Language Query:**
```
Find customers who have spent more than $1000 in total.
```

**Generated SQL:**
```sql
WITH customer_spending AS (
    SELECT 
        c.customer_id, 
        c.customer_name, 
        SUM(oi.quantity * p.price) as total_spent
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    JOIN order_items oi ON o.order_id = oi.order_id
    JOIN products p ON oi.product_id = p.product_id
    GROUP BY c.customer_id, c.customer_name
)
SELECT customer_id, customer_name, total_spent
FROM customer_spending
WHERE total_spent > 1000
ORDER BY total_spent DESC;
```

**Description:**
This query uses a Common Table Expression (CTE) to calculate total spending for each customer and then filters for those who have spent more than $1000.

## Data Analysis Queries

### Time Series Analysis

**Natural Language Query:**
```
Show me monthly sales totals for the past year.
```

**Generated SQL:**
```sql
SELECT 
    DATE_TRUNC('month', o.order_date) as month,
    SUM(oi.quantity * p.price) as monthly_sales
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id
WHERE o.order_date >= CURRENT_DATE - INTERVAL '1 year'
GROUP BY DATE_TRUNC('month', o.order_date)
ORDER BY month;
```

**Description:**
This query aggregates sales data by month for the past year, showing monthly sales totals.

### Cohort Analysis

**Natural Language Query:**
```
Analyze customer retention by signup month.
```

**Generated SQL:**
```sql
WITH cohorts AS (
    SELECT 
        customer_id,
        DATE_TRUNC('month', signup_date) as cohort_month,
        DATE_TRUNC('month', order_date) as order_month
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
),
cohort_size AS (
    SELECT cohort_month, COUNT(DISTINCT customer_id) as num_customers
    FROM cohorts
    GROUP BY cohort_month
),
retention AS (
    SELECT 
        c.cohort_month,
        c.order_month,
        COUNT(DISTINCT c.customer_id) as num_customers,
        EXTRACT(MONTH FROM c.order_month) - EXTRACT(MONTH FROM c.cohort_month) as months_since_signup
    FROM cohorts c
    GROUP BY c.cohort_month, c.order_month
)
SELECT 
    r.cohort_month,
    r.months_since_signup,
    r.num_customers,
    cs.num_customers as original_cohort_size,
    ROUND(r.num_customers::numeric / cs.num_customers, 2) as retention_rate
FROM retention r
JOIN cohort_size cs ON r.cohort_month = cs.cohort_month
WHERE r.months_since_signup >= 0
ORDER BY r.cohort_month, r.months_since_signup;
```

**Description:**
This query performs a cohort analysis to track customer retention rates based on the month they signed up.

### Funnel Analysis

**Natural Language Query:**
```
Show me the conversion funnel from page view to purchase.
```

**Generated SQL:**
```sql
WITH funnel_stages AS (
    SELECT 
        user_id,
        MAX(CASE WHEN event_type = 'page_view' THEN 1 ELSE 0 END) as viewed,
        MAX(CASE WHEN event_type = 'add_to_cart' THEN 1 ELSE 0 END) as added_to_cart,
        MAX(CASE WHEN event_type = 'checkout' THEN 1 ELSE 0 END) as checked_out,
        MAX(CASE WHEN event_type = 'purchase' THEN 1 ELSE 0 END) as purchased
    FROM user_events
    WHERE event_date >= CURRENT_DATE - INTERVAL '30 days'
    GROUP BY user_id
)
SELECT 
    SUM(viewed) as viewed_count,
    SUM(added_to_cart) as added_to_cart_count,
    SUM(checked_out) as checked_out_count,
    SUM(purchased) as purchased_count,
    ROUND(SUM(added_to_cart)::numeric / SUM(viewed), 3) as view_to_cart_rate,
    ROUND(SUM(checked_out)::numeric / SUM(added_to_cart), 3) as cart_to_checkout_rate,
    ROUND(SUM(purchased)::numeric / SUM(checked_out), 3) as checkout_to_purchase_rate,
    ROUND(SUM(purchased)::numeric / SUM(viewed), 3) as overall_conversion_rate
FROM funnel_stages;
```

**Description:**
This query analyzes the conversion funnel from page view to purchase, showing counts and conversion rates at each stage.

## Specialized Queries

### Geographic Analysis

**Natural Language Query:**
```
Show me sales totals by country for Q1 2025.
```

**Generated SQL:**
```sql
SELECT 
    c.country,
    SUM(oi.quantity * p.price) as total_sales
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id
WHERE o.order_date BETWEEN '2025-01-01' AND '2025-03-31'
GROUP BY c.country
ORDER BY total_sales DESC;
```

**Description:**
This query aggregates sales data by customer country for the first quarter of 2025.

### Product Performance

**Natural Language Query:**
```
Which products have the highest profit margin?
```

**Generated SQL:**
```sql
SELECT 
    product_name,
    price,
    cost,
    price - cost as profit,
    ROUND((price - cost) / price * 100, 2) as profit_margin_percentage
FROM products
ORDER BY profit_margin_percentage DESC
LIMIT 10;
```

**Description:**
This query calculates profit margins for products and ranks them from highest to lowest.

### Customer Segmentation

**Natural Language Query:**
```
Segment customers by total spending into high, medium, and low value.
```

**Generated SQL:**
```sql
WITH customer_spending AS (
    SELECT 
        c.customer_id,
        c.customer_name,
        SUM(oi.quantity * p.price) as total_spent
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    JOIN order_items oi ON o.order_id = oi.order_id
    JOIN products p ON oi.product_id = p.product_id
    GROUP BY c.customer_id, c.customer_name
),
spending_percentiles AS (
    SELECT 
        customer_id,
        customer_name,
        total_spent,
        NTILE(3) OVER (ORDER BY total_spent) as spending_tier
    FROM customer_spending
)
SELECT 
    customer_id,
    customer_name,
    total_spent,
    CASE 
        WHEN spending_tier = 1 THEN 'Low Value'
        WHEN spending_tier = 2 THEN 'Medium Value'
        WHEN spending_tier = 3 THEN 'High Value'
    END as customer_segment
FROM spending_percentiles
ORDER BY total_spent DESC;
```

**Description:**
This query segments customers into high, medium, and low value based on their total spending.

## Performance-Optimized Queries

### Using Indexes

**Natural Language Query:**
```
Find recent orders for customer ID 12345 with optimized performance.
```

**Generated SQL:**
```sql
-- Assumes indexes on customer_id and order_date
SELECT o.order_id, o.order_date, o.total_amount
FROM orders o
WHERE o.customer_id = 12345
  AND o.order_date >= CURRENT_DATE - INTERVAL '90 days'
ORDER BY o.order_date DESC
LIMIT 10;
```

**Description:**
This query is optimized to use indexes on customer_id and order_date for faster retrieval of recent orders.

### Pagination

**Natural Language Query:**
```
Show me page 3 of product results with 20 items per page.
```

**Generated SQL:**
```sql
SELECT product_id, product_name, price, category
FROM products
ORDER BY product_name
LIMIT 20 OFFSET 40;
```

**Description:**
This query implements pagination to efficiently retrieve the third page of product results with 20 items per page.

### Materialized Views

**Natural Language Query:**
```
Get the latest sales dashboard data using the materialized view.
```

**Generated SQL:**
```sql
-- Assumes a materialized view has been created
SELECT * FROM sales_dashboard_mv
WHERE report_date = CURRENT_DATE;
```

**Description:**
This query uses a materialized view to quickly retrieve pre-aggregated sales dashboard data.

## Security-Focused Queries

### Row-Level Security

**Natural Language Query:**
```
Show me only the orders for my department.
```

**Generated SQL:**
```sql
-- Assumes a session variable for department_id
SELECT o.order_id, o.order_date, c.customer_name
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
WHERE o.department_id = current_setting('app.current_department_id')::integer;
```

**Description:**
This query implements row-level security by filtering orders based on the user's department.

### Parameterized Queries

**Natural Language Query:**
```
Find products matching the user-provided category safely.
```

**Generated SQL:**
```sql
-- Parameterized query to prevent SQL injection
PREPARE product_search(text) AS
SELECT product_id, product_name, price
FROM products
WHERE category = $1;

EXECUTE product_search('Electronics');
```

**Description:**
This query uses parameterization to safely handle user input and prevent SQL injection attacks.

## Conclusion

These sample queries demonstrate the range of capabilities offered by the SQL Agent system. Users can adapt these examples to their specific needs or use them as templates for creating more complex queries.

For more information on query capabilities and optimization techniques, refer to the API documentation and user guide.
