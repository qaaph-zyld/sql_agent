"""
Data Quality Report Manager

This script coordinates the generation of all data quality reports.
It imports and runs all report modules, generates a summary report,
and provides a command-line interface for running reports.
"""

import os
import sys
import pandas as pd
import logging
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
import argparse

# Import core modules
from scripts.data_quality.data_quality_core import ConfigManager, DataQualityReport

# Import report modules
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'reports'))
from reports.missing_cost_report import MissingCostReport
from reports.missing_routing_report import MissingRoutingReport
from reports.wip_overstock_report import WIPOverstockReport
from reports.new_items_report import NewItemsReport
from reports.inventory_check_report import InventoryCheckReport
from reports.prod_line_issues_report import ProdLineIssuesReport
from reports.group_issues_report import GroupIssuesReport
from reports.epic_status_report import EpicStatusReport
from reports.operation_check_report import OperationCheckReport
from reports.cycle_count_due_report import CycleCountDueReport
from reports.slow_moving_report import SlowMovingReport
from reports.item_type_error_report import ItemTypeErrorReport

# Configure logging
logger = logging.getLogger(__name__)

class ReportManager:
    """Manages the generation of all data quality reports"""
    
    def __init__(self):
        self.config_manager = ConfigManager()
        self.reports = {}
        self.report_date = datetime.now().strftime("%Y-%m-%d")
        self.output_dir = "reports"
        
        # Ensure output directory exists
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def generate_all_reports(self):
        """Generate all data quality reports"""
        logger.info("Starting generation of all data quality reports")
        
        # Generate missing cost report
        missing_cost_report = MissingCostReport(self.config_manager)
        self.reports['missing_cost'] = missing_cost_report.generate_report()
        
        # Generate missing routing report
        missing_routing_report = MissingRoutingReport(self.config_manager)
        self.reports['missing_routing'] = missing_routing_report.generate_report()
        
        # Generate WIP overstock report
        wip_overstock_report = WIPOverstockReport(self.config_manager)
        self.reports['wip_overstock'] = wip_overstock_report.generate_report()
        
        # Generate new items report
        new_items_report = NewItemsReport(self.config_manager)
        self.reports['new_items'] = new_items_report.generate_report()
        
        # Generate inventory check report
        inventory_check_report = InventoryCheckReport(self.config_manager)
        self.reports['inventory_check'] = inventory_check_report.generate_report()
        
        # Generate product line issues report
        prod_line_issues_report = ProdLineIssuesReport(self.config_manager)
        self.reports['prod_line_issues'] = prod_line_issues_report.generate_report()
        
        # Generate group issues report
        group_issues_report = GroupIssuesReport(self.config_manager)
        self.reports['group_issues'] = group_issues_report.generate_report()
        
        # Generate EPIC status report
        epic_status_report = EpicStatusReport(self.config_manager)
        self.reports['epic_status'] = epic_status_report.generate_report()
        
        # Generate operation check report
        operation_check_report = OperationCheckReport(self.config_manager)
        self.reports['operation_check'] = operation_check_report.generate_report()
        
        # Generate cycle count due report
        cycle_count_due_report = CycleCountDueReport(self.config_manager)
        self.reports['cycle_count_due'] = cycle_count_due_report.generate_report()
        
        # Generate slow moving inventory report
        slow_moving_report = SlowMovingReport(self.config_manager)
        self.reports['slow_moving'] = slow_moving_report.generate_report()
        
        # Generate item type error report
        item_type_error_report = ItemTypeErrorReport(self.config_manager)
        self.reports['item_type_error'] = item_type_error_report.generate_report()
        
        # Generate summary report
        self.generate_summary_report()
        
        logger.info("All data quality reports generated successfully")
        
        return self.reports
    
    def generate_report_by_type(self, report_type):
        """Generate a specific report by type"""
        logger.info(f"Generating report for type: {report_type}")
        
        if report_type == 'missing_cost':
            report = MissingCostReport(self.config_manager)
            self.reports['missing_cost'] = report.generate_report()
        
        elif report_type == 'missing_routing':
            report = MissingRoutingReport(self.config_manager)
            self.reports['missing_routing'] = report.generate_report()
        
        elif report_type == 'wip_overstock':
            report = WIPOverstockReport(self.config_manager)
            self.reports['wip_overstock'] = report.generate_report()
        
        elif report_type == 'new_items':
            report = NewItemsReport(self.config_manager)
            self.reports['new_items'] = report.generate_report()
        
        elif report_type == 'inventory_check':
            report = InventoryCheckReport(self.config_manager)
            self.reports['inventory_check'] = report.generate_report()
        
        elif report_type == 'prod_line_issues':
            report = ProdLineIssuesReport(self.config_manager)
            self.reports['prod_line_issues'] = report.generate_report()
        
        elif report_type == 'group_issues':
            report = GroupIssuesReport(self.config_manager)
            self.reports['group_issues'] = report.generate_report()
        
        elif report_type == 'epic_status':
            report = EpicStatusReport(self.config_manager)
            self.reports['epic_status'] = report.generate_report()
        
        elif report_type == 'operation_check':
            report = OperationCheckReport(self.config_manager)
            self.reports['operation_check'] = report.generate_report()
            
        elif report_type == 'cycle_count_due':
            report = CycleCountDueReport(self.config_manager)
            self.reports['cycle_count_due'] = report.generate_report()
            
        elif report_type == 'slow_moving':
            report = SlowMovingReport(self.config_manager)
            self.reports['slow_moving'] = report.generate_report()
            
        elif report_type == 'item_type_error':
            report = ItemTypeErrorReport(self.config_manager)
            self.reports['item_type_error'] = report.generate_report()
        
        else:
            logger.error(f"Unknown report type: {report_type}")
            raise ValueError(f"Unknown report type: {report_type}")
        
        # Generate summary report
        self.generate_summary_report()
        
        logger.info(f"Report for type {report_type} generated successfully")
        
        return self.reports
    
    def generate_summary_report(self):
        """Generate summary report of all data quality issues"""
        logger.info("Generating summary report")
        
        summary_data = []
        
        # Collect summary data from all reports
        if 'missing_cost' in self.reports:
            metadata = self.reports['missing_cost']['metadata']
            summary_data.append({
                'Issue Type': 'Missing Cost Information',
                'Count': metadata['total_count'],
                'Groups Affected': metadata['groups_affected'],
                'Plants Affected': metadata['plants_affected'],
                'Top Group': metadata['top_group'],
                'Top Group Count': metadata['top_group_count']
            })
        
        if 'missing_routing' in self.reports:
            metadata = self.reports['missing_routing']['metadata']
            summary_data.append({
                'Issue Type': 'Missing Routing Information',
                'Count': metadata['total_count'],
                'Groups Affected': metadata['groups_affected'],
                'Plants Affected': metadata['plants_affected'],
                'Top Group': metadata['top_group'],
                'Top Group Count': metadata['top_group_count']
            })
            
        if 'wip_overstock' in self.reports:
            metadata = self.reports['wip_overstock']['metadata']
            summary_data.append({
                'Issue Type': 'WIP Overstock Issues',
                'Count': metadata['total_count'],
                'Groups Affected': metadata['groups_affected'],
                'Plants Affected': metadata['plants_affected'],
                'Total Value': metadata['total_overstock_value'],
                'Top Group': metadata['top_group'],
                'Top Group Count': metadata['top_group_count']
            })
            
        if 'new_items' in self.reports:
            metadata = self.reports['new_items']['metadata']
            summary_data.append({
                'Issue Type': 'New Items (Last 30 Days)',
                'Count': metadata['total_count'],
                'Groups Affected': metadata['groups_affected'],
                'Plants Affected': metadata['plants_affected'],
                'Top Group': metadata['top_group'],
                'Top Group Count': metadata['top_group_count']
            })
            
        if 'inventory_check' in self.reports:
            metadata = self.reports['inventory_check']['metadata']
            summary_data.append({
                'Issue Type': 'Items with Inventory',
                'Count': metadata['total_count'],
                'Groups Affected': metadata['groups_affected'],
                'Plants Affected': metadata['plants_affected'],
                'Total Value': metadata.get('total_inventory_value', 0),
                'Top Group': metadata['top_group'],
                'Top Group Count': metadata['top_group_count']
            })
            
        if 'prod_line_issues' in self.reports:
            metadata = self.reports['prod_line_issues']['metadata']
            summary_data.append({
                'Issue Type': 'Missing Product Line Issues',
                'Count': metadata['total_count'],
                'Groups Affected': metadata['groups_affected'],
                'Plants Affected': metadata['plants_affected'],
                'Top Group': metadata['top_group'],
                'Top Group Count': metadata['top_group_count']
            })
            
        if 'group_issues' in self.reports:
            metadata = self.reports['group_issues']['metadata']
            summary_data.append({
                'Issue Type': 'Missing Group Issues',
                'Count': metadata['total_count'],
                'Prod Lines Affected': metadata['prodlines_affected'],
                'Plants Affected': metadata['plants_affected'],
                'Top Prod Line': metadata['top_prodline'],
                'Top Prod Line Count': metadata['top_prodline_count']
            })
            
        if 'epic_status' in self.reports:
            metadata = self.reports['epic_status']['metadata']
            summary_data.append({
                'Issue Type': 'EPIC Status Items in BOM',
                'Count': metadata['total_count'],
                'Groups Affected': metadata['groups_affected'],
                'Plants Affected': metadata['plants_affected'],
                'Top Group': metadata['top_group'],
                'Top Group Count': metadata['top_group_count']
            })
            
        if 'operation_check' in self.reports:
            metadata = self.reports['operation_check']['metadata']
            summary_data.append({
                'Issue Type': 'Operation Check Issues',
                'Count': metadata['total_count'],
                'Groups Affected': metadata['groups_affected'],
                'Plants Affected': metadata['plants_affected'],
                'Top Group': metadata['top_group'],
                'Top Group Count': metadata['top_group_count']
            })
            
        if 'cycle_count_due' in self.reports:
            metadata = self.reports['cycle_count_due']['metadata']
            summary_data.append({
                'Issue Type': 'Cycle Count Due Items',
                'Count': metadata['total_count'],
                'Groups Affected': metadata['groups_affected'],
                'Plants Affected': metadata['plants_affected'],
                'Avg Days Overdue': metadata['avg_days_overdue'],
                'Never Counted': metadata['never_counted'],
                'A Items Due': metadata['a_items_due'],
                'B Items Due': metadata['b_items_due'],
                'C Items Due': metadata['c_items_due'],
                'Top Group': metadata['top_group'],
                'Top Group Count': metadata['top_group_count']
            })
            
        if 'slow_moving' in self.reports:
            metadata = self.reports['slow_moving']['metadata']
            summary_data.append({
                'Issue Type': 'Slow-Moving Inventory',
                'Count': metadata['total_count'],
                'Groups Affected': metadata['groups_affected'],
                'Total Value': metadata['total_value'],
                'Warning Count': metadata['warning_count'],
                'Critical Count': metadata['critical_count'],
                'No Movement Count': metadata['no_movement_count'],
                'Top Group': metadata['top_group'],
                'Top Group Count': metadata['top_group_count'],
                'Top Group Value': metadata['top_group_value']
            })
            
        if 'item_type_error' in self.reports:
            metadata = self.reports['item_type_error']['metadata']
            summary_data.append({
                'Issue Type': 'Item Type Errors',
                'Count': metadata['total_count'],
                'Groups Affected': metadata['groups_affected'],
                'Plants Affected': metadata['plants_affected'],
                'Error Types': metadata['error_types'],
                'Top Error': metadata['top_error'],
                'Top Error Count': metadata['top_error_count'],
                'Top Group': metadata['top_group'],
                'Top Group Count': metadata['top_group_count']
            })
        
        # Create summary DataFrame
        summary_df = pd.DataFrame(summary_data)
        
        # Export summary report
        summary_file = f"data_quality_summary_{self.report_date}.xlsx"
        output_path = os.path.join(self.output_dir, summary_file)
        summary_df.to_excel(output_path, index=False)
        
        logger.info(f"Generated summary report: {output_path}")
        
        # Generate summary chart
        if not summary_df.empty:
            plt.figure(figsize=(10, 6))
            sns.barplot(x='Issue Type', y='Count', data=summary_df)
            plt.title('Data Quality Issues Summary')
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            chart_file = f"data_quality_summary_chart_{self.report_date}.png"
            chart_path = os.path.join(self.output_dir, chart_file)
            plt.savefig(chart_path)
            plt.close()
            
            logger.info(f"Generated summary chart: {chart_path}")
        
        return summary_file

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Generate data quality reports')
    
    parser.add_argument(
        '--report-type',
        choices=[
            'all', 
            'missing_cost', 
            'missing_routing', 
            'wip_overstock',
            'new_items',
            'inventory_check',
            'prod_line_issues',
            'group_issues',
            'epic_status',
            'operation_check',
            'cycle_count_due',
            'slow_moving',
            'item_type_error'
        ],
        default='all',
        help='Type of report to generate (default: all)'
    )
    
    return parser.parse_args()

