"""
PDF Field Description Extractor

This script extracts field descriptions from the DatabaseDefinitions_TR_v2019EE.pdf document
and enhances the existing database documentation with these descriptions.

It preserves all existing documentation while adding the extracted field descriptions
as a layered enhancement.
"""

import os
import re
import json
import PyPDF2
import pandas as pd
from pathlib import Path

# PDF document path
PDF_PATH = "DatabaseDefinitions_TR_v2019EE.pdf"

# Database documentation directory
DB_DOCS_DIR = os.path.join("Database_tables", "QADEE2798")

def extract_text_from_pdf(pdf_path):
    """
    Extract text from PDF document
    
    Args:
        pdf_path: Path to PDF document
        
    Returns:
        Extracted text as string
    """
    print(f"Extracting text from {pdf_path}...")
    
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            
            # Extract text from each page
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                text += page.extract_text() + "\n"
                
                # Print progress every 10 pages
                if (page_num + 1) % 10 == 0:
                    print(f"Processed {page_num + 1} pages...")
            
            return text
    except Exception as e:
        print(f"Error extracting text from PDF: {str(e)}")
        return ""

def parse_table_definitions(pdf_text):
    """
    Parse table definitions from PDF text
    
    Args:
        pdf_text: Extracted text from PDF
        
    Returns:
        Dictionary mapping table names to field descriptions
    """
    print("Parsing table definitions...")
    
    # Dictionary to store table definitions
    table_definitions = {}
    
    # Regular expression to find table definitions
    # Looking for patterns like "Table: 15" or "Table: active_schd_det"
    table_pattern = r"Table:\s+(\w+)"
    
    # Split the text by table headers
    table_sections = re.split(table_pattern, pdf_text)
    
    # Process each section (skipping the first which is before any table)
    for i in range(1, len(table_sections), 2):
        if i + 1 < len(table_sections):
            table_name = table_sections[i].strip()
            table_content = table_sections[i + 1].strip()
            
            # Parse field definitions
            field_definitions = parse_field_definitions(table_content)
            
            # Store in dictionary
            table_definitions[table_name] = field_definitions
            
            print(f"Parsed definitions for table: {table_name} ({len(field_definitions)} fields)")
    
    return table_definitions

def parse_field_definitions(table_content):
    """
    Parse field definitions from table content
    
    Args:
        table_content: Content of a table section from PDF
        
    Returns:
        Dictionary mapping field names to descriptions
    """
    # Dictionary to store field definitions
    field_definitions = {}
    
    # Regular expression to find field definitions
    # Looking for patterns like "Field: in_part" followed by description
    field_pattern = r"Field:\s+(\w+)\s+(.+?)(?=Field:|$)"
    
    # Find all field definitions
    field_matches = re.finditer(field_pattern, table_content, re.DOTALL)
    
    for match in field_matches:
        field_name = match.group(1).strip()
        field_description = match.group(2).strip()
        
        # Clean up description (remove extra whitespace)
        field_description = re.sub(r'\s+', ' ', field_description)
        
        # Store in dictionary
        field_definitions[field_name] = field_description
    
    return field_definitions

def enhance_field_descriptions(table_definitions):
    """
    Enhance existing field descriptions with those extracted from PDF
    
    Args:
        table_definitions: Dictionary mapping table names to field descriptions
    """
    print("\nEnhancing field descriptions in markdown files...")
    
    # Get all table directories
    table_dirs = [d for d in os.listdir(DB_DOCS_DIR) if os.path.isdir(os.path.join(DB_DOCS_DIR, d))]
    
    for table_dir in table_dirs:
        # Extract table name from directory name (remove "dbo." prefix)
        table_name = table_dir.replace("dbo.", "")
        
        # Check if we have definitions for this table
        if table_name in table_definitions:
            print(f"Enhancing descriptions for table: {table_name}")
            
            # Path to field names markdown file
            md_path = os.path.join(DB_DOCS_DIR, table_dir, f"{table_name}_field_names.md")
            
            if os.path.exists(md_path):
                # Read existing markdown content
                with open(md_path, 'r', encoding='utf-8') as f:
                    md_content = f.read()
                
                # Enhance descriptions
                enhanced_content = enhance_markdown_descriptions(md_content, table_definitions[table_name])
                
                # Write enhanced content back to file
                with open(md_path, 'w', encoding='utf-8') as f:
                    f.write(enhanced_content)
                
                print(f"Enhanced descriptions saved to {md_path}")
            else:
                print(f"Markdown file not found: {md_path}")
        else:
            print(f"No definitions found for table: {table_name}")

def enhance_markdown_descriptions(md_content, field_definitions):
    """
    Enhance markdown content with field descriptions
    
    Args:
        md_content: Existing markdown content
        field_definitions: Dictionary mapping field names to descriptions
        
    Returns:
        Enhanced markdown content
    """
    # Regular expression to find field rows in markdown table
    field_pattern = r'\| (\w+) \| ([^|]+) \| ([^|]+) \| ([^|]+) \| ([^|]+) \| ([^|]+) \|'
    
    # Function to replace field descriptions
    def replace_description(match):
        field_name = match.group(1)
        data_type = match.group(2)
        primary_key = match.group(3)
        foreign_key = match.group(4)
        nullable = match.group(5)
        description = match.group(6)
        
        # If we have a description from PDF and current description is generic
        if field_name in field_definitions and description.strip() == 'No description available':
            # Use the description from PDF
            new_description = field_definitions[field_name]
            return f"| {field_name} | {data_type} | {primary_key} | {foreign_key} | {nullable} | {new_description} |"
        
        # Otherwise keep the existing description
        return match.group(0)
    
    # Replace descriptions in markdown content
    enhanced_content = re.sub(field_pattern, replace_description, md_content)
    
    return enhanced_content

