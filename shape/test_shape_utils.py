import datetime
import unittest
from shape import utils

class TestShapeUtils(unittest.TestCase):
    # Test methods will go here
    def test_check_shape(self):
        data = {
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

        shape = {
            "folder": {
                "date_joined_comp": None,
                "salary": [
                {"date_started": None}
                ]
            },
            "inputs": {
                "current_date": None
            }
        }

        match, missing_keys = utils.check_shape(shape, data)

        self.assertEqual(match, True)
        self.assertEqual(missing_keys, [])

    def test_check_shape_missing_folder(self):
            data = {
                "inputs": {
                    "current_date": "2024-03-31"
                }
            }

            shape = {
                "folder": {
                    "date_joined_comp": None,
                    "salary": [
                    {"date_started": None}
                    ]
                },
                "inputs": {
                    "current_date": None
                }
            }

            match, missing_keys = utils.check_shape(shape, data)

            self.assertEqual(match, False)
            self.assertEqual(missing_keys, ["folder"])
