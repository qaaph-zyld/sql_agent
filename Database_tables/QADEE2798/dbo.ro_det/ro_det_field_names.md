# Table: ro_det

## Fields

| Field Name | Data Type | Primary Key | Foreign Key | Nullable | Description |
|------------|-----------|-------------|-------------|----------|-------------|
| ro_routing | varchar(30) |  |  | YES | No description available |
| ro_op | int |  |  | YES | No description available |
| ro_desc | varchar(80) |  |  | YES | No description available |
| ro_wkctr | varchar(80) |  |  | YES | No description available |
| ro_setup | decimal(38,10) |  |  | YES | No description available |
| ro_run | decimal(38,10) |  |  | YES | No description available |
| ro_move | decimal(38,10) |  |  | YES | No description available |
| ro_yield_pct | decimal(38,10) |  |  | YES | No description available |
| ro_tool | varchar(80) |  |  | YES | No description available |
| ro_vend | varchar(80) |  |  | YES | No description available |
| ro_sub_cost | decimal(38,10) |  |  | YES | No description available |
| ro_start | smalldatetime |  |  | YES | No description available |
| ro_end | smalldatetime |  |  | YES | No description available |
| ro_tran_qty | int |  |  | YES | No description available |
| ro_inv_value | decimal(38,10) |  |  | YES | No description available |
| ro_cmtindx | int |  |  | YES | No description available |
| ro_mch | varchar(80) |  |  | YES | No description available |
| ro_milestone | bit |  |  | YES | No description available |
| ro_batch | decimal(38,10) |  |  | YES | No description available |
| ro_user1 | varchar(80) |  |  | YES | No description available |
| ro_user2 | varchar(80) |  |  | YES | No description available |
| ro_std_op | varchar(80) |  |  | YES | No description available |
| ro_setup_men | decimal(38,10) |  |  | YES | No description available |
| ro_men_mch | decimal(38,10) |  |  | YES | No description available |
| ro_mch_op | int |  |  | YES | No description available |
| ro_lbr_ovhd | decimal(38,10) |  |  | YES | No description available |
| ro_queue | decimal(38,10) |  |  | YES | No description available |
| ro_wait | decimal(38,10) |  |  | YES | No description available |
| ro_sub_lead | int |  |  | YES | No description available |
| ro_cyc_unit | decimal(38,10) |  |  | YES | No description available |
| ro_cyc_rate | decimal(38,10) |  |  | YES | No description available |
| ro__chr01 | varchar(80) |  |  | YES | No description available |
| ro__chr02 | varchar(80) |  |  | YES | No description available |
| ro__chr03 | varchar(80) |  |  | YES | No description available |
| ro__chr04 | varchar(80) |  |  | YES | No description available |
| ro__chr05 | varchar(80) |  |  | YES | No description available |
| ro__dte01 | smalldatetime |  |  | YES | No description available |
| ro__dte02 | smalldatetime |  |  | YES | No description available |
| ro__dec01 | decimal(38,10) |  |  | YES | No description available |
| ro__dec02 | decimal(38,10) |  |  | YES | No description available |
| ro__log01 | bit |  |  | YES | No description available |
| ro_std_batch | decimal(38,10) |  |  | YES | No description available |
| ro_rollup | bit |  |  | YES | No description available |
| ro_rollup_id | varchar(80) |  |  | YES | No description available |
| ro_elm_lbr | varchar(80) |  |  | YES | No description available |
| ro_elm_bdn | varchar(80) |  |  | YES | No description available |
| ro_elm_sub | varchar(20) |  |  | YES | No description available |
| ro_start_ecn | varchar(80) |  |  | YES | No description available |
| ro_end_ecn | varchar(80) |  |  | YES | No description available |
| ro_po_nbr | varchar(80) |  |  | YES | No description available |
| ro_po_line | int |  |  | YES | No description available |
| ro_mv_nxt_op | bit |  |  | YES | No description available |
| ro_wipmtl_part | varchar(30) |  |  | YES | No description available |
| ro_auto_lbr | bit |  |  | YES | No description available |
| ro_bom_code | varchar(30) |  |  | YES | No description available |
| ro_cost | decimal(38,10) |  |  | YES | No description available |
| ro_fsm_type | varchar(80) |  |  | YES | No description available |
| ro_price | decimal(38,10) |  |  | YES | No description available |
| ro_mod_date | smalldatetime |  |  | YES | No description available |
| ro_mod_userid | varchar(80) |  |  | YES | No description available |
| ro__qadc01 | varchar(80) |  |  | YES | No description available |
| ro__qadc02 | varchar(80) |  |  | YES | No description available |
| ro__qadc03 | varchar(80) |  |  | YES | No description available |
| ro__qade01 | decimal(38,10) |  |  | YES | No description available |
| ro__qade02 | decimal(38,10) |  |  | YES | No description available |
| ro__qadt01 | smalldatetime |  |  | YES | No description available |
| ro__qadt02 | smalldatetime |  |  | YES | No description available |
| ro__qadl01 | bit |  |  | YES | No description available |
| ro__qadl02 | bit |  |  | YES | No description available |
| ro_fsc_code | varchar(80) |  |  | YES | No description available |
| oid_ro_det | decimal(38,10) | Yes |  | NO | No description available |

## SQL Query Example

```sql
SELECT [ro_routing], [ro_op], [ro_desc], [ro_wkctr], [ro_setup], [ro_run], [ro_move], [ro_yield_pct], [ro_tool], [ro_vend], [ro_sub_cost], [ro_start], [ro_end], [ro_tran_qty], [ro_inv_value], [ro_cmtindx], [ro_mch], [ro_milestone], [ro_batch], [ro_user1], [ro_user2], [ro_std_op], [ro_setup_men], [ro_men_mch], [ro_mch_op], [ro_lbr_ovhd], [ro_queue], [ro_wait], [ro_sub_lead], [ro_cyc_unit], [ro_cyc_rate], [ro__chr01], [ro__chr02], [ro__chr03], [ro__chr04], [ro__chr05], [ro__dte01], [ro__dte02], [ro__dec01], [ro__dec02], [ro__log01], [ro_std_batch], [ro_rollup], [ro_rollup_id], [ro_elm_lbr], [ro_elm_bdn], [ro_elm_sub], [ro_start_ecn], [ro_end_ecn], [ro_po_nbr], [ro_po_line], [ro_mv_nxt_op], [ro_wipmtl_part], [ro_auto_lbr], [ro_bom_code], [ro_cost], [ro_fsm_type], [ro_price], [ro_mod_date], [ro_mod_userid], [ro__qadc01], [ro__qadc02], [ro__qadc03], [ro__qade01], [ro__qade02], [ro__qadt01], [ro__qadt02], [ro__qadl01], [ro__qadl02], [ro_fsc_code], [oid_ro_det]
FROM [QADEE2798].[dbo].[ro_det]
```
