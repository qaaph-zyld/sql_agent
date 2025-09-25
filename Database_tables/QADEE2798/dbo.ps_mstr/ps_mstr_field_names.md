# Table: ps_mstr

## Fields

| Field Name | Data Type | Primary Key | Foreign Key | Nullable | Description |
|------------|-----------|-------------|-------------|----------|-------------|
| ps_par | varchar(30) |  |  | YES | No description available |
| ps_comp | varchar(30) |  |  | YES | No description available |
| ps_ref | varchar(30) |  |  | YES | No description available |
| ps_qty_per | decimal(38,10) |  |  | YES | No description available |
| ps_scrp_pct | decimal(38,10) |  |  | YES | No description available |
| ps_ps_code | varchar(30) |  |  | YES | No description available |
| ps_lt_off | int |  |  | YES | No description available |
| ps_start | smalldatetime |  |  | YES | No description available |
| ps_end | smalldatetime |  |  | YES | No description available |
| ps_rmks | varchar(30) |  |  | YES | No description available |
| ps_op | int |  |  | YES | No description available |
| ps_item_no | int |  |  | YES | No description available |
| ps_mandatory | bit |  |  | YES | No description available |
| ps_exclusive | bit |  |  | YES | No description available |
| ps_process | varchar(80) |  |  | YES | No description available |
| ps_qty_type | varchar(30) |  |  | YES | No description available |
| ps_user1 | varchar(80) |  |  | YES | No description available |
| ps_user2 | varchar(80) |  |  | YES | No description available |
| ps_fcst_pct | decimal(38,10) |  |  | YES | No description available |
| ps_default | bit |  |  | YES | No description available |
| ps_group | varchar(80) |  |  | YES | No description available |
| ps_critical | bit |  |  | YES | No description available |
| ps_qty_per_b | decimal(38,10) |  |  | YES | No description available |
| ps_comp_um | varchar(30) |  |  | YES | No description available |
| ps_um_conv | decimal(38,10) |  |  | YES | No description available |
| ps_assay | decimal(38,10) |  |  | YES | No description available |
| ps_comm_code | varchar(80) |  |  | YES | No description available |
| ps_non_bal | bit |  |  | YES | No description available |
| ps__qad01 | bit |  |  | YES | No description available |
| ps_userid | varchar(80) |  |  | YES | No description available |
| ps_mod_date | smalldatetime |  |  | YES | No description available |
| ps_batch_pct | decimal(38,10) |  |  | YES | No description available |
| ps_cmtindx | int |  |  | YES | No description available |
| ps_start_ecn | varchar(80) |  |  | YES | No description available |
| ps_end_ecn | varchar(80) |  |  | YES | No description available |
| ps_joint_type | varchar(30) |  |  | YES | No description available |
| ps_cop_qty | decimal(38,10) |  |  | YES | No description available |
| ps_cst_pct | decimal(38,10) |  |  | YES | No description available |
| ps_prod_pct | decimal(38,10) |  |  | YES | No description available |
| ps_qty_cons | decimal(38,10) |  |  | YES | No description available |
| ps_qty_exch | decimal(38,10) |  |  | YES | No description available |
| ps_qty_diag | decimal(38,10) |  |  | YES | No description available |
| ps__chr01 | varchar(80) |  |  | YES | No description available |
| ps__chr02 | varchar(80) |  |  | YES | No description available |
| ps__dte01 | smalldatetime |  |  | YES | No description available |
| ps__dte02 | smalldatetime |  |  | YES | No description available |
| ps__dec01 | decimal(38,10) |  |  | YES | No description available |
| ps__dec02 | decimal(38,10) |  |  | YES | No description available |
| ps__log01 | bit |  |  | YES | No description available |
| ps__log02 | bit |  |  | YES | No description available |
| ps__qadc01 | varchar(80) |  |  | YES | No description available |
| ps__qadc02 | varchar(80) |  |  | YES | No description available |
| ps__qadt01 | smalldatetime |  |  | YES | No description available |
| ps__qadt02 | smalldatetime |  |  | YES | No description available |
| ps__qadt03 | smalldatetime |  |  | YES | No description available |
| ps__qadd01 | decimal(38,10) |  |  | YES | No description available |
| ps__qadd02 | decimal(38,10) |  |  | YES | No description available |
| ps__qadl01 | bit |  |  | YES | No description available |
| ps__qadl02 | bit |  |  | YES | No description available |
| oid_ps_mstr | decimal(38,10) | Yes |  | NO | No description available |
| ps_all_pol | varchar(8) |  |  | YES | No description available |
| ps_comp_iss_pol | varchar(8) |  |  | YES | No description available |
| ps_pick_pol | varchar(8) |  |  | YES | No description available |

## SQL Query Example

```sql
SELECT [ps_par], [ps_comp], [ps_ref], [ps_qty_per], [ps_scrp_pct], [ps_ps_code], [ps_lt_off], [ps_start], [ps_end], [ps_rmks], [ps_op], [ps_item_no], [ps_mandatory], [ps_exclusive], [ps_process], [ps_qty_type], [ps_user1], [ps_user2], [ps_fcst_pct], [ps_default], [ps_group], [ps_critical], [ps_qty_per_b], [ps_comp_um], [ps_um_conv], [ps_assay], [ps_comm_code], [ps_non_bal], [ps__qad01], [ps_userid], [ps_mod_date], [ps_batch_pct], [ps_cmtindx], [ps_start_ecn], [ps_end_ecn], [ps_joint_type], [ps_cop_qty], [ps_cst_pct], [ps_prod_pct], [ps_qty_cons], [ps_qty_exch], [ps_qty_diag], [ps__chr01], [ps__chr02], [ps__dte01], [ps__dte02], [ps__dec01], [ps__dec02], [ps__log01], [ps__log02], [ps__qadc01], [ps__qadc02], [ps__qadt01], [ps__qadt02], [ps__qadt03], [ps__qadd01], [ps__qadd02], [ps__qadl01], [ps__qadl02], [oid_ps_mstr], [ps_all_pol], [ps_comp_iss_pol], [ps_pick_pol]
FROM [QADEE2798].[dbo].[ps_mstr]
```
