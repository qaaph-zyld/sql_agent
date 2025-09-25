# SQL Performance Analysis and Recommendations

Date: 2025-08-15 09:43 (+02:00)
Database: QADEE2798 (SQL Server)

## Current Query Structure Analysis

### Main Query: `inventory_query.sql`
The main query uses multiple CTEs (Common Table Expressions) with complex joins:

1. **CombinedParts**: Base part master filter
2. **ParentCTE**: Parent parts from BOM structure
3. **ChildCTE**: Child parts from BOM structure  
4. **BOMStatusCTE**: Full outer join to determine SFG status
5. **PsOpCTE**: Operations data
6. **InventoryByArea**: WIP quantity aggregation with zone filtering
7. **WIPMinimumData**: Historical transaction analysis for min/max calculations
8. **Final SELECT**: Multiple left joins with cost, supplier, project data

### Performance Bottlenecks Identified

#### 1. Complex CTE Chain
- Multiple CTEs with FULL OUTER JOINs
- Repeated scans of `ps_mstr` table (3 times in different CTEs)
- Large intermediate result sets

#### 2. WIP Quantity Calculation
```sql
LEFT JOIN (
  SELECT
    ld.[ld_site] AS [Plant],
    ld.[ld_part] AS [Item_Number],
    SUM(CASE WHEN xz.[xxwezoned_area_id] = 'WIP' THEN ld.[ld_qty_oh] ELSE 0 END) AS [WIP_Qty]
  FROM [QADEE2798].[dbo].[ld_det] ld
  JOIN [QADEE2798].[dbo].[xxwezoned_det] xz ON ld.[ld_loc] = xz.[xxwezoned_loc]
  GROUP BY ld.[ld_site], ld.[ld_part]
) ia ON cp.[pt_site] = ia.[Plant] AND cp.[pt_part] = ia.[Item_Number]
```
- Potential table scan on `ld_det` (inventory detail)
- Join with zone mapping table
- GROUP BY aggregation

#### 3. Historical Transaction Analysis
```sql
LEFT JOIN (
  SELECT 
    tr_part,
    tr_site,
    CAST(ISNULL(AVG(CASE WHEN Daily_Qty > 0 THEN Daily_Qty END) * 7, 0) AS INT) AS [WIP_minimum],
    CAST(ISNULL(AVG(CASE WHEN Daily_Qty > 0 THEN Daily_Qty END) * 7, 0) AS INT) AS [WIP_maximum]
  FROM (
    SELECT
      tr_part,
      tr_site,
      CAST(tr_effdate AS DATE) AS tr_date,
      SUM(ABS(tr_qty)) AS Daily_Qty
    FROM [QADEE2798].[dbo].[tr_hist]
    WHERE tr_type = 'iss-wo'
      AND tr_effdate >= DATEADD(WEEK, -4, GETDATE())
    GROUP BY tr_part, tr_site, CAST(tr_effdate AS DATE)
  ) DailyData
  GROUP BY tr_part, tr_site
) wip ON cp.[pt_part] = wip.[tr_part] AND cp.[pt_site] = wip.[tr_site]
```
- Nested subquery with date filtering
- Multiple GROUP BY operations
- Potential scan of large `tr_hist` table

## Index Recommendations

### High Priority Indexes

1. **Part Master Optimization**
```sql
-- Covering index for part master queries
CREATE NONCLUSTERED INDEX IX_pt_mstr_covering
ON [dbo].[pt_mstr] ([pt_site], [pt_part], [pt_part_type])
INCLUDE ([pt_added], [pt_vend], [pt_dsgn_grp], [pt_prod_line], [pt_desc1])
```

2. **BOM Structure Optimization**
```sql
-- Parent parts index
CREATE NONCLUSTERED INDEX IX_ps_mstr_parent
ON [dbo].[ps_mstr] ([ps_end], [ps_par])
INCLUDE ([ps_op])

-- Child parts index  
CREATE NONCLUSTERED INDEX IX_ps_mstr_child
ON [dbo].[ps_mstr] ([ps_end], [ps_comp])
```

