from typing import Union, Any, Dict, List


class ConfigRecord(object):
    def __init__(self, name: str, parent: Union[str, None], data: Dict[str, Any]):
        self.name = name
        self.parent: str = parent or name
        self.data = data

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(name: '{self.name}', parent: '{self.parent}')"


class ConfigNode(object):
    def __init__(self, record: ConfigRecord = None):
        self.parent: ConfigNode = None
        self.children: List[ConfigNode] = []
        self.record: ConfigRecord = record

    @property
    def name(self):
        return self.record.name

    def __str__(self) -> str:
        name = 'No Name'
        parent_name = None
        # noinspection PyBroadException
        try:
            name = self.record.name or name
        except:
            pass
        # noinspection PyBroadException
        try:
            parent_name = self.parent.record.name
        except:
            pass
        children_str = '[' + ', '.join([str(i) for i in self.children]) + ']'
        return f"ConfigNode(name: '{name}', parent: {parent_name}, children: {children_str}, record: {self.record})"
