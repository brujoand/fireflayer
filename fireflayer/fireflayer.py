#!/usr/bin/env python3

import argparse
import os
import yaml

from flask import Flask,request
from waitress import serve

import logging
from logging.config import dictConfig

from fireflayer.firefly_client import FireflyClient
from fireflayer.split_transaction import SplitTransaction
from fireflayer.flayer import Flayer

parser = argparse.ArgumentParser()

parser.add_argument("--dry-run", help="Dry run (No side effects)", action="store_true")
parser.add_argument("--log-level", help="Change log level (default: INFO)", default="INFO", choices=['WARN', 'INFO', 'DEBUG'])
parser.add_argument("--port", help="Set the port for the webserver to listen on", default=8080)
parser.add_argument("action", help="Which action to execute", choices=['webhook', 'process_one', 'process'])
args = parser.parse_args()

dictConfig({
  'version': 1,
  'formatters': {'default': {
    'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
  }},
  'handlers': {'wsgi': {
    'class': 'logging.StreamHandler',
    'stream': 'ext://flask.logging.wsgi_errors_stream',
    'formatter': 'default'
  }},
  'root': {
    'level': args.log_level,
    'handlers': ['wsgi']
  }
})


auth_token = os.environ['FIREFLAYER_AUTH_TOKEN']
api_url = os.environ['FIREFLAYER_API_URL']
config_path = os.environ['FIREFLAYER_CONFIG_PATH']
config = yaml.safe_load(open(config_path, 'r'))

fireflayer = Flask(__name__)
firefly_client = FireflyClient(api_url, auth_token)

@fireflayer.route('/webhook', methods=['POST'])
def webook():
  logging.info("Webhook received")
  process_transaction(request.json)
  return "Webhook processed!"

@fireflayer.route('/health')
def health():
  return 'ok'

def process_transaction(webhook_data):
  logging.info("Processing transaction")
  content = webhook_data['content']
  transaction_id = content['id']
  group_title = content['group_title']
  transactions = content['transactions']
  flay_and_update(SplitTransaction(transaction_id, group_title, transactions))

def flay_and_update(split_transaction):
  incoming_transaction_json = split_transaction.as_minimal_json()
  transaction_id = split_transaction.transaction_id

  flayer = Flayer(config["flay"])
  for transaction in split_transaction.transactions:
    flayer.flay(transaction)

  if (args.dry_run):
    logging.info("Skipping upload due to 'dry-run'")
  else:
    transaction_json = split_transaction.as_minimal_json()
    if (incoming_transaction_json == transaction_json):
      logging.info(f"Transaction with id {transaction_id} has no changes, skipping upload")
    else:
      try:
        firefly_client.update_transaction(transaction_id, transaction_json)
      except Exception as err:
        logging.error(f"Failed to update transaction '{transaction_id}': {err}")


def main():
  match args.action:
    case 'webhook':
      serve(fireflayer, host="0.0.0.0", port=args.port)
    case 'process':
      for transaction in firefly_client.list_transactions():
        flay_and_update(transaction)
    case 'process_one':
      transaction_id = input("Transaction id: ")
      transaction = firefly_client.get_transaction(transaction_id)
      flay_and_update(transaction)

