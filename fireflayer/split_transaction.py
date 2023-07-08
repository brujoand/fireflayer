from fireflayer.transaction import Transaction

class SplitTransaction:
  def __init__(self, group_title, transactions):
    self.apply_rules = True
    self.fire_webhooks = False
    self.group_title = group_title
    self.transactions = [Transaction(transaction) for transaction in transactions]

  def flay(self, config):
    changed = False
    for transaction in self.transactions:
      if (transaction.flay(config)):
        changed = True

    return changed
