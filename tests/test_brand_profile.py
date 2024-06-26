import json
import pytest

from sqlalchemy import text
from utils import jqutils

base_api_url = "/api"

##########################
# TEST - BRAND PROFILE
########################## 
def do_check_brand_profile_name_availability(client, headers, payload):
    """
    CHECK BRAND PROFILE AVAILABILITY
    """
    response = client.post(base_api_url + "/brand-profile/availability", headers=headers, json=payload)
    return response

def do_add_brand_profile(client, headers, payload):
    """
    ADD BRAND PROFILE
    """
    response = client.post(base_api_url + "/brand-profile", headers=headers, json=payload)
    return response

def do_get_brand_profile(client, headers, brand_profile_id):
    """
    GET BRAND PROFILE
    """
    response = client.get(base_api_url + f"/brand-profile/{brand_profile_id}", headers=headers)
    return response

def do_update_brand_profile(client, headers, brand_profile_id, payload):
    """
    UPDATE BRAND PROFILE
    """
    response = client.put(base_api_url + f"/brand-profile/{brand_profile_id}", headers=headers, json=payload)
    return response

def do_delete_brand_profile(client, headers, brand_profile_id):
    """
    DELETE BRAND PROFILE
    """
    response = client.delete(base_api_url + f"/brand-profile/{brand_profile_id}", headers=headers)
    return response

def do_get_brand_profile_list(client, headers):
    """
    GET BRAND PROFILE LIST
    """
    response = client.get(base_api_url + "/brand-profiles", headers=headers)
    return response

def do_get_plans_by_brand_profile(client, headers, brand_profile_id, menu_group_info_p=False):
    """
    GET PLANS BY BRAND PROFILE
    """
    request_url = base_api_url + f"/brand-profile/{brand_profile_id}/plans"
    if menu_group_info_p:
        request_url += "?menu_group_info_p=1"
    response = client.get(request_url, headers=headers)
    return response

def do_bulk_update_brand_profile_plan(client, headers, brand_profile_id, payload):
    """
    BULK UPDATE BRAND PROFILE PLANS
    """
    response = client.put(base_api_url + f"/brand-profile/{brand_profile_id}/plans", headers=headers, json=payload)
    return response

##########################
# GLOBALS
########################## 
brand_profile_id = None
plan_id = None

##########################
# FIXTURES
##########################
@pytest.fixture(scope="module", autouse=True)
def existing_brand_profile_count():
    db_engine = jqutils.get_db_engine()
    
    query = text("""
        SELECT COUNT(1) AS cnt
        FROM brand_profile
        WHERE meta_status = :meta_status
    """)
    with db_engine.connect() as conn:
        result = conn.execute(query, meta_status="active").fetchone()
        return result["cnt"]

##########################
# TEST CASES
########################## 
def test_add_brand_profile(client, content_team_headers):
    """
    Test: Add Brand Profile
    """
    payload = {
        "brand_profile_name": "qoqo",
        "external_brand_profile_id": "1",
        "plan_list": [
            {
                "plan_name": "breakfast + lunch + dinner",
                "external_plan_id": "1",
                "menu_group_id_list": [1, 2]
            }
        ]
    }
    response = do_add_brand_profile(client, content_team_headers, payload)
    assert response.status_code == 200

    response_json = response.get_json()
    assert response_json["status"] == "successful"
    assert response_json["action"] == "add_brand_profile"

    global brand_profile_id
    response_data = response_json["data"]
    brand_profile_id = response_data["brand_profile_id"]
    
    # validate that same brand profile name cannot be added again
    response = do_add_brand_profile(client, content_team_headers, payload)
    assert response.status_code == 200
    
    response_json = response.get_json()
    assert response_json["status"] == "failed"
    assert response_json["message"] == "Brand profile name already in use."

def test_brand_profile_availability(client, content_team_headers):
    """
    Test: Check Brand Profile Availability
    """
    payload = {
        "brand_profile_name": "qoqo"
    }
    response = do_check_brand_profile_name_availability(client, content_team_headers, payload)
    assert response.status_code == 200
    response_json = json.loads(response.data)
    assert response_json["status"] == "successful"
    assert response_json["action"] == "check_brand_profile_name_availability"

    response_data = response_json["data"]
    assert response_data["available_p"] == 0

