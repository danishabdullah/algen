from __future__ import print_function, unicode_literals

__author__ = "danishabdullah"

__all__ = ("POSTGRES_TYPES", "MUTABLE_DICT_TYPES", "NO_PARAMS_TYPES")

POSTGRES_TYPES = ('HSTORE', 'ARRAY', 'JSON', 'JSONB')
MUTABLE_DICT_TYPES = ('HSTORE', 'JSON', 'JSONB')
NO_PARAMS_TYPES = ('Integer', 'BigInteger', 'Float', 'Decimal', 'Numeric', 'JSONB', 'JSON', 'HSTORE')
