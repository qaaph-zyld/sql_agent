# QADEE2798 Data Lineage Documentation

This document provides comprehensive data lineage information for the QADEE2798 database.

## Master Data Flow Diagram

![Master Data Flow Diagram](master_data_flow.png)

## Business Processes

### Inventory Management

Tracks inventory levels, movements, and adjustments

![Inventory Management Data Flow](data_flow_inventory_management.png)

#### Tables Involved

- [15](dbo.15/15_field_names.md): Inventory Master - Contains inventory quantities and status information
- [tr_hist](dbo.tr_hist/tr_hist_field_names.md): Transaction History - Contains historical transaction information

#### Data Flows

| Source Table | Target Table | Description |
|--------------|--------------|-------------|
| [tr_hist](dbo.tr_hist/tr_hist_field_names.md) | [15](dbo.15/15_field_names.md) | Inventory transactions update inventory levels |

#### Example Query

```sql
-- Inventory Management Query Example
SELECT 
    i.in_part AS 'Part Number',
    i.in_site AS 'Site',
    i.in_qty_oh AS 'On Hand Qty',
    t.tr_date AS 'Last Transaction Date',
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

### Sales Order Processing

Manages sales orders from creation to fulfillment

![Sales Order Processing Data Flow](data_flow_sales_order_processing.png)

#### Tables Involved

- [so_mstr](dbo.so_mstr/so_mstr_field_names.md): Sales Order Master - Contains header information for sales orders
- [sod_det](dbo.sod_det/sod_det_field_names.md): Sales Order Detail - Contains line item details for sales orders
- [15](dbo.15/15_field_names.md): Inventory Master - Contains inventory quantities and status information
- [tr_hist](dbo.tr_hist/tr_hist_field_names.md): Transaction History - Contains historical transaction information
- [ad_mstr](dbo.ad_mstr/ad_mstr_field_names.md): Address Master - Contains address information for customers and vendors

#### Data Flows

| Source Table | Target Table | Description |
|--------------|--------------|-------------|
| [so_mstr](dbo.so_mstr/so_mstr_field_names.md) | [sod_det](dbo.sod_det/sod_det_field_names.md) | Sales order header to detail |
| [sod_det](dbo.sod_det/sod_det_field_names.md) | [tr_hist](dbo.tr_hist/tr_hist_field_names.md) | Sales order fulfillment creates transactions |
| [tr_hist](dbo.tr_hist/tr_hist_field_names.md) | [15](dbo.15/15_field_names.md) | Transactions update inventory levels |
| [ad_mstr](dbo.ad_mstr/ad_mstr_field_names.md) | [so_mstr](dbo.so_mstr/so_mstr_field_names.md) | Customer information for sales orders |

#### Example Query

```sql
-- Sales Order Processing Query Example
SELECT 
    so.so_nbr AS 'Order Number',
    so.so_cust AS 'Customer',
    ad.ad_name AS 'Customer Name',
    so.so_ord_date AS 'Order Date',
    sod.sod_part AS 'Part Number',
    sod.sod_qty_ord AS 'Ordered Qty',
    i.in_qty_oh AS 'On Hand Qty',
    t.tr_date AS 'Transaction Date'
FROM 
    [QADEE2798].[dbo].[so_mstr] so
JOIN 
    [QADEE2798].[dbo].[sod_det] sod ON so.so_nbr = sod.sod_nbr
LEFT JOIN 
    [QADEE2798].[dbo].[ad_mstr] ad ON so.so_cust = ad.ad_addr
LEFT JOIN 
    [QADEE2798].[dbo].[15] i ON sod.sod_part = i.in_part
LEFT JOIN 
    [QADEE2798].[dbo].[tr_hist] t ON sod.sod_part = t.tr_part AND t.tr_nbr = so.so_nbr
WHERE 
    so.so_nbr = 'ORDER_NUMBER'
