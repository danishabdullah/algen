# Algen

Algen generates opionated ORM classes for sqlalchemy given a simple schema
either as a commandline string or as a yaml file. It is designed to have
minimal dependencies and is trivially extensible. A command line tool
is bundled along to help generate the models. For DB specific types,
only postgres is currently supported. The tool currently assumes that
sqlalchemy's declarative base object is to be imported like
    ```from .alchemy_base import Base```
The library prefers making the code verbose rather than concise for the
sake of having better auto-completion and help from your editor/IDE
e.g. first style is preferred to the second one:
```python
def update(self, a=None, b=None):
    if a is not None:
        self.a = a
    if b is not None:
        self.b = b
```
```python
def update(self, **kwargs):
    for k,v in kwargs.items():
        if hasattr(self, k) and v is not None:
            setattr(self, k, v)
```


### CLI
```bash
$ algen --help
Usage: algen [OPTIONS]

Options:
  -n, --name TEXT         Name of model
  -c, --columns TEXT      Column definition. e.g. col_name:col_type Can be
                          used multiple times hence named columns. e.g. -c
                          foo:Int -c bar:Unicode(20)
  -d, --destination PATH  Destination directory. Default will assume 'models'
                          directory inside the current working directory
  -y, --yaml PATH         Yaml file describing the Model. This supersedes the
                          column definition provided through --columns option.
  --help                  Show this message and exit.
```

Given a file as follows:
```yaml
Person:
  columns:
    - name: id
      type: BigInteger
      primary_key: True
      auto_increment: True
    - name: name
      type: Unicode(255)
    - name: is_vip
      type: Boolean
    - name: created_at
      type: DateTime(timezone=True)
      server_default: now() at time zone 'utc'
    - name: updated_at
      type: DateTime(timezone=True)
      server_default: now() at time zone 'utc'
  relationships:
    - name: addresses
      class: Address
      back_populates: 'person'

Address:
  columns:
    - name: id
      type: BigInteger
      primary_key: True
      auto_increment: True
    - name: line1
      type: Unicode()
    - name: line2
      type: Unicode()
    - name: line3
      type: Unicode()
    - name: postcode
      type: Unicode(10)
      index: True
    - name: created_at
      type: DateTime(timezone=True)
      server_default: now() at time zone 'utc'
    - name: updated_at
      type: DateTime(timezone=True)
      server_default: now() at time zone 'utc'
  foreign_keys:
    - name: person_id
      type: BigInteger
      reference:
        table: persons
        column: id
      nullable: False
  relationships:
    - name: person
      class: Person
      back_populates: 'addresses'

```

The cli tool will create two the following two files ```person.py```  and  ```address.py```.

```python
from __future__ import unicode_literals, absolute_import, print_function

from collections import namedtuple

from sqlalchemy import Column, Unicode, BigInteger, DateTime, ForeignKey
from sqlalchemy.orm import relationship


from .alchemy_base import Base

__author__ = 'danishabdullah'


class Address(Base):
    __tablename__ = 'addresses'

    id = Column(BigInteger, auto_increment=True, primary_key=True)
    line1 = Column(Unicode(), )
    line2 = Column(Unicode(), )
    line3 = Column(Unicode(), )
    postcode = Column(Unicode(10), index=True)
    created_at = Column(DateTime(timezone=True), server_default="now() at time zone 'utc'")
    updated_at = Column(DateTime(timezone=True), server_default="now() at time zone 'utc'")

    # --- Foreign Keys ---
    person_id = Column(BigInteger, ForeignKey('persons.id'), nullable=False)

    # --- Relationships ---
    person = relationship('Person', back_populates='addresses')

    def __init__(self, id=None, line1=None, line2=None, line3=None, postcode=None, created_at=None, updated_at=None, person_id=None):
        self.id = id
        self.line1 = line1
        self.line2 = line2
        self.line3 = line3
        self.postcode = postcode
        self.created_at = created_at
        self.updated_at = updated_at
        self.person_id = person_id

    def add(self, session):
        session.add(self)

    def update(self, line1=None, line2=None, line3=None, postcode=None, created_at=None, updated_at=None, person_id=None):
        # This function only updates a value if it is not None.
        # Falsy values go through in the normal way.
        # To set things to None use the usual syntax:
        #    Address.column_name = None

        if line1 is not None:
            self.line1 = line1

        if line2 is not None:
            self.line2 = line2

        if line3 is not None:
            self.line3 = line3

        if postcode is not None:
            self.postcode = postcode

        if created_at is not None:
            self.created_at = created_at

        if updated_at is not None:
            self.updated_at = updated_at

        if person_id is not None:
            self.person_id = person_id

    def delete(self, session):
        session.delete(self)

    def to_dict(self):
        return {x: y for x, y in self.__dict__.items() if not x.startswith("_sa")}

    def get_proxy_cls(self):
        # AddressProxy is useful when you want to persist data
        # independent of the sqlalchemy session. It's just a namedtuple
        # that has very low memory/cpu footprint compared the regular
        # orm class instances.
        keys = self.to_dict().keys()
        name = "AddressProxy"
        return namedtuple(name, keys)

    def to_proxy(self):
        # Proxy-ing is useful when you want to persist data
        # independent of the sqlalchemy session. It's just a namedtuple
        # that has very low memory/cpu footprint compared the regular
        # orm class instances.
        cls = self._get_proxy_cls()
        return cls(**self.to_dict())

    @classmethod
    def from_proxy(cls, proxy):
        return cls(**proxy._asdict())

    def __hash__(self):
        return hash(str(self.id))

    def __eq__(self, other):
        return (self.id == other.id)

    def __neq__(self, other):
        return not (self.id == other.id)

    def __str__(self):
        return "<Address: {id}>".format(id=self.id)

    def __unicode__(self):
        return "<Address: {id}>".format(id=self.id)

    def __repr__(self):
        return "<Address: {id}>".format(id=self.id)

```

