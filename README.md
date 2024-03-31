# PythonCalcs: A POC for Data Packaging and Calculation

This repository demonstrates a Python proof-of-concept (POC) for packaging member data and performing calculations using the pandas library. It showcases how to:

- **Specify required data formats:** Define the expected structure of member data for accurate processing.
- **Request data based on shape:** Retrieve data adhering to the specified format to ensure compatibility with calculations.
- **Process data with pandas:** Use pandas to manipulate and analyse the acquired data.
- **Produce meaningful output:** Generate results which can be used as either validations, or updates.

## Getting Started

### Prerequisites

Ensure you have Python 3.x and the pandas library installed. You can install pandas using `pip install pandas`.

Azure Functions Core Tools: Install the Azure Functions Core Tools following the instructions from here: https://learn.microsoft.com/en-us/azure/azure-functions/functions-run-local

### Running the Example

   ```bash
   cd calc_service
   func start
   ```
## Example: validate salary years

An example of how to provide sample salary records and do some simple dataframe manipulation

### Example input

```json
{
  "folder": {
    "date_joined_comp": "2022-12-01",
    "salary": [
      {"date_started": "2022-12-01"},
      {"date_started": "2023-04-01"}
    ]
  },
  "inputs": {
    "current_date": "2024-03-31"
  }
}
```