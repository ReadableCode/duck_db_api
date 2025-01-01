import io
import os

import duckdb
import pandas as pd
from fastapi import FastAPI, File, HTTPException, Request, UploadFile

app = FastAPI()

# Ensure /data directory exists at the project root
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data_dir = os.path.join(project_root, "data")
os.makedirs(data_dir, exist_ok=True)

# Initialize DuckDB connection
db_path = os.path.join(data_dir, "data_store.db")
conn = duckdb.connect(db_path)


@app.post("/raw_query/")
async def raw_query(request: Request):
    """
    Execute a raw SQL query.
    JSON Body Format:
    {
        "query": "SELECT * FROM table_name;",
        "params": []  # Optional list of query parameters
    }
    """
    try:
        # Parse JSON body
        body = await request.json()
        query = body.get("query")
        params = body.get("params", [])

        if not query:
            raise HTTPException(status_code=400, detail="Query must be provided.")

        # Optional: Validate query (e.g., restrict certain commands for safety)
        if query.strip().lower().startswith("drop"):
            raise HTTPException(
                status_code=403, detail="DROP statements are not allowed."
            )

        # Execute query
        result = conn.execute(query, params).fetchdf()
        return {"status": "success", "data": result.to_dict(orient="records")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/create_table/")
def create_table(table_name: str, columns: str):
    """
    Dynamically create a table.
    - `table_name`: Name of the table to create.
    - `columns`: Column definitions (e.g., "id INTEGER, value TEXT").
    """
    try:
        if not table_name.isidentifier():
            raise HTTPException(status_code=400, detail="Invalid table name.")

        conn.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({columns});")
        return {"message": f"Table '{table_name}' created successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/insert/")
async def insert_data(request: Request):
    """
    Insert data into a specified table.
    JSON Body Format:
    {
        "table_name": "table_name_here",
        "data": {"column1": "value1", "column2": "value2"}
    }
    """
    try:
        # Parse JSON body
        body = await request.json()
        table_name = body.get("table_name")
        data = body.get("data")

        if not table_name or not isinstance(data, dict):
            raise HTTPException(
                status_code=400, detail="Both 'table_name' and 'data' are required."
            )

        if not table_name.isidentifier():
            raise HTTPException(status_code=400, detail="Invalid table name.")

        # Prepare SQL query
        columns = ", ".join(data.keys())
        placeholders = ", ".join(["?"] * len(data))
        values = tuple(data.values())

        conn.execute(
            f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders});", values
        )
        return {"message": f"Data inserted into '{table_name}' successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/query/")
def query_data(query: str, table_name: str = None):
    """
    Query data from the database.
    - `table_name`: Name of the table (optional if a raw query is provided).
    - `query`: SQL query to execute.
    """
    try:
        if table_name and not table_name.isidentifier():
            raise HTTPException(status_code=400, detail="Invalid table name.")

        query = query or f"SELECT * FROM {table_name}" if table_name else query
        if not query:
            raise HTTPException(status_code=400, detail="A query must be provided.")

        result = conn.execute(query).fetchdf()
        return result.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
def health_check():
    return {"status": "OK"}


@app.post("/upload/")
def upload_data(table_name: str, file: UploadFile = File(...)):
    """
    Upload CSV or Parquet data to a specified table.
    - `table_name`: Name of the table to upload data into.
    """
    try:
        if not table_name.isidentifier():
            raise HTTPException(status_code=400, detail="Invalid table name.")

        # Read file content
        content = file.file.read()
        df = None

        # Detect file type and load into pandas DataFrame
        if file.filename.endswith(".csv"):
            df = pd.read_csv(io.BytesIO(content))
        elif file.filename.endswith(".parquet"):
            df = pd.read_parquet(io.BytesIO(content))
        else:
            raise HTTPException(
                status_code=400, detail="Unsupported file type. Use CSV or Parquet."
            )

        # Insert data into DuckDB
        conn.register("upload_df", df)
        conn.execute(f"INSERT INTO {table_name} SELECT * FROM upload_df")
        return {"message": "Data uploaded successfully", "rows_inserted": len(df)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        file.file.close()
