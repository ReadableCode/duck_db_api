# duck_db_api

## Running the service

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

## Running with docker

```bash
docker build -t duck_db_api .
```

```bash
docker run -d --name duck_db_api -p 8000:8000 duck_db_api
```

## Basic Interactions

Check that the site it up with your browset:

```bash
curl http://localhost:8000/
```

```bash
# 1. Create a Table
curl -X POST "http://localhost:8000/create_table/?table_name=test_table&columns=id+INTEGER,+value+TEXT"

# 2. List All Tables
curl -X GET "http://localhost:8000/query/?query=SELECT+name+FROM+sqlite_master+WHERE+type='table';"

# 3. Insert Data into a Table
curl -X POST "http://localhost:8000/insert/" \
     -H "Content-Type: application/json" \
     -d '{"table_name": "test_table", "data": {"id": 1, "value": "sample data"}}'

# 4. Query Data from a Table
curl -X GET "http://localhost:8000/query/?query=SELECT+*+FROM+test_table"
```

```powershell
# 1. Create a Table
Invoke-WebRequest -Uri "http://localhost:8000/create_table/?table_name=test_table&columns=id+INTEGER,+value+TEXT" `
                  -Method POST

# 2. List All Tables
Invoke-WebRequest -Uri "http://localhost:8000/query/?table_name=sqlite_master&query=SELECT+name+FROM+sqlite_master+WHERE+type='table';" `
                  -Method GET

# 3. Insert Data into a Table
Invoke-WebRequest -Uri "http://localhost:8000/insert/" `
                  -Method POST `
                  -Headers @{"Content-Type"="application/json"} `
                  -Body '{"table_name": "test_table", "data": {"id": 1, "value": "sample data that is longer"}}'

# 4. Query Data from a Table
Invoke-WebRequest -Uri "http://localhost:8000/query/?query=SELECT+*+FROM+test_table;" -Method GET
```