3. **Inventory Location Optimization**
```sql
-- Inventory detail with location
CREATE NONCLUSTERED INDEX IX_ld_det_site_part_loc
ON [dbo].[ld_det] ([ld_site], [ld_part], [ld_loc])
INCLUDE ([ld_qty_oh])

-- Zone mapping
CREATE NONCLUSTERED INDEX IX_xxwezoned_det_loc_area
ON [dbo].[xxwezoned_det] ([xxwezoned_loc], [xxwezoned_area_id])
```

4. **Transaction History Optimization**
```sql
-- Transaction history for WIP calculations
CREATE NONCLUSTERED INDEX IX_tr_hist_type_date_part
ON [dbo].[tr_hist] ([tr_type], [tr_effdate], [tr_part], [tr_site])
INCLUDE ([tr_qty])
```

5. **Cost Data Optimization**
```sql
-- Standard cost index
CREATE NONCLUSTERED INDEX IX_sct_det_site_part_sim
ON [dbo].[sct_det] ([sct_site], [sct_part], [sct_sim])
INCLUDE ([sct_cst_tot])
```

### Medium Priority Indexes

6. **Filtered Indexes for Active Data**
```sql
-- Active BOM entries only
CREATE NONCLUSTERED INDEX IX_ps_mstr_active_parent
ON [dbo].[ps_mstr] ([ps_par])
WHERE [ps_end] IS NULL

CREATE NONCLUSTERED INDEX IX_ps_mstr_active_child
ON [dbo].[ps_mstr] ([ps_comp])  
WHERE [ps_end] IS NULL
```

## Query Optimization Strategies

### 1. Materialized Views for Aggregations
Create indexed views for frequently accessed aggregations:

```sql
-- WIP quantities by part
CREATE VIEW vw_WIP_Quantities
WITH SCHEMABINDING
AS
SELECT
  ld.[ld_site] AS [Plant],
  ld.[ld_part] AS [Item_Number],
  SUM(CASE WHEN xz.[xxwezoned_area_id] = 'WIP' THEN ld.[ld_qty_oh] ELSE 0 END) AS [WIP_Qty],
  COUNT_BIG(*) AS cnt
FROM [dbo].[ld_det] ld
JOIN [dbo].[xxwezoned_det] xz ON ld.[ld_loc] = xz.[xxwezoned_loc]
GROUP BY ld.[ld_site], ld.[ld_part]

CREATE UNIQUE CLUSTERED INDEX IX_vw_WIP_Quantities
ON vw_WIP_Quantities ([Plant], [Item_Number])
```

### 2. Pre-computed WIP Min/Max Table
Create a nightly job to populate WIP minimums and maximums:

```sql
CREATE TABLE WIP_MinMax_Cache (
  Plant VARCHAR(10),
  Item_Number VARCHAR(50),
  WIP_minimum INT,
  WIP_maximum INT,
  LastUpdated DATETIME2,
  CONSTRAINT PK_WIP_MinMax PRIMARY KEY (Plant, Item_Number)
)

-- Refresh procedure (run nightly)
CREATE PROCEDURE sp_RefreshWIPMinMax
AS
BEGIN
  TRUNCATE TABLE WIP_MinMax_Cache
  
  INSERT INTO WIP_MinMax_Cache (Plant, Item_Number, WIP_minimum, WIP_maximum, LastUpdated)
  SELECT 
    tr_site AS Plant,
    tr_part AS Item_Number,
    CAST(ISNULL(AVG(CASE WHEN Daily_Qty > 0 THEN Daily_Qty END) * 7, 0) AS INT) AS WIP_minimum,
    CAST(ISNULL(AVG(CASE WHEN Daily_Qty > 0 THEN Daily_Qty END) * 7, 0) AS INT) AS WIP_maximum,
    GETDATE() AS LastUpdated
  FROM (
    SELECT
      tr_part,
      tr_site,
      CAST(tr_effdate AS DATE) AS tr_date,
      SUM(ABS(tr_qty)) AS Daily_Qty
    FROM [dbo].[tr_hist]
    WHERE tr_type = 'iss-wo'
      AND tr_effdate >= DATEADD(WEEK, -4, GETDATE())
    GROUP BY tr_part, tr_site, CAST(tr_effdate AS DATE)
  ) DailyData
  GROUP BY tr_part, tr_site
END
```

