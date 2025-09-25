# QADEE2798 Query Builder Templates

This document provides query templates for common database operations.

## Inventory Queries

### Inventory Levels

```sql
-- Get current inventory levels for specific parts
SELECT 
    in_part AS 'Part Number',
    in_site AS 'Site',
    in_qty_oh AS 'On Hand Qty',
    in_qty_avail AS 'Available Qty',
    in_qty_all AS 'Allocated Qty',
    in_qty_ord AS 'Ordered Qty'
FROM 
    [QADEE2798].[dbo].[15]
WHERE 
    in_part IN ('PART1', 'PART2', 'PART3')
    -- AND in_site = 'SITE'
ORDER BY 
    in_part, in_site
```

### Low Inventory Alert

```sql
-- Find parts with inventory below reorder point
SELECT 
    i.in_part AS 'Part Number',
    i.in_site AS 'Site',
    p.pt_desc1 AS 'Description',
    i.in_qty_oh AS 'On Hand Qty',
    i.in_rop AS 'Reorder Point',
    i.in_sfty_stk AS 'Safety Stock',
    i.in_rop - i.in_qty_oh AS 'Shortage'
FROM 
    [QADEE2798].[dbo].[15] i
LEFT JOIN 
    [QADEE2798].[dbo].[pt_mstr] p ON i.in_part = p.pt_part
WHERE 
    i.in_qty_oh < i.in_rop
    -- AND i.in_site = 'SITE'
ORDER BY 
    (i.in_rop - i.in_qty_oh) DESC
```

## Transaction History

### Recent Transactions

```sql
-- Get recent transactions for a specific part
SELECT 
    tr_part AS 'Part Number',
    tr_site AS 'Site',
    tr_date AS 'Transaction Date',
    tr_type AS 'Transaction Type',
    tr_qty_loc AS 'Quantity',
    tr_um AS 'Unit of Measure',
    tr_ref AS 'Reference',
    tr_nbr AS 'Transaction Number'
FROM 
    [QADEE2798].[dbo].[tr_hist]
WHERE 
    tr_part = 'PART_NUMBER'
    -- AND tr_site = 'SITE'
    AND tr_date >= DATEADD(day, -30, GETDATE()) -- Last 30 days
ORDER BY 
    tr_date DESC
```

### Transaction Summary

```sql
-- Get transaction summary by type for a specific part
SELECT 
    tr_part AS 'Part Number',
    tr_type AS 'Transaction Type',
    COUNT(*) AS 'Transaction Count',
    SUM(tr_qty_loc) AS 'Total Quantity',
    MIN(tr_date) AS 'First Transaction',
    MAX(tr_date) AS 'Last Transaction'
FROM 
    [QADEE2798].[dbo].[tr_hist]
WHERE 
    tr_part = 'PART_NUMBER'
    AND tr_date >= DATEADD(month, -3, GETDATE()) -- Last 3 months
GROUP BY 
    tr_part, tr_type
ORDER BY 
    tr_part, tr_type
```

## Sales Orders

### Open Sales Orders

```sql
-- Get open sales orders with details
SELECT 
    so.so_nbr AS 'Order Number',
    so.so_cust AS 'Customer',
    ad.ad_name AS 'Customer Name',
    so.so_ord_date AS 'Order Date',
    so.so_due_date AS 'Due Date',
    sod.sod_line AS 'Line',
    sod.sod_part AS 'Part Number',
    pt.pt_desc1 AS 'Description',
    sod.sod_qty_ord AS 'Ordered Qty',
    sod.sod_qty_ship AS 'Shipped Qty',
    sod.sod_price AS 'Price'
FROM 
    [QADEE2798].[dbo].[so_mstr] so
JOIN 
    [QADEE2798].[dbo].[sod_det] sod ON so.so_nbr = sod.sod_nbr
LEFT JOIN 
    [QADEE2798].[dbo].[ad_mstr] ad ON so.so_cust = ad.ad_addr
LEFT JOIN 
    [QADEE2798].[dbo].[pt_mstr] pt ON sod.sod_part = pt.pt_part
WHERE 
    sod.sod_qty_ord > sod.sod_qty_ship
    -- AND so.so_cust = 'CUSTOMER'
ORDER BY 
    so.so_due_date
```

