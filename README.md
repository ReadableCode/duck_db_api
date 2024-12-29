# duck_db_api

## Running the service

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

## Basic Interactions

```bash
# DuckDB API Cheat Sheet

# 1. Create a Table
curl -X GET "http://localhost:8000/query/?query=CREATE+TABLE+IF+NOT+EXISTS+test_table+(id+INTEGER,+value+TEXT);"

# 2. List All Tables
curl -X GET "http://localhost:8000/query/?query=SELECT+name+FROM+sqlite_master+WHERE+type='table';"

# 3. Insert Data into a Table
curl -X GET "http://localhost:8000/query/?query=INSERT+INTO+test_table+(id,+value)+VALUES+(1,+%27sample+data%27);"

# 4. Query Data from a Table
curl -X GET "http://localhost:8000/query/?query=SELECT+*+FROM+test_table;"

```

```powershell
# 1. Create a Table
Invoke-WebRequest -Uri "http://localhost:8000/query/?query=CREATE+TABLE+IF+NOT+EXISTS+test_table+(id+INTEGER,+value+TEXT);" -Method GET

# 2. List All Tables
Invoke-WebRequest -Uri "http://localhost:8000/query/?query=SELECT+name+FROM+sqlite_master+WHERE+type='table';" -Method GET

# 3. Insert Data into a Table
Invoke-WebRequest -Uri "http://localhost:8000/query/?query=INSERT+INTO+test_table+(id,+value)+VALUES+(1,+%27sample+data%27);" -Method GET

# 4. Query Data from a Table
Invoke-WebRequest -Uri "http://localhost:8000/query/?query=SELECT+*+FROM+test_table;" -Method GET

```
