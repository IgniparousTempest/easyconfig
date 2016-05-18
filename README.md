# easyconfig
EasyConfig is a simple and extensible configuration tool for Python.

## Example 1
With the following config files:
```
Base : {
    "databaseUrl" : "localhost:8001",
    "datatbaseName" : "CoolDb",
    "username" : "user",
    "password" : "pass"
}

Base.Test -> Test

Base.Release -> Release :+ {
    "databaseUrl" : "address.eu-west-1.rds.amazonaws.com",
    "username" : "release-user",
    "password" : "p4ssword"
}
```

```python
from easyconfig import EasyConfig

config = EasyConfig(stage='Release')

# Which is better?
config['awsRDS.databaseUrl']
config['awsRDS']['databaseUrl']
config.get('awsRDS.databaseUrl')
config.get('awsRDS', 'databaseUrl')
```

```python
import MySQLdb
from easyconfig import EasyConfig

config = EasyConfig(stage='Release')
database_url = config['awsRDS.databaseUrl']  # address.eu-west-1.rds.amazonaws.com
db_name = config['awsRDS.databaseUrl']       # CoolDb
username = config['awsRDS.databaseUrl']      # release-user
password = config['awsRDS.databaseUrl']      # p4ssword

db = MySQLdb.connect(database_url, username, password, database_url)
```

## Example 2
With the following config files:

```
Base : {
  "government" : {
    "leader" : "No one"
  },
  "awsRDS" : {
    "databaseUrl" : "address.us-east-1.rds.amazonaws.com"
  }
}
```
```
Base.SouthAfrica -> SouthAfrica : {
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
Base.Australia -> Australia : {
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