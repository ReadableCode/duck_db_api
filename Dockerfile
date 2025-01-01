# Use an official Python image as the base
FROM python:3.13-slim

# Set the working directory in the container
WORKDIR /duck_db_api

# Copy only the requirements file first to leverage Docker caching
COPY requirements.txt /duck_db_api/

# Install dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files into the container
COPY . /duck_db_api

# Expose the port your app runs on
EXPOSE 8000

# run the command from the src directory
# Command to run the application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
