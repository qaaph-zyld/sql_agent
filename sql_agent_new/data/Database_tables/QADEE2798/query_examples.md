# Query Examples for QADEE2798 Database

This document provides example queries that demonstrate how to work with the QADEE2798 database.

## Inventory and Transaction History

```sql
-- Get inventory and recent transactions for a specific part
SELECT 
    i.in_part,
    i.in_site,
    i.in_qty_oh AS 'On Hand Qty',
    i.in_qty_avail AS 'Available Qty',
    t.tr_date AS 'Transaction Date',
    t.tr_type AS 'Transaction Type',
    t.tr_qty_loc AS 'Transaction Qty'
FROM 
    [QADEE2798].[dbo].[15] i
LEFT JOIN 
    [QADEE2798].[dbo].[tr_hist] t ON i.in_part = t.tr_part AND i.in_site = t.tr_site
WHERE 
    i.in_part = 'PART_NUMBER'
ORDER BY 
    t.tr_date DESC
```

## Sales Orders and Details

```sql
-- Get sales orders with details and customer information
SELECT 
    so.so_nbr AS 'Order Number',
    so.so_cust AS 'Customer',
    ad.ad_name AS 'Customer Name',
    so.so_ord_date AS 'Order Date',
    sod.sod_part AS 'Part Number',
    sod.sod_qty_ord AS 'Ordered Qty',
    sod.sod_price AS 'Price'
FROM 
    [QADEE2798].[dbo].[so_mstr] so
JOIN 
    [QADEE2798].[dbo].[sod_det] sod ON so.so_nbr = sod.sod_nbr
LEFT JOIN 
    [QADEE2798].[dbo].[ad_mstr] ad ON so.so_cust = ad.ad_addr
ORDER BY 
    so.so_ord_date DESC
```

## Purchase Orders and Vendors

```sql
-- Get purchase orders with vendor information
SELECT 
    po.po_nbr AS 'PO Number',
    po.po_vend AS 'Vendor Code',
    vd.vd_name AS 'Vendor Name',
    po.po_ord_date AS 'Order Date',
    pod.pod_part AS 'Part Number',
    pod.pod_qty_ord AS 'Ordered Qty'
FROM 
    [QADEE2798].[dbo].[po_mstr] po
JOIN 
    [QADEE2798].[dbo].[pod_det] pod ON po.po_nbr = pod.pod_nbr
LEFT JOIN 
    [QADEE2798].[dbo].[vd_mstr] vd ON po.po_vend = vd.vd_addr
ORDER BY 
    po.po_ord_date DESC
```

## Production Scheduling

```sql
-- Get active production schedules
SELECT 
    s.schd_nbr AS 'Schedule Number',
    s.schd_line AS 'Line',
    s.schd_date AS 'Schedule Date',
    s.schd_discr_qty AS 'Discrete Qty',
    s.schd_cum_qty AS 'Cumulative Qty',
    i.in_qty_oh AS 'On Hand Qty',
    i.in_qty_avail AS 'Available Qty'
FROM 
    [QADEE2798].[dbo].[active_schd_det] s
LEFT JOIN 
    [QADEE2798].[dbo].[15] i ON s.schd_part = i.in_part
WHERE 
    s.schd_date >= GETDATE()
ORDER BY 
    s.schd_date
```
