from __future__ import print_function, unicode_literals

from .statements import *
from .orm import *
from .funcs import *

__author__ = "danishabdullah"

__all__ = ("AlchemyTemplate",)


class AlchemyTemplate(object):
    """
    Provides "string.Template" representations of different parts of a sqlalchemy orm class.
    """

    def __init__(self):
        self.model = cls
        self.column_definition = column_definition
        self.mutable_dict_type = mutable_dict_type
        self.column_arg = column_arg
        self.func_arg = func_arg
        self.col_assignment = col_assignment
        self.not_none_col_assignment = not_none_col_assignment
        self.named_import = named_import
        self.init_function = init
        self.add_function = add
        self.delete_function = delete
        self.update_function = update
        self.comparator_function = comparator
        self.representor_function = representor
        self.hash_function = hash_function
        self.col_evaluator = col_evaluator
        self.col_accessor = col_accessor
        self.to_dict_function = to_dict
        self.get_proxy_cls_function = get_proxy_cls
        self.to_proxy_function = to_proxy
        self.from_proxy_function = from_proxy
        self.key_col_comparator = key_col_comparator
