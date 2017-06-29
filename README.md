# EasyConfig
EasyConfig is a simple and extensible configuration tool for Python. EasyConfig enables inheritance based configuration definition, which can be used to specify region or release stage specific configuration (or any other conceivable configuration sub-stage). If you can read JSON, you can read EasyConfig!

##### Table of Contents
[Installation](#installation)
[Example 1](#example_1_-_inheritance)
[Example 2](#example_2)
[Syntax](#syntax)
[Data Types](#datatypes)

## Installation
`pip install easyconfig`

## Example 1 - Inheritance
The following config file defines the parameters for connecting to a database for a production release and a development release:
```json
Base : {
    'database_url': 'localhost:8001',
    'database_name': 'MyDB',
    'username': 'user',
    'password': 'pass'
}

Testing extends Base : {
}

Release extends Base : {
    'database_url': 'address.eu-west-1.rds.amazonaws.com',
    'username': 'release-user',
    'password': 'p4ssword'
}
```
The config can be accessed in the following way:
```python
import MySQLdb
from easyconfig import EasyConfig

config = EasyConfig(stage='Release')
database_url = config.database_url  # address.eu-west-1.rds.amazonaws.com
db_name = config.database_name      # MyDB
username = config.username          # release-user
password = config.password          # p4ssword

db = MySQLdb.connect(database_url, username, password, database_url)

config = EasyConfig(stage='Testing')
database_url = config.database_url  # localhost:8001
db_name = config.database_name      # MyDB
username = config.username          # user
password = config.password          # password

db = MySQLdb.connect(database_url, username, password, database_url)
```

A better example of achieving the same result is as follows, is using EasyConfig as an input to a factory:
```python
import MySQLdb
from easyconfig import EasyConfig

def get_database_connection(config):
    database_url = config.database_url
    db_name = config.database_name
    username = config.username
    password = config.password

    return MySQLdb.connect(database_url, username, password, database_url)

if __name__ == "__main__":
    config = EasyConfig(stage='Release') # Simply changing the name of the stage here is all that is needed to change the configuration of your programme
    db = get_database_connection(config)
```

## Example 2
The following shows the definition of some countries on Earth:

```json
Earth : {
  'planet' : 'Earth',
  'population' : '7.51 billion'
}
```
```json
Africa extends Earth : {
  'continent' : 'Africa',
  'government' : {
    'overridden node' : 'Only Africa will have this key as all child configs do not extend this node'
  },
  'population' : '1.22 billion'
}
```
```json
SouthAfrica extends Africa : {
  'country': 'South Africa',
  "government" : {
    "leader" : "Jacob Zuma",
    "leader title" : "president"
  },
  'population' : '52.9 million'
}
```
```json
Morocco extends Africa : {
  'country': 'Morocco',
  "government" : {
    "leader" : "Mohammed VI",
    "leader title" : "king"
  },
  'population' : '53.8 million'
}
```
This is how to use it:
```python
from easyconfig import EasyConfig

config = EasyConfig(stage='SouthAfrica')
```

## Syntax

Each config definition starts with a name, followed by an optional parent:
```
Espresso extends Coffee
```
Where `Espresso` is the name of the config, and `Coffee` is the parent config.

After the name, the config definition requires a config block:
```
Espresso extends Coffee : {
    "root" : "text",
    "nested" : {
        "level1" : "text"
    }
}
```
Code blocks can have nested code blocks.
A `:` signifies a new block that overrides it's parent, a `:+` is a code block that extends its parent.

## Data Types
Currently the only permissible data types for the parameters of the config are the following Python primitives (Although anything that can be serialised can be retrieved):

| Data Type |   Example   |
| --------- | ----------- |
| int       | 1           |
| float     | -0.2        |
| list      | ["text", 1, True] |
| None      | None        |
| boolean   | True        |
| string    | "Some text" |
| dict      | {'a': 1}    |

If there you have any suggestions, please feel free to create an issue.
