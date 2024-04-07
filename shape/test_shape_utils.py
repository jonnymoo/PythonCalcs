import pytest
from shape import shape_utils

def test_check_shape():
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

    match, missing_keys = shape_utils.check_shape(shape, data)

    assert match == True
    assert missing_keys == []

def test_check_shape_missing_folder():
    data = {
        "inputs": {
            "current_date": "2024-03-31"
        }
    }

    shape = {
        "folder": {
            "datejoinedcomp": None
        },
        "inputs": {
            "current_date": None
        }
    }

    match, missing_keys = shape_utils.check_shape(shape, data)

    assert match == False
    assert len(missing_keys) == 1
    assert missing_keys[0]["key"] == "folder"

    expected_example_sql = """
    SELECT 
    (SELECT TOP 1 
        datejoinedcomp
    FROM UPMFOLDER folder1
    WHERE folder1.folderID = @keyobjectid
    FOR JSON PATH, INCLUDE_NULL_VALUES, WITHOUT_ARRAY_WRAPPER) AS folder 
    FOR JSON PATH, WITHOUT_ARRAY_WRAPPER"""
    assert "".join(missing_keys[0]["example-sql"].split()) == "".join(expected_example_sql.split())


def test_create_sql():
    required_shape = {
        "folder": {
            "datejoinedcomp": None,
            "payroll": {
            "payrollname": None
            },
            "salary": [
            {"basicsalary": None}
            ]
        }
    }

    expected = """
    SELECT 
        (SELECT TOP 1 
            datejoinedcomp, 
            (SELECT TOP 1 payrollname
            FROM UPMPAYROLL payroll2
            WHERE payroll2.payrollID = folder1.payrollID
            FOR JSON PATH, INCLUDE_NULL_VALUES, WITHOUT_ARRAY_WRAPPER) AS payroll, 
            (SELECT basicsalary
            FROM UPMsalary salary2
            WHERE salary2.folderID = folder1.folderID
            FOR JSON PATH, INCLUDE_NULL_VALUES) AS salary
        FROM UPMFOLDER folder1
        WHERE folder1.folderID = @keyobjectid
        FOR JSON PATH, INCLUDE_NULL_VALUES, WITHOUT_ARRAY_WRAPPER) AS folder 
    FOR JSON PATH, WITHOUT_ARRAY_WRAPPER"""

    sql = shape_utils.create_sql(required_shape)
    assert "".join(sql.split()) == "".join(expected.split())
