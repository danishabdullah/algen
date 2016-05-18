from __future__ import print_function, unicode_literals

import re
from getpass import getuser

from algen.consts import POSTGRES_TYPES, MUTABLE_DICT_TYPES, NO_PARAMS_TYPES
from algen.templates import ALCHEMY_TEMPLATES

__author__ = "danishabdullah"

TYPE_INFO_REGEX = re.compile("(^\w+)(\(.*\)$)?")

__all__ = ('ModelCompiler',)


class ModelCompiler(object):
    """
    Class for compiling and producing a Sql Alchemy model from user provided definition.

    Everything is implemented as a property for rapid development without any  thought
    for speed.
    """

    def __init__(self, name, column_def):
        assert isinstance(column_def, dict)
        self.model_def = {'name': column_def}
        self.username = getuser()
        self.tab = '    '
        self.class_name = name
        self.column_definitions = column_def['columns']

    @property
    def table_name(self):
        """Pluralises the class_name using utterly simple algo and returns as table_name"""
        if not self.class_name:
            raise ValueError
        else:
            class_name = self.class_name.lower()
        last_letter = class_name[-1]
        if last_letter in ("y",):
            return "{}ies".format(class_name[:-1])
        elif last_letter in ("s",):
            return "{}es".format(class_name)
        else:
            return "{}s".format(class_name)

    @staticmethod
    def get_column_type(string):
        return ModelCompiler.get_col_type_info(string)[0]

    @staticmethod
    def get_type_params(string):
        return ModelCompiler.get_col_type_info(string)[1]

    @staticmethod
    def get_col_type_info(string):
        for match in TYPE_INFO_REGEX.finditer(string):
            name, params = match.groups()
            return name if name else '', params if params else ''
        return '', ''

    @property
    def types(self):
        """All the unique types found in user supplied model"""
        res = []
        for column in self.column_definitions:
            tmp = column.get('type', None)
            res.append(ModelCompiler.get_column_type(tmp)) if tmp else False
        res = list(set(res))
        return res

    @property
    def postgres_types(self):
        """Returns known postgres only types referenced in user supplied model"""
        return [n for n in self.types if n in POSTGRES_TYPES]

    @property
    def standard_types(self):
        """Returns non-postgres types referenced in user supplied model"""
        return [n for n in self.types if n not in POSTGRES_TYPES]

    @property
    def mutable_dict_types(self):
        return [n for n in self.types if n in MUTABLE_DICT_TYPES]

    @property
    def primary_keys(self):
        """Returns the primary keys referenced in user supplied model"""
        res = []
        for column in self.column_definitions:
            if 'primary_key' in column.keys():
                tmp = column.get('primary_key', None)
                res.append(column['name']) if tmp else False
        return res

    @property
    def compiled_named_imports(self):
        """Returns compiled named imports required for the model"""
        res = []
        if self.postgres_types:
            res.append(
                ALCHEMY_TEMPLATES.named_import.safe_substitute(
                    module='sqlalchemy.dialects.postgresql',
                    labels=", ".join(self.postgres_types)))
        if self.mutable_dict_types:
            res.append(
                ALCHEMY_TEMPLATES.named_import.safe_substitute(
                    module='sqlalchemy.ext.mutable', labels='MutableDict'
                ))
        return "\n".join(res)

    @property
    def compiled_columns(self):
        """Returns compiled column definitions"""

        def get_column_args(column):
            tmp = []
            for arg_name, arg_val in column.items():
                if arg_name not in ('name', 'type'):
                    tmp.append(ALCHEMY_TEMPLATES.column_arg.safe_substitute(arg_name=arg_name,
                                                                            arg_val=arg_val))
            return ", ".join(tmp)

        res = []
        for column in self.column_definitions:
            column_args = get_column_args(column)
            column_type, type_params = ModelCompiler.get_col_type_info(column.get('type'))
            column_name = column.get('name')
            if column_type in MUTABLE_DICT_TYPES:
                column_type = ALCHEMY_TEMPLATES.mutable_dict_type.safe_substitute(type=column_type)
            res.append(
                ALCHEMY_TEMPLATES.column_definition.safe_substitute(column_name=column_name,
                                                                    column_type=column_type,
                                                                    column_args=column_args,
                                                                    type_params=type_params))
        join_string = "\n" + self.tab
        return join_string.join(res)

    @property
    def columns(self):
        """Return names of all the columns referenced in user supplied model"""
        return [col['name'] for col in self.column_definitions]

    @property
    def compiled_init_func(self):
        """Returns compiled init function"""

        def get_column_assignment(column_name):
            return ALCHEMY_TEMPLATES.col_assignment.safe_substitute(col_name=column_name)

        def get_compiled_args(arg_name):
            return ALCHEMY_TEMPLATES.func_arg.safe_substitute(arg_name=arg_name)

        join_string = "\n" + self.tab + self.tab
        column_assignments = join_string.join([get_column_assignment(n) for n in self.columns])
        init_args = ", ".join(get_compiled_args(n) for n in self.columns)
        return ALCHEMY_TEMPLATES.init_function.safe_substitute(col_assignments=column_assignments,
                                                               init_args=init_args)

    @property
    def compiled_update_func(self):
        """Returns compiled update function"""

        def get_not_none_col_assignment(column_name):
            return ALCHEMY_TEMPLATES.not_none_col_assignment.safe_substitute(col_name=column_name)

        def get_compiled_args(arg_name):
            return ALCHEMY_TEMPLATES.func_arg.safe_substitute(arg_name=arg_name)

        join_string = "\n" + self.tab + self.tab
        columns = [n for n in self.columns if n not in self.primary_keys]
        not_none_col_assignments = join_string.join([get_not_none_col_assignment(n) for n in columns])
        update_args = ", ".join(get_compiled_args(n) for n in columns)
        return ALCHEMY_TEMPLATES.update_function.safe_substitute(not_none_col_assignments=not_none_col_assignments,
                                                                 update_args=update_args,
                                                                 class_name=self.class_name)

    @property
    def compiled_hash_func(self):
        """Returns compiled hash function based on hash of stringified primary_keys.
        This isn't the most efficient way"""

        def get_primary_key_str(pkey_name):
            return "str(self.{})".format(pkey_name)

        hash_str = "+ ".join([get_primary_key_str(n) for n in self.primary_keys])
        return ALCHEMY_TEMPLATES.hash_function.safe_substitute(concated_primary_key_strs=hash_str)

    def comparator_compiler(self, negation_type):
        def get_primary_key_comparator(pkey_name):
            return ALCHEMY_TEMPLATES.key_col_comparator.safe_substitute(col=pkey_name)

        assert negation_type in ('positive', 'negative')
        negation_marker = "not " if negation_type == 'negative' else ""
        func_name = "__neq__" if negation_type == 'negative' else "__eq__"
        key_comparators = [get_primary_key_comparator(n) for n in self.primary_keys]
        key_comparators = " and ".join(key_comparators)
        return ALCHEMY_TEMPLATES.comparator_function.safe_substitute(func_name=func_name,
                                                                     negation_marker=negation_marker,
                                                                     key_col_comparisons=key_comparators)

    @property
    def compiled_eq_func(self):
        """Returns compiled equality function"""
        return self.comparator_compiler('positive')

    @property
    def compiled_neq_func(self):
        return self.comparator_compiler('negative')

    def representation_function_compiler(self, func_name):
        """Generic function can be used to compile __repr__ or __unicode__ or __str__"""

        def get_col_accessor(col):
            return ALCHEMY_TEMPLATES.col_accessor.safe_substitute(col=col)

        def get_col_evaluator(col):
            return ALCHEMY_TEMPLATES.col_evaluator.safe_substitute(col=col)

        col_evaluators = ", ".join([get_col_evaluator(n) for n in self.primary_keys])
        col_accessors = ", ".join([get_col_accessor(n) for n in self.primary_keys])

        return ALCHEMY_TEMPLATES.representor_function.safe_substitute(func_name=func_name,
                                                                      col_accessors=col_accessors,
                                                                      col_evaluators=col_evaluators,
                                                                      class_name=self.class_name)

    @property
    def compiled_str_func(self):
        """Returns compiled __str__ function"""
        return self.representation_function_compiler('str')

    @property
    def compiled_unicode_func(self):
        """Return compiled __unicode__ function"""
        return self.representation_function_compiler('unicode')

    @property
    def compiled_repr_func(self):
        """Returns compiled __repr__ function"""
        return self.representation_function_compiler('repr')

    @property
    def compiled_proxy_cls_func(self):
        """Returns compile get_proxy_cls function"""
        return ALCHEMY_TEMPLATES.get_proxy_cls_function.safe_substitute(class_name=self.class_name)

    @property
    def compiled_model(self):
        """Returns compile ORM class for the user supplied model"""
        return ALCHEMY_TEMPLATES.model.safe_substitute(class_name=self.class_name,
                                                       table_name=self.table_name,
                                                       column_definitions=self.compiled_columns,
                                                       init_function=self.compiled_init_func,
                                                       update_function=self.compiled_update_func,
                                                       hash_function=self.compiled_hash_func,
                                                       eq_function=self.compiled_eq_func,
                                                       neq_function=self.compiled_neq_func,
                                                       str_function=self.compiled_str_func,
                                                       unicode_function=self.compiled_unicode_func,
                                                       repr_function=self.compiled_repr_func,
                                                       types=", ".join(self.standard_types),
                                                       username=self.username,
                                                       named_imports=self.compiled_named_imports,
                                                       get_proxy_cls_function=self.compiled_proxy_cls_func,
                                                       add_function=ALCHEMY_TEMPLATES.add_function.template,
                                                       delete_function=ALCHEMY_TEMPLATES.delete_function.template,
                                                       to_dict_function=ALCHEMY_TEMPLATES.to_dict_function.template,
                                                       to_proxy_function=ALCHEMY_TEMPLATES.to_proxy_function.template,
                                                       from_proxy_function=ALCHEMY_TEMPLATES.from_proxy_function.template)
