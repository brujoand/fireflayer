import json

class SplitTransaction:
  def __init__(self, transaction_id, group_title, transactions):
    self.transaction_id = transaction_id
    self.apply_rules = True
    self.fire_webhooks = False
    self.group_title = group_title
    self.transactions = transactions

  def as_minimal_json(self):
    data = {
      "apply_rules": self.apply_rules,
      "fire_webhooks": self.fire_webhooks,
      "group_title": self.group_title,
      "transactions": self.transactions
    }

    return json.dumps(data)
