# Getting Started with Grafana 
Grafana enables DIGIT to query, visualize, alert on, and explore metrics, logs, and traces. Dashboards are created and managed in Grafana. The purpose of this documentation is to support DIGIT users with onboarding materials so that you can quickly and confidently explore available dashboards, extract insights, and contribute to data-driven processes.

## Login
Access Grafana by clicking the link in the top navigation of TANF Data Portal, and log in using your assigned username and password.

<img width="1198" height="338" alt="image" src="https://github.com/user-attachments/assets/4749a539-613f-4769-b6d6-d26ae957211d" />

With your access, you can:
- View all available dashboards
- Use filters to customize data views
- Export individual widgets from dashboards
- Run queries to explore data as needed

<img width="3250" height="1758" alt="image" src="https://github.com/user-attachments/assets/076e9803-f9ed-4d63-9980-d3ba8fa3dbda" />

If you encounter any issues logging in or accessing certain features, please contact **tanfdata@acf.hhs.gov**.

## Dashboards
Each dashboard includes an Overview to describe the purpose and intention. 
| Dashboard | Description and Purpose | Filters Needed (for QA Testing) |
|---|---|---|
| [DIGIT] Query Views by program type, record type, and time period | Dashboard with pre-set query params (prod) | Program Type, Record Type, and Time Period |
| [DIGIT] STTs missing Approved Users | List of STTs with no approved users in TDP (prod) | STT Region, STT Code, and STT |
| [DIGIT] TDP Submission History | Production data submission history | Program Type, Section, Fiscal Year, Fiscal Quarter, STT Region, STT Type, STT |

### Set Dashboard Time Range
*Note: Time settings are saved on a per-dashboard basis.*

To view the **time range** setting on a dashboard, hover over the time menu located in the top menu.

<img width="1190" height="88" alt="image" src="https://github.com/user-attachments/assets/16f265ce-88d2-4c9a-ab60-94bf8cde546a" />

<img width="330" height="304" alt="image" src="https://github.com/user-attachments/assets/d76c0ccb-d840-45ba-89b2-880d58987052" />

Hovering over the menu displays the current time range setting.

DIGIT dashboards reflect the most recent records, so choose a time range within the last 24 hours. To adjust the time range on a dashboard, click the time menu to select a relative time range or set custom absolute time ranges.

<img width="1096" height="870" alt="image" src="https://github.com/user-attachments/assets/020ea481-5d56-4e0f-a57a-73de9176ff50" />

The time menu provides inputs to set absolute and relative time ranges or select common or recently used time ranges

The **timezone** and **fiscal year** settings can be changed from the **time** menu by clicking the **Change time settings** button.

