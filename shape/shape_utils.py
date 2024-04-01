import json

def check_shape(required_shape, actual_input):
    # Recursively check for matching keys and types
    def check_nested(required, actual):
        missing_keys = []
        for key, req_value in required.items():
            if key not in actual:
                missing_keys.append(key)
            elif isinstance(req_value, dict):
                if not isinstance(actual[key], dict):
                    missing_keys.append(f"{key} (expected a nested object)")
                else:
                    missing_keys.extend(check_nested(req_value, actual[key]))
            elif isinstance(req_value, list):
                if not isinstance(actual[key], list):
                    missing_keys.append(f"{key} (expected a list)")
                elif len(req_value) > 0 and isinstance(req_value[0], dict):
                    for i, item in enumerate(actual[key]):
                        missing_keys.extend(check_nested(req_value[0], item))
        return missing_keys

    # Perform the shape check
    missing_keys = check_nested(required_shape, actual_input)

    # Return result and any missing keys
    return len(missing_keys) == 0, missing_keys
