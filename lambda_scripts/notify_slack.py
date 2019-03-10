import os
import logging
from urllib.request import Request, urlopen
import json

CHANNEL = os.environ["CHANNEL"]
HOOK_URL = os.environ["HOOK_URL"]

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)


def lambda_handler(event, _context):
    message = event["message"]

    contents = {
        "channel": CHANNEL,
        "text": message,
        "username": "incoming-webhook"
    }
    post_message(contents)

    return event


def post_message(contents):

    req = Request(HOOK_URL, json.dumps(contents).encode('utf-8'))
    response = urlopen(req)
    response.read()
    LOGGER.info("Message posted to %s", contents["channel"])
