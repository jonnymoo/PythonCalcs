import json

def check_shape(required_shape, actual_input):
    # Recursively check for matching keys and types
    def check_nested(required, actual):
        missing_keys = []
        for key, req_value in required.items():
            if key not in actual:
                lower_key = key.lower()
                if lower_key not in ["folder", "person", "paylocation", "payroll", "payrollmember", "company", "client", "scheme", "area", "system"]:
                    missing_keys.append({"key": key, "reason": "missing"})
                else:
                    example_sql = create_sql({key: req_value}) 
                    missing_keys.append({"key": key, "reason": "missing", "example-sql": example_sql})
            elif isinstance(req_value, dict):
                if not isinstance(actual[key], dict):
                    missing_keys.append({"key": key, "reason":"expected a nested object"})
                else:
                    missing_keys.extend(check_nested(req_value, actual[key]))
            elif isinstance(req_value, list):
                if not isinstance(actual[key], list):
                    missing_keys.append({"key": key, "reason":"expected a list"})
                elif len(req_value) > 0 and isinstance(req_value[0], dict):
                    for i, item in enumerate(actual[key]):
                        missing_keys.extend(check_nested(req_value[0], item))
        return missing_keys

    # Perform the shape check
    missing_keys = check_nested(required_shape, actual_input)

    # Return result and any missing keys
    return len(missing_keys) == 0, missing_keys

def create_sql(required_shape, id_param_name="@keyobjectid"):
  """
  Creates a SQL statement string based on a UPM object shape definition.

  Args:
      required_shape: A dictionary representing the required shape of the UPM object.
      folder_id_param_name: The name of the parameter used for folder ID in the WHERE clause (default: "@folderid").

  Returns:
      A string containing the generated SQL statement.
  """
  def build_nested_sql( obj, root_alias = None, root_name = None, counter=1):
    # Function to recursively build nested SQL queries with explicit column selection
    selected_columns = []
    for key, value in obj.items():
      if isinstance(value, dict):
        # Object - many-to-one relationship
        alias = f"{key}{counter}"
        selected_columns.append(f"""
          (SELECT TOP 1 {build_nested_sql(value, alias, key, counter+1)}
          FROM UPM{key.upper()} {alias}
          {f"WHERE {alias}.{key}ID = {root_alias}.{key}ID" if root_alias else f"WHERE {alias}.{key}ID = {id_param_name}"}
          FOR JSON PATH, INCLUDE_NULL_VALUES, WITHOUT_ARRAY_WRAPPER) AS {key}
        """)
      elif isinstance(value, list):
        # List - one-to-many relationship with foreign key on child
        alias = f"{key}{counter}"
        selected_columns.append(f"""
          (SELECT {build_nested_sql(value[0], alias, key, counter+1)}
          FROM UPM{key} {alias}
          {f"WHERE {alias}.{root_name}ID = {root_alias}.{root_name}ID" if root_alias else ""}
          FOR JSON PATH, INCLUDE_NULL_VALUES) AS {key}
        """)
      else:
        # Normal member - column name 
        selected_columns.append(key)
    return (", ".join(selected_columns)).strip()

  # Build selected columns with explicit names from the shape definition
  return f"SELECT {build_nested_sql(required_shape)} FOR JSON PATH, WITHOUT_ARRAY_WRAPPER"