### 3. Simplified BOM Status Logic
Replace complex FULL OUTER JOIN with simpler approach:

```sql
-- Create BOM status cache table
CREATE TABLE BOM_Status_Cache (
  Plant VARCHAR(10),
  Item_Number VARCHAR(50),
  IsParent BIT,
  IsChild BIT,
  IsSFG BIT,
  LastUpdated DATETIME2,
  CONSTRAINT PK_BOM_Status PRIMARY KEY (Plant, Item_Number)
)
```

## Performance Testing Queries

### 1. Execution Plan Analysis
```sql
SET STATISTICS IO ON
SET STATISTICS TIME ON

-- Test main query with actual execution plan
-- [Include main query here]

SET STATISTICS IO OFF
SET STATISTICS TIME OFF
```

### 2. Index Usage Analysis
```sql
-- Check index usage stats
SELECT 
  i.name AS IndexName,
  s.user_seeks,
  s.user_scans,
  s.user_lookups,
  s.user_updates
FROM sys.dm_db_index_usage_stats s
JOIN sys.indexes i ON s.object_id = i.object_id AND s.index_id = i.index_id
JOIN sys.objects o ON i.object_id = o.object_id
WHERE o.name IN ('pt_mstr', 'ps_mstr', 'ld_det', 'tr_hist', 'sct_det', 'xxwezoned_det')
ORDER BY s.user_seeks + s.user_scans + s.user_lookups DESC
```

## Implementation Priority

### Phase 4A: Immediate Wins (Low Risk)
1. Create covering indexes for part master and cost tables
2. Add indexes for BOM structure queries
3. Implement query hints for problematic joins

### Phase 4B: Structural Changes (Medium Risk)
1. Create materialized view for WIP quantities
2. Implement WIP min/max cache table with nightly refresh
3. Add filtered indexes for active BOM entries

### Phase 4C: Advanced Optimization (Higher Risk)
1. Partition large tables by date (tr_hist) or site
2. Implement columnstore indexes for analytical queries
3. Consider query store for automatic plan optimization

## Monitoring and Validation

### Key Metrics to Track
- Query execution time (target: <2 seconds for main query)
- Logical reads (target: <50,000 per query)
- CPU time (target: <1000ms)
- Wait statistics (identify blocking/locking issues)

### Validation Queries
```sql
-- Before/after performance comparison
SELECT 
  execution_count,
  total_elapsed_time / execution_count AS avg_elapsed_time_ms,
  total_logical_reads / execution_count AS avg_logical_reads,
  total_worker_time / execution_count AS avg_cpu_time_ms
FROM sys.dm_exec_query_stats qs
CROSS APPLY sys.dm_exec_sql_text(qs.sql_handle) st
WHERE st.text LIKE '%inventory_query%'
```

## Expected Outcomes

### Performance Improvements
- 50-80% reduction in query execution time
- 60-90% reduction in logical reads
- Improved concurrency and reduced blocking
- More predictable response times

### Scalability Benefits
- Better performance as data volume grows
- Reduced impact on other database operations
- Improved cache efficiency
- Lower resource consumption

## Risk Mitigation

### Backup Strategy
- Full database backup before index creation
- Test all changes in development environment first
- Implement changes during maintenance window
- Monitor for 24-48 hours after implementation

### Rollback Plan
- Document all index creation scripts
- Prepare DROP INDEX statements for quick rollback
- Monitor key performance counters
- Have DBA on standby during implementation
