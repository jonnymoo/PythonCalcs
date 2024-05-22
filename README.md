# PythonCalcs: A POC for Data Packaging and Calculation

This repository demonstrates a Python proof-of-concept (POC) for packaging member data and performing calculations using the pandas library. It showcases how to:

- **Request data based on shape:** Retrieve data adhering to the specified format to ensure compatibility with calculations.
- **Process data with pandas:** Use pandas to manipulate and analyse the acquired data.
- **Produce meaningful output:** Generate results which can be used as either validations, or updates.

## Shapes

See https://codepen.io/Jonny-Muir/full/XWQqqwy for an example of how to build a shape.

## Concepts

- A calc is a stateless functions accessible at a REST end point
- The calc understands the shapes of data required
- Data is passed in (not collected)
- Shapes can be used by consumers and used to generate ways of getting the minimum data required to process the calc (e.g. a sql server for JSON PATH statement)
- Workflow can be used to orchestrate the calling of the end point and using the results
- Other consumers can call the same REST APIs (or just use the function standalone)
- Juypter notebooks can be used to create live specification / documentation

## Getting Started

### Prerequisites

Ensure you have Python 3.x and the pandas library installed. You can install pandas using `pip install pandas`.

Azure Functions Core Tools: Install the Azure Functions Core Tools following the instructions from here: https://learn.microsoft.com/en-us/azure/azure-functions/functions-run-local

### Running the Example

   ```bash
   func start
   ```

## Example: validate salary years

An example of how to provide sample salary records and do some simple dataframe manipulation

### Example input

```json
{
  "folder": {
    "datejoinedcomp": "2022-12-01",
    "salary": [
      {"datestarted": "2022-12-01"},
      {"datestarted": "2023-04-01"}
    ]
  },
  "inputs": {
    "current_date": "2024-03-31"
  }
}
```

### Example output if shape passed
```json
{
  "outputs": {
    "validation_passed": "true", 
    "missing_years": []
  }
}
```

### Example output if shape not passed

```json
{
  "required": {
  "folder": {
    "datejoinedcomp": null, 
    "salary": [{
      "datestarted": null
      }]
    }, 
    "inputs": {
      "current_date": null
    }
  }, 
  "missing_keys": [{
    "key": "folder", 
    "reason": "missing"
  }]
}
```

### Example get data from SQL Server database

To do this you will need to set environment variables to connect to a shape database e.g.

```bash
export SHAPE_SERVER_NAME="mydatabaseserver" SHAPE_USER="myuser" SHAPE_USER_PASSWORD="mypassword" SHAPE_DATABASE="mydatabase"
```

And then pass it a shape - tip, get this from the [shape builder](https://codepen.io/Jonny-Muir/full/XWQqqwy)
