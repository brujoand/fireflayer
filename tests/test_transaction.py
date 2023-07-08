from fireflayer.transaction import Transaction

def test_extract_payment_tag():
  flay_config = {
    "function": "extract_tag",
    "arguments": {
      "source_field": "description",
      "pattern": r'^(.+)\ ?\*',
      "group": 1
      }
    }

  transaction_data = {
    "transaction_journal_id": 1337,
    "description": "PayPal *Ice Cream 4 Realz",
    "tags": ["some existing tag"]
  }

  transaction = Transaction(transaction_data)
  transaction.flay([flay_config])
  assert(transaction.transaction['tags'] == ['some existing tag', 'PayPal'])

def test_remove_payment_tag():
  flay_config = {
    "function": "replace",
    "arguments": {
      "source_fields": ["description", "destination_name"],
      "pattern": r'^(.+)\ ?\*',
      "value": ""
      }
    }

  transaction_data = {
    "transaction_journal_id": 1337,
    "description": "PayPal *Ice Cream 4 Realz",
    "destination_id": 420,
    "destination_name": "PayPal *Ice Cream 4 Realz",
  }

  transaction = Transaction(transaction_data)
  transaction.flay([flay_config])
  assert(transaction.transaction['description'] == "Ice Cream 4 Realz")
  assert(transaction.transaction['destination_name'] == "Ice Cream 4 Realz")
  assert("description_id" not in transaction.transaction)

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

  transaction_data = {
    "transaction_journal_id": 1337,
    "destination_id": 69,
    "destination_name": "Coop Obs",
    "category_id": 420,
    "category_name": "Foodstuff",
  }

  transaction = Transaction(transaction_data)
  transaction.flay([flay_config])
  assert(transaction.transaction['category_name'] == "Dagligvare")

def test_destination_by_tags():

  flay_config = {
    "function": "destination_by_tags",
    "arguments": {
      "tag_names": ['PayPal']
      }
    }

  transaction_data = {
    "transaction_journal_id": 1337,
    "destination_id": 69,
    "destination_name": "HTNS456HTNS",
    "tags": ["PayPal"]
  }

  transaction = Transaction(transaction_data)
  transaction.flay([flay_config])
  assert(transaction.transaction['destination_name'] == "PayPal")
  assert("destination_id" not in transaction.transaction)

