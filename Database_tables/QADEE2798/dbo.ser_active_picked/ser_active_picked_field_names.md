# Table: ser_active_picked

## Fields

| Field Name | Data Type | Primary Key | Foreign Key | Nullable | Description |
|------------|-----------|-------------|-------------|----------|-------------|
| ser_serial_id | varchar(40) |  |  | YES | No description available |
| oid_ser_mstr_parent | decimal(38,10) |  |  | YES | No description available |
| ser_stage | varchar(10) |  |  | YES | No description available |
| ser_pack_code | varchar(18) |  |  | YES | No description available |
| ser_prt_lbl | bit |  |  | YES | No description available |
| oid_loc_mstr | decimal(38,10) |  |  | YES | No description available |
| ser_site | varchar(80) |  |  | YES | No description available |
| ser_loc | varchar(30) |  |  | YES | No description available |
| ser_part | varchar(30) |  |  | YES | No description available |
| ser_lotser | varchar(30) |  |  | YES | No description available |
| ser_ref | varchar(80) |  |  | YES | No description available |
| ser_qty_pck | decimal(38,10) |  |  | YES | No description available |
| ser_qty_avail | decimal(38,10) |  |  | YES | No description available |
| ser_um | varchar(30) |  |  | YES | No description available |
| ser_mod_userid | varchar(80) |  |  | YES | No description available |
| ser_mod_date | smalldatetime |  |  | YES | No description available |
| ser_user1 | varchar(80) |  |  | YES | No description available |
| ser_user2 | varchar(80) |  |  | YES | No description available |
| ser__qadc01 | varchar(80) |  |  | YES | No description available |
| ser__qadc02 | varchar(80) |  |  | YES | No description available |
| oid_ser_mstr | decimal(38,10) | Yes |  | NO | No description available |
| ser_ship_wt | decimal(38,10) |  |  | YES | No description available |
| ser_ship_wt_um | varchar(30) |  |  | YES | No description available |
| ser_size | decimal(20,10) |  |  | YES | No description available |
| ser_size_um | varchar(30) |  |  | YES | No description available |
| oid_ld_det | decimal(38,10) |  |  | YES | No description available |
| ser_truck_loaded | bit |  |  | YES | No description available |
| ser_gross_weight | decimal(38,10) |  |  | YES | No description available |
| ser_gross_weight_um | varchar(30) |  |  | YES | No description available |
| ser_unloaded | bit |  |  | YES | No description available |
| ser_phantom | bit |  |  | YES | No description available |
| ser_vend_lot | varchar(30) |  |  | YES | No description available |
| ser_ext_sn_id | varchar(40) |  |  | YES | No description available |
| ser_commission_date | smalldatetime |  |  | YES | No description available |
| ser_origin_code | varchar(16) |  |  | YES | No description available |

## SQL Query Example

```sql
SELECT [ser_serial_id], [oid_ser_mstr_parent], [ser_stage], [ser_pack_code], [ser_prt_lbl], [oid_loc_mstr], [ser_site], [ser_loc], [ser_part], [ser_lotser], [ser_ref], [ser_qty_pck], [ser_qty_avail], [ser_um], [ser_mod_userid], [ser_mod_date], [ser_user1], [ser_user2], [ser__qadc01], [ser__qadc02], [oid_ser_mstr], [ser_ship_wt], [ser_ship_wt_um], [ser_size], [ser_size_um], [oid_ld_det], [ser_truck_loaded], [ser_gross_weight], [ser_gross_weight_um], [ser_unloaded], [ser_phantom], [ser_vend_lot], [ser_ext_sn_id], [ser_commission_date], [ser_origin_code]
FROM [QADEE2798].[dbo].[ser_active_picked]
```
