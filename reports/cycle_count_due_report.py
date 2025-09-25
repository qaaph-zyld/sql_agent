"""
Cycle Count Due Report Module

This module generates reports on items that are due for cycle count.
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

class CycleCountDueReport(DataQualityReport):
    """Report on items due for cycle count"""
    
    def __init__(self, config_manager):
        super().__init__(config_manager)
        self.report_type = "cycle_count_due"
    
    def generate_report(self):
        """Generate report on items due for cycle count"""
        logger.info("Generating cycle count due report")
        
        # Execute direct query for items due for cycle count
        query = """
        WITH LastCycleCount AS (
            SELECT 
                tr_part,
                tr_site,
                MAX(tr_effdate) AS last_count_date
            FROM 
                [QADEE2798].[dbo].[tr_hist]
            WHERE 
                tr_type = 'ADJ-PHY'  -- Physical adjustment type for cycle counts
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
            lcc.last_count_date AS [Last Cycle Count Date],
            CASE 
                WHEN lcc.last_count_date IS NULL THEN 'Never Counted'
                WHEN DATEDIFF(day, lcc.last_count_date, GETDATE()) > 
                    CASE 
                        WHEN pt.pt_abc = 'A' THEN 30  -- A items counted every 30 days
                        WHEN pt.pt_abc = 'B' THEN 90  -- B items counted every 90 days
                        WHEN pt.pt_abc = 'C' THEN 180 -- C items counted every 180 days
                        ELSE 365                      -- Default to yearly for other codes
                    END THEN 'Due'
                ELSE 'Not Due'
            END AS [Cycle Count Due],
            DATEDIFF(day, lcc.last_count_date, GETDATE()) AS [Days Since Last Count],
            CASE 
                WHEN pt.pt_abc = 'A' THEN 30
                WHEN pt.pt_abc = 'B' THEN 90
                WHEN pt.pt_abc = 'C' THEN 180
                ELSE 365
            END AS [Count Frequency Days],
            CASE 
                WHEN lcc.last_count_date IS NULL THEN GETDATE()
                ELSE DATEADD(day, 
                    CASE 
                        WHEN pt.pt_abc = 'A' THEN 30
                        WHEN pt.pt_abc = 'B' THEN 90
                        WHEN pt.pt_abc = 'C' THEN 180
                        ELSE 365
                    END, 
                    lcc.last_count_date)
            END AS [Next Count Due Date]
        FROM 
            [QADEE2798].[dbo].[pt_mstr] pt
        LEFT JOIN 
            [QADEE2798].[dbo].[sct_det] sct ON pt.pt_part = sct.sct_part AND pt.pt_site = sct.sct_site AND sct.sct_sim = 'standard'
        LEFT JOIN 
            LastCycleCount lcc ON pt.pt_part = lcc.tr_part AND pt.pt_site = lcc.tr_site
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
            AND (
                (lcc.last_count_date IS NULL AND inv.[Total Inv] > 0) -- Never counted with inventory
                OR 
                (DATEDIFF(day, lcc.last_count_date, GETDATE()) > 
                    CASE 
                        WHEN pt.pt_abc = 'A' THEN 30
                        WHEN pt.pt_abc = 'B' THEN 90
                        WHEN pt.pt_abc = 'C' THEN 180
                        ELSE 365
                    END)
            )
        ORDER BY 
            [Next Count Due Date], pt.pt_abc
        """
        
        df = self.execute_query(query)
        logger.info(f"Found {len(df)} items due for cycle count")
        
        # Add days overdue column
        df['Days Overdue'] = df.apply(
            lambda row: max(0, (datetime.now() - pd.to_datetime(row['Next Count Due Date'])).days),
            axis=1
        )
        
        # Generate summary by ABC code
        abc_summary = df.groupby(['ABC Code']).size().reset_index(name='Count')
        
        # Generate summary by group
        group_summary = df.groupby(['Group']).size().reset_index(name='Count')
        group_summary = group_summary.sort_values('Count', ascending=False)
        
        # Generate summary by plant
        plant_summary = df.groupby(['Plant']).size().reset_index(name='Count')
        
        # Generate summary by FG/SFG/RM
        type_summary = df.groupby(['FG/SFG/RM']).size().reset_index(name='Count')
        type_summary = type_summary.sort_values('Count', ascending=False)
        
        # Generate summary by days overdue ranges
        df['Overdue Range'] = pd.cut(
            df['Days Overdue'],
            bins=[-1, 0, 30, 60, 90, 180, float('inf')],
            labels=['Not Overdue', '1-30 days', '31-60 days', '61-90 days', '91-180 days', 'Over 180 days']
        )
        overdue_summary = df.groupby(['Overdue Range']).size().reset_index(name='Count')
        
        # Export detailed report
        detail_file = f"{self.report_type}_detail_{self.report_date}.xlsx"
        self.export_to_excel(df, detail_file)
        
        # Export summary reports
        abc_file = f"{self.report_type}_by_abc_{self.report_date}.xlsx"
        self.export_to_excel(abc_summary, abc_file)
        
        group_file = f"{self.report_type}_by_group_{self.report_date}.xlsx"
        self.export_to_excel(group_summary, group_file)
        
        plant_file = f"{self.report_type}_by_plant_{self.report_date}.xlsx"
        self.export_to_excel(plant_summary, plant_file)
        
        type_file = f"{self.report_type}_by_type_{self.report_date}.xlsx"
        self.export_to_excel(type_summary, type_file)
        
        overdue_file = f"{self.report_type}_by_overdue_{self.report_date}.xlsx"
        self.export_to_excel(overdue_summary, overdue_file)
        
        # Generate charts
        self._generate_charts(abc_summary, group_summary, plant_summary, type_summary, overdue_summary)
        
        # Calculate average days overdue
        avg_days_overdue = df['Days Overdue'].mean()
        
        # Save metadata
        metadata = {
            'report_date': self.report_date,
            'total_count': len(df),
            'groups_affected': df['Group'].nunique(),
            'plants_affected': df['Plant'].nunique(),
            'types_affected': df['FG/SFG/RM'].nunique(),
            'avg_days_overdue': float(avg_days_overdue),
            'never_counted': int(df[df['Last Cycle Count Date'].isnull()].shape[0]),
            'a_items_due': int(df[df['ABC Code'] == 'A'].shape[0]),
            'b_items_due': int(df[df['ABC Code'] == 'B'].shape[0]),
            'c_items_due': int(df[df['ABC Code'] == 'C'].shape[0]),
            'top_group': group_summary.iloc[0]['Group'] if not group_summary.empty else None,
            'top_group_count': int(group_summary.iloc[0]['Count']) if not group_summary.empty else 0
        }
        
        metadata_file = f"{self.report_type}_metadata_{self.report_date}.json"
        self.save_metadata(metadata, metadata_file)
        
        # Generate trend analysis if historical data is available
        self._generate_trend_analysis()
        
        logger.info("Cycle count due report generation completed")
        
        return {
            'detail_file': detail_file,
            'abc_file': abc_file,
            'group_file': group_file,
            'plant_file': plant_file,
            'type_file': type_file,
            'overdue_file': overdue_file,
            'metadata': metadata
        }
    
    def _generate_charts(self, abc_summary, group_summary, plant_summary, type_summary, overdue_summary):
        """Generate charts for the report"""
        # ABC chart
        plt.figure(figsize=(10, 6))
        sns.barplot(x='ABC Code', y='Count', data=abc_summary)
        plt.title('Cycle Count Due Items by ABC Code')
        plt.tight_layout()
        
        abc_chart = f"{self.report_type}_abc_chart_{self.report_date}.png"
        plt.savefig(os.path.join(self.output_dir, abc_chart))
        plt.close()
        
        # Group chart - top 10
        plt.figure(figsize=(12, 6))
        top_groups = group_summary.head(10)
        sns.barplot(x='Group', y='Count', data=top_groups)
        plt.title('Top 10 Groups with Cycle Count Due Items')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        group_chart = f"{self.report_type}_group_chart_{self.report_date}.png"
        plt.savefig(os.path.join(self.output_dir, group_chart))
        plt.close()
        
        # Plant chart
        plt.figure(figsize=(10, 6))
        sns.barplot(x='Plant', y='Count', data=plant_summary)
        plt.title('Cycle Count Due Items by Plant')
        plt.tight_layout()
        
        plant_chart = f"{self.report_type}_plant_chart_{self.report_date}.png"
        plt.savefig(os.path.join(self.output_dir, plant_chart))
        plt.close()
        
        # Type chart
        plt.figure(figsize=(10, 6))
        sns.barplot(x='FG/SFG/RM', y='Count', data=type_summary)
        plt.title('Cycle Count Due Items by Item Type')
        plt.tight_layout()
        
        type_chart = f"{self.report_type}_type_chart_{self.report_date}.png"
        plt.savefig(os.path.join(self.output_dir, type_chart))
        plt.close()
        
        # Overdue range chart
        plt.figure(figsize=(12, 6))
        sns.barplot(x='Overdue Range', y='Count', data=overdue_summary)
        plt.title('Cycle Count Due Items by Overdue Range')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        overdue_chart = f"{self.report_type}_overdue_chart_{self.report_date}.png"
        plt.savefig(os.path.join(self.output_dir, overdue_chart))
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
            plt.title('Trend of Cycle Count Due Items')
            plt.xlabel('Date')
            plt.ylabel('Number of Items')
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            count_trend_chart = f"{self.report_type}_count_trend_{self.report_date}.png"
            plt.savefig(os.path.join(self.output_dir, count_trend_chart))
            plt.close()
            
            # Generate trend chart for average days overdue
            plt.figure(figsize=(12, 6))
            sns.lineplot(x='date', y='avg_days_overdue', data=trend_df)
            plt.title('Trend of Average Days Overdue for Cycle Counts')
            plt.xlabel('Date')
            plt.ylabel('Average Days Overdue')
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            overdue_trend_chart = f"{self.report_type}_overdue_trend_{self.report_date}.png"
            plt.savefig(os.path.join(self.output_dir, overdue_trend_chart))
            plt.close()
            
            # Generate trend chart for ABC breakdown
            plt.figure(figsize=(12, 6))
            sns.lineplot(x='date', y='a_items_due', data=trend_df, label='A Items')
            sns.lineplot(x='date', y='b_items_due', data=trend_df, label='B Items')
            sns.lineplot(x='date', y='c_items_due', data=trend_df, label='C Items')
            plt.title('Trend of Cycle Count Due Items by ABC Code')
            plt.xlabel('Date')
            plt.ylabel('Number of Items')
            plt.legend()
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            abc_trend_chart = f"{self.report_type}_abc_trend_{self.report_date}.png"
            plt.savefig(os.path.join(self.output_dir, abc_trend_chart))
            plt.close()
            
            logger.info(f"Generated trend analysis charts")

if __name__ == "__main__":
    # This allows the module to be run directly for testing
    from scripts.data_quality.data_quality_core import ConfigManager
    
    config_manager = ConfigManager()
    report = CycleCountDueReport(config_manager)
    report.generate_report()
