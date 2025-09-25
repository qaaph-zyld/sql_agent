# Database Summary: QADEE2798

## Tables (23)

- [15](dbo.15/15_field_names.md)
- [PreShipperShipper](dbo.PreShipperShipper/PreShipperShipper_field_names.md)
- [active_schd_det](dbo.active_schd_det/active_schd_det_field_names.md)
- [ad_mstr](dbo.ad_mstr/ad_mstr_field_names.md)
- [ld_det](dbo.ld_det/ld_det_field_names.md)
- [pckc_mstr](dbo.pckc_mstr/pckc_mstr_field_names.md)
- [picked_serial_link](dbo.picked_serial_link/picked_serial_link_field_names.md)
- [po_mstr](dbo.po_mstr/po_mstr_field_names.md)
- [pod_det](dbo.pod_det/pod_det_field_names.md)
- [ps_mstr](dbo.ps_mstr/ps_mstr_field_names.md)
- [pt_mstr](dbo.pt_mstr/pt_mstr_field_names.md)
- [ptpac_det](dbo.ptpac_det/ptpac_det_field_names.md)
- [ro_det](dbo.ro_det/ro_det_field_names.md)
- [sch_mstr](dbo.sch_mstr/sch_mstr_field_names.md)
- [sct_det](dbo.sct_det/sct_det_field_names.md)
- [ser_active_picked](dbo.ser_active_picked/ser_active_picked_field_names.md)
- [ser_item_detail](dbo.ser_item_detail/ser_item_detail_field_names.md)
- [serh_hist](dbo.serh_hist/serh_hist_field_names.md)
- [so_mstr](dbo.so_mstr/so_mstr_field_names.md)
- [sod_det](dbo.sod_det/sod_det_field_names.md)
- [tr_hist](dbo.tr_hist/tr_hist_field_names.md)
- [vd_mstr](dbo.vd_mstr/vd_mstr_field_names.md)
- [xxwezoned_det](dbo.xxwezoned_det/xxwezoned_det_field_names.md)

## Table Descriptions

| Table | Description | Primary Purpose |
|-------|-------------|----------------|
| [15](dbo.15/15_field_names.md) | Inventory Master | Contains inventory quantities and status information for items at specific sites |
| [active_schd_det](dbo.active_schd_det/active_schd_det_field_names.md) | Active Schedule Details | Contains active schedule information for production and shipping |
| [ad_mstr](dbo.ad_mstr/ad_mstr_field_names.md) | Address Master | Contains address information for customers, vendors, and other entities |
| [ld_det](dbo.ld_det/ld_det_field_names.md) | Load Details | Contains details about shipment loads |
| [pckc_mstr](dbo.pckc_mstr/pckc_mstr_field_names.md) | Pick Confirmation Master | Contains information about pick confirmations |
| [picked_serial_link](dbo.picked_serial_link/picked_serial_link_field_names.md) | Picked Serial Link | Links picked items to serial numbers |
| [po_mstr](dbo.po_mstr/po_mstr_field_names.md) | Purchase Order Master | Contains header information for purchase orders |
| [pod_det](dbo.pod_det/pod_det_field_names.md) | Purchase Order Detail | Contains line item details for purchase orders |
| [ps_mstr](dbo.ps_mstr/ps_mstr_field_names.md) | Product Structure Master | Contains bill of materials information |
| [pt_mstr](dbo.pt_mstr/pt_mstr_field_names.md) | Part Master | Contains part information including costs and classifications |
| [ptpac_det](dbo.ptpac_det/ptpac_det_field_names.md) | Part Package Detail | Contains packaging information for parts |
| [ro_det](dbo.ro_det/ro_det_field_names.md) | Release Order Detail | Contains details for release orders |
| [sch_mstr](dbo.sch_mstr/sch_mstr_field_names.md) | Schedule Master | Contains header information for production schedules |
| [sct_det](dbo.sct_det/sct_det_field_names.md) | Schedule Transaction Detail | Contains transaction details for schedules |
| [ser_active_picked](dbo.ser_active_picked/ser_active_picked_field_names.md) | Serial Active Picked | Contains information about picked serialized items |
| [ser_item_detail](dbo.ser_item_detail/ser_item_detail_field_names.md) | Serial Item Detail | Contains details about serialized items |
| [serh_hist](dbo.serh_hist/serh_hist_field_names.md) | Serial History | Contains historical information about serialized items |
| [so_mstr](dbo.so_mstr/so_mstr_field_names.md) | Sales Order Master | Contains header information for sales orders |
| [sod_det](dbo.sod_det/sod_det_field_names.md) | Sales Order Detail | Contains line item details for sales orders |
| [tr_hist](dbo.tr_hist/tr_hist_field_names.md) | Transaction History | Contains historical transaction information |
| [vd_mstr](dbo.vd_mstr/vd_mstr_field_names.md) | Vendor Master | Contains vendor information |
| [xxwezoned_det](dbo.xxwezoned_det/xxwezoned_det_field_names.md) | Custom Zone Detail | Contains custom zone information for warehouse management |

