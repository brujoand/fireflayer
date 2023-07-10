import json
import logging
import requests
from requests.exceptions import HTTPError
from fireflayer.split_transaction import SplitTransaction

class FireflyClient:
  def __init__(self, firefly_url, access_token):
    self.configuration = {
      "host": firefly_url,
      "headers": {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/vnd.api+json",
        "Content-Type": "application/json"
        }
    }

    api_response = self.get_relative_request(path="api/v1/about")
    logging.info(f"Successfully connected to Firefly version {api_response['data']['version']}")

  def get_relative_request(self, path):
    return self.get_request(url=f"{self.configuration['host']}/{path}")

  def get_request(self, url):
    try:
      response = requests.get(url, headers=self.configuration['headers'])
      response.raise_for_status()
      return response.json()
    except HTTPError as http_err:
      logging.error(f'HTTP error occurred: {http_err}')
    except Exception as err:
      logging.error(f'Exception occured: {err}')

  def update_transaction(self, transaction_id, split_transaction):
    payload = json.dumps(split_transaction, default=lambda o: o.__dict__, sort_keys=True, indent=2)
    url = f"{self.configuration['host']}/api/v1/transactions/{transaction_id}"
    try:
      result = requests.put(url, json=payload, headers=self.configuration['headers'])
      if result.status_code == requests.codes.ok:
        logging.debug(f"Succesfully updated transaction {transaction_id}")
      else:
        logging.error(f"Got HTTP {result.status_code} when updating transaction {transaction_id}: {result.json()}")
    except HTTPError as http_err:
      logging.error(f'HTTP error occurred: {http_err}')


  def list_transactions(self):
    current_page = f"{self.configuration['host']}/api/v1/transactions?type=default&page=1"

    while(True):
      logging.debug(f"fetching page {current_page}")
      api_response = self.get_request(url=current_page)
      for data in api_response['data']:
        transaction_id = data['id']
        attributes = data['attributes']
        group_title = attributes['group_title']
        transactions = attributes['transactions']
        yield (transaction_id, SplitTransaction(group_title, transactions))
      try:
        current_page = api_response['links']['next']
      except KeyError:
        logging.debug("No more transactions to list")
        break