def main():
    """Main function"""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("data_quality.log"),
            logging.StreamHandler()
        ]
    )
    
    logger.info("Starting data quality report generation")
    
    # Parse command line arguments
    args = parse_arguments()
    
    # Create report manager
    report_manager = ReportManager()
    
    # Generate reports based on command line arguments
    if args.report_type == 'all':
        reports = report_manager.generate_all_reports()
    else:
        reports = report_manager.generate_report_by_type(args.report_type)
    
    logger.info("Data quality report generation completed")
    
    # Print summary of generated reports
    print("\nData Quality Reports Generated:")
    print("==============================")
    
    for report_type, report_data in reports.items():
        if report_type == 'missing_cost':
            print(f"\nMissing Cost Report:")
            print(f"  Total items with missing cost: {report_data['metadata']['total_count']}")
            print(f"  Groups affected: {report_data['metadata']['groups_affected']}")
            print(f"  Plants affected: {report_data['metadata']['plants_affected']}")
            print(f"  Top group: {report_data['metadata']['top_group']} ({report_data['metadata']['top_group_count']} items)")
        
        elif report_type == 'missing_routing':
            print(f"\nMissing Routing Report:")
            print(f"  Total items with missing routing: {report_data['metadata']['total_count']}")
            print(f"  Groups affected: {report_data['metadata']['groups_affected']}")
            print(f"  Plants affected: {report_data['metadata']['plants_affected']}")
            print(f"  Top group: {report_data['metadata']['top_group']} ({report_data['metadata']['top_group_count']} items)")
            
        elif report_type == 'wip_overstock':
            print(f"\nWIP Overstock Report:")
            print(f"  Total items with WIP overstock issues: {report_data['metadata']['total_count']}")
            print(f"  Total overstock value: ${report_data['metadata']['total_overstock_value']:,.2f}")
            print(f"  Groups affected: {report_data['metadata']['groups_affected']}")
            print(f"  Plants affected: {report_data['metadata']['plants_affected']}")
            print(f"  Top group: {report_data['metadata']['top_group']} (${report_data['metadata']['top_group_value']:,.2f})")

    
    print("\nReports saved to the 'reports' directory.")

if __name__ == "__main__":
    main()