## Common Query Patterns

### Inventory Queries

```sql
-- Get current inventory levels for all items
SELECT in_part, in_site, in_qty_oh, in_qty_avail
FROM [QADEE2798].[dbo].[15]
ORDER BY in_part, in_site
```

### Transaction History Queries

```sql
-- Get transaction history for a specific part
SELECT tr_part, tr_date, tr_type, tr_qty_loc
FROM [QADEE2798].[dbo].[tr_hist]
WHERE tr_part = 'PART_NUMBER'
ORDER BY tr_date DESC
```

### Sales Order Queries

```sql
-- Get sales orders with details
SELECT so.so_nbr, so.so_cust, so.so_ord_date, sod.sod_part, sod.sod_qty_ord
FROM [QADEE2798].[dbo].[so_mstr] so
JOIN [QADEE2798].[dbo].[sod_det] sod ON so.so_nbr = sod.sod_nbr
ORDER BY so.so_ord_date DESC
```

## Inferred Relationships

These relationships are inferred based on naming conventions and column types. They may not represent actual foreign key constraints in the database.

| Table | Column | References Table | References Column | Confidence |
|-------|--------|------------------|-------------------|------------|
| [ld_det](dbo.ld_det/ld_det_field_names.md) | oid_ld_det | [ser_active_picked](dbo.ser_active_picked/ser_active_picked_field_names.md) | oid_ld_det | Medium |
| [picked_serial_link](dbo.picked_serial_link/picked_serial_link_field_names.md) | oid_ser_mstr | [ser_active_picked](dbo.ser_active_picked/ser_active_picked_field_names.md) | oid_ser_mstr | Medium |
| [po_mstr](dbo.po_mstr/po_mstr_field_names.md) | po_so_nbr | [so_mstr](dbo.so_mstr/so_mstr_field_names.md) | so_nbr | Medium |
| [pod_det](dbo.pod_det/pod_det_field_names.md) | pod__qad15 | [15](dbo.15/15_field_names.md) | in_mrp | High |
| [pod_det](dbo.pod_det/pod_det_field_names.md) | pod__qad15 | [15](dbo.15/15_field_names.md) | in_rollup | High |
| [pod_det](dbo.pod_det/pod_det_field_names.md) | pod__qad15 | [15](dbo.15/15_field_names.md) | in__qadl01 | High |
| [pod_det](dbo.pod_det/pod_det_field_names.md) | pod__qad15 | [15](dbo.15/15_field_names.md) | in__qadl02 | High |
| [pod_det](dbo.pod_det/pod_det_field_names.md) | pod__qad15 | [15](dbo.15/15_field_names.md) | in_wh | High |
| [pod_det](dbo.pod_det/pod_det_field_names.md) | pod_po_site | [po_mstr](dbo.po_mstr/po_mstr_field_names.md) | po_site | Medium |
| [pod_det](dbo.pod_det/pod_det_field_names.md) | pod_sod_line | [sod_det](dbo.sod_det/sod_det_field_names.md) | sod_line | Medium |
| [pt_mstr](dbo.pt_mstr/pt_mstr_field_names.md) | pt__qad15 | [15](dbo.15/15_field_names.md) | in_mrp | High |
| [pt_mstr](dbo.pt_mstr/pt_mstr_field_names.md) | pt__qad15 | [15](dbo.15/15_field_names.md) | in_rollup | High |
| [pt_mstr](dbo.pt_mstr/pt_mstr_field_names.md) | pt__qad15 | [15](dbo.15/15_field_names.md) | in__qadl01 | High |
| [pt_mstr](dbo.pt_mstr/pt_mstr_field_names.md) | pt__qad15 | [15](dbo.15/15_field_names.md) | in__qadl02 | High |
| [pt_mstr](dbo.pt_mstr/pt_mstr_field_names.md) | pt__qad15 | [15](dbo.15/15_field_names.md) | in_wh | High |
| [pt_mstr](dbo.pt_mstr/pt_mstr_field_names.md) | pt_po_site | [po_mstr](dbo.po_mstr/po_mstr_field_names.md) | po_site | Medium |
| [ro_det](dbo.ro_det/ro_det_field_names.md) | ro_po_nbr | [po_mstr](dbo.po_mstr/po_mstr_field_names.md) | po_nbr | Medium |
| [ser_active_picked](dbo.ser_active_picked/ser_active_picked_field_names.md) | oid_ld_det | [ld_det](dbo.ld_det/ld_det_field_names.md) | ld_qty_oh | High |
| [ser_active_picked](dbo.ser_active_picked/ser_active_picked_field_names.md) | oid_ld_det | [ld_det](dbo.ld_det/ld_det_field_names.md) | ld_assay | High |
| [ser_active_picked](dbo.ser_active_picked/ser_active_picked_field_names.md) | oid_ld_det | [ld_det](dbo.ld_det/ld_det_field_names.md) | ld_qty_all | High |
| [ser_active_picked](dbo.ser_active_picked/ser_active_picked_field_names.md) | oid_ld_det | [ld_det](dbo.ld_det/ld_det_field_names.md) | ld_qty_frz | High |
| [ser_active_picked](dbo.ser_active_picked/ser_active_picked_field_names.md) | oid_ld_det | [ld_det](dbo.ld_det/ld_det_field_names.md) | ld_work | High |
| [ser_active_picked](dbo.ser_active_picked/ser_active_picked_field_names.md) | oid_ld_det | [ld_det](dbo.ld_det/ld_det_field_names.md) | ld__dec01 | High |
| [ser_active_picked](dbo.ser_active_picked/ser_active_picked_field_names.md) | oid_ld_det | [ld_det](dbo.ld_det/ld_det_field_names.md) | ld__dec02 | High |
| [ser_active_picked](dbo.ser_active_picked/ser_active_picked_field_names.md) | oid_ld_det | [ld_det](dbo.ld_det/ld_det_field_names.md) | ld_cost | High |
| [ser_active_picked](dbo.ser_active_picked/ser_active_picked_field_names.md) | oid_ld_det | [ld_det](dbo.ld_det/ld_det_field_names.md) | ld_cust_consign_qty | High |
| [ser_active_picked](dbo.ser_active_picked/ser_active_picked_field_names.md) | oid_ld_det | [ld_det](dbo.ld_det/ld_det_field_names.md) | ld_supp_consign_qty | High |
| [ser_active_picked](dbo.ser_active_picked/ser_active_picked_field_names.md) | oid_ld_det | [ld_det](dbo.ld_det/ld_det_field_names.md) | oid_ld_det | High |
| [ser_active_picked](dbo.ser_active_picked/ser_active_picked_field_names.md) | oid_ld_det | [ld_det](dbo.ld_det/ld_det_field_names.md) | ld_exp_qtyin | High |
| [ser_active_picked](dbo.ser_active_picked/ser_active_picked_field_names.md) | oid_ld_det | [ld_det](dbo.ld_det/ld_det_field_names.md) | ld_exp_qtyout | High |
| [ser_active_picked](dbo.ser_active_picked/ser_active_picked_field_names.md) | oid_ser_mstr | [picked_serial_link](dbo.picked_serial_link/picked_serial_link_field_names.md) | oid_ser_mstr | Medium |
| [ser_item_detail](dbo.ser_item_detail/ser_item_detail_field_names.md) | usrw_decfld[15] | [15](dbo.15/15_field_names.md) | in_qty_oh | High |
| [ser_item_detail](dbo.ser_item_detail/ser_item_detail_field_names.md) | usrw_decfld[15] | [15](dbo.15/15_field_names.md) | in_qty_req | High |
| [ser_item_detail](dbo.ser_item_detail/ser_item_detail_field_names.md) | usrw_decfld[15] | [15](dbo.15/15_field_names.md) | in_qty_all | High |
| [ser_item_detail](dbo.ser_item_detail/ser_item_detail_field_names.md) | usrw_decfld[15] | [15](dbo.15/15_field_names.md) | in_qty_ord | High |
| [ser_item_detail](dbo.ser_item_detail/ser_item_detail_field_names.md) | usrw_decfld[15] | [15](dbo.15/15_field_names.md) | in_qty_chg | High |
| [ser_item_detail](dbo.ser_item_detail/ser_item_detail_field_names.md) | usrw_decfld[15] | [15](dbo.15/15_field_names.md) | in_qty_avail | High |
| [ser_item_detail](dbo.ser_item_detail/ser_item_detail_field_names.md) | usrw_decfld[15] | [15](dbo.15/15_field_names.md) | in_sls_chg | High |
| [ser_item_detail](dbo.ser_item_detail/ser_item_detail_field_names.md) | usrw_decfld[15] | [15](dbo.15/15_field_names.md) | in_iss_chg | High |
| [ser_item_detail](dbo.ser_item_detail/ser_item_detail_field_names.md) | usrw_decfld[15] | [15](dbo.15/15_field_names.md) | in_avg_iss | High |
| [ser_item_detail](dbo.ser_item_detail/ser_item_detail_field_names.md) | usrw_decfld[15] | [15](dbo.15/15_field_names.md) | in_avg_sls | High |
| [ser_item_detail](dbo.ser_item_detail/ser_item_detail_field_names.md) | usrw_decfld[15] | [15](dbo.15/15_field_names.md) | in_qty_nonet | High |
| [ser_item_detail](dbo.ser_item_detail/ser_item_detail_field_names.md) | usrw_decfld[15] | [15](dbo.15/15_field_names.md) | in_assay | High |
| [ser_item_detail](dbo.ser_item_detail/ser_item_detail_field_names.md) | usrw_decfld[15] | [15](dbo.15/15_field_names.md) | in_cust_consign_qty | High |
| [ser_item_detail](dbo.ser_item_detail/ser_item_detail_field_names.md) | usrw_decfld[15] | [15](dbo.15/15_field_names.md) | in_supp_consign_qty | High |
| [ser_item_detail](dbo.ser_item_detail/ser_item_detail_field_names.md) | usrw_decfld[15] | [15](dbo.15/15_field_names.md) | oid_in_mstr | High |
| [ser_item_detail](dbo.ser_item_detail/ser_item_detail_field_names.md) | usrw_logfld[15] | [15](dbo.15/15_field_names.md) | in_mrp | High |
| [ser_item_detail](dbo.ser_item_detail/ser_item_detail_field_names.md) | usrw_logfld[15] | [15](dbo.15/15_field_names.md) | in_rollup | High |
| [ser_item_detail](dbo.ser_item_detail/ser_item_detail_field_names.md) | usrw_logfld[15] | [15](dbo.15/15_field_names.md) | in__qadl01 | High |
| [ser_item_detail](dbo.ser_item_detail/ser_item_detail_field_names.md) | usrw_logfld[15] | [15](dbo.15/15_field_names.md) | in__qadl02 | High |
| [ser_item_detail](dbo.ser_item_detail/ser_item_detail_field_names.md) | usrw_logfld[15] | [15](dbo.15/15_field_names.md) | in_wh | High |
| [ser_item_detail](dbo.ser_item_detail/ser_item_detail_field_names.md) | usrw_intfld[15] | [15](dbo.15/15_field_names.md) | in__qadi01 | High |
| [ser_item_detail](dbo.ser_item_detail/ser_item_detail_field_names.md) | usrw_intfld[15] | [15](dbo.15/15_field_names.md) | in__qadi02 | High |
| [ser_item_detail](dbo.ser_item_detail/ser_item_detail_field_names.md) | usrw_intfld[15] | [15](dbo.15/15_field_names.md) | in_level | High |
| [ser_item_detail](dbo.ser_item_detail/ser_item_detail_field_names.md) | usrw_intfld[15] | [15](dbo.15/15_field_names.md) | in_proj_use | High |
| [serh_hist](dbo.serh_hist/serh_hist_field_names.md) | oid_tr_hist | [tr_hist](dbo.tr_hist/tr_hist_field_names.md) | tr_loc_begin | High |
| [serh_hist](dbo.serh_hist/serh_hist_field_names.md) | oid_tr_hist | [tr_hist](dbo.tr_hist/tr_hist_field_names.md) | tr_begin_qoh | High |
| [serh_hist](dbo.serh_hist/serh_hist_field_names.md) | oid_tr_hist | [tr_hist](dbo.tr_hist/tr_hist_field_names.md) | tr_qty_req | High |
| [serh_hist](dbo.serh_hist/serh_hist_field_names.md) | oid_tr_hist | [tr_hist](dbo.tr_hist/tr_hist_field_names.md) | tr_qty_chg | High |
| [serh_hist](dbo.serh_hist/serh_hist_field_names.md) | oid_tr_hist | [tr_hist](dbo.tr_hist/tr_hist_field_names.md) | tr_qty_short | High |
| [serh_hist](dbo.serh_hist/serh_hist_field_names.md) | oid_tr_hist | [tr_hist](dbo.tr_hist/tr_hist_field_names.md) | tr_mtl_std | High |
| [serh_hist](dbo.serh_hist/serh_hist_field_names.md) | oid_tr_hist | [tr_hist](dbo.tr_hist/tr_hist_field_names.md) | tr_lbr_std | High |
| [serh_hist](dbo.serh_hist/serh_hist_field_names.md) | oid_tr_hist | [tr_hist](dbo.tr_hist/tr_hist_field_names.md) | tr_bdn_std | High |
| [serh_hist](dbo.serh_hist/serh_hist_field_names.md) | oid_tr_hist | [tr_hist](dbo.tr_hist/tr_hist_field_names.md) | tr_price | High |
| [serh_hist](dbo.serh_hist/serh_hist_field_names.md) | oid_tr_hist | [tr_hist](dbo.tr_hist/tr_hist_field_names.md) | tr_gl_amt | High |
| [serh_hist](dbo.serh_hist/serh_hist_field_names.md) | oid_tr_hist | [tr_hist](dbo.tr_hist/tr_hist_field_names.md) | tr_sub_std | High |
| [serh_hist](dbo.serh_hist/serh_hist_field_names.md) | oid_tr_hist | [tr_hist](dbo.tr_hist/tr_hist_field_names.md) | tr_qty_loc | High |
| [serh_hist](dbo.serh_hist/serh_hist_field_names.md) | oid_tr_hist | [tr_hist](dbo.tr_hist/tr_hist_field_names.md) | tr_ex_rate | High |
| [serh_hist](dbo.serh_hist/serh_hist_field_names.md) | oid_tr_hist | [tr_hist](dbo.tr_hist/tr_hist_field_names.md) | tr_ovh_std | High |
| [serh_hist](dbo.serh_hist/serh_hist_field_names.md) | oid_tr_hist | [tr_hist](dbo.tr_hist/tr_hist_field_names.md) | tr_assay | High |
| [serh_hist](dbo.serh_hist/serh_hist_field_names.md) | oid_tr_hist | [tr_hist](dbo.tr_hist/tr_hist_field_names.md) | tr__dec01 | High |
| [serh_hist](dbo.serh_hist/serh_hist_field_names.md) | oid_tr_hist | [tr_hist](dbo.tr_hist/tr_hist_field_names.md) | tr__dec02 | High |
| [serh_hist](dbo.serh_hist/serh_hist_field_names.md) | oid_tr_hist | [tr_hist](dbo.tr_hist/tr_hist_field_names.md) | tr__dec03 | High |
| [serh_hist](dbo.serh_hist/serh_hist_field_names.md) | oid_tr_hist | [tr_hist](dbo.tr_hist/tr_hist_field_names.md) | tr__dec04 | High |
| [serh_hist](dbo.serh_hist/serh_hist_field_names.md) | oid_tr_hist | [tr_hist](dbo.tr_hist/tr_hist_field_names.md) | tr__dec05 | High |
| [serh_hist](dbo.serh_hist/serh_hist_field_names.md) | oid_tr_hist | [tr_hist](dbo.tr_hist/tr_hist_field_names.md) | tr_covered_amt | High |
| [serh_hist](dbo.serh_hist/serh_hist_field_names.md) | oid_tr_hist | [tr_hist](dbo.tr_hist/tr_hist_field_names.md) | tr_cprice | High |
| [serh_hist](dbo.serh_hist/serh_hist_field_names.md) | oid_tr_hist | [tr_hist](dbo.tr_hist/tr_hist_field_names.md) | tr_ex_rate2 | High |
| [serh_hist](dbo.serh_hist/serh_hist_field_names.md) | oid_tr_hist | [tr_hist](dbo.tr_hist/tr_hist_field_names.md) | oid_tr_hist | High |
| [serh_hist](dbo.serh_hist/serh_hist_field_names.md) | oid_tr_hist | [tr_hist](dbo.tr_hist/tr_hist_field_names.md) | tr_qty_cn_adj | High |
| [serh_hist](dbo.serh_hist/serh_hist_field_names.md) | oid_tr_hist | [tr_hist](dbo.tr_hist/tr_hist_field_names.md) | oid_lgd_mstr | High |
| [serh_hist](dbo.serh_hist/serh_hist_field_names.md) | oid_tr_hist | [tr_hist](dbo.tr_hist/tr_hist_field_names.md) | tr_wo_qty_comp | High |
| [serh_hist](dbo.serh_hist/serh_hist_field_names.md) | oid_tr_hist | [tr_hist](dbo.tr_hist/tr_hist_field_names.md) | tr_wo_qty_ord | High |
| [serh_hist](dbo.serh_hist/serh_hist_field_names.md) | oid_tr_hist | [tr_hist](dbo.tr_hist/tr_hist_field_names.md) | tr_wo_yield_pct | High |
| [serh_hist](dbo.serh_hist/serh_hist_field_names.md) | oid_tr_hist | [tr_hist](dbo.tr_hist/tr_hist_field_names.md) | tr_intercompanyref | High |
| [serh_hist](dbo.serh_hist/serh_hist_field_names.md) | oid_tr_hist | [tr_hist](dbo.tr_hist/tr_hist_field_names.md) | tr_gl_amt_sc | High |
| [sod_det](dbo.sod_det/sod_det_field_names.md) | sod_btb_pod_line | [pod_det](dbo.pod_det/pod_det_field_names.md) | pod_line | Medium |
| [tr_hist](dbo.tr_hist/tr_hist_field_names.md) | tr__chr15 | [15](dbo.15/15_field_names.md) | in_site | High |
| [tr_hist](dbo.tr_hist/tr_hist_field_names.md) | tr__chr15 | [15](dbo.15/15_field_names.md) | in_user1 | High |
| [tr_hist](dbo.tr_hist/tr_hist_field_names.md) | tr__chr15 | [15](dbo.15/15_field_names.md) | in_user2 | High |
| [tr_hist](dbo.tr_hist/tr_hist_field_names.md) | tr__chr15 | [15](dbo.15/15_field_names.md) | in_gl_set | High |
| [tr_hist](dbo.tr_hist/tr_hist_field_names.md) | tr__chr15 | [15](dbo.15/15_field_names.md) | in_cur_set | High |
| [tr_hist](dbo.tr_hist/tr_hist_field_names.md) | tr__chr15 | [15](dbo.15/15_field_names.md) | in__qadc02 | High |
| [tr_hist](dbo.tr_hist/tr_hist_field_names.md) | tr__chr15 | [15](dbo.15/15_field_names.md) | in_loc | High |
| [tr_hist](dbo.tr_hist/tr_hist_field_names.md) | tr__chr15 | [15](dbo.15/15_field_names.md) | in_loc_type | High |
| [tr_hist](dbo.tr_hist/tr_hist_field_names.md) | tr__chr15 | [15](dbo.15/15_field_names.md) | in_rollup_id | High |
| [tr_hist](dbo.tr_hist/tr_hist_field_names.md) | tr__chr15 | [15](dbo.15/15_field_names.md) | in__qadc03 | High |
| [tr_hist](dbo.tr_hist/tr_hist_field_names.md) | tr__chr15 | [15](dbo.15/15_field_names.md) | in__qadc04 | High |
| [tr_hist](dbo.tr_hist/tr_hist_field_names.md) | tr__chr15 | [15](dbo.15/15_field_names.md) | in__qadc01 | High |
| [tr_hist](dbo.tr_hist/tr_hist_field_names.md) | tr__chr15 | [15](dbo.15/15_field_names.md) | in_gl_cost_site | High |
| [tr_hist](dbo.tr_hist/tr_hist_field_names.md) | oid_tr_hist | [serh_hist](dbo.serh_hist/serh_hist_field_names.md) | oid_tr_hist | Medium |

### Relationship Diagram (Inferred)

![Database Relationships (Inferred)](database_relationships_inferred.png)