*Additional information about supported time units and relative ranges can be found in the [Set dashboard time range](https://grafana.com/docs/grafana/latest/dashboards/use-dashboards/#set-dashboard-time-range) section of Grafana's documentation site.*

### Filter Dashboard Data

#### Query Variables

Variables can be used to dynamically change the data displayed on a dashboard. They are displayed as dropdown lists at the top of the dashboard.

<img width="2836" height="282" alt="image" src="https://github.com/user-attachments/assets/f072342c-a3c1-42e5-bcc8-909f7579a93a" />

*Advanced documentation about creating and working with variables can be found in the [Variables](https://grafana.com/docs/grafana/latest/dashboards/variables/) section of the Grafana documentation site.*

### Export Data to CSV
1. Click the **Menu** in the upper right corner of a panel, and select **Inspect**, then select **Data** (keyboard shortcut i)

<img width="656" height="366" alt="image" src="https://github.com/user-attachments/assets/631edb8b-9460-448e-8746-5d634cdad881" />

Clicking **Inspect** will open a side panel to look at the data, stats, and JSON.

2. Click **Data options** to adjust settings, then click **Download CSV**

<img width="1240" height="600" alt="image" src="https://github.com/user-attachments/assets/a24b6ed0-bcf6-4cef-9013-23e49c3da6d0" />

Clicking **Data options** opens a dropdown to toggle **Formatted data** and **Download for Excel**

### Querying Datasets

*Note: Firefox or Edge browsers are recommended for the best performance when running large queries in Grafana.*

You can use the Query inspector to inspect raw data, export data to a CSV file, export log results, and view query requests.
1. Navigate to the **Explore** page. *Note: you must have either the editor or administrator basic role or the data sources explore  role to access Explore in Grafana.*

2. Use the query **Builder** UI to create your query, or use the **Code** option to write an SQL query. To switch between methods, use the **Builder** and **Code** buttons in the upper right of the query block

For queries that could potentially return more than 1 million records at a time, it is recommended to filter records by reporting month. 

<img width="1520" height="524" alt="image" src="https://github.com/user-attachments/assets/e0c07c5c-1971-409b-9693-9266a0dd7594" />

A warning will occur when the 1 million row limit is reached.

If you receive a Warning that there are more than 20 columns in the query, you can choose to show all columns.

3. Click **Run Query**.
4. Query results will be displayed in a table below the query row 
5. To export the query results, click the **Query inspector** button at the bottom of the query row, then select the Data tab
6. Open the **Data options** section to change the settings as needed, then click the **Download CSV** button

<img width="1520" height="865" alt="image" src="https://github.com/user-attachments/assets/04368b75-6519-4804-be4f-0865a9414737" />

The **Query inspector** button is below the query row, and opens a panel below with tabs for Stats, Query, JSON, and Data. Select the **Data** tab to download a CSV.

#### Examples of Common SQL Queries

##### Preview Data from Any Table

To use the **Builder** UI to create a query to preview data from a table:

1. Select the table view to query from the **Table** dropdown.
   
Below is a list of table views that are most relevant to your data tasks:

| Table View | Description | 
|---|---|
| tanf_t1 | T1 records for states and territories | 
| tanf_t2 | T2 records for states and territories | 
| tanf_t3 | T3 records for states and territories | 
| tanf_t4 | T4 records for states and territories | 
| tanf_t5 | T5 records for states and territories | 
| tanf_t6 | T6 records for states and territories | 
| tanf_t7 | T7 records for states and territories | 
| ssp_m1 | M1 records for states and territories | 
| ssp_m2 | M2 records for states and territories | 
| ssp_m3 | M3 records for states and territories | 
| ssp_m4 | M4 records for states and territories | 
| ssp_m5 | M5 records for states and territories | 
| ssp_m6 | M6 records for states and territories | 
| ssp_m7 | M7 records for states and territories | 
| tribal_tanf_t1 | T1 records for tribes | 
| tribal_tanf_t2 | T2 records for tribes | 
| tribal_tanf_t3 | T3 records for tribes | 
| tribal_tanf_t4 | T4 records for tribes | 
| tribal_tanf_t5 | T5 records for tribes | 
| tribal_tanf_t6 | T6 records for tribes | 
| tribal_tanf_t7 | T7 records for tribes | 
| stt_section_to_type_mapping | Metadata for each table view | 
| mr_record_counts_by_table_view | Most recent record count by table view and STT | 

2. Select the **Column** (selecting * means you would like to retrieve all columns)
3. *(Optional)* Ensure the **Order** toggle is selected to limit results

<img width="1520" height="778" alt="image" src="https://github.com/user-attachments/assets/722ff1a5-e5d9-4a4f-a2bc-ccc71cae40ef" />

The same query can be written in SQL and run in the **Code** view:

```
SELECT *    -- select all columns/fields
FROM ssp_m1 -- ssp, active m1 (family-level) records
LIMIT 100;  -- limit results to 100 records
```

##### Aggregate Counts: Total Records vs. Unique Cases

To build a query that compares the total number of records versus unique cases:
1. Select the "tanf_t1" table to query from the **Table** dropdown
2. Select * in the **Column** dropdown (selecting * means you would like to retrieve all columns), select the Aggregation method **Count**, and input an Alias of "total_records" to label the query results column
3. Click the + to add another column to the query
4. Select the "CASE_NUMBER" column to query, select the Aggregation method Count, and input an Alias of "unique_cases" to label the second column of query results column
*Note: The Builder UI does not provide a way to remove duplicate rows from the result set using the DISTINCT keyword; if this action is desired, using the Code method to input your query will provide more flexibility.*
5. Click the Run query button

<img width="1520" height="805" alt="image" src="https://github.com/user-attachments/assets/bf09d9ad-9448-4c00-be18-2b9295101925" />

The same query can be written in SQL and run in the **Code** view:

```
SELECT 
    COUNT(*) AS total_records,
    COUNT(DISTINCT "CASE_NUMBER") AS unique_cases
FROM tanf_t1;-- TANF, active t1 (family-level) records
```

##### Grouped Counts: Total Records by Month and STT
1. Select the tanf_t6 table to query from the **Table** dropdown
2. Select "STT" as the first **Column**
3. Click the + to add another column to the query, and select "RPT_MONTH_YEAR"
4. Click the + to add another column to the query, and select *, set the Aggregation to COUNT
5. Ensure the **Group**, and Order toggles are switch on
6. Select "STT" in the Group by column dropdown
7. Click the + to add another group by column attribute, and select "RPT_MONTH_YEAR"
8. In the Order by dropdown, select "STT"; (optional) click to sort by ascending or descending  
*Note: The Builder UI limits ordering to one attribute, if multiple ordering attributes are desired, the Code option will provide more flexibility.*
9. Click the **Run query** button

<img width="1520" height="1063" alt="image" src="https://github.com/user-attachments/assets/6c2cd849-7554-45da-84c4-5747b4c6bd06" />

The same query can be written in SQL and run in the Code view:

```
ELECT 
    "STT", -- State or territory 
    "RPT_MONTH_YEAR",     -- Reporting month (e.g., 202401, 202402)             
    COUNT(*) AS total_records
FROM tanf_t6 -- TANF,  t6 (aggregate-level) records
GROUP BY  "STT","RPT_MONTH_YEAR"
ORDER BY "STT","RPT_MONTH_YEAR";
```

*Advanced documentation about ways to explore data in Grafana is available in the [Explore](https://grafana.com/docs/grafana/latest/explore/get-started-with-explore/#get-started-with-explore) section of the Grafana documentation site.*