```

### Purchase Order Processing

Manages purchase orders from creation to receipt

![Purchase Order Processing Data Flow](data_flow_purchase_order_processing.png)

#### Tables Involved

- [po_mstr](dbo.po_mstr/po_mstr_field_names.md): Purchase Order Master - Contains header information for purchase orders
- [pod_det](dbo.pod_det/pod_det_field_names.md): Purchase Order Detail - Contains line item details for purchase orders
- [15](dbo.15/15_field_names.md): Inventory Master - Contains inventory quantities and status information
- [tr_hist](dbo.tr_hist/tr_hist_field_names.md): Transaction History - Contains historical transaction information
- [vd_mstr](dbo.vd_mstr/vd_mstr_field_names.md): Vendor Master - Contains vendor information

#### Data Flows

| Source Table | Target Table | Description |
|--------------|--------------|-------------|
| [po_mstr](dbo.po_mstr/po_mstr_field_names.md) | [pod_det](dbo.pod_det/pod_det_field_names.md) | Purchase order header to detail |
| [pod_det](dbo.pod_det/pod_det_field_names.md) | [tr_hist](dbo.tr_hist/tr_hist_field_names.md) | Purchase order receipt creates transactions |
| [tr_hist](dbo.tr_hist/tr_hist_field_names.md) | [15](dbo.15/15_field_names.md) | Transactions update inventory levels |
| [vd_mstr](dbo.vd_mstr/vd_mstr_field_names.md) | [po_mstr](dbo.po_mstr/po_mstr_field_names.md) | Vendor information for purchase orders |

#### Example Query

```sql
-- Purchase Order Processing Query Example
SELECT * FROM [QADEE2798].[dbo].[po_mstr] JOIN [QADEE2798].[dbo].[pod_det]
WHERE 1=1
```

### Production Scheduling

Manages production schedules and work orders

![Production Scheduling Data Flow](data_flow_production_scheduling.png)

#### Tables Involved

- [sch_mstr](dbo.sch_mstr/sch_mstr_field_names.md): Schedule Master - Contains header information for production schedules
- [active_schd_det](dbo.active_schd_det/active_schd_det_field_names.md): Active Schedule Details - Contains active schedule information
- [sct_det](dbo.sct_det/sct_det_field_names.md): Schedule Transaction Detail - Contains transaction details for schedules
- [15](dbo.15/15_field_names.md): Inventory Master - Contains inventory quantities and status information
- [tr_hist](dbo.tr_hist/tr_hist_field_names.md): Transaction History - Contains historical transaction information
- [pt_mstr](dbo.pt_mstr/pt_mstr_field_names.md): Part Master - Contains part information including costs and classifications

#### Data Flows

| Source Table | Target Table | Description |
|--------------|--------------|-------------|
| [sch_mstr](dbo.sch_mstr/sch_mstr_field_names.md) | [active_schd_det](dbo.active_schd_det/active_schd_det_field_names.md) | Schedule header to active detail |
| [active_schd_det](dbo.active_schd_det/active_schd_det_field_names.md) | [sct_det](dbo.sct_det/sct_det_field_names.md) | Schedule execution creates transactions |
| [sct_det](dbo.sct_det/sct_det_field_names.md) | [tr_hist](dbo.tr_hist/tr_hist_field_names.md) | Schedule transactions update history |
| [tr_hist](dbo.tr_hist/tr_hist_field_names.md) | [15](dbo.15/15_field_names.md) | Transactions update inventory levels |
| [pt_mstr](dbo.pt_mstr/pt_mstr_field_names.md) | [sch_mstr](dbo.sch_mstr/sch_mstr_field_names.md) | Part information for scheduling |

#### Example Query

```sql
-- Production Scheduling Query Example
SELECT * FROM [QADEE2798].[dbo].[sch_mstr] JOIN [QADEE2798].[dbo].[active_schd_det]
WHERE 1=1
```

### Serial Number Tracking

Tracks serialized items throughout their lifecycle

![Serial Number Tracking Data Flow](data_flow_serial_tracking.png)

#### Tables Involved

- [ser_item_detail](dbo.ser_item_detail/ser_item_detail_field_names.md): Serial Item Detail - Contains details about serialized items
- [ser_active_picked](dbo.ser_active_picked/ser_active_picked_field_names.md): Serial Active Picked - Contains information about picked serialized items
- [serh_hist](dbo.serh_hist/serh_hist_field_names.md): Serial History - Contains historical information about serialized items
- [tr_hist](dbo.tr_hist/tr_hist_field_names.md): Transaction History - Contains historical transaction information

#### Data Flows

| Source Table | Target Table | Description |
|--------------|--------------|-------------|
| [ser_item_detail](dbo.ser_item_detail/ser_item_detail_field_names.md) | [ser_active_picked](dbo.ser_active_picked/ser_active_picked_field_names.md) | Serial items to picked status |
| [ser_active_picked](dbo.ser_active_picked/ser_active_picked_field_names.md) | [serh_hist](dbo.serh_hist/serh_hist_field_names.md) | Active serials to history |
| [serh_hist](dbo.serh_hist/serh_hist_field_names.md) | [tr_hist](dbo.tr_hist/tr_hist_field_names.md) | Serial history linked to transactions |

#### Example Query

```sql
-- Serial Number Tracking Query Example
SELECT * FROM [QADEE2798].[dbo].[ser_item_detail] JOIN [QADEE2798].[dbo].[ser_active_picked]
WHERE 1=1
```

### Shipping and Logistics

Manages shipping, loads, and deliveries

![Shipping and Logistics Data Flow](data_flow_shipping_and_logistics.png)

#### Tables Involved

- [ld_det](dbo.ld_det/ld_det_field_names.md): Load Details - Contains details about shipment loads
- [so_mstr](dbo.so_mstr/so_mstr_field_names.md): Sales Order Master - Contains header information for sales orders
- [sod_det](dbo.sod_det/sod_det_field_names.md): Sales Order Detail - Contains line item details for sales orders
- [tr_hist](dbo.tr_hist/tr_hist_field_names.md): Transaction History - Contains historical transaction information
- [ad_mstr](dbo.ad_mstr/ad_mstr_field_names.md): Address Master - Contains address information for customers and vendors

#### Data Flows

| Source Table | Target Table | Description |
|--------------|--------------|-------------|
| [so_mstr](dbo.so_mstr/so_mstr_field_names.md) | [ld_det](dbo.ld_det/ld_det_field_names.md) | Sales orders to load details |
| [sod_det](dbo.sod_det/sod_det_field_names.md) | [ld_det](dbo.ld_det/ld_det_field_names.md) | Sales order lines to load details |
| [ld_det](dbo.ld_det/ld_det_field_names.md) | [tr_hist](dbo.tr_hist/tr_hist_field_names.md) | Load shipment creates transactions |
| [ad_mstr](dbo.ad_mstr/ad_mstr_field_names.md) | [ld_det](dbo.ld_det/ld_det_field_names.md) | Address information for shipping |

#### Example Query

```sql
-- Shipping and Logistics Query Example
SELECT * FROM [QADEE2798].[dbo].[ld_det] JOIN [QADEE2798].[dbo].[so_mstr]
WHERE 1=1
```

## Table Lineage

### 15

#### Incoming Data

| Source Table | Process | Description |
|--------------|---------|-------------|
| [tr_hist](dbo.tr_hist/tr_hist_field_names.md) | Inventory Management | Inventory transactions update inventory levels |
| [tr_hist](dbo.tr_hist/tr_hist_field_names.md) | Sales Order Processing | Transactions update inventory levels |
| [tr_hist](dbo.tr_hist/tr_hist_field_names.md) | Purchase Order Processing | Transactions update inventory levels |
| [tr_hist](dbo.tr_hist/tr_hist_field_names.md) | Production Scheduling | Transactions update inventory levels |

### active_schd_det

#### Incoming Data

| Source Table | Process | Description |
|--------------|---------|-------------|
| [sch_mstr](dbo.sch_mstr/sch_mstr_field_names.md) | Production Scheduling | Schedule header to active detail |

#### Outgoing Data

| Target Table | Process | Description |
|--------------|---------|-------------|
| [sct_det](dbo.sct_det/sct_det_field_names.md) | Production Scheduling | Schedule execution creates transactions |

### ad_mstr


#### Outgoing Data

| Target Table | Process | Description |
|--------------|---------|-------------|
| [so_mstr](dbo.so_mstr/so_mstr_field_names.md) | Sales Order Processing | Customer information for sales orders |
| [ld_det](dbo.ld_det/ld_det_field_names.md) | Shipping and Logistics | Address information for shipping |

### ld_det

#### Incoming Data

| Source Table | Process | Description |
|--------------|---------|-------------|
| [so_mstr](dbo.so_mstr/so_mstr_field_names.md) | Shipping and Logistics | Sales orders to load details |
| [sod_det](dbo.sod_det/sod_det_field_names.md) | Shipping and Logistics | Sales order lines to load details |
| [ad_mstr](dbo.ad_mstr/ad_mstr_field_names.md) | Shipping and Logistics | Address information for shipping |

#### Outgoing Data

| Target Table | Process | Description |
|--------------|---------|-------------|
| [tr_hist](dbo.tr_hist/tr_hist_field_names.md) | Shipping and Logistics | Load shipment creates transactions |

### po_mstr

#### Incoming Data

| Source Table | Process | Description |
|--------------|---------|-------------|
| [vd_mstr](dbo.vd_mstr/vd_mstr_field_names.md) | Purchase Order Processing | Vendor information for purchase orders |

#### Outgoing Data

| Target Table | Process | Description |
|--------------|---------|-------------|
| [pod_det](dbo.pod_det/pod_det_field_names.md) | Purchase Order Processing | Purchase order header to detail |

### pod_det

#### Incoming Data

| Source Table | Process | Description |
|--------------|---------|-------------|
| [po_mstr](dbo.po_mstr/po_mstr_field_names.md) | Purchase Order Processing | Purchase order header to detail |

#### Outgoing Data

| Target Table | Process | Description |
|--------------|---------|-------------|
| [tr_hist](dbo.tr_hist/tr_hist_field_names.md) | Purchase Order Processing | Purchase order receipt creates transactions |

### pt_mstr


#### Outgoing Data

| Target Table | Process | Description |
|--------------|---------|-------------|
| [sch_mstr](dbo.sch_mstr/sch_mstr_field_names.md) | Production Scheduling | Part information for scheduling |

### sch_mstr

#### Incoming Data

| Source Table | Process | Description |
|--------------|---------|-------------|
| [pt_mstr](dbo.pt_mstr/pt_mstr_field_names.md) | Production Scheduling | Part information for scheduling |

#### Outgoing Data

| Target Table | Process | Description |
|--------------|---------|-------------|
| [active_schd_det](dbo.active_schd_det/active_schd_det_field_names.md) | Production Scheduling | Schedule header to active detail |

### sct_det

#### Incoming Data

| Source Table | Process | Description |
|--------------|---------|-------------|
| [active_schd_det](dbo.active_schd_det/active_schd_det_field_names.md) | Production Scheduling | Schedule execution creates transactions |

#### Outgoing Data

| Target Table | Process | Description |
|--------------|---------|-------------|
| [tr_hist](dbo.tr_hist/tr_hist_field_names.md) | Production Scheduling | Schedule transactions update history |

### ser_active_picked

#### Incoming Data

| Source Table | Process | Description |
|--------------|---------|-------------|
| [ser_item_detail](dbo.ser_item_detail/ser_item_detail_field_names.md) | Serial Number Tracking | Serial items to picked status |

#### Outgoing Data

| Target Table | Process | Description |
|--------------|---------|-------------|
| [serh_hist](dbo.serh_hist/serh_hist_field_names.md) | Serial Number Tracking | Active serials to history |

### ser_item_detail


#### Outgoing Data

| Target Table | Process | Description |
|--------------|---------|-------------|
| [ser_active_picked](dbo.ser_active_picked/ser_active_picked_field_names.md) | Serial Number Tracking | Serial items to picked status |

### serh_hist

#### Incoming Data

| Source Table | Process | Description |
|--------------|---------|-------------|
| [ser_active_picked](dbo.ser_active_picked/ser_active_picked_field_names.md) | Serial Number Tracking | Active serials to history |

#### Outgoing Data

| Target Table | Process | Description |
|--------------|---------|-------------|
| [tr_hist](dbo.tr_hist/tr_hist_field_names.md) | Serial Number Tracking | Serial history linked to transactions |

### so_mstr

#### Incoming Data

| Source Table | Process | Description |
|--------------|---------|-------------|
| [ad_mstr](dbo.ad_mstr/ad_mstr_field_names.md) | Sales Order Processing | Customer information for sales orders |

#### Outgoing Data

| Target Table | Process | Description |
|--------------|---------|-------------|
| [sod_det](dbo.sod_det/sod_det_field_names.md) | Sales Order Processing | Sales order header to detail |
| [ld_det](dbo.ld_det/ld_det_field_names.md) | Shipping and Logistics | Sales orders to load details |

### sod_det

#### Incoming Data

| Source Table | Process | Description |
|--------------|---------|-------------|
| [so_mstr](dbo.so_mstr/so_mstr_field_names.md) | Sales Order Processing | Sales order header to detail |

#### Outgoing Data

| Target Table | Process | Description |
|--------------|---------|-------------|
| [tr_hist](dbo.tr_hist/tr_hist_field_names.md) | Sales Order Processing | Sales order fulfillment creates transactions |
| [ld_det](dbo.ld_det/ld_det_field_names.md) | Shipping and Logistics | Sales order lines to load details |

### tr_hist

#### Incoming Data

| Source Table | Process | Description |
|--------------|---------|-------------|
| [sod_det](dbo.sod_det/sod_det_field_names.md) | Sales Order Processing | Sales order fulfillment creates transactions |
| [pod_det](dbo.pod_det/pod_det_field_names.md) | Purchase Order Processing | Purchase order receipt creates transactions |
| [sct_det](dbo.sct_det/sct_det_field_names.md) | Production Scheduling | Schedule transactions update history |
| [serh_hist](dbo.serh_hist/serh_hist_field_names.md) | Serial Number Tracking | Serial history linked to transactions |
| [ld_det](dbo.ld_det/ld_det_field_names.md) | Shipping and Logistics | Load shipment creates transactions |

#### Outgoing Data

| Target Table | Process | Description |
|--------------|---------|-------------|
| [15](dbo.15/15_field_names.md) | Inventory Management | Inventory transactions update inventory levels |
| [15](dbo.15/15_field_names.md) | Sales Order Processing | Transactions update inventory levels |
| [15](dbo.15/15_field_names.md) | Purchase Order Processing | Transactions update inventory levels |
| [15](dbo.15/15_field_names.md) | Production Scheduling | Transactions update inventory levels |

### vd_mstr


#### Outgoing Data

| Target Table | Process | Description |
|--------------|---------|-------------|
| [po_mstr](dbo.po_mstr/po_mstr_field_names.md) | Purchase Order Processing | Vendor information for purchase orders |


## Custom SQL Queries

The following custom SQL queries provide additional insights into data flows and relationships:

### Customer_Demand_per_BOM

**Business Process:** Sales Order Processing

**Tables Used:**

- [so_mstr](dbo.so_mstr/so_mstr_field_names.md)
- [sch_mstr](dbo.sch_mstr/sch_mstr_field_names.md)
- [ps_mstr](dbo.ps_mstr/ps_mstr_field_names.md)
- [sod_det](dbo.sod_det/sod_det_field_names.md)
- [active_schd_det](dbo.active_schd_det/active_schd_det_field_names.md)

[View SQL File](custom_sql_queries/Customer_Demand_per_BOM.sql)

### Item_Master_all_no_xc_rc

**Business Process:** Item Master

**Tables Used:**

- [ld_det](dbo.ld_det/ld_det_field_names.md)
- [sct_det](dbo.sct_det/sct_det_field_names.md)
- [tr_hist](dbo.tr_hist/tr_hist_field_names.md)
- [15](dbo.15/15_field_names.md)
- [xxwezoned_det](dbo.xxwezoned_det/xxwezoned_det_field_names.md)
- [ps_mstr](dbo.ps_mstr/ps_mstr_field_names.md)
- [pt_mstr](dbo.pt_mstr/pt_mstr_field_names.md)
- [in_mstr](dbo.in_mstr/in_mstr_field_names.md)

[View SQL File](custom_sql_queries/Item_Master_all_no_xc_rc.sql)

### MMV

**Business Process:** Inventory Management

**Tables Used:**

- [tr_hist](dbo.tr_hist/tr_hist_field_names.md)

[View SQL File](custom_sql_queries/MMV.sql)

### Custom Query Diagram

![Custom SQL Queries and Table Relationships](custom_query_diagram.png)

