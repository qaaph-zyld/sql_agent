# Table: ad_mstr

## Fields

| Field Name | Data Type | Primary Key | Foreign Key | Nullable | Description |
|------------|-----------|-------------|-------------|----------|-------------|
| ad_addr | varchar(80) |  |  | YES | No description available |
| ad_name | varchar(80) |  |  | YES | No description available |
| ad_line1 | varchar(36) |  |  | YES | No description available |
| ad_line2 | varchar(36) |  |  | YES | No description available |
| ad_city | varchar(30) |  |  | YES | No description available |
| ad_state | varchar(30) |  |  | YES | No description available |
| ad_zip | varchar(30) |  |  | YES | No description available |
| ad_type | varchar(80) |  |  | YES | No description available |
| ad_attn | varchar(30) |  |  | YES | No description available |
| ad_phone | varchar(30) |  |  | YES | No description available |
| ad_ext | varchar(30) |  |  | YES | No description available |
| ad_ref | varchar(80) |  |  | YES | No description available |
| ad_sort | varchar(80) |  |  | YES | No description available |
| ad_country | varchar(30) |  |  | YES | No description available |
| ad_attn2 | varchar(30) |  |  | YES | No description available |
| ad_phone2 | varchar(30) |  |  | YES | No description available |
| ad_ext2 | varchar(30) |  |  | YES | No description available |
| ad_fax | varchar(30) |  |  | YES | No description available |
| ad_fax2 | varchar(30) |  |  | YES | No description available |
| ad_line3 | varchar(36) |  |  | YES | No description available |
| ad_user1 | varchar(80) |  |  | YES | No description available |
| ad_user2 | varchar(80) |  |  | YES | No description available |
| ad_lang | varchar(30) |  |  | YES | No description available |
| ad_pst_id | varchar(30) |  |  | YES | No description available |
| ad_date | smalldatetime |  |  | YES | No description available |
| ad_county | varchar(30) |  |  | YES | No description available |
| ad_temp | bit |  |  | YES | No description available |
| ad_bk_acct1 | varchar(30) |  |  | YES | No description available |
| ad_bk_acct2 | varchar(30) |  |  | YES | No description available |
| ad_format | int |  |  | YES | No description available |
| ad_vat_reg | varchar(30) |  |  | YES | No description available |
| ad_coc_reg | varchar(80) |  |  | YES | No description available |
| ad_gst_id | varchar(30) |  |  | YES | No description available |
| ad_tax_type | varchar(30) |  |  | YES | No description available |
| ad_taxc | varchar(30) |  |  | YES | No description available |
| ad_taxable | bit |  |  | YES | No description available |
| ad_tax_in | bit |  |  | YES | No description available |
| ad_edi_tpid | varchar(30) |  |  | YES | No description available |
| ad_timezone | varchar(80) |  |  | YES | No description available |
| ad_mod_date | smalldatetime |  |  | YES | No description available |
| ad_userid | varchar(80) |  |  | YES | No description available |
| ad_edi_id | varchar(30) |  |  | YES | No description available |
| ad_edi_ctrl[1] | varchar(630) |  |  | YES | No description available |
| ad_edi_ctrl[2] | varchar(630) |  |  | YES | No description available |
| ad_edi_ctrl[3] | varchar(630) |  |  | YES | No description available |
| ad_edi_ctrl[4] | varchar(630) |  |  | YES | No description available |
| ad_edi_ctrl[5] | varchar(630) |  |  | YES | No description available |
| ad_conrep | varchar(30) |  |  | YES | No description available |
| ad_barlbl_prt | varchar(380) |  |  | YES | No description available |
| ad_barlbl_val | varchar(30) |  |  | YES | No description available |
| ad_calendar | varchar(80) |  |  | YES | No description available |
| ad_edi_std | varchar(80) |  |  | YES | No description available |
| ad_edi_level | varchar(80) |  |  | YES | No description available |
| ad__qad01 | varchar(80) |  |  | YES | No description available |
| ad__qad02 | varchar(80) |  |  | YES | No description available |
| ad__qad03 | varchar(80) |  |  | YES | No description available |
| ad__qad04 | varchar(80) |  |  | YES | No description available |
| ad__qad05 | varchar(80) |  |  | YES | No description available |
| ad__chr01 | varchar(80) |  |  | YES | No description available |
| ad__chr02 | varchar(80) |  |  | YES | No description available |
| ad__chr03 | varchar(80) |  |  | YES | No description available |
| ad__chr04 | varchar(80) |  |  | YES | No description available |
| ad__chr05 | varchar(80) |  |  | YES | No description available |
| ad_tp_loc_code | varchar(30) |  |  | YES | No description available |
| ad_ctry | varchar(30) |  |  | YES | No description available |
| ad_tax_zone | varchar(30) |  |  | YES | No description available |
| ad_tax_usage | varchar(80) |  |  | YES | No description available |
| ad_misc1_id | varchar(30) |  |  | YES | No description available |
| ad_misc2_id | varchar(30) |  |  | YES | No description available |
| ad_misc3_id | varchar(30) |  |  | YES | No description available |
| ad_wk_offset | int |  |  | YES | No description available |
| ad_inv_mthd | varchar(30) |  |  | YES | No description available |
| ad_sch_mthd | varchar(30) |  |  | YES | No description available |
| ad_po_mthd | varchar(30) |  |  | YES | No description available |
| ad_asn_data | varchar(256) |  |  | YES | No description available |
| ad_intr_division | varchar(30) |  |  | YES | No description available |
| ad_tax_report | bit |  |  | YES | No description available |
| ad_name_control | varchar(30) |  |  | YES | No description available |
| ad_last_file | bit |  |  | YES | No description available |
| oid_ad_mstr | decimal(38,10) | Yes |  | NO | No description available |
| ad_email | varchar(48) |  |  | YES | No description available |
| ad_email2 | varchar(48) |  |  | YES | No description available |
| ad_bus_relation | varchar(20) |  |  | YES | No description available |
| ad_priority | varchar(16) |  |  | YES | No description available |
| ad_route | varchar(16) |  |  | YES | No description available |
| ad_loadseq | varchar(16) |  |  | YES | No description available |
| ad_pick_by_date | bit |  |  | YES | No description available |
| ad_profile | varchar(16) |  |  | YES | No description available |
| ad_address_id | bigint |  |  | YES | No description available |
| ad_tax_in_city | bit |  |  | YES | No description available |
| ad_ns_pr_list | varchar(16) |  |  | YES | No description available |
| ad_alt_um | varchar(4) |  |  | YES | No description available |
| ad_city_code | varchar(20) |  |  | YES | No description available |

