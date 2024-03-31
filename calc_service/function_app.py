import azure.functions as func
import datetime
import json
import logging
from example_validation import validation_logic

def validate_data_http(req: func.HttpRequest) -> func.HttpResponse:

  status_code = 200

  try:
    # Get the data from the request body (adjust based on your data format)
    data = req.get_json()
    
    # Call the validation logic from the imported module
    response = json.dumps(validation_logic.validate_salary_records(data))

  except Exception as e:  # Catch any exceptions raised during validation
    response = f"Validation error: {str(e)}"
    status_code = 500  # Internal Server Error

  return func.HttpResponse(
      body=response,
      status_code=status_code,
      mimetype="text/plain"
  )

app = func.FunctionApp()
app.route("validate")(validate_data_http)