def test_get_brand_profile(client, content_team_headers):
    """
    Test: Get Brand Profile
    """
    response = do_get_brand_profile(client, content_team_headers, brand_profile_id)
    assert response.status_code == 200
    response_json = json.loads(response.data)
    assert response_json["status"] == "successful"
    assert response_json["action"] == "get_brand_profile"

    response_data = response_json["data"]
    assert response_data["brand_profile_name"] == "qoqo"
    
    assert len(response_data["plan_list"]) == 1, "plan list should have 1 item."
    assert len(response_data["plan_list"][0]["menu_group_list"]) == 2, "menu group list should have 2 items."
    
    global plan_id
    plan_id = response_data["plan_list"][0]["plan_id"]

def test_update_brand_profile(client, content_team_headers):
    """
    Test: Update Brand Profile
    """
    payload = {
        "brand_profile_name": "tolpin",
        "external_brand_profile_id": "2",
        "plan_list": [
            {
                "plan_id": plan_id,
                "plan_name": "Weight Loss",
                "external_plan_id": "P-001",
                "menu_group_id_list": [3, 2]
            },
            {
                "plan_id": None,
                "plan_name": "Keto Diet",
                "external_plan_id": "P-002",
                "menu_group_id_list": [1, 2, 3]
            }
        ]
    }
    response = do_update_brand_profile(client, content_team_headers, brand_profile_id, payload)
    assert response.status_code == 200
    response_json = json.loads(response.data)

    assert response_json["status"] == "successful"
    assert response_json["action"] == "update_brand_profile"

    """
    Test: Get Brand Profile
    """
    response = do_get_brand_profile(client, content_team_headers, brand_profile_id)
    assert response.status_code == 200
    response_json = json.loads(response.data)
    assert response_json["status"] == "successful"
    assert response_json["action"] == "get_brand_profile"

    response_data = response_json["data"]
    assert response_data["brand_profile_name"] == "tolpin"

def test_get_brand_profile_list(client, content_team_headers, existing_brand_profile_count):
    """
    Test: Get Brand Profile List
    """
    response = do_get_brand_profile_list(client, content_team_headers)
    assert response.status_code == 200
    response_json = json.loads(response.data)
    assert response_json["status"] == "successful"
    assert response_json["action"] == "get_brand_profiles"
    
    response_data = response_json["data"]
    expected_brand_profile_count = existing_brand_profile_count + 1
    assert len(response_data) == expected_brand_profile_count, f"Brand Profile List should have {expected_brand_profile_count} items."

def test_get_plans_by_brand_profile(client, content_team_headers):
    """
    Test: Get Brand Profile Plans Without Menu Group Info
    """
    global brand_profile_id
    response = do_get_plans_by_brand_profile(client, content_team_headers, brand_profile_id)
    assert response.status_code == 200
    
    response_json = json.loads(response.data)
    assert response_json["status"] == "successful"
    assert response_json["action"] == "get_plans_by_brand_profile"
    
    response_data = response_json["data"]
    brand_profile_id = response_data["brand_profile_id"]
    plan_list = response_data["plan_list"]
    
    assert brand_profile_id
    assert len(plan_list) == 2, "plan list should have 2 item."

def test_get_plans_by_brand_profile_with_menu_group_info(client, content_team_headers):
    """
    Test: Get Brand Profile Plans With Menu Group Info
    """
    global brand_profile_id
    
    response = do_get_plans_by_brand_profile(client, content_team_headers, brand_profile_id, menu_group_info_p=True)
    assert response.status_code == 200
    
    response_json = json.loads(response.data)
    assert response_json["status"] == "successful"
    assert response_json["action"] == "get_plans_by_brand_profile"
    
    response_data = response_json["data"]
    brand_profile_id = response_data["brand_profile_id"]
    plan_list = response_data["plan_list"]
    
    assert brand_profile_id
    assert len(plan_list) == 2, "plan list should have 2 items."
    assert len(plan_list[0]["menu_group_list"]) == 2, "menu group list should have 2 items."

def test_delete_brand_profile(client, content_team_headers, existing_brand_profile_count):
    """
    Test: Delete Brand Profile
    """
    response = do_delete_brand_profile(client, content_team_headers, brand_profile_id)
    assert response.status_code == 200
    response_json = json.loads(response.data)
    assert response_json["status"] == "successful"
    assert response_json["action"] == "delete_brand_profile"

    """
    Test: Get Brand Profile List
    """
    response = do_get_brand_profile_list(client, content_team_headers)
    assert response.status_code == 200
    response_json = json.loads(response.data)
    assert response_json["status"] == "successful"
    assert response_json["action"] == "get_brand_profiles"
    response_data = response_json["data"]
    assert len(response_data) == existing_brand_profile_count, "Brand Profile List should have {existing_brand_profile_count} item."