```python
from __future__ import unicode_literals, absolute_import, print_function

from collections import namedtuple

from sqlalchemy import Column, Unicode, BigInteger, Boolean, DateTime
from sqlalchemy.orm import relationship


from .alchemy_base import Base

__author__ = 'danishabdullah'


class Person(Base):
    __tablename__ = 'persons'

    id = Column(BigInteger, auto_increment=True, primary_key=True)
    name = Column(Unicode(255), )
    is_vip = Column(Boolean, )
    created_at = Column(DateTime(timezone=True), server_default="now() at time zone 'utc'")
    updated_at = Column(DateTime(timezone=True), server_default="now() at time zone 'utc'")

    # --- Foreign Keys ---


    # --- Relationships ---
    addresses = relationship('Address', back_populates='person')

    def __init__(self, id=None, name=None, is_vip=None, created_at=None, updated_at=None):
        self.id = id
        self.name = name
        self.is_vip = is_vip
        self.created_at = created_at
        self.updated_at = updated_at

    def add(self, session):
        session.add(self)

    def update(self, name=None, is_vip=None, created_at=None, updated_at=None):
        # This function only updates a value if it is not None.
        # Falsy values go through in the normal way.
        # To set things to None use the usual syntax:
        #    Person.column_name = None

        if name is not None:
            self.name = name

        if is_vip is not None:
            self.is_vip = is_vip

        if created_at is not None:
            self.created_at = created_at

        if updated_at is not None:
            self.updated_at = updated_at

    def delete(self, session):
        session.delete(self)

    def to_dict(self):
        return {x: y for x, y in self.__dict__.items() if not x.startswith("_sa")}

    def get_proxy_cls(self):
        # PersonProxy is useful when you want to persist data
        # independent of the sqlalchemy session. It's just a namedtuple
        # that has very low memory/cpu footprint compared the regular
        # orm class instances.
        keys = self.to_dict().keys()
        name = "PersonProxy"
        return namedtuple(name, keys)

    def to_proxy(self):
        # Proxy-ing is useful when you want to persist data
        # independent of the sqlalchemy session. It's just a namedtuple
        # that has very low memory/cpu footprint compared the regular
        # orm class instances.
        cls = self._get_proxy_cls()
        return cls(**self.to_dict())

    @classmethod
    def from_proxy(cls, proxy):
        return cls(**proxy._asdict())

    def __hash__(self):
        return hash(str(self.id))

    def __eq__(self, other):
        return (self.id == other.id)

    def __neq__(self, other):
        return not (self.id == other.id)

    def __str__(self):
        return "<Person: {id}>".format(id=self.id)

    def __unicode__(self):
        return "<Person: {id}>".format(id=self.id)

    def __repr__(self):
        return "<Person: {id}>".format(id=self.id)

```
