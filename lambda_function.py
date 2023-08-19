from typing import Dict, Any

import requests
import json
import os.path
import sys
import logging
from datetime import date
from requests.exceptions import HTTPError
from requests.adapters import HTTPAdapter
from urllib3 import Retry

#logging.basicConfig(level=logging.DEBUG)

CREDS_FILE = "./.pixela_creds"
PIXELA_ENDPOINT = "https://pixe.la/v1"

with open(CREDS_FILE) as json_creds:
    user_params = json.load(json_creds)

headers = {
    "X-USER-TOKEN": user_params['token']
}


def call_pixela(endpoint, payload, method, auth_headers=None):
    """Sends data to the Pixela API"""
    if auth_headers is None:
        auth_headers = {}

    # Pixela API denies 25% of requests, therefore a retry mechanism is required.
    # This also means a custom error handler is required rather than raise_for_status()
    pixela_session = requests.Session()
    # POST is not a default allowed_method. That bug took a while to find.
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[500, 502, 503, 504], allowed_methods=['POST', 'DELETE'])
    pixela_session.mount('https://', HTTPAdapter(max_retries=retries))
    if method == "post":
        response = pixela_session.post(url=endpoint, json=payload, headers=auth_headers)
    elif method == "delete":
        response = pixela_session.delete(url=endpoint, json=payload, headers=auth_headers)
    else:
        print("Error: Method not supported")
        sys.exit(1)
    print("Configuring Pixela...")
    #response.raise_for_status()

    response_text = json.loads(response.text.encode('utf-8'))
    if response_text['isSuccess']:
        print(f"Success: {response.status_code} {response_text['message']}")

    lambda_response = {
        'statusCode': response.status_code,
        'body': response_text['message']
    }

    return lambda_response


def create_user():
    """Creates a user via the Pixela API"""
    if os.path.exists(CREDS_FILE):
        user_endpoint = f"{PIXELA_ENDPOINT}/users"
        lambda_response = call_pixela(user_endpoint, user_params, "post")
    return lambda_response


def delete_user(username):
    """Deletes a user via the Pixela API"""
    user_endpoint = f"{PIXELA_ENDPOINT}/users/{username}"
    lambda_response = call_pixela(user_endpoint, username, "delete", headers)
    return lambda_response


def create_graph(graph, description, unit):
    """Creates a new graph via the Pixela API"""
    graph_endpoint = f"{PIXELA_ENDPOINT}/users/{user_params['username']}/graphs"

    graph_config = {
        "id": graph,
        "name": description,
        "unit": unit,
        "type": "int",
        "color": "shibafu"
    }

    lambda_response = call_pixela(graph_endpoint, graph_config, "post", headers)

    return lambda_response


def delete_graph(graph_name):
    """Deletes a graph via the Pixela API"""
    graph_endpoint = f"{PIXELA_ENDPOINT}/users/{user_params['username']}/graphs/{graph_name}"

    lambda_response = call_pixela(graph_endpoint, graph_name, "delete", headers)

    return lambda_response


def create_pixel(graph, duration):
    """Creates a new graph via the Pixela API"""
    pixel_endpoint = f"{PIXELA_ENDPOINT}/users/{user_params['username']}/graphs/{graph}"

    pixel_config = {
        "date": date.today().strftime("%Y%m%d"),
        "quantity": duration
    }

    lambda_response = call_pixela(pixel_endpoint, pixel_config, "post", headers)

    return lambda_response


def delete_current_pixel(graph):
    """Deletes today's pixel data via the Pixela API"""
    today = date.today().strftime("%Y%m%d")
    pixel_endpoint = f"{PIXELA_ENDPOINT}/users/{user_params['username']}/graphs/{graph}/{today}"

    lambda_response = call_pixela(pixel_endpoint, graph, "delete", headers)

    return lambda_response


def lambda_handler(event, context):
    # Log the received event for future debugging purposes
    print(event)
    #event_data = event
    event_data = json.loads(event["body"])
    if event_data['action'] == "create_graph":
        return create_graph(event_data['graph'], event_data['description'], event_data['unit'])
    elif event_data['action'] == "delete_graph":
        return delete_graph(event_data['graph'])
    elif event_data['action'] == "create_pixel":
        return create_pixel(event_data['graph'], event_data['duration'])
    elif event_data['action'] == "delete_pixel":
        return delete_current_pixel(event_data['graph'])


# Test the lambda function locally
if __name__ == "__main__":
    event_create_graph = {
        "action": "create_graph",
        "graph": "test-graph",
        "description": "Graph for test case",
        "unit": "hours"
    }
    event_create_pixel = {
        "action": "create_pixel",
        "graph": "test-graph",
        "duration": "30"
    }
    event_delete_graph = {
        "action": "delete_graph",
        "graph": "test-graph",
    }
    context = []
    print(lambda_handler(event_create_graph, context))
    print(lambda_handler(event_create_pixel, context))
    print(lambda_handler(event_delete_graph, context))
