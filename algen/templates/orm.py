from __future__ import print_function, unicode_literals
from string import Template

__author__ = "danishabdullah"

__all__ = ('cls',)

cls = Template("""from __future__ import unicode_literals, absolute_import, print_function

from collections import namedtuple

from sqlalchemy import Column, $types
$named_imports

from .alchemy_base import Base

__author__ = '$username'


class $class_name(Base):
    __tablename__ = '$table_name'

    $column_definitions

    $init_function
    $add_function
    $update_function
    $delete_function
    $to_dict_function
    $get_proxy_cls_function
    $to_proxy_function
    $from_proxy_function
    $hash_function
    $eq_function
    $neq_function
    $str_function
    $unicode_function
    $repr_function
""")
