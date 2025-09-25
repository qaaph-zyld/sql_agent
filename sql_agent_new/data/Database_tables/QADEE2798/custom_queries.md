# Custom SQL Queries Documentation

This document provides documentation for custom SQL queries used with the QADEE2798 database.

## Table of Contents

- [Queries](#queries)
  - [Customer_Demand_per_BOM](#query-customer_demand_per_bom)
  - [Item_Master_all_no_xc_rc](#query-item_master_all_no_xc_rc)
  - [MMV](#query-mmv)
- [Business Processes](#business-processes)
  - [Sales Order Processing](#process-sales-order-processing)
  - [Item Master](#process-item-master)
  - [Inventory Management](#process-inventory-management)

## Queries

### Customer_Demand_per_BOM <a name="query-customer_demand_per_bom"></a>

**Business Process:** Sales Order Processing

**Tables Used:**

- [so_mstr](dbo.so_mstr/so_mstr_field_names.md)
- [sch_mstr](dbo.sch_mstr/sch_mstr_field_names.md)
- [ps_mstr](dbo.ps_mstr/ps_mstr_field_names.md)
- [sod_det](dbo.sod_det/sod_det_field_names.md)
- [active_schd_det](dbo.active_schd_det/active_schd_det_field_names.md)

[View SQL File](custom_sql_queries/Customer_Demand_per_BOM.sql)

### Item_Master_all_no_xc_rc <a name="query-item_master_all_no_xc_rc"></a>

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

### MMV <a name="query-mmv"></a>

**Business Process:** Inventory Management

**Tables Used:**

- [tr_hist](dbo.tr_hist/tr_hist_field_names.md)

[View SQL File](custom_sql_queries/MMV.sql)


## Business Processes

### Sales Order Processing <a name="process-sales-order-processing"></a>

**Queries:**

- [Customer_Demand_per_BOM](#query-customer_demand_per_bom)

**Tables:**

- [so_mstr](dbo.so_mstr/so_mstr_field_names.md)
- [sch_mstr](dbo.sch_mstr/sch_mstr_field_names.md)
- [ps_mstr](dbo.ps_mstr/ps_mstr_field_names.md)
- [sod_det](dbo.sod_det/sod_det_field_names.md)
- [active_schd_det](dbo.active_schd_det/active_schd_det_field_names.md)

### Item Master <a name="process-item-master"></a>

**Queries:**

- [Item_Master_all_no_xc_rc](#query-item_master_all_no_xc_rc)

**Tables:**

- [ld_det](dbo.ld_det/ld_det_field_names.md)
- [sct_det](dbo.sct_det/sct_det_field_names.md)
- [tr_hist](dbo.tr_hist/tr_hist_field_names.md)
- [xxwezoned_det](dbo.xxwezoned_det/xxwezoned_det_field_names.md)
- [15](dbo.15/15_field_names.md)
- [ps_mstr](dbo.ps_mstr/ps_mstr_field_names.md)
- [pt_mstr](dbo.pt_mstr/pt_mstr_field_names.md)
- [in_mstr](dbo.in_mstr/in_mstr_field_names.md)

### Inventory Management <a name="process-inventory-management"></a>

**Queries:**

- [MMV](#query-mmv)

**Tables:**

- [tr_hist](dbo.tr_hist/tr_hist_field_names.md)

