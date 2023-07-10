from fireflayer.flayer import Flayer

def test_extract_payment_tag():
  flay_config = {
    "function": "extract_tag",
    "arguments": {
      "source_field": "description",
      "pattern": r'^(.+)\ ?\*',
      "group": 1
      }
    }

  transaction = {
    "transaction_journal_id": 1337,
    "description": "PayPal *Ice Cream 4 Realz",
    "tags": ["some existing tag"]
  }

  flayer = Flayer([flay_config])
  flayer.flay(transaction)
  assert(transaction['tags'] == ['some existing tag', 'PayPal'])

def test_remove_payment_tag():
  flay_config = {
    "function": "replace",
    "arguments": {
      "source_fields": ["description", "destination_name"],
      "pattern": r'^(.+)\ ?\*',
      "value": ""
      }
    }

  transaction = {
    "transaction_journal_id": 1337,
    "description": "PayPal *Ice Cream 4 Realz",
    "destination_id": 420,
    "destination_name": "PayPal *Ice Cream 4 Realz",
    }

  flayer = Flayer([flay_config])
  flayer.flay(transaction)
  assert(transaction['description'] == "Ice Cream 4 Realz")
  assert(transaction['destination_name'] == "Ice Cream 4 Realz")
  assert("description_id" not in transaction)

def test_category_by_filter():
  flay_config = {
    "function": "category_by_filter",
    "arguments": {
      "source_fields": ["destination_name"],
      "category_name": "Dagligvare",
      "includes": ["oBs", "Deli", "Market"],
      "excludes": ["Obs Bygg"],
      "case_sensitive": False
      }
    }

  transaction = {
    "transaction_journal_id": 1337,
    "destination_id": 69,
    "destination_name": "Coop Obs",
    "category_id": 420,
    "category_name": "Foodstuff",
    }

  flayer = Flayer([flay_config])
  flayer.flay(transaction)
  assert(transaction['category_name'] == "Dagligvare")

def test_destination_by_tags():

  flay_config = {
    "function": "destination_by_tags",
    "arguments": {
      "tag_names": ['PayPal']
      }
    }

  transaction = {
    "transaction_journal_id": 1337,
    "destination_id": 69,
    "destination_name": "HTNS456HTNS",
    "tags": ["PayPal"]
  }

  flayer = Flayer([flay_config])
  flayer.flay(transaction)
  assert(transaction['destination_name'] == "PayPal")
  assert("destination_id" not in transaction)

