from __future__ import print_function, unicode_literals
from string import Template

__author__ = "danishabdullah"

__all__ = ('column_definition', 'mutable_dict_type', 'column_arg', 'func_arg', 'col_assignment', 'named_import',
           'not_none_col_assignment', 'key_col_comparison', 'key_evaluator', 'key_accessor')

column_definition = Template("$column_name = Column($column_type$type_params, $column_args)")
mutable_dict_type = Template("MutableDict.as_mutable($type)")
column_arg = Template("$arg_name=$arg_val")
func_arg = Template("$arg_name=None")
col_assignment = Template("self.$col_name = $col_name")
not_none_col_assignment = Template("""
        if {col_name} is not None:
            self.$col_name = $col_name
""")
key_col_comparison = Template("self.$key_name == other.$key_name")
named_import = "from $module import $labels"
key_evaluator = Template("{$key_name}")
key_accessor = Template("$key=self.$key")
