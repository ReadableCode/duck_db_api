import io
from pathlib import Path
from typing import List

import duckdb
import pandas as pd
from fastapi import FastAPI, File, HTTPException, Request, UploadFile

app = FastAPI()

# Ensure /data directory exists at the project root
project_root = Path(__file__).resolve().parent.parent
data_dir = project_root / "data"
data_dir.mkdir(exist_ok=True)

# Initialize DuckDB connection
db_path = data_dir / "data_store.db"
conn = duckdb.connect(str(db_path))


@app.on_event("startup")
def startup_event():
    # Create a sample table (only if it doesn't exist)
    conn.execute("CREATE TABLE IF NOT EXISTS test_table (id INTEGER, value TEXT);")


@app.post("/insert/")
async def insert_data(request: Request):
    try:
        # Parse JSON body
        data = await request.json()
        id = data.get("id")
        value = data.get("value")

        if id is None or value is None:
            raise HTTPException(
                status_code=400, detail="Both 'id' and 'value' are required"
            )

        conn.execute("INSERT INTO test_table VALUES (?, ?);", (id, value))
        return {"message": "Data inserted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/query/")
def query_data(query: str):
    try:
        # Execute SQL query
        result = conn.execute(query).fetchdf()
        # Convert result to JSON
        return result.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
def health_check():
    return {"status": "OK"}


@app.post("/upload/")
def upload_data(file: UploadFile = File(...)):
    try:
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
        conn.execute("INSERT INTO data SELECT * FROM upload_df")
        return {"message": "Data uploaded successfully", "rows_inserted": len(df)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        file.file.close()
