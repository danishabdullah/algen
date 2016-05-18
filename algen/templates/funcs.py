from __future__ import print_function, unicode_literals
from string import Template

__author__ = "danishabdullah"

__all__ = ("to_dict", "get_proxy_cls", "to_proxy", "from_proxy", "init", "add", "delete", "update", "comparator",
           "hash_function", "representor")

to_dict = Template("""
    def to_dict(self):
        return {x: y for x, y in self.__dict__.items() if not x.startswith("_sa")}""")

get_proxy_cls = Template("""
    def get_proxy_cls(self):
        # ${class_name}Proxy is useful when you want to persist data
        # independent of the sqlalchemy session. It's just a namedtuple
        # that has very low memory/cpu footprint compared the regular
        # orm class instances.
        keys = self.to_dict().keys()
        name = "${class_name}Proxy"
        return namedtuple(name, keys)""")

to_proxy = Template("""
    def to_proxy(self):
        # Proxy-ing is useful when you want to persist data
        # independent of the sqlalchemy session. It's just a namedtuple
        # that has very low memory/cpu footprint compared the regular
        # orm class instances.
        cls = self._get_proxy_cls()
        return cls(**self.to_dict())""")

from_proxy = Template("""
    @classmethod
    def from_proxy(cls, proxy):
        return cls(**proxy._asdict())""")

init = Template("""
    def __init__(self, $init_args):
        $col_assignments""")

add = Template("""
    def add(self, session):
        session.add(self)""")

delete = Template("""
    def delete(self, session):
        session.delete(self)""")

update = Template("""
    def update(self, $update_args):
        # This function only updates a value if it is not None.
        # Falsy values go through in the normal way.
        # To set things to None use the usual syntax:
        #    $class_name.column_name = None
        $not_none_col_assignments""")

comparator = Template("""
    def $func_name(self, other):
        return $negation_marker($key_col_comparisons)""")

representor = Template("""
    def __${func_name}__(self):
        return "<$class_name: $col_evaluators>".format($col_accessors)""")

hash_function = Template("""
    def __hash__(self):
        return hash($concated_primary_key_strs)""")
