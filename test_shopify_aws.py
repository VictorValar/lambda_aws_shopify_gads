
import app
import json
import logging
from dotenv import load_dotenv
import os


def test_shopify_aws():
    with open('order.json', 'r') as file:
        paid_event = json.load(file)

        response = app.lambda_handler(paid_event, None)

    logging.warning(response)

    assert response == True


test_shopify_aws()