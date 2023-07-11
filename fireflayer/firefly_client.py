import logging
import requests
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
    response = requests.get(url, headers=self.configuration['headers'])
    response.raise_for_status()
    return response.json()

  def parse_split_transaction(self, data):
    transaction_id = data['id']
    attributes = data['attributes']
    group_title = attributes['group_title']
    transactions = attributes['transactions']
    return SplitTransaction(transaction_id, group_title, transactions)


  def update_transaction(self, transaction_id, split_transaction_json):
    url = f"{self.configuration['host']}/api/v1/transactions/{transaction_id}"
    result = requests.put(url, data=split_transaction_json, headers=self.configuration['headers'])
    if result.status_code == requests.codes.ok:
      logging.debug(f"Succesfully updated transaction {transaction_id}")
    else:
      logging.error(f"Got HTTP {result.status_code} when updating transaction {transaction_id}: {result.json()}")

  def list_transactions(self):
    current_page = f"{self.configuration['host']}/api/v1/transactions?type=default&page=1"

    while(True):
      logging.debug(f"fetching page {current_page}")
      api_response = self.get_request(url=current_page)
      for data in api_response['data']:
        yield self.parse_split_transaction(data)
      try:
        current_page = api_response['links']['next']
      except KeyError:
        logging.debug("No more transactions to list")
        break

  def get_transaction(self, transaction_id):
    api_response = self.get_relative_request(path=f"api/v1/transactions/{transaction_id}")
    return self.parse_split_transaction(api_response['data'])
