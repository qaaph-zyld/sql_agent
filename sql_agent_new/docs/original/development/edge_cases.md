# SQL Agent Edge Case Catalog

This document catalogs identified edge cases for the SQL Agent project. Understanding and addressing these scenarios is crucial for building a robust and reliable system.

## Categories

### 1. Natural Language Input
Concerns related to the variety and complexity of user queries.

- **Ambiguity**:
  - *Example*: "Show me sales data for London." (Which year? Which London office if multiple?)
- **Unsupported Phrasing/Grammar**:
  - *Example*: Highly colloquial or grammatically incorrect sentences that the NLP model struggles with.
- **Very Long or Complex Queries**:
  - *Example*: A single natural language query attempting to combine multiple distinct analytical questions.
- **Very Short/Vague Queries**:
  - *Example*: "Data for users."
- **Use of Special Characters or Emojis**:
  - *Example*: Queries containing `!@#$%^&*()` or emojis that might break parsing.
- **Negations and Complex Logic**:
  - *Example*: "Find customers who have not placed orders for products in category X but have ordered from category Y."
- **Temporal Queries with Complex Relative Dates**:
  - *Example*: "Sales from three Mondays ago until last Tuesday."

### 2. Schema Interpretation
Challenges arising from the structure and metadata of the database schema.

- **Unusual Table/Column Names**:
  - *Example*: Names with spaces, special characters, reserved SQL keywords (e.g., a column named `Order` or `SELECT`).
- **Missing or Incomplete Metadata**:
  - *Example*: Tables without defined primary/foreign keys, missing `distinct_values` or `row_count` for selectivity estimation.
- **Complex Relationships**:
  - *Example*: Many-to-many relationships requiring multiple join tables, circular dependencies (if not handled carefully).
- **Unsupported or Rare Data Types**:
  - *Example*: Custom data types, BLOB/CLOB, XML, JSON types if not explicitly supported by generation logic.
- **Very Wide Tables (Many Columns) or Very Narrow Tables**:
  - *Example*: Tables with hundreds of columns, or tables with only one or two columns.
- **Schema Changes During Agent Operation** (Dynamic Schemas):
  - *Example*: A table is dropped or a column renamed while the agent has an old version of the schema cached.

### 3. SQL Generation
Issues specific to the process of translating understood intent into SQL queries.

- **SQL Dialect Differences**:
  - *Example*: Date functions, string manipulation, or LIMIT clause syntax varying between PostgreSQL, MySQL, SQL Server, etc.
- **Generation of Overly Complex or Inefficient Queries**:
  - *Example*: Unnecessary subqueries, inefficient join orders not caught by basic optimizers.
- **Correct Alias Handling for Tables and Columns**:
  - *Example*: Ensuring aliases are unique and correctly applied, especially in self-joins or complex subqueries.
- **Aggregate Functions with Grouping Issues**:
  - *Example*: Incorrectly applying `GROUP BY` for requested aggregations, or handling `HAVING` clauses.
- **Window Functions**:
  - *Example*: Correctly generating syntax for complex window functions if they are supported.
- **Case Sensitivity**: 
  - *Example*: Schema has mixed-case identifiers, but generated SQL uses all lower/upper case, leading to errors on case-sensitive databases.

### 4. Data & Database Interaction
Problems related to the actual data within the database or the database's behavior.

- **Empty Tables or Tables with No Matching Data**:
  - *Example*: Queries that should logically return no rows.
- **Tables with Massive Row Counts**:
  - *Example*: Queries that might inadvertently try to process or return huge datasets without proper filtering, leading to performance issues.
- **NULL Value Handling in Conditions and Joins**:
  - *Example*: `WHERE column = NULL` vs `WHERE column IS NULL`.
- **Database Errors or Timeouts**:
  - *Example*: Network issues, database server down, query execution exceeding configured timeouts.
- **Data Type Mismatches in Comparisons**:
  - *Example*: Comparing a string column with a number implicitly or explicitly.
- **Character Encoding Issues**:
  - *Example*: User input in one encoding, database stores in another.

### 5. Security Considerations
Potential vulnerabilities or security-related edge cases.

- **Indirect SQL Injection (via NL interpretation)**:
  - *Example*: NL query crafted to make the agent generate SQL that accesses unauthorized data, even if the NL itself isn't SQL.
- **Data Exposure through Broad Queries**:
  - *Example*: A simple NL query that translates to `SELECT * FROM sensitive_table` if not properly constrained.
- **Denial of Service (DoS)**:
  - *Example*: NL queries that lead to extremely resource-intensive SQL queries, overwhelming the database.
- **Information Leakage through Error Messages**:
  - *Example*: Database errors revealing too much schema information or internal state.

### 6. Performance & Scalability

- **Queries leading to full table scans on large tables.**
- **Inefficient join strategies for multi-table queries.**
- **Handling requests that would return an excessively large result set.**

---
*This document is a living document and will be updated as more edge cases are identified.*