def create_table_relationship_documentation():
    """
    Create comprehensive table relationship documentation
    """
    print("\nCreating table relationship documentation...")
    
    # Path to database summary markdown file
    summary_path = os.path.join(DB_DOCS_DIR, "database_summary.md")
    
    # Read existing summary content
    with open(summary_path, 'r', encoding='utf-8') as f:
        summary_content = f.read()
    
    # Add table descriptions section
    summary_content += "\n## Table Descriptions\n\n"
    summary_content += "| Table | Description | Primary Purpose |\n"
    summary_content += "|-------|-------------|----------------|\n"
    
    # Add descriptions for each table
    table_descriptions = {
        "15": "Inventory Master | Contains inventory quantities and status information for items at specific sites",
        "active_schd_det": "Active Schedule Details | Contains active schedule information for production and shipping",
        "ad_mstr": "Address Master | Contains address information for customers, vendors, and other entities",
        "ld_det": "Load Details | Contains details about shipment loads",
        "pckc_mstr": "Pick Confirmation Master | Contains information about pick confirmations",
        "picked_serial_link": "Picked Serial Link | Links picked items to serial numbers",
        "po_mstr": "Purchase Order Master | Contains header information for purchase orders",
        "pod_det": "Purchase Order Detail | Contains line item details for purchase orders",
        "ps_mstr": "Product Structure Master | Contains bill of materials information",
        "pt_mstr": "Part Master | Contains part information including costs and classifications",
        "ptpac_det": "Part Package Detail | Contains packaging information for parts",
        "ro_det": "Release Order Detail | Contains details for release orders",
        "sch_mstr": "Schedule Master | Contains header information for production schedules",
        "sct_det": "Schedule Transaction Detail | Contains transaction details for schedules",
        "ser_active_picked": "Serial Active Picked | Contains information about picked serialized items",
        "ser_item_detail": "Serial Item Detail | Contains details about serialized items",
        "serh_hist": "Serial History | Contains historical information about serialized items",
        "so_mstr": "Sales Order Master | Contains header information for sales orders",
        "sod_det": "Sales Order Detail | Contains line item details for sales orders",
        "tr_hist": "Transaction History | Contains historical transaction information",
        "vd_mstr": "Vendor Master | Contains vendor information",
        "xxwezoned_det": "Custom Zone Detail | Contains custom zone information for warehouse management"
    }
    
    for table, description in table_descriptions.items():
        parts = description.split(" | ")
        if len(parts) == 2:
            table_type, purpose = parts
            summary_content += f"| [{table}](dbo.{table}/{table}_field_names.md) | {table_type} | {purpose} |\n"
    
    # Add common queries section
    summary_content += "\n## Common Query Patterns\n\n"
    summary_content += "### Inventory Queries\n\n"
    summary_content += "```sql\n"
    summary_content += "-- Get current inventory levels for all items\n"
    summary_content += "SELECT in_part, in_site, in_qty_oh, in_qty_avail\n"
    summary_content += "FROM [QADEE2798].[dbo].[15]\n"
    summary_content += "ORDER BY in_part, in_site\n"
    summary_content += "```\n\n"
    
    summary_content += "### Transaction History Queries\n\n"
    summary_content += "```sql\n"
    summary_content += "-- Get transaction history for a specific part\n"
    summary_content += "SELECT tr_part, tr_date, tr_type, tr_qty_loc\n"
    summary_content += "FROM [QADEE2798].[dbo].[tr_hist]\n"
    summary_content += "WHERE tr_part = 'PART_NUMBER'\n"
    summary_content += "ORDER BY tr_date DESC\n"
    summary_content += "```\n\n"
    
    summary_content += "### Sales Order Queries\n\n"
    summary_content += "```sql\n"
    summary_content += "-- Get sales orders with details\n"
    summary_content += "SELECT so.so_nbr, so.so_cust, so.so_ord_date, sod.sod_part, sod.sod_qty_ord\n"
    summary_content += "FROM [QADEE2798].[dbo].[so_mstr] so\n"
    summary_content += "JOIN [QADEE2798].[dbo].[sod_det] sod ON so.so_nbr = sod.sod_nbr\n"
    summary_content += "ORDER BY so.so_ord_date DESC\n"
    summary_content += "```\n"
    
    # Write enhanced summary content back to file
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write(summary_content)
    
    print(f"Enhanced database summary saved to {summary_path}")

def main():
    """Main function to extract field descriptions and enhance documentation"""
    # Check if PDF exists
    if not os.path.exists(PDF_PATH):
        print(f"PDF file not found: {PDF_PATH}")
        return
    
    # Extract text from PDF
    pdf_text = extract_text_from_pdf(PDF_PATH)
    
    if not pdf_text:
        print("Failed to extract text from PDF")
        return
    
    # Parse table definitions
    table_definitions = parse_table_definitions(pdf_text)
    
    # Save extracted definitions to JSON for reference
    with open("extracted_field_definitions.json", 'w', encoding='utf-8') as f:
        json.dump(table_definitions, f, indent=2)
    
    print(f"Extracted definitions saved to extracted_field_definitions.json")
    
    # Enhance field descriptions in markdown files
    enhance_field_descriptions(table_definitions)
    
    # Create table relationship documentation
    create_table_relationship_documentation()
    
    print("\nField description enhancement complete!")

if __name__ == "__main__":
    main()
