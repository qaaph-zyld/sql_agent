"""
Slow-Moving Inventory Report Module

This module generates reports on items with slow-moving inventory.
It identifies items with no movement in the last 90-180 days.
"""

import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import logging

# Add parent directory to path to import core module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.data_quality.data_quality_core import DataQualityReport

logger = logging.getLogger(__name__)

class SlowMovingReport(DataQualityReport):
    """Report on items with slow-moving inventory"""
    
    def __init__(self, config_manager):
        super().__init__(config_manager)
        self.report_type = "slow_moving"
    
    def generate_report(self):
        """Generate report on items with slow-moving inventory"""
        logger.info("Generating slow-moving inventory report")
        
        # Execute direct query for items with slow-moving inventory
        query = """
        WITH LastMovement AS (
            SELECT 
                tr_part,
                tr_site,
                MAX(tr_effdate) AS last_movement_date
            FROM 
                [QADEE2798].[dbo].[tr_hist]
            WHERE 
                tr_type IN ('ISS-WO', 'ISS-SO', 'RCT-PO')  -- Issue to Work Order, Issue to Sales Order, Receipt from PO
            GROUP BY 
                tr_part, tr_site
        )
        SELECT 
            pt.pt_part AS [Item Number], 
            pt.pt_desc1 AS [Description], 
            pt.pt_group AS [Group], 
            pt.pt_prod_line AS [Prod Line], 
            CASE 
                WHEN b.Parent = 'Yes' AND b.Child = 'No' THEN 'FG'
                WHEN b.SFG = 'Yes' THEN 'SFG'
                WHEN b.Parent = 'No' AND b.Child = 'Yes' THEN 'RM'
                ELSE 'No BOM'
            END AS [FG/SFG/RM],
            pt.pt_site AS [Plant],
            ISNULL(sct.sct_cst_tot, 0) AS [Standard Cost],
            pt.pt_abc AS [ABC Code],
            inv.[Total Inv] AS [Inventory Quantity],
            inv.[Total Inv] * ISNULL(sct.sct_cst_tot, 0) AS [Inventory Value],
            lm.last_movement_date AS [Last Movement Date],
            DATEDIFF(day, lm.last_movement_date, GETDATE()) AS [Days Since Last Movement],
            CASE 
                WHEN lm.last_movement_date IS NULL THEN 'No Movement History'
                WHEN DATEDIFF(day, lm.last_movement_date, GETDATE()) BETWEEN 90 AND 180 THEN 'Warning (90-180 days)'
                WHEN DATEDIFF(day, lm.last_movement_date, GETDATE()) > 180 THEN 'Critical (>180 days)'
                ELSE 'Normal'
            END AS [Slow-moving Warning]
        FROM 
            [QADEE2798].[dbo].[pt_mstr] pt
        LEFT JOIN 
            [QADEE2798].[dbo].[sct_det] sct ON pt.pt_part = sct.sct_part AND pt.pt_site = sct.sct_site AND sct.sct_sim = 'standard'
        LEFT JOIN 
            LastMovement lm ON pt.pt_part = lm.tr_part AND pt.pt_site = lm.tr_site
        LEFT JOIN (
            SELECT 
                ps_par AS [Item Number],
                '2798' AS [Plant],
                'Yes' AS [Parent],
                CASE WHEN EXISTS (
                    SELECT 1 FROM [QADEE2798].[dbo].[ps_mstr] ps2 
                    WHERE ps2.ps_comp = ps1.ps_par AND ps2.ps_end IS NULL
                ) THEN 'Yes' ELSE 'No' END AS [Child],
                CASE WHEN EXISTS (
                    SELECT 1 FROM [QADEE2798].[dbo].[ps_mstr] ps2 
                    WHERE ps2.ps_comp = ps1.ps_par AND ps2.ps_end IS NULL
                ) THEN 'Yes' ELSE 'No' END AS [SFG]
            FROM 
                [QADEE2798].[dbo].[ps_mstr] ps1
            WHERE 
                ps1.ps_end IS NULL
            GROUP BY 
                ps1.ps_par
        ) b ON pt.pt_part = b.[Item Number] AND pt.pt_site = b.[Plant]
        LEFT JOIN (
            SELECT 
                in_part,
                in_site,
                in_qty_oh + in_qty_nonet AS [Total Inv]
            FROM 
                [QADEE2798].[dbo].[15]
        ) inv ON pt.pt_part = inv.in_part AND pt.pt_site = inv.in_site
        WHERE 
            pt.pt_part_type NOT IN ('xc','rc')
            AND inv.[Total Inv] > 0  -- Only items with inventory
            AND (
                lm.last_movement_date IS NULL  -- No movement history
                OR DATEDIFF(day, lm.last_movement_date, GETDATE()) >= 90  -- No movement in at least 90 days
            )
        ORDER BY 
            [Days Since Last Movement] DESC, [Inventory Value] DESC
        """
        
        df = self.execute_query(query)
        logger.info(f"Found {len(df)} items with slow-moving inventory")
        
        # Convert Last Movement Date to datetime
        df['Last Movement Date'] = pd.to_datetime(df['Last Movement Date'])
        
        # Add movement age category
        df['Movement Age Category'] = pd.cut(
            df['Days Since Last Movement'],
            bins=[-1, 90, 180, 365, 730, float('inf')],
            labels=['<90 days', '90-180 days', '181-365 days', '1-2 years', '>2 years']
        )
        
        # Generate summary by movement age category
        age_summary = df.groupby(['Movement Age Category']).agg({
            'Item Number': 'count',
            'Inventory Value': 'sum'
        }).reset_index()
        age_summary.columns = ['Movement Age Category', 'Count', 'Total Value']
        
        # Generate summary by ABC code
        abc_summary = df.groupby(['ABC Code']).agg({
            'Item Number': 'count',
            'Inventory Value': 'sum'
        }).reset_index()
        abc_summary.columns = ['ABC Code', 'Count', 'Total Value']
        
        # Generate summary by group
        group_summary = df.groupby(['Group']).agg({
            'Item Number': 'count',
            'Inventory Value': 'sum'
        }).reset_index()
        group_summary.columns = ['Group', 'Count', 'Total Value']
        group_summary = group_summary.sort_values('Total Value', ascending=False)
        
        # Generate summary by FG/SFG/RM
        type_summary = df.groupby(['FG/SFG/RM']).agg({
            'Item Number': 'count',
            'Inventory Value': 'sum'
        }).reset_index()
        type_summary.columns = ['FG/SFG/RM', 'Count', 'Total Value']
        type_summary = type_summary.sort_values('Total Value', ascending=False)
        
        # Generate summary by slow-moving warning
        warning_summary = df.groupby(['Slow-moving Warning']).agg({
            'Item Number': 'count',
            'Inventory Value': 'sum'
        }).reset_index()
        warning_summary.columns = ['Slow-moving Warning', 'Count', 'Total Value']
        
        # Export detailed report
        detail_file = f"{self.report_type}_detail_{self.report_date}.xlsx"
        self.export_to_excel(df, detail_file)
        
        # Export summary reports
        age_file = f"{self.report_type}_by_age_{self.report_date}.xlsx"
        self.export_to_excel(age_summary, age_file)
        
        abc_file = f"{self.report_type}_by_abc_{self.report_date}.xlsx"
        self.export_to_excel(abc_summary, abc_file)
        
        group_file = f"{self.report_type}_by_group_{self.report_date}.xlsx"
        self.export_to_excel(group_summary, group_file)
        
        type_file = f"{self.report_type}_by_type_{self.report_date}.xlsx"
        self.export_to_excel(type_summary, type_file)
        
        warning_file = f"{self.report_type}_by_warning_{self.report_date}.xlsx"
        self.export_to_excel(warning_summary, warning_file)
        
        # Generate charts
        self._generate_charts(age_summary, abc_summary, group_summary, type_summary, warning_summary)
        
        # Calculate total slow-moving inventory value
        total_value = df['Inventory Value'].sum()
        
        # Save metadata
        metadata = {
            'report_date': self.report_date,
            'total_count': len(df),
            'groups_affected': df['Group'].nunique(),
            'total_value': float(total_value),
            'warning_count': int(df[df['Slow-moving Warning'] == 'Warning (90-180 days)'].shape[0]),
            'critical_count': int(df[df['Slow-moving Warning'] == 'Critical (>180 days)'].shape[0]),
            'no_movement_count': int(df[df['Slow-moving Warning'] == 'No Movement History'].shape[0]),
            'top_group': group_summary.iloc[0]['Group'] if not group_summary.empty else None,
            'top_group_count': int(group_summary.iloc[0]['Count']) if not group_summary.empty else 0,
            'top_group_value': float(group_summary.iloc[0]['Total Value']) if not group_summary.empty else 0
        }
        
        metadata_file = f"{self.report_type}_metadata_{self.report_date}.json"
        self.save_metadata(metadata, metadata_file)
        
        # Generate trend analysis if historical data is available
        self._generate_trend_analysis()
        
        logger.info("Slow-moving inventory report generation completed")
        
        return {
            'detail_file': detail_file,
            'age_file': age_file,
            'abc_file': abc_file,
            'group_file': group_file,
            'type_file': type_file,
            'warning_file': warning_file,
            'metadata': metadata
        }
    
    def _generate_charts(self, age_summary, abc_summary, group_summary, type_summary, warning_summary):
        """Generate charts for the report"""
        # Age category chart
        plt.figure(figsize=(12, 6))
        sns.barplot(x='Movement Age Category', y='Total Value', data=age_summary)
        plt.title('Slow-Moving Inventory Value by Age Category')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        age_chart = f"{self.report_type}_age_chart_{self.report_date}.png"
        plt.savefig(os.path.join(self.output_dir, age_chart))
        plt.close()
        
        # ABC chart
        plt.figure(figsize=(10, 6))
        sns.barplot(x='ABC Code', y='Total Value', data=abc_summary)
        plt.title('Slow-Moving Inventory Value by ABC Code')
        plt.tight_layout()
        
        abc_chart = f"{self.report_type}_abc_chart_{self.report_date}.png"
        plt.savefig(os.path.join(self.output_dir, abc_chart))
        plt.close()
        
        # Group chart - top 10
        plt.figure(figsize=(12, 6))
        top_groups = group_summary.head(10)
        sns.barplot(x='Group', y='Total Value', data=top_groups)
        plt.title('Top 10 Groups by Slow-Moving Inventory Value')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        group_chart = f"{self.report_type}_group_chart_{self.report_date}.png"
        plt.savefig(os.path.join(self.output_dir, group_chart))
        plt.close()
        
        # Type chart
        plt.figure(figsize=(10, 6))
        sns.barplot(x='FG/SFG/RM', y='Total Value', data=type_summary)
        plt.title('Slow-Moving Inventory Value by Item Type')
        plt.tight_layout()
        
        type_chart = f"{self.report_type}_type_chart_{self.report_date}.png"
        plt.savefig(os.path.join(self.output_dir, type_chart))
        plt.close()
        
        # Warning chart
        plt.figure(figsize=(12, 6))
        sns.barplot(x='Slow-moving Warning', y='Total Value', data=warning_summary)
        plt.title('Slow-Moving Inventory Value by Warning Category')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        warning_chart = f"{self.report_type}_warning_chart_{self.report_date}.png"
        plt.savefig(os.path.join(self.output_dir, warning_chart))
        plt.close()
    
    def _generate_trend_analysis(self):
        """Generate trend analysis based on historical data"""
        historical_data = self.get_historical_data(self.report_type, days=90)
        
        if len(historical_data) > 1:
            # Create DataFrame from historical data
            trend_df = pd.DataFrame(historical_data)
            
            # Sort by date
            trend_df['date'] = pd.to_datetime(trend_df['date'])
            trend_df = trend_df.sort_values('date')
            
            # Generate trend chart for total count
            plt.figure(figsize=(12, 6))
            sns.lineplot(x='date', y='total_count', data=trend_df)
            plt.title('Trend of Slow-Moving Inventory Items')
            plt.xlabel('Date')
            plt.ylabel('Number of Items')
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            count_trend_chart = f"{self.report_type}_count_trend_{self.report_date}.png"
            plt.savefig(os.path.join(self.output_dir, count_trend_chart))
            plt.close()
            
            # Generate trend chart for total value
            plt.figure(figsize=(12, 6))
            sns.lineplot(x='date', y='total_value', data=trend_df)
            plt.title('Trend of Slow-Moving Inventory Value')
            plt.xlabel('Date')
            plt.ylabel('Inventory Value')
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            value_trend_chart = f"{self.report_type}_value_trend_{self.report_date}.png"
            plt.savefig(os.path.join(self.output_dir, value_trend_chart))
            plt.close()
            
            # Generate trend chart for warning/critical breakdown
            plt.figure(figsize=(12, 6))
            sns.lineplot(x='date', y='warning_count', data=trend_df, label='Warning (90-180 days)')
            sns.lineplot(x='date', y='critical_count', data=trend_df, label='Critical (>180 days)')
            sns.lineplot(x='date', y='no_movement_count', data=trend_df, label='No Movement History')
            plt.title('Trend of Slow-Moving Inventory by Category')
            plt.xlabel('Date')
            plt.ylabel('Number of Items')
            plt.legend()
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            category_trend_chart = f"{self.report_type}_category_trend_{self.report_date}.png"
            plt.savefig(os.path.join(self.output_dir, category_trend_chart))
            plt.close()
            
            logger.info(f"Generated trend analysis charts")

if __name__ == "__main__":
    # This allows the module to be run directly for testing
    from scripts.data_quality.data_quality_core import ConfigManager
    
    config_manager = ConfigManager()
    report = SlowMovingReport(config_manager)
    report.generate_report()
