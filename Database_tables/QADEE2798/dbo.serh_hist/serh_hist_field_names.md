# Table: serh_hist

## Fields

| Field Name | Data Type | Primary Key | Foreign Key | Nullable | Description |
|------------|-----------|-------------|-------------|----------|-------------|
| serh_trans_nbr | bigint |  |  | YES | No description available |
| serh_trans_type | varchar(8) |  |  | YES | No description available |
| serh_serial_id | varchar(40) |  |  | YES | No description available |
| serh_parent_id | varchar(40) |  |  | YES | No description available |
| serh_site | varchar(80) |  |  | YES | No description available |
| serh_loc | varchar(30) |  |  | YES | No description available |
| serh_part | varchar(30) |  |  | YES | No description available |
| serh_lotser | varchar(30) |  |  | YES | No description available |
| serh_ref | varchar(80) |  |  | YES | No description available |
| serh_begin_qoh | decimal(38,10) |  |  | YES | No description available |
| serh_qty_chg | decimal(38,10) |  |  | YES | No description available |
| serh_pack_um | varchar(30) |  |  | YES | No description available |
| serh_content_um | varchar(30) |  |  | YES | No description available |
| serh_stage | varchar(18) |  |  | YES | No description available |
| serh_pack_code | varchar(18) |  |  | YES | No description available |
| oid_tr_hist | decimal(38,10) |  |  | YES | No description available |
| serh_trans_date | smalldatetime |  |  | YES | No description available |
| serh_trans_time | int |  |  | YES | No description available |
| serh_mod_userid | varchar(80) |  |  | YES | No description available |
| serh_mod_date | smalldatetime |  |  | YES | No description available |
| serh_user1 | varchar(80) |  |  | YES | No description available |
| serh_user2 | varchar(80) |  |  | YES | No description available |
| serh__qadc01 | varchar(80) |  |  | YES | No description available |
| serh__qadc02 | varchar(80) |  |  | YES | No description available |
| oid_serh_hist | decimal(38,10) | Yes |  | NO | No description available |
| serh_program | varchar(12) |  |  | YES | No description available |
| oid_parent | decimal(38,10) |  |  | YES | No description available |
| serh_parent_table | varchar(18) |  |  | YES | No description available |
| serh_cnt_open | bit |  |  | YES | No description available |
| serh_cnt_qty | decimal(38,10) |  |  | YES | No description available |
| serh_master_id | varchar(40) |  |  | YES | No description available |
| serh_cnt_init | bit |  |  | YES | No description available |
| serh_master_stage | varchar(10) |  |  | YES | No description available |
| serh_cause | varchar(40) |  |  | YES | No description available |
| serh_phantom | bit |  |  | YES | No description available |
| serh_commission_date | smalldatetime |  |  | YES | No description available |
| serh_qty_pck | decimal(38,10) |  |  | YES | No description available |
| serh_prt_lbl | bit |  |  | YES | No description available |
| serh_vend_lot | varchar(30) |  |  | YES | No description available |
| serh_ext_sn_id | varchar(40) |  |  | YES | No description available |
| serh_origin_code | varchar(16) |  |  | YES | No description available |
| oid_pickh_hist | decimal(38,10) |  |  | YES | No description available |

## SQL Query Example

```sql
SELECT [serh_trans_nbr], [serh_trans_type], [serh_serial_id], [serh_parent_id], [serh_site], [serh_loc], [serh_part], [serh_lotser], [serh_ref], [serh_begin_qoh], [serh_qty_chg], [serh_pack_um], [serh_content_um], [serh_stage], [serh_pack_code], [oid_tr_hist], [serh_trans_date], [serh_trans_time], [serh_mod_userid], [serh_mod_date], [serh_user1], [serh_user2], [serh__qadc01], [serh__qadc02], [oid_serh_hist], [serh_program], [oid_parent], [serh_parent_table], [serh_cnt_open], [serh_cnt_qty], [serh_master_id], [serh_cnt_init], [serh_master_stage], [serh_cause], [serh_phantom], [serh_commission_date], [serh_qty_pck], [serh_prt_lbl], [serh_vend_lot], [serh_ext_sn_id], [serh_origin_code], [oid_pickh_hist]
FROM [QADEE2798].[dbo].[serh_hist]
```
