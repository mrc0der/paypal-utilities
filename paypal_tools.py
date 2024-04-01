import logging
import os
import sys
import click
import requests

ENV = os.getenv("ENVIRONMENT", 'dev')

# PayPal API base URL
if ENV == 'prod':
    PAYPAL_API_BASE = (
        "https://api.sandbox.paypal.com"
    )
else:
    # Use "https://api.sandbox.paypal.com" for sandbox
    PAYPAL_API_BASE = (
        "https://api.sandbox.paypal.com"
    )

# PayPal API credentials
CLIENT_ID = os.getenv("PAYPAL_CLIENT_ID")
PAYPAL_SECRET = os.getenv("PAYPAL_SECRET")

if CLIENT_ID is None:
    logging.error("CLIENT_ID is not set")
    sys.exit(1)

if PAYPAL_SECRET is None:
    logging.error("PAYPAL_SECRET is not set")
    sys.exit(1)

def get_paypal_token():
    """Obtain a PayPal API OAuth token."""
    url = f"{PAYPAL_API_BASE}/v1/oauth2/token"
    headers = {"Accept": "application/json", "Accept-Language": "en_US"}
    response = requests.post(
        url,
        headers=headers,
        auth=(CLIENT_ID, PAYPAL_SECRET),
        data={"grant_type": "client_credentials"},
    )
    return response.json()["access_token"]


def list_webhooks():
    """List current PayPal webhooks."""
    access_token = get_paypal_token()
    url = f"{PAYPAL_API_BASE}/v1/notifications/webhooks"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        webhooks = response.json()["webhooks"]
        print("Got webhooks...")
        for webhook in webhooks:
            print(f"Webhook ID: {webhook['id']}, URL: {webhook['url']}")
            for eventtype in webhook["event_types"]:
                print(f"{eventtype['name']} - {eventtype['description']}")
    else:
        print(f"Failed to list webhooks, status code: {response.status_code}")


def create_webhook(url, event_types):
    """
    Create a new PayPal webhook.

    Args:
        url (str): The URL for the webhook.
        event_types (list): List of event types to subscribe to.
    """
    access_token = get_paypal_token()
    webhook_url = f"{PAYPAL_API_BASE}/v1/notifications/webhooks"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
    }
    payload = {
        "url": url,
        "event_types": [{"name": event_name} for event_name in event_types],
    }
    response = requests.post(webhook_url, headers=headers, json=payload)

    if response.status_code in [200, 201]:
        print("Webhook created successfully.")
        print(response.json())
    else:
        print(
            f"Failed to create webhook, status code: {response.status_code}, error: {response.text}"
        )


def delete_webhook(webhook_id):
    """
    Delete a PayPal webhook by its ID.

    Args:
        webhook_id (str): The ID of the webhook to be deleted.
    """
    access_token = get_paypal_token()
    url = f"{PAYPAL_API_BASE}/v1/notifications/webhooks/{webhook_id}"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
    }

    response = requests.delete(url, headers=headers)

    if response.status_code in [200, 204]:  # 204 No Content for successful deletion
        print(f"Webhook with ID {webhook_id} deleted successfully.")
    else:
        print(
            f"Failed to delete webhook, status code: {response.status_code}, error: {response.text}"
        )


def webhook_event_types_list():
    """List all available PayPal webhook event types and return them as a list."""
    access_token = get_paypal_token()
    url = f"{PAYPAL_API_BASE}/v1/notifications/webhooks-event-types"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    response = requests.get(url, headers=headers)

    event_type_list = []

    if response.status_code == 200:
        event_types = response.json().get("event_types", [])
        for event_type in event_types:
            event_type_list.append(event_type["name"])
    else:
        print(f"Failed to list event types, status code: {response.status_code}")

    return event_type_list


WEBHOOK_EVENT_TYPES = webhook_event_types_list()

print(f"Available webhooks: {WEBHOOK_EVENT_TYPES}")

# Example usage: List current webhooks
list_webhooks()

# Example usage
# create_webhook("https://api.n3rd-media.com/v1/paypal-order", WEBHOOK_EVENT_TYPES)

# delete_webhook('webhook_id_here')

# TODO: Adding click
# FIXME as this is not working yet
@click.command()
@click.option('-l', '--list-webhooks', 'list')
def paypal_utilities(string):
    click.echo(string)
