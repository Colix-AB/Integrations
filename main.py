import requests
from prefect import flow
from prefect import task
from prefect.context import get_run_context

import json

# API endpoint for users
API_URL = "https://core-api-test.colixsystems.com/api/v2/appletUsers/a81baef3-4267-4648-9b3a-357319f57577?includes=User,UserGroups"

@task
def fetch_users():
    """Fetch users from the API."""

    # Bearer token
    bearer_token = "secret"

    # Add the token to the Authorization header
    headers = {
        "Authorization": f"Bearer {bearer_token}"
    }

    response = requests.get(API_URL, headers=headers)

    if response.status_code == 200:
        return response.json()  # Assuming the response is a JSON array of users
    else:
        raise Exception(f"Failed to fetch users: {response.status_code}")

@task
def filter_users(users,filter_param):
    """Filter users by param."""
    #print(users)
    hits = []
    for user in users:
        if filter_param.lower() in user['user']['userName'].lower():
            print(user['user']['userName'])
            hits.append(user['user']['userName'])
    return hits

@task
def send_slack_notification(users,filter_param):
    """Send a Slack message with the filtered output."""
    context = get_run_context()

    # Slack token for your bot
    webhook_url = "secret"

    # Prepare the message content
    message = {
        "text": f"{filter_param} has the following users: {users} in test"
    }

    print(message)

    response = requests.post(webhook_url, data=json.dumps(message), headers={'Content-Type': 'application/json'})
    if response.status_code == 200:
        print("Message sent successfully!")
    else:
        print(f"Error sending message: {response.status_code, response}")

@flow
def get_users_flow(filter_param):
    users = fetch_users()
    filtered_users = filter_users(users, filter_param)
    send_slack_notification(filtered_users, filter_param)
