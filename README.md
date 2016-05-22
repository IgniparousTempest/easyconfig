# easyconfig
EasyConfig is a simple and extensible configuration tool for Python. EasyConfig enables inheritance based configuration definition, which can be used to specify region or release stage specific configuration (or any other conceivable configuration sub-stage).

## Example 1
The following config file defines the parameters for connecting to a database for a production release and a development release:
```
Base : {
    "databaseUrl" : "localhost:8001",
    "datatbaseName" : "CoolDb",
    "username" : "user",
    "password" : "pass"
}

Base.Testing -> Testing :+ {
}

Base.Release -> Release :+ {
    "databaseUrl" : "address.eu-west-1.rds.amazonaws.com",
    "username" : "release-user",
    "password" : "p4ssword"
}
```
The config can be accessed in the following way:
```python
import MySQLdb
from easyconfig import EasyConfig

config = EasyConfig(stage='Release')
database_url = config.awsRDS.databaseUrl  # address.eu-west-1.rds.amazonaws.com
db_name = config.awsRDS.databaseUrl       # CoolDb
username = config.awsRDS.databaseUrl      # release-user
password = config.awsRDS.databaseUrl      # p4ssword

db = MySQLdb.connect(database_url, username, password, database_url)

config = EasyConfig(stage='Testing')
database_url = config.awsRDS.databaseUrl  # localhost:8001
db_name = config.awsRDS.databaseUrl       # CoolDb
username = config.awsRDS.databaseUrl      # user
password = config.awsRDS.databaseUrl      # password

db = MySQLdb.connect(database_url, username, password, database_url)
```

A better example of acheiving the same result is as follows:
```python
import MySQLdb
from easyconfig import EasyConfig

def get_database_connection(config):
    database_url = config.awsRDS.databaseUrl
    db_name = config.awsRDS.databaseUrl
    username = config.awsRDS.databaseUrl
    password = config.awsRDS.databaseUrl

    return MySQLdb.connect(database_url, username, password, database_url)

if __name__ == "__main__":
    config = EasyConfig(stage='Release') # Simply changing the name of the stage here is all that is needed to change the configuration of your programme
    db = get_database_connection(config)
```
These are simple examples, in a real production environment you could substitute the username and password parameters for a URL in a secret store database.

## Example 2
With the following config files:

```
Base : {
  "government" : {
    "base_only_value" : None
  },
  "awsRDS" : {
    "databaseUrl" : "localhost:8001"
  }
}
```
```
Base.Testing -> Testing :+ {
}
```
```
Base.Release -> Release :+ {
  "awsRDS" : {
    "databaseUrl" : "address.us-east-1.rds.amazonaws.com"
  }
}
```
```
Base.Release.SouthAfrica -> SouthAfrica : {
  "government" : {
    "leader" : "Jacob Zuma",
    "leaderTitle" : "president",
    "population" : 52980000
  },
  "awsRDS" :+ {
    "databaseName" : "SouthAfrica"
  }
}
```
```
Base.Release.Australia -> Australia : {
  "government" : {
    "leader" : "Malcolm Turnbull",
    "leaderTitle" : "prime minister",
    "population" : 23130000
  },
  "awsRDS" :+ {
    "databaseName" : "Australia"
  }
}
```

## Syntax

Each config definition starts with a name: an inheritance path followed by an optional alias:
```
Earth.Africa.Egypt.Cairo -> Cairo
```
Where `Earth.Africa.Egypt.Cairo` is the inheritance path, which means `Cairo` inherits from `Egypt`, `Egypt` inherits from `Africa` and, `Africa` inherits from `Earth`. The alias is `Cairo`.

After the name, the config definition requires a config block:
```
Earth.Africa.Egypt.Cairo -> Cairo :+ {
    "root" : "text",
    "nested" : {
        "level1" : "text"
    }
}
```
Code blocks can have nested code blocks.
A `:` signifies a new block that overrides it's parent, a `:+` is a code block that extends its parent.

## Datatypes
Currently the only permissible datatypes for the parameters of the config are the following Python primitives:

| -------- | ------- |
| Datatype | Example |
| -------- | ------- |
| int      | 1       |
| float    | -0.2    |
| list     | ["text", 1, True] |
| None     | None    |
| boolean  | True    |
| string   | "Some text" |
| dict     | {a: 1}  |
| -------- | ------- |

A nested dict can be retrieved by using the `.as_dict()` method on the config file.

If there you have any suggestions, please feel free to contact me.