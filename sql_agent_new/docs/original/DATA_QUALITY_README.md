# Data Quality Reporting System

## Overview

The Data Quality Reporting System is a comprehensive solution for monitoring and improving data quality in the QADEE2798 database. It generates reports on various data quality criteria, providing insights into potential issues and areas for improvement.

## Reports

The system generates the following reports:

1. **Missing Cost Report** - Identifies items with missing cost information
2. **Missing Routing Report** - Identifies items with missing routing information
3. **WIP Overstock Report** - Identifies items with WIP overstock issues
4. **New Items Report** - Identifies items added within the last 30 days
5. **Inventory Check Report** - Identifies items with non-zero inventory
6. **Product Line Issues Report** - Identifies items in BOM with missing product line
7. **Group Issues Report** - Identifies items in BOM with missing group
8. **EPIC Status Report** - Identifies EPIC status items in BOM
9. **Operation Check Report** - Identifies items with multiple operations but not in both plants
10. **Cycle Count Due Report** - Identifies items due for cycle count
11. **Slow-Moving Report** - Identifies items with low movement (90-180 days)
12. **Item Type Error Report** - Identifies items where Item Type doesn't match BOM status

## System Components

The system consists of the following components:

- **data_quality_core.py** - Core module with base classes and utilities
- **data_quality_manager.py** - Main script for generating reports
- **reports/** - Directory containing individual report modules
- **schedule_reports.bat** - Batch script for scheduling report generation

## Usage

### Running Reports

To run all reports:

```bash
python data_quality_manager.py --report-type all
```

To run a specific report:

```bash
python data_quality_manager.py --report-type missing_cost
```

Available report types:
- `missing_cost`
- `missing_routing`
- `wip_overstock`
- `new_items`
- `inventory_check`
- `prod_line_issues`
- `group_issues`
- `epic_status`
- `operation_check`
- `cycle_count_due`
- `slow_moving`
- `item_type_error`

### Scheduling Reports

To schedule reports to run automatically, use the provided batch script with Windows Task Scheduler:

1. Open Windows Task Scheduler
2. Create a new task
3. Set the trigger (e.g., daily at 6:00 AM)
4. Set the action to run the `schedule_reports.bat` script
5. Configure additional settings as needed

## Report Outputs

Reports are saved to the `reports` directory with the following formats:

- **Detail Reports** - Excel files with detailed information for each issue
- **Summary Reports** - Excel files with summary information by various dimensions
- **Charts** - PNG files with visualizations of key metrics
- **Metadata** - JSON files with metadata for trend analysis

## Integration with Power BI

To integrate with Power BI:

1. Create a Power BI project
2. Connect to the Excel files in the `reports` directory
3. Create visualizations based on the report data
4. Set up automatic refresh to keep the dashboard up to date

## Maintenance

### Adding New Reports

To add a new report:

1. Create a new report module in the `reports` directory
2. Implement the report class, inheriting from `DataQualityReport`
3. Update `data_quality_manager.py` to include the new report

### Modifying Existing Reports

To modify an existing report:

1. Open the report module in the `reports` directory
2. Update the SQL query or report generation logic
3. Test the report to ensure it works correctly

## Troubleshooting

### Common Issues

- **Database Connection Errors** - Check the database connection settings in `data_quality_core.py`
- **Missing Tables** - Verify that the tables referenced in the SQL queries exist in the database
- **Report Generation Errors** - Check the log file for error messages

### Logging

The system logs information to the `data_quality.log` file, which can be used for troubleshooting.

## Contact

For questions or issues, contact the system administrator.
