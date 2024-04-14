import json
from typing import Dict
import string

allowed_chars = set(string.ascii_letters + string.digits + '_')

def sanitize_name(name):
  """
  Sanitizes a string by removing non-alphanumeric characters.

  Args:
      name: The string to be sanitized.

  Returns:
      A new string containing only alphanumeric characters and underscores.
  """
  return ''.join([char for char in name if char in allowed_chars])

def shape(shape):
  """
  Decorator to define the required shape for a function.
  """
  def decorator(func):
    def wrapped_func(data):
      return validate_with_shape(func, shape, data)
    return wrapped_func  
  return decorator

def validate_with_shape(func, shape, data):
  match, missing_keys = check_shape(shape, data)
  if not match:
    raise ValueError( {
      "required": shape,
      "missing_keys": missing_keys
    })
  return func(data)

def check_shape(required_shape, actual_input):
    # Recursively check for matching keys and types
    def check_nested(required, actual):
        missing_keys = []
        for key, req_value in required.items():
            if key not in actual:
                missing_keys.append({"key": key, "reason": "missing"})
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

def create_sql(required_shape, id_param_name=None):
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
    filters = []
    bindvars = []

    for key, value in obj.items():
      key = sanitize_name(key)
      
      if isinstance(value, dict):
        # Object - many-to-one relationship
        alias = f"{key}{counter}"
        nested_sql, nested_bindvars, nested_filters = build_nested_sql(value, alias, key, counter+1)
        bindvars.extend(nested_bindvars)
        whereclauses = []
        if(root_alias):
          whereclauses.append(f"{alias}.{key}ID = {root_alias}.{key}ID")
        elif(id_param_name):
          whereclauses.append(f"{alias}.{key}ID = {id_param_name}")
        
        whereclauses.extend(nested_filters)
        
        selected_columns.append(f"""
          (SELECT {nested_sql}
          FROM UPM{key.upper()} {alias}
          {"WHERE " if len(whereclauses) else ""}{" AND ".join(whereclauses)}
          FOR JSON PATH, INCLUDE_NULL_VALUES) AS {key}
        """)
      elif isinstance(value, list):
        # List - one-to-many relationship with foreign key on child
        alias = f"{key}{counter}"
        nested_sql, nested_bindvars, nested_filters = build_nested_sql(value[0], alias, key, counter+1)
        bindvars.extend(nested_bindvars)
        whereclauses = []
        if(root_alias):
          whereclauses.append(f"{alias}.{root_name}ID = {root_alias}.{root_name}ID")

        selected_columns.append(f"""
          (SELECT {nested_sql}
          FROM UPM{key} {alias}
          {"WHERE " if len(whereclauses) else ""}{" AND ".join(whereclauses)}
          FOR JSON PATH, INCLUDE_NULL_VALUES) AS {key}
        """)
      elif(value):
        bindvars.append(value)
        filters.append(f"{root_alias}.{key} = %s")
      else:
        # Normal member - column name 
        selected_columns.append(key)
        
    return (", ".join(selected_columns)).strip(), bindvars, filters

  # Build selected columns with explicit names from the shape definition
  nested_sql, nested_bindvars, _ = build_nested_sql(required_shape)
  return f"SELECT {nested_sql} FOR JSON PATH", nested_bindvars