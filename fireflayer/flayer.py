import logging
import re

class Flayer:
  def __init__(self, flay_config):
    self.flay_config = flay_config

  def adjust_for_updated_field(self, transaction, changed_field):
    field_prefixes = ['destination', 'source', 'category']

    for field_prefix in field_prefixes:
      field_name = f"{field_prefix}_name"
      field_id = f"{field_prefix}_id"
      if (field_name == changed_field and field_id in transaction):
        del transaction[field_id]

  def remove_null_fields(self, transaction):
    targets = []
    for key, value in transaction.items():
      if (value is None):
        targets += [key]

    for target in targets:
      del transaction[target]


  def replace(self, transaction, source_fields, pattern, value):
    for source_field in source_fields:
      current_value = transaction[source_field]
      changed_value = re.sub(pattern, value, current_value)
      if (current_value != changed_value):
        transaction[source_field] = changed_value
        logging.debug(f"Replace({source_field}) '{current_value}' -> '{changed_value}'")
        self.adjust_for_updated_field(transaction, source_field)

  def extract_tag(self, transaction, source_field, pattern, group):
    match = re.search(pattern, transaction[source_field])
    if match:
      value = match.group(group).strip()
      current_tags = transaction['tags']
      if (value not in current_tags):
        transaction['tags'] += [value]
        logging.debug(f"extract_tag(tags) '{current_tags}' + '[{value}]'")
        self.adjust_for_updated_field(transaction, 'tags')

  def is_contained(self, value, list_values):
    for list_value in list_values:
      if (list_value in value):
        return True
    return False

  def tag_by_filter(self, transaction, source_fields, tag_name, includes, excludes = [], case_sensitive = False):
    for source_field in source_fields:
      value = transaction[source_field]
      current_tags = transaction['tags']

      if (not case_sensitive):
        value = value.upper()
        includes = [includes.upper() for x in list]
        excludes = [excludes.upper() for x in list]

      if(self.is_contained(value, includes) and not self.is_contained(value, excludes)):
        transaction['tags'] += [tag_name]
        logging.debug(f"tag_by_filter(tags) '{current_tags}' + '[{tag_name}]'")
        self.adjust_for_updated_field(transaction, 'tags')

  def category_by_filter(self, transaction, source_fields, category_name, includes, excludes = [], case_sensitive = False):
    for source_field in source_fields:
      value = transaction[source_field]
      current_category = transaction['category_name']

      if (current_category == category_name):
        logging.debug(f"category_by_filter(Category) already set to '{current_category}', skipping..")
        return

      if (not case_sensitive):
        value = value.upper()
        includes = (value.upper() for value in includes)
        excludes = (value.upper() for value in excludes)

      if(self.is_contained(value, includes) and not self.is_contained(value, excludes)):
        transaction['category_name'] = category_name
        logging.debug(f"category_by_filter(Category) '{current_category}' -> '{category_name}'")
        self.adjust_for_updated_field(transaction, 'category_name')

  def destination_by_tags(self, transaction, tag_names, destination_name = ""):
    for tag_name in tag_names:
      if (tag_name in transaction['tags']):
        if (destination_name == ""):
          destination_name = tag_name

        current_destination = transaction['destination_name']
        transaction['destination_name'] = destination_name
        logging.debug(f"destination_by_tag(Destination_name) '{current_destination}' -> '{destination_name}'")
        self.adjust_for_updated_field(transaction, 'destination_name')

  def flay(self, transaction):
    logging.debug(f"Starting to flay transaction {transaction['transaction_journal_id']}")
    for flay in self.flay_config:
      arguments = flay["arguments"]
      arguments['transaction'] = transaction
      match flay["function"]:
        case "extract_tag":
          self.extract_tag(**arguments)
        case "replace":
          self.replace(**arguments)
        case "tag_by_filter":
          self.tag_by_filter(**arguments)
        case "category_by_filter":
          self.category_by_filter(**arguments)
        case "destination_by_tags":
          self.destination_by_tags(**arguments)
        case _:
          raise RuntimeError(f"Invalid flay config, unknown function {flay['function']}")

    self.remove_null_fields(transaction)
    logging.debug(f"Done flaying transaction {transaction['transaction_journal_id']}")
