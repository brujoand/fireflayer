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

parser = argparse.ArgumentParser()

parser.add_argument("--dry-run", help="Dry run (No side effects)", action="store_true")
parser.add_argument("--log-level", help="Change log level (default: INFO)", default="INFO", choices=['WARN', 'INFO', 'DEBUG'])
parser.add_argument("--port", help="Set the port for the webserver to listen on", default=8080)
parser.add_argument("action", help="Which action to execute", choices=['webhook', 'process'])
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
  flay_and_update(transaction_id, SplitTransaction(group_title, transactions))

def flay_and_update(transaction_id, split_transaction):
  if(split_transaction.flay(config["flay"])):
    if (args.dry_run):
      logging.info("Skipping upload due to 'dry-run'")
    else:
      firefly_client.update_transaction(transaction_id, split_transaction)
  else:
    logging.debug(f"No changes made to transaction {transaction_id}, skipping upload")

def main():
  match args.action:
    case 'webhook':
      serve(fireflayer, host="0.0.0.0", port=args.port)
    case 'process':
      for transaction_id, transaction in firefly_client.list_transactions():
        flay_and_update(transaction_id, transaction)
