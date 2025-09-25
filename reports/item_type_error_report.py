"""
Item Type Error Report Module

This module generates reports on items where the Item Type doesn't match BOM status.
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

class ItemTypeErrorReport(DataQualityReport):
    """Report on items where Item Type doesn't match BOM status"""
    
    def __init__(self, config_manager):
        super().__init__(config_manager)
        self.report_type = "item_type_error"
    
    def generate_report(self):
        """Generate report on items with item type errors"""
        logger.info("Generating item type error report")
        
        # Execute direct query for items with item type errors
        query = """
        WITH BOMStatus AS (
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
        )
        SELECT 
            pt.pt_part AS [Item Number], 
            pt.pt_desc1 AS [Description], 
            pt.pt_group AS [Group], 
            pt.pt_prod_line AS [Prod Line], 
            pt.pt_part_type AS [Item Type],
            CASE 
                WHEN b.Parent = 'Yes' AND b.Child = 'No' THEN 'FG'
                WHEN b.SFG = 'Yes' THEN 'SFG'
                WHEN b.Parent = 'No' AND b.Child = 'Yes' THEN 'RM'
                ELSE 'No BOM'
            END AS [BOM Status],
            pt.pt_site AS [Plant],
            ISNULL(sct.sct_cst_tot, 0) AS [Standard Cost],
            CASE
                WHEN (pt.pt_part_type = 'fg' AND (b.Parent = 'No' OR b.Parent IS NULL)) THEN 'FG type but not a parent in BOM'
                WHEN (pt.pt_part_type = 'rm' AND b.Parent = 'Yes') THEN 'RM type but is a parent in BOM'
                WHEN (pt.pt_part_type = 'fg' AND b.SFG = 'Yes') THEN 'FG type but is a SFG in BOM'
                WHEN (pt.pt_part_type = 'rm' AND b.SFG = 'Yes') THEN 'RM type but is a SFG in BOM'
                WHEN (pt.pt_part_type = 'sf' AND b.SFG = 'No') THEN 'SF type but not a SFG in BOM'
                WHEN (pt.pt_part_type = 'sf' AND b.Parent = 'No') THEN 'SF type but not a parent in BOM'
                WHEN (pt.pt_part_type = 'sf' AND b.Child = 'No') THEN 'SF type but not a child in BOM'
                ELSE NULL
            END AS [Item Type Error]
        FROM 
            [QADEE2798].[dbo].[pt_mstr] pt
        LEFT JOIN 
            [QADEE2798].[dbo].[sct_det] sct ON pt.pt_part = sct.sct_part AND pt.pt_site = sct.sct_site AND sct.sct_sim = 'standard'
        LEFT JOIN 
            BOMStatus b ON pt.pt_part = b.[Item Number] AND pt.pt_site = b.[Plant]
        WHERE 
            pt.pt_part_type NOT IN ('xc','rc')
            AND (
                (pt.pt_part_type = 'fg' AND (b.Parent = 'No' OR b.Parent IS NULL))
                OR (pt.pt_part_type = 'rm' AND b.Parent = 'Yes')
                OR (pt.pt_part_type = 'fg' AND b.SFG = 'Yes')
                OR (pt.pt_part_type = 'rm' AND b.SFG = 'Yes')
                OR (pt.pt_part_type = 'sf' AND b.SFG = 'No')
                OR (pt.pt_part_type = 'sf' AND b.Parent = 'No')
                OR (pt.pt_part_type = 'sf' AND b.Child = 'No')
            )
        ORDER BY 
            pt.pt_part_type, pt.pt_group, pt.pt_part
        """
        
        df = self.execute_query(query)
        logger.info(f"Found {len(df)} items with item type errors")
        
        # Generate summary by error type
        error_summary = df.groupby(['Item Type Error']).size().reset_index(name='Count')
        error_summary = error_summary.sort_values('Count', ascending=False)
        
        # Generate summary by item type
        type_summary = df.groupby(['Item Type']).size().reset_index(name='Count')
        type_summary = type_summary.sort_values('Count', ascending=False)
        
        # Generate summary by group
        group_summary = df.groupby(['Group']).size().reset_index(name='Count')
        group_summary = group_summary.sort_values('Count', ascending=False)
        
        # Generate summary by BOM status
        bom_summary = df.groupby(['BOM Status']).size().reset_index(name='Count')
        bom_summary = bom_summary.sort_values('Count', ascending=False)
        
        # Export detailed report
        detail_file = f"{self.report_type}_detail_{self.report_date}.xlsx"
        self.export_to_excel(df, detail_file)
        
        # Export summary reports
        error_file = f"{self.report_type}_by_error_{self.report_date}.xlsx"
        self.export_to_excel(error_summary, error_file)
        
        type_file = f"{self.report_type}_by_itemtype_{self.report_date}.xlsx"
        self.export_to_excel(type_summary, type_file)
        
        group_file = f"{self.report_type}_by_group_{self.report_date}.xlsx"
        self.export_to_excel(group_summary, group_file)
        
        bom_file = f"{self.report_type}_by_bomstatus_{self.report_date}.xlsx"
        self.export_to_excel(bom_summary, bom_file)
        
        # Generate charts
        self._generate_charts(error_summary, type_summary, group_summary, bom_summary)
        
        # Save metadata
        metadata = {
            'report_date': self.report_date,
            'total_count': len(df),
            'groups_affected': df['Group'].nunique(),
            'plants_affected': df['Plant'].nunique(),
            'error_types': df['Item Type Error'].nunique(),
            'top_error': error_summary.iloc[0]['Item Type Error'] if not error_summary.empty else None,
            'top_error_count': int(error_summary.iloc[0]['Count']) if not error_summary.empty else 0,
            'top_group': group_summary.iloc[0]['Group'] if not group_summary.empty else None,
            'top_group_count': int(group_summary.iloc[0]['Count']) if not group_summary.empty else 0
        }
        
        metadata_file = f"{self.report_type}_metadata_{self.report_date}.json"
        self.save_metadata(metadata, metadata_file)
        
        # Generate trend analysis if historical data is available
        self._generate_trend_analysis()
        
        logger.info("Item type error report generation completed")
        
        return {
            'detail_file': detail_file,
            'error_file': error_file,
            'type_file': type_file,
            'group_file': group_file,
            'bom_file': bom_file,
            'metadata': metadata
        }
    
    def _generate_charts(self, error_summary, type_summary, group_summary, bom_summary):
        """Generate charts for the report"""
        # Error type chart
        plt.figure(figsize=(14, 6))
        sns.barplot(x='Item Type Error', y='Count', data=error_summary)
        plt.title('Item Type Errors by Category')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        error_chart = f"{self.report_type}_error_chart_{self.report_date}.png"
        plt.savefig(os.path.join(self.output_dir, error_chart))
        plt.close()
        
        # Item type chart
        plt.figure(figsize=(10, 6))
        sns.barplot(x='Item Type', y='Count', data=type_summary)
        plt.title('Item Type Errors by Item Type')
        plt.tight_layout()
        
        type_chart = f"{self.report_type}_itemtype_chart_{self.report_date}.png"
        plt.savefig(os.path.join(self.output_dir, type_chart))
        plt.close()
        
        # Group chart - top 10
        plt.figure(figsize=(12, 6))
        top_groups = group_summary.head(10)
        sns.barplot(x='Group', y='Count', data=top_groups)
        plt.title('Top 10 Groups with Item Type Errors')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        group_chart = f"{self.report_type}_group_chart_{self.report_date}.png"
        plt.savefig(os.path.join(self.output_dir, group_chart))
        plt.close()
        
        # BOM status chart
        plt.figure(figsize=(10, 6))
        sns.barplot(x='BOM Status', y='Count', data=bom_summary)
        plt.title('Item Type Errors by BOM Status')
        plt.tight_layout()
        
        bom_chart = f"{self.report_type}_bomstatus_chart_{self.report_date}.png"
        plt.savefig(os.path.join(self.output_dir, bom_chart))
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
            
            # Generate trend chart
            plt.figure(figsize=(12, 6))
            sns.lineplot(x='date', y='total_count', data=trend_df)
            plt.title('Trend of Items with Item Type Errors')
            plt.xlabel('Date')
            plt.ylabel('Number of Items')
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            trend_chart = f"{self.report_type}_trend_{self.report_date}.png"
            plt.savefig(os.path.join(self.output_dir, trend_chart))
            plt.close()
            
            logger.info(f"Generated trend analysis chart: {trend_chart}")

if __name__ == "__main__":
    # This allows the module to be run directly for testing
    from scripts.data_quality.data_quality_core import ConfigManager
    
    config_manager = ConfigManager()
    report = ItemTypeErrorReport(config_manager)
    report.generate_report()
