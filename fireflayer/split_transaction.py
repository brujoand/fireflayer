class SplitTransaction:
  def __init__(self, group_title, transactions):
    self.apply_rules = True
    self.fire_webhooks = False
    self.group_title = group_title or ""
    self.transactions = transactions
