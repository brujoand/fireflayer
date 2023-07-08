import logging
import re

class Transaction:
  def __init__(self, transaction):
    self.transaction = transaction

  def replace(self, source_fields, pattern, value):
    changed_fields = []
    for source_field in source_fields:
      current_value = self.transaction[source_field]
      changed_value = re.sub(pattern, value, current_value)
      if (current_value != changed_value):
        self.transaction[source_field] = changed_value
        logging.debug(f"Replace({source_field}) '{current_value}' -> '{changed_value}'")
        changed_fields += [source_field]
    return changed_fields

  def extract_tag(self, source_field, pattern, group):
    match = re.search(pattern, self.transaction[source_field])
    if match:
      value = match.group(group).strip()
      current_tags = self.transaction['tags']
      if (value not in current_tags):
        self.transaction['tags'] += [value]
        logging.debug(f"extract_tag(tags) '{current_tags}' + '[{value}]'")
        return ['tags']
    return []

  def is_contained(self, value, list_values):
    for list_value in list_values:
      if (list_value in value):
        return True
    return False

  def tag_by_filter(self, source_fields, tag_name, includes, excludes = [], case_sensitive = False):
    for source_field in source_fields:
      value = self.transaction[source_field]
      current_tags = self.transaction['tags']

      if (not case_sensitive):
        value = value.upper()
        includes = [includes.upper() for x in list]
        excludes = [excludes.upper() for x in list]

      if(self.is_contained(value, includes) and not self.is_contained(value, excludes)):
        self.transaction['tags'] += [tag_name]
        logging.debug(f"tag_by_filter(tags) '{current_tags}' + '[{tag_name}]'")
        return ["tags"]
    return []

  def category_by_filter(self, source_fields, category_name, includes, excludes = [], case_sensitive = False):
    for source_field in source_fields:
      value = self.transaction[source_field]
      current_category = self.transaction['category_name']

      if (current_category == category_name):
        logging.debug(f"category_by_filter(Category) already set to '{current_category}', skipping..")
        return []

      if (not case_sensitive):
        value = value.upper()
        includes = (value.upper() for value in includes)
        excludes = (value.upper() for value in excludes)

      if(self.is_contained(value, includes) and not self.is_contained(value, excludes)):
        self.transaction['category_name'] = category_name
        logging.debug(f"category_by_filter(Category) '{current_category}' -> '{category_name}'")
        return ["category_name"]
    return []

  def destination_by_tags(self, tag_names, destination_name = ""):
    for tag_name in tag_names:
      if (tag_name in self.transaction['tags']):
        if (destination_name == ""):
          destination_name = tag_name

        current_destination = self.transaction['destination_name']
        self.transaction['destination_name'] = destination_name
        logging.debug(f"destination_by_tag(Destination_name) '{current_destination}' -> '{destination_name}'")
        return ["destination_name"]
    return []

  def remove_changed_field_ids(self, changed_fields):
    field_prefixes = ['destination', 'source', 'category']

    for field_prefix in field_prefixes:
      if (f"{field_prefix}_name" in changed_fields):
        del self.transaction[f"{field_prefix}_id"]

  def remove_null_fields(self):
    targets = []
    for key, value in self.transaction.items():
      if (value is None):
        targets += [key]

    for target in targets:
      del self.transaction[target]

  def flay(self, flay_config):
    logging.debug(f"Starting to flay transaction {self.transaction['transaction_journal_id']}")
    changed_fields = []
    for flay in flay_config:
      arguments = flay["arguments"]
      match flay["function"]:
        case "extract_tag":
          changed_fields += self.extract_tag(**arguments)
        case "replace":
          changed_fields += self.replace(**arguments)
        case "tag_by_filter":
          changed_fields += self.tag_by_filter(**arguments)
        case "category_by_filter":
          changed_fields += self.category_by_filter(**arguments)
        case "destination_by_tags":
          changed_fields += self.destination_by_tags(**arguments)
        case _:
          raise RuntimeError(f"Invalid flay config, unknown function {flay['function']}")

    if (len(changed_fields) > 0):
      self.remove_changed_field_ids(changed_fields)
      self.remove_null_fields()
      logging.debug(f"Done flaying transaction {self.transaction['transaction_journal_id']}")
      return True
    else:
      return False

