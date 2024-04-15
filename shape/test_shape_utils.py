import pytest
from shape import shape_utils
import json

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
        (SELECT TOP 1 datejoinedcomp, 
            (SELECT TOP 1 payrollname
            FROM UPMPAYROLL payroll2
            WHERE payroll2.payrollID = folder1.payrollID
            FOR JSON PATH, INCLUDE_NULL_VALUES) AS convert_to_object_payroll, 
            (SELECT basicsalary
            FROM UPMsalary salary2
            WHERE salary2.folderID = folder1.folderID
            FOR JSON PATH, INCLUDE_NULL_VALUES) AS salary
        FROM UPMFOLDER folder1
        WHERE folder1.folderID = @keyobjectid
        FOR JSON PATH, INCLUDE_NULL_VALUES) AS convert_to_object_folder 
    FOR JSON PATH"""

    sql,_ = shape_utils.create_sql(required_shape,"@keyobjectid")
    assert "".join(sql.split()) == "".join(expected.split())

def test_create_sql_sanitised():
    required_shape = {
        "folder": {
            "date joined comp;": None,
            "payroll": {
            "payrollname": None
            },
            "sal;ary": [
            {"basicsalary": None}
            ]
        }
    }

    expected = """
    SELECT 
        (SELECT TOP 1 datejoinedcomp, 
            (SELECT TOP 1 payrollname
            FROM UPMPAYROLL payroll2
            WHERE payroll2.payrollID = folder1.payrollID
            FOR JSON PATH, INCLUDE_NULL_VALUES) AS convert_to_object_payroll, 
            (SELECT basicsalary
            FROM UPMsalary salary2
            WHERE salary2.folderID = folder1.folderID
            FOR JSON PATH, INCLUDE_NULL_VALUES) AS salary
        FROM UPMFOLDER folder1
        WHERE folder1.folderID = @keyobjectid
        FOR JSON PATH, INCLUDE_NULL_VALUES) AS convert_to_object_folder 
    FOR JSON PATH"""

    sql,_ = shape_utils.create_sql(required_shape,"@keyobjectid")
    assert "".join(sql.split()) == "".join(expected.split())



def test_create_sql_no_primary_key():
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
            FOR JSON PATH, INCLUDE_NULL_VALUES) AS convert_to_object_payroll, 
            (SELECT basicsalary
            FROM UPMsalary salary2
            WHERE salary2.folderID = folder1.folderID
            FOR JSON PATH, INCLUDE_NULL_VALUES) AS salary
        FROM UPMFOLDER folder1
        FOR JSON PATH, INCLUDE_NULL_VALUES) AS convert_to_object_folder 
    FOR JSON PATH"""

    sql,_ = shape_utils.create_sql(required_shape)
    assert "".join(sql.split()) == "".join(expected.split())


def test_create_sql_with_filter():
    required_shape = {
        "folder": {
            "datejoinedcomp": None,
            "folderref": "MYREF",
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
            FOR JSON PATH, INCLUDE_NULL_VALUES) AS convert_to_object_payroll, 
            (SELECT basicsalary
            FROM UPMsalary salary2
            WHERE salary2.folderID = folder1.folderID
            FOR JSON PATH, INCLUDE_NULL_VALUES) AS salary
        FROM UPMFOLDER folder1
        WHERE folder1.folderref = %s
        FOR JSON PATH, INCLUDE_NULL_VALUES) AS convert_to_object_folder 
    FOR JSON PATH"""

    sql,bindvars = shape_utils.create_sql(required_shape)
    assert "".join(sql.split()) == "".join(expected.split())
    assert bindvars == ["MYREF"]

def test_create_sql_top_level_list():
    required_shape = {
        "folder": [{
            "datejoinedcomp": None
        }]
    }

    expected = """
    SELECT 
        (SELECT datejoinedcomp
        FROM UPMfolder folder1
        FOR JSON PATH, INCLUDE_NULL_VALUES) AS folder 
    FOR JSON PATH"""

    sql,_ = shape_utils.create_sql(required_shape)
    assert "".join(sql.split()) == "".join(expected.split())

def test_create_sql_top_level_list_with_filter():
    required_shape = {
        'folder': [{'datejoinedcomp': None,
                    'folderref': 'FRA4'}]}

    expected = """
    SELECT 
        (SELECT datejoinedcomp
        FROM UPMfolder folder1
        WHERE folder1.folderref = %s
        FOR JSON PATH, INCLUDE_NULL_VALUES) AS folder 
    FOR JSON PATH"""

    sql,bindvars = shape_utils.create_sql(required_shape)
    assert "".join(sql.split()) == "".join(expected.split())
    assert bindvars == ["FRA4"]

def test_create_sql_two_objects():
    required_shape = {
        "folder": {
            "payroll": {
            "payrollname": None
            },
            "client": {
            "clientname": None
            }
        }
    }

    expected = """
    SELECT (SELECT TOP 1 (SELECT TOP 1 payrollname
                        FROM UPMPAYROLL payroll2
                        WHERE payroll2.payrollID = folder1.payrollID
                        FOR JSON PATH, INCLUDE_NULL_VALUES) AS convert_to_object_payroll,
                        (SELECT TOP 1 clientname
                        FROM UPMCLIENT client2
                        WHERE client2.clientID = folder1.clientID
                        FOR JSON PATH, INCLUDE_NULL_VALUES) AS convert_to_object_client
            FROM UPMFOLDER folder1
            FOR JSON PATH, INCLUDE_NULL_VALUES) AS convert_to_object_folder 
    FOR JSON PATH"""

    sql,_ = shape_utils.create_sql(required_shape)
    assert "".join(sql.split()) == "".join(expected.split())


def test_convert_to_object_with_sub_list():
    result = [{'convert_to_object_test': [{'convert_to_object_subobject':[{'mything':'thingy'}]}]}]
    converted = shape_utils.convert_lists_to_objects(result)
    assert converted == {'test': {'subobject':{'mything':'thingy'}}}

def test_convert_to_object_with_sub_object():
    result = [{"convert_to_object_folder":[{"convert_to_object_payroll":[{"payrollname":"Main Payroll"}],"convert_to_object_client":[{"clientname":"Test Client 1"}]}]}]
    converted = shape_utils.convert_lists_to_objects(result)
    assert converted == {"folder":{"payroll":{"payrollname":"Main Payroll"},"client":{"clientname":"Test Client 1"}}}


def test_convert_to_object_no_converts():
    result = [{"thing1": [{"thing2":"thing2val"}]}]
    converted = shape_utils.convert_lists_to_objects(result)
    assert converted == {"thing1": [{"thing2":"thing2val"}]}

def test_convert_to_object_from_jsonloads_no_converts():
    result = "[{\"thing1\": [{\"thing2\":\"thing2val\"}]}]"
    result_json = json.loads(result)
    converted = shape_utils.convert_lists_to_objects(result_json)
    assert converted == {"thing1": [{"thing2":"thing2val"}]}

def test_convert_object_from_jsonload():
    result = "[{\"convert_to_object_folder\":[{\"datejoinedcomp\":\"1987-04-04T00:00:00\",\"salary\":[{\"datestarted\":\"2020-01-01T00:00:00\"}]}]}]"    
    result_json = json.loads(result)
    converted = shape_utils.convert_lists_to_objects(result_json)
    assert converted == {"folder":{"datejoinedcomp":"1987-04-04T00:00:00","salary":[{"datestarted":"2020-01-01T00:00:00"}]}}

def test_convert_empty_lists():
    result = [{"emptything1": None}]
    converted = shape_utils.convert_lists_to_objects(result)
    assert converted == {"emptything1": []}