## SQL Query Example

```sql
SELECT [ad_addr], [ad_name], [ad_line1], [ad_line2], [ad_city], [ad_state], [ad_zip], [ad_type], [ad_attn], [ad_phone], [ad_ext], [ad_ref], [ad_sort], [ad_country], [ad_attn2], [ad_phone2], [ad_ext2], [ad_fax], [ad_fax2], [ad_line3], [ad_user1], [ad_user2], [ad_lang], [ad_pst_id], [ad_date], [ad_county], [ad_temp], [ad_bk_acct1], [ad_bk_acct2], [ad_format], [ad_vat_reg], [ad_coc_reg], [ad_gst_id], [ad_tax_type], [ad_taxc], [ad_taxable], [ad_tax_in], [ad_edi_tpid], [ad_timezone], [ad_mod_date], [ad_userid], [ad_edi_id], [ad_edi_ctrl[1]], [ad_edi_ctrl[2]], [ad_edi_ctrl[3]], [ad_edi_ctrl[4]], [ad_edi_ctrl[5]], [ad_conrep], [ad_barlbl_prt], [ad_barlbl_val], [ad_calendar], [ad_edi_std], [ad_edi_level], [ad__qad01], [ad__qad02], [ad__qad03], [ad__qad04], [ad__qad05], [ad__chr01], [ad__chr02], [ad__chr03], [ad__chr04], [ad__chr05], [ad_tp_loc_code], [ad_ctry], [ad_tax_zone], [ad_tax_usage], [ad_misc1_id], [ad_misc2_id], [ad_misc3_id], [ad_wk_offset], [ad_inv_mthd], [ad_sch_mthd], [ad_po_mthd], [ad_asn_data], [ad_intr_division], [ad_tax_report], [ad_name_control], [ad_last_file], [oid_ad_mstr], [ad_email], [ad_email2], [ad_bus_relation], [ad_priority], [ad_route], [ad_loadseq], [ad_pick_by_date], [ad_profile], [ad_address_id], [ad_tax_in_city], [ad_ns_pr_list], [ad_alt_um], [ad_city_code]
FROM [QADEE2798].[dbo].[ad_mstr]
```
