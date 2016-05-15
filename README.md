# easyconfig
A simple and extensible configuration parser for Python

# Example 1
With the following config files:

```
AwesomeApp#Base : {
  "awsRDS" : {
    "databaseUrl" : "localhost:8001"
  }
}
```

```
AwesomeApp#Test : @AwesomeApp#Base
```

```
AwesomeApp#Release : @AwesomeApp#Base.Release

AwesomeApp#Base.Release : {
  "awsRDS" : {
    "databaseUrl" : "address.eu-west-1.rds.amazonaws.com"
  }
}
```

# Example 2
With the following config files:

```
UltimateApp#Base : {
  "government" : {
    "leader" : "No one"
  },
  "awsRDS" : {
    "databaseUrl" : "address.us-east-1.rds.amazonaws.com"
  }
}
```

```
UltimateApp#SouthAfrica : @UltimateApp#Base.SouthAfrica

UltimateApp#Base.SouthAfrica : {
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
UltimateApp#Australia : @UltimateApp#Base.Australia

UltimateApp#Base.Australia : {
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

```python
```