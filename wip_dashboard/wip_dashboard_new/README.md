# Inventory Dashboard - Complete Solution

## Overview
This is a complete React-based inventory dashboard that connects directly to SQL Server database `qadee2798` on server `a265m001`. The dashboard matches the provided screenshot layout with real-time data refresh capabilities.

## Features
- **Real-time SQL Server connectivity** with refresh button
- **Interactive filters** for Design Group, Prod Line, and Item Type
- **Summary cards** showing key metrics (Total Items, Total Value, Total CMAT, Total Inventory)
- **Pie chart** showing inventory distribution by Design Group
- **Bar chart** showing Top 10 Parts by selected metric (Total COGS or Total CMAT)
- **Detailed data table** with all inventory information
- **Responsive design** matching the provided screenshot layout

## Quick Start (Immediate Use)

### Prerequisites
- Node.js installed on your system
- Access to SQL Server `a265m001` with database `qadee2798`

### 1. Install Dependencies (Already Done)
```bash
npm install
```

### 2. Start the Backend Server
Open a terminal in this folder and run:
```bash
node server.js
```
You should see: `Server running at http://localhost:3001`

### 3. Start the Frontend Development Server
Open another terminal in this folder and run:
```bash
npm run dev
```
You should see: `Local: http://localhost:5173/`

### 4. Access the Dashboard
Open your browser and navigate to: `http://localhost:5173/`

## Database Configuration
The dashboard connects to:
- **Server**: a265m001
- **Database**: qadee2798
- **Username**: PowerBI
- **Password**: P0werB1

Connection settings are configured in `server.js` and can be modified if needed.

## File Structure
```
wip_dashboard_new/
├── src/
│   ├── App.tsx                 # Main app component
│   ├── InventoryDashboard.tsx  # Main dashboard component
│   ├── main.tsx               # React entry point
│   └── index.css              # Styles
├── server.js                  # Backend API server
├── inventory_query.sql        # SQL query for data
├── package.json              # Dependencies
├── vite.config.ts            # Vite configuration
├── tsconfig.json             # TypeScript configuration
└── index.html                # HTML template
```

## API Endpoints
- `GET /api/inventory` - Fetches all inventory data from the database

## Dashboard Components

### Sidebar Controls
- **Refresh Data Button**: Reloads data from SQL Server
- **COGS Type Selector**: Switch between Total COGS and Total CMAT
- **Design Group Filter**: Filter by specific design groups
- **Prod Line Filter**: Filter by production lines
- **Item Type Filter**: Filter by FG/SFG/RM types

### Main Dashboard
- **Summary Cards**: Key metrics at the top
- **Pie Chart**: Distribution by Design Group
- **Bar Chart**: Top 10 Parts by selected metric
- **Data Table**: Detailed inventory information (first 100 rows displayed)

## Customization
- Modify `inventory_query.sql` to change the data source query
- Update `server.js` to change database connection settings
- Customize `InventoryDashboard.tsx` to modify the UI layout
- Adjust styles in `index.css` for visual changes

## Troubleshooting

### Backend Server Issues
- Ensure SQL Server is accessible from your machine
- Verify database credentials are correct
- Check that port 3001 is not in use by another application

### Frontend Issues
- Ensure port 5173 is available
- Check browser console for any JavaScript errors
- Verify the backend server is running before starting the frontend

### Database Connection Issues
- Test SQL Server connectivity using SQL Server Management Studio
- Ensure the PowerBI user has appropriate permissions
- Check network connectivity to server a265m001

## Production Deployment
For production use:
1. Run `npm run build` to create optimized production files
2. Deploy the `dist/` folder to a web server
3. Deploy `server.js` to a Node.js hosting environment
4. Update the API endpoint in the frontend to point to your production server

## Support
This dashboard is ready for immediate use. Both servers should be running and the dashboard should be accessible at `http://localhost:5173/` with live data from your SQL Server database.
