# FireFlayer
A python app to clean (or flay if you will)
  [firefly-iii](https://www.firefly-iii.org/) transactions as they are imported
  or in bulk.

## Usage
Can be started in either `webook` or `process` mode, where the former is
probably what you would want most of the time, while the latter is useful to
process all existing transactions.

FireFlayer expects a configuration file in Yaml format `fireflayer_config.yaml`
which should contain `flays` which are actions to perform on any given
transaction processed.

As an example:

```yaml
---
flay:
  - name: Extract Payment services as tags
    function: extract_tag
    arguments:
      source_field: description
      pattern: '^(.+)\ ?\*'
      group: 1
  - name: Remove Payment services from description and destination_name
    function: replace
    arguments:
      source_fields:
        - description
        - destination_name
      pattern: '^(.+)\ ?\*'
      value: ''
  - name: Override destination_name for cryptic payment providers
    function: destination_by_tags
    arguments:
      tag_names: ['Microsoft', 'AMZN Mktp US', 'GOOGLE',]
  - name: Set groceries as category
    function: category_by_filter
    arguments:
      source_fields:
        - destination_name
      category_name: Groceries
      includes:
        - Obs
        - Extra
        - Prix
      excludes:
        - Obs Bygg
      case_sensitive: false
```

With the configuration above and a transaction with the description "PayPal *Ice
Cream Shop" "PayPal" would be extracted as a tag in the first stage. In the
second stage we remove "PayPal *" from the `description` and `destination_name`
fields.

Sometimes though these payment providers create weird contents for `destination_name` like
"AMZN Mktp US * HTNS456HTNS", which ends up as "HTNS456HTNS" after the first 2
stages. So the third stage sets the `destination_name` to the extracted payment provider tag instead.

The last stage is used to add a category based on "destination_name". In this
case if there are transactions going to both `Obs` and `Obs Bygg` where one is
a supermarket and the other a hardware store, only `Obs` will get the category
`groceries`.

## Configuration
FireFlayer expects the following environment variables

```
FIREFLAYER_AUTH_TOKEN # https://docs.firefly-iii.org/firefly-iii/api/
FIREFLAYER_API_URL # The url to the api https://firefly.yourdomain.com
FIREFLAYER_CONFIG_PATH # The path to the yaml config file
```

Command line invocation:
```
usage: fireflayer.app [-h] [--dry-run] [--log-level {INFO,DEBUG}] {webhook,process}

positional arguments:
  {webhook,process}     Which action to execute

options:
  -h, --help            show this help message and exit
  --dry-run             Dry run (No side effects)
  --log-level {INFO,DEBUG}
                        Change log level (default: INFO)
```
