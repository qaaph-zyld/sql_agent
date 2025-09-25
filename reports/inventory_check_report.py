"""
Inventory Check Report Module

This module generates reports on items with inventory (Total Inv <> 0).
"""

import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import logging

# Add parent directory to path to import core module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.data_quality.data_quality_core import DataQualityReport

logger = logging.getLogger(__name__)

class InventoryCheckReport(DataQualityReport):
    """Report on items with inventory"""
    
    def __init__(self, config_manager):
        super().__init__(config_manager)
        self.report_type = "inventory_check"
    
    def generate_report(self):
        """Generate report on items with inventory"""
        logger.info("Generating inventory check report")
        
        # Execute direct query for items with inventory
        query = """
        WITH InventoryInfo AS (
            SELECT 
                in_site,
                in_part,
                in_qty_oh AS [Total Qty Nettable],
                in_qty_nonet AS [Total Qty Nonet],
                in_qty_oh + in_qty_nonet AS [Total Inv]
            FROM 
                [QADEE2798].[dbo].[15]
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
            ii.[Total Qty Nettable],
            ii.[Total Qty Nonet],
            ii.[Total Inv],
            CASE WHEN ii.[Total Inv] <> 0 THEN 'Yes' ELSE 'No' END AS [Inventory Check],
            ii.[Total Inv] * ISNULL(sct.sct_cst_tot, 0) AS [Inventory Value]
        FROM 
            [QADEE2798].[dbo].[pt_mstr] pt
        LEFT JOIN 
            [QADEE2798].[dbo].[sct_det] sct ON pt.pt_part = sct.sct_part AND pt.pt_site = sct.sct_site AND sct.sct_sim = 'standard'
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
        LEFT JOIN
            InventoryInfo ii ON pt.pt_site = ii.in_site AND pt.pt_part = ii.in_part
        WHERE 
            pt.pt_part_type NOT IN ('xc','rc')
            AND ii.[Total Inv] <> 0
        ORDER BY 
            [Inventory Value] DESC
        """
        
        df = self.execute_query(query)
        logger.info(f"Found {len(df)} items with inventory")
        
        # Generate summary by group
        group_summary = df.groupby(['Group']).agg({
            'Item Number': 'count',
            'Inventory Value': 'sum'
        }).reset_index()
        group_summary.columns = ['Group', 'Count', 'Total Value']
        group_summary = group_summary.sort_values('Total Value', ascending=False)
        
        # Generate summary by plant
        plant_summary = df.groupby(['Plant']).agg({
            'Item Number': 'count',
            'Inventory Value': 'sum'
        }).reset_index()
        plant_summary.columns = ['Plant', 'Count', 'Total Value']
        
        # Generate summary by FG/SFG/RM
        type_summary = df.groupby(['FG/SFG/RM']).agg({
            'Item Number': 'count',
            'Inventory Value': 'sum'
        }).reset_index()
        type_summary.columns = ['FG/SFG/RM', 'Count', 'Total Value']
        type_summary = type_summary.sort_values('Total Value', ascending=False)
        
        # Export detailed report
        detail_file = f"{self.report_type}_detail_{self.report_date}.xlsx"
        self.export_to_excel(df, detail_file)
        
        # Export summary reports
        group_file = f"{self.report_type}_by_group_{self.report_date}.xlsx"
        self.export_to_excel(group_summary, group_file)
        
        plant_file = f"{self.report_type}_by_plant_{self.report_date}.xlsx"
        self.export_to_excel(plant_summary, plant_file)
        
        type_file = f"{self.report_type}_by_type_{self.report_date}.xlsx"
        self.export_to_excel(type_summary, type_file)
        
        # Generate charts
        self._generate_charts(group_summary, plant_summary, type_summary)
        
        # Calculate total inventory value
        total_inventory_value = df['Inventory Value'].sum()
        
        # Save metadata
        metadata = {
            'report_date': self.report_date,
            'total_count': len(df),
            'groups_affected': df['Group'].nunique(),
            'plants_affected': df['Plant'].nunique(),
            'types_affected': df['FG/SFG/RM'].nunique(),
            'total_inventory_value': float(total_inventory_value),
            'top_group': group_summary.iloc[0]['Group'] if not group_summary.empty else None,
            'top_group_count': int(group_summary.iloc[0]['Count']) if not group_summary.empty else 0,
            'top_group_value': float(group_summary.iloc[0]['Total Value']) if not group_summary.empty else 0
        }
        
        metadata_file = f"{self.report_type}_metadata_{self.report_date}.json"
        self.save_metadata(metadata, metadata_file)
        
        # Generate trend analysis if historical data is available
        self._generate_trend_analysis()
        
        logger.info("Inventory check report generation completed")
        
        return {
            'detail_file': detail_file,
            'group_file': group_file,
            'plant_file': plant_file,
            'type_file': type_file,
            'metadata': metadata
        }
    
    def _generate_charts(self, group_summary, plant_summary, type_summary):
        """Generate charts for the report"""
        # Group chart - top 10 by value
        plt.figure(figsize=(12, 6))
        top_groups = group_summary.head(10)
        sns.barplot(x='Group', y='Total Value', data=top_groups)
        plt.title('Top 10 Groups by Inventory Value')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        group_chart = f"{self.report_type}_group_chart_{self.report_date}.png"
        plt.savefig(os.path.join(self.output_dir, group_chart))
        plt.close()
        
        # Plant chart
        plt.figure(figsize=(10, 6))
        sns.barplot(x='Plant', y='Total Value', data=plant_summary)
        plt.title('Inventory Value by Plant')
        plt.tight_layout()
        
        plant_chart = f"{self.report_type}_plant_chart_{self.report_date}.png"
        plt.savefig(os.path.join(self.output_dir, plant_chart))
        plt.close()
        
        # Type chart
        plt.figure(figsize=(10, 6))
        sns.barplot(x='FG/SFG/RM', y='Total Value', data=type_summary)
        plt.title('Inventory Value by Item Type')
        plt.tight_layout()
        
        type_chart = f"{self.report_type}_type_chart_{self.report_date}.png"
        plt.savefig(os.path.join(self.output_dir, type_chart))
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
            
            # Generate trend chart for count
            plt.figure(figsize=(12, 6))
            sns.lineplot(x='date', y='total_count', data=trend_df)
            plt.title('Trend of Items with Inventory')
            plt.xlabel('Date')
            plt.ylabel('Number of Items')
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            count_trend_chart = f"{self.report_type}_count_trend_{self.report_date}.png"
            plt.savefig(os.path.join(self.output_dir, count_trend_chart))
            plt.close()
            
            # Generate trend chart for value
            plt.figure(figsize=(12, 6))
            sns.lineplot(x='date', y='total_inventory_value', data=trend_df)
            plt.title('Trend of Total Inventory Value')
            plt.xlabel('Date')
            plt.ylabel('Inventory Value')
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            value_trend_chart = f"{self.report_type}_value_trend_{self.report_date}.png"
            plt.savefig(os.path.join(self.output_dir, value_trend_chart))
            plt.close()
            
            logger.info(f"Generated trend analysis charts")

if __name__ == "__main__":
    # This allows the module to be run directly for testing
    from scripts.data_quality.data_quality_core import ConfigManager
    
    config_manager = ConfigManager()
    report = InventoryCheckReport(config_manager)
    report.generate_report()
