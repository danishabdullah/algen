from __future__ import print_function, unicode_literals

__author__ = "danishabdullah"

__all__ = ("POSTGRES_TYPES", "MUTABLE_DICT_TYPES", "NO_PARAMS_TYPES")

POSTGRES_TYPES = ('ARRAY', 'BIGINT', 'BIT', 'BOOLEAN', 'BYTEA', 'CHAR', 'CIDR', 'DATE', 'DOUBLE_PRECISION', 'ENUM',
                  'FLOAT', 'HSTORE', 'INET', 'INTEGER', 'INTERVAL', 'JSON', 'JSONB', 'MACADDR', 'NUMERIC', 'OID',
                  'REAL', 'SMALLINT', 'TEXT', 'TIME', 'TIMESTAMP', 'UUID', 'VARCHAR', 'INT4RANGE', 'INT8RANGE',
                  'NUMRANGE', 'DATERANGE', 'TSRANGE', 'TSTZRANGE', 'TS')
MUTABLE_DICT_TYPES = ('HSTORE', 'JSON', 'JSONB')
NO_PARAMS_TYPES = ('Integer', 'BigInteger', 'Float', 'Decimal', 'Numeric', 'JSONB', 'JSON', 'HSTORE')
