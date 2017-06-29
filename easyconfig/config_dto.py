from typing import Union, Any, Dict, List


class ConfigRecord(object):
    def __init__(self, name: str, parent: Union[str, None], record: Dict[str, Any]):
        self.name = name
        self.parent: str = parent or name
        self.record = record


class ConfigNode(object):
    def __init__(self, record: ConfigRecord = None):
        self.parent: ConfigNode = None
        self.children: List[ConfigNode] = []
        self.record: ConfigRecord = record

    def __str__(self) -> str:
        return f"ConfigNode(parent: {self.parent}, children: {self.children}, record: {self.record})"
