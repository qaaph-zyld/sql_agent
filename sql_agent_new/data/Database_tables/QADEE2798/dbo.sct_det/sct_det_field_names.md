# Table: sct_det

## Fields

| Field Name | Data Type | Primary Key | Foreign Key | Nullable | Description |
|------------|-----------|-------------|-------------|----------|-------------|
| sct_sim | varchar(80) |  |  | YES | No description available |
| sct_part | varchar(30) |  |  | YES | No description available |
| sct_cst_tot | decimal(38,10) |  |  | YES | No description available |
| sct_mtl_tl | decimal(38,10) |  |  | YES | No description available |
| sct_lbr_tl | decimal(38,10) |  |  | YES | No description available |
| sct_bdn_tl | decimal(38,10) |  |  | YES | No description available |
| sct_ovh_tl | decimal(38,10) |  |  | YES | No description available |
| sct_sub_tl | decimal(38,10) |  |  | YES | No description available |
| sct_mtl_ll | decimal(38,10) |  |  | YES | No description available |
| sct_lbr_ll | decimal(38,10) |  |  | YES | No description available |
| sct_bdn_ll | decimal(38,10) |  |  | YES | No description available |
| sct_ovh_ll | decimal(38,10) |  |  | YES | No description available |
| sct_sub_ll | decimal(38,10) |  |  | YES | No description available |
| sct_cst_date | smalldatetime |  |  | YES | No description available |
| sct_user1 | varchar(80) |  |  | YES | No description available |
| sct_user2 | varchar(80) |  |  | YES | No description available |
| sct_serial | varchar(50) |  |  | YES | No description available |
| sct_site | varchar(80) |  |  | YES | No description available |
| sct_rollup | bit |  |  | YES | No description available |
| sct_rollup_id | varchar(30) |  |  | YES | No description available |
| sct_nrv | decimal(38,10) |  |  | YES | No description available |
| sct__qadc01 | varchar(80) |  |  | YES | No description available |
| sct_cost_changed | bit |  |  | YES | No description available |
| oid_sct_det | decimal(38,10) | Yes |  | NO | No description available |

## SQL Query Example

```sql
SELECT [sct_sim], [sct_part], [sct_cst_tot], [sct_mtl_tl], [sct_lbr_tl], [sct_bdn_tl], [sct_ovh_tl], [sct_sub_tl], [sct_mtl_ll], [sct_lbr_ll], [sct_bdn_ll], [sct_ovh_ll], [sct_sub_ll], [sct_cst_date], [sct_user1], [sct_user2], [sct_serial], [sct_site], [sct_rollup], [sct_rollup_id], [sct_nrv], [sct__qadc01], [sct_cost_changed], [oid_sct_det]
FROM [QADEE2798].[dbo].[sct_det]
```
