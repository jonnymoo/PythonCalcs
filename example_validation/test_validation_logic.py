import datetime
import unittest
from example_validation import validation_logic

class TestValidationLogic(unittest.TestCase):
    # Test methods will go here
    def test_validate_salary_records(self):
        data = {
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

        expected_result = {
            "outputs": {
                "all_present": "true",
                "missing_years": []
            }
        }

        result = validation_logic.validate_salary_records(data)
        self.assertEqual(result, expected_result)  # Assert the expected output
