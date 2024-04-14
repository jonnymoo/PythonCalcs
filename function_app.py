import azure.functions as func
import json
from example_validation import validation_logic
from shape import shape_utils
import pymssql
import os

server_name = os.environ.get('SHAPE_SERVER_NAME')
user = os.environ.get('SHAPE_USER')
password = os.environ.get('SHAPE_USER_PASSWORD')
database = os.environ.get('SHAPE_DATABASE')


app = func.FunctionApp()

@app.route(route="validate")
def validate_data_http(req: func.HttpRequest) -> func.HttpResponse:

  status_code = 200

  try:
    # Get the data from the request body (adjust based on your data format)
    data = req.get_json()
    
    # Call the validation logic from the imported module
    response = validation_logic.validate_salary_records(data);
  
  except Exception as e:  # Catch any exceptions raised during validation
    response = {"message": str(e)}
    status_code = 500  # Internal Server Error

  return func.HttpResponse(
      body=json.dumps(response),
      status_code=status_code,
      mimetype="application/json"
  )

@app.route(route="shape-query")
def query_http(req: func.HttpRequest) -> func.HttpResponse:

  status_code = 200

  try:
    # Get the data from the request body (adjust based on your data format)
    data = req.get_json()
    
    # Get the required SQL
    sql, bind_vars = shape_utils.create_sql(data);
    sql = f"SELECT CAST (({sql}) AS NVARCHAR(MAX))"
    
    # Connect to SQL Server database using integrated security
    with pymssql.connect(server_name,user,password,database) as conn:
      with conn.cursor() as cursor:
        cursor.execute(sql, bind_vars)
        row = cursor.fetchone()
        return func.HttpResponse(
          body=shape_utils.convert_lists_to_objects(row[0].get_json()),
          status_code=200,
          mimetype="application/json")

  except Exception as e:  # Catch any exceptions raised during validation
    response = {"message": str(e)}
    status_code = 500  # Internal Server Error

  return func.HttpResponse(
      body=json.dumps(response),
      status_code=status_code,
      mimetype="application/json"
  )