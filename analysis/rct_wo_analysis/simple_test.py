# Simple database test script
import pymssql
import sys

def test_connection():
    try:
        print("Testing connection to a265m001...")
        conn = pymssql.connect(
            server='a265m001',
            user='PowerBI',
            password='P0werB1',
            database='QADEE2798'
        )
        
        cursor = conn.cursor()
        cursor.execute("SELECT @@VERSION")
        version = cursor.fetchone()[0]
        print(f"✅ Connected to SQL Server: {version}")
        
        # Check if tables exist
        cursor.execute("""
            SELECT TABLE_NAME 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_SCHEMA = 'dbo' 
            AND TABLE_NAME IN ('tr_hist', 'pt_mstr')
        """)
        tables = [row[0] for row in cursor.fetchall()]
        print(f"Found tables: {', '.join(tables)}")
        
        # Get row counts
        cursor.execute("SELECT COUNT(*) FROM tr_hist WHERE tr_type = 'RCT-WO'")
        rct_wo_count = cursor.fetchone()[0]
        print(f"Found {rct_wo_count} RCT-WO transactions")
        
        # Get date range
        cursor.execute("""
            SELECT MIN(tr_date) as min_date, MAX(tr_date) as max_date 
            FROM tr_hist 
            WHERE tr_type = 'RCT-WO'
        """)
        min_date, max_date = cursor.fetchone()
        print(f"Date range of RCT-WO transactions: {min_date} to {max_date}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        return False

if __name__ == "__main__":
    if test_connection():
        print("\n✅ Connection test successful! You can now run the analysis.")
        print("Run: python generate_report.py")
    else:
        print("\n❌ Connection test failed. Please check your credentials and try again.")
        sys.exit(1)
