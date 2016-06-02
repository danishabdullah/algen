from __future__ import print_function, unicode_literals

from os import getcwd, path, makedirs
import logging

import yaml
import click

from algen.compilers import ModelCompiler
from algen.logger import LOG

__author__ = "danishabdullah"


class DirectoryCreationException(Exception):
    pass


class FileNotFound(Exception):
    pass


class InvalidModelDefinition(Exception):
    pass


def check_or_create_models_dir(destination=None):
    dir = destination or "{}/models".format(getcwd())
    if not path.exists(dir):
        click.echo("Didn't find {}. Creating now.".format(dir))
        try:
            makedirs(dir)
        except Exception as e:
            raise DirectoryCreationException
    return dir


def create_col_def_dict_from_cli_input(col_input):
    col_name, col_type = col_input.split(':')
    return {'name': col_name, 'type': col_type}


def parse_cli_columns(name, columns):
    column_defs = [create_col_def_dict_from_cli_input(n) for n in columns]
    res = {name: {'columns': column_defs}}
    ensure_names(res)
    ensure_types(res)
    return res


def ensure_names(model_defs):
    for key, model_def in model_defs.items():
        LOG.info("Validating column names for '{}'".format(key))
        for column in model_def['columns']:
            if not column.get('name', None):
                msg = "Missing 'name' for a column in '{}'".format(key)
                LOG.error(msg)
                click.echo(msg)
                raise InvalidModelDefinition(msg)


def ensure_types(model_defs):
    for key, model_def in model_defs.items():
        LOG.info("Validating column types for '{}'".format(key))
        for column in model_def['columns']:
            if not column.get('type', None):
                msg = "Missing 'type' for '{}' in '{}'".format(column.get('name', ''), key)
                LOG.error(msg)
                click.echo(msg)
                raise InvalidModelDefinition(msg)


def ensure_foreign_keys(model_defs):
    for key, model_def in model_defs.items():
        LOG.info("Validating foreign keys for '{}'".format(key))
        for column in model_def.get('foreign_keys', []):
            if not column.get('name', None):
                msg = "Missing 'name' from foreign key column in '{}'".format(key)
                LOG.error(msg)
                click.echo(msg)
                raise InvalidModelDefinition(msg)
            if not column.get('type', None):
                msg = "Missing 'type' from foreign key column '{}' in '{}'".format(column['name'], key)
                LOG.error(msg)
                click.echo(msg)
                raise InvalidModelDefinition(msg)
            reference = column.get('reference', None)
            if not reference:
                msg = "Missing 'reference' from foreign key '{}' in '{}'".format(column['name'], key)
                LOG.error(msg)
                click.echo(msg)
                raise InvalidModelDefinition(msg)
            assert isinstance(reference, dict)
            if not reference.get('table', None):
                msg = "Missing 'reference.name' from foreign key '{}' in '{}'".format(column['name'], key)
                LOG.error(msg)
                click.echo(msg)
                raise InvalidModelDefinition(msg)
            if not reference.get('column', None):
                msg = "Missing 'reference.column' from foreign key '{}' in '{}'".format(column['name'], key)
                LOG.error(msg)
                click.echo(msg)
                raise InvalidModelDefinition(msg)


def ensure_relationships(model_defs):
    for key, model_def in model_defs.items():
        LOG.info("Validating relationships for '{}'".format(key))
        for column in model_def.get('relationships', []):
            if not column.get('name', None):
                msg = "Missing 'name' from relationship column in '{}'".format(key)
                LOG.error(msg)
                click.echo(msg)
                raise InvalidModelDefinition(msg)
            if not column.get('class', None):
                msg = "Missing 'class' from relationship column '{}' in '{}'".format(column.get('name'), key)
                LOG.error(msg)
                click.echo(msg)
                raise InvalidModelDefinition(msg)


def parse_yaml(pth):
    if not path.exists(pth):
        raise FileNotFound

    LOG.info("Parsing YAML from '{}'".format(pth))
    with open(pth, 'r') as fyle:
        model_defs = yaml.load(fyle)
    assert isinstance(model_defs, dict)
    ensure_names(model_defs)
    ensure_types(model_defs)
    ensure_foreign_keys(model_defs)
    ensure_relationships(model_defs)
    return model_defs


def get_model_defs(name=None, columns=None, yaml=None):
    if yaml:
        model_defs = parse_yaml(yaml)
    else:
        model_defs = parse_cli_columns(name, columns)
    return model_defs


@click.command()
@click.option('--name', '-n', help='Name of model', type=str)
@click.option('--columns', '-c',
              help=("Column definition. e.g. col_name:col_type"
                    " Can be used multiple times hence named "
                    "columns. e.g. -c foo:Int -c bar:Unicode(20)"),
              type=str, multiple=True)
@click.option('--destination', '-d', help=("Destination directory. Default will "
                                           "assume 'models' directory inside the"
                                           " current working directory"),
              type=click.Path(exists=True))
@click.option('--yaml', '-y', help=("Yaml file describing the Model. This "
                                    "supersedes the column definition provided "
                                    "through --columns option."),
              type=click.Path(exists=True))
@click.option('--verbose', '-v', help=("Show detailed logging info"), is_flag=True)
def cli(name, columns, destination, yaml, verbose):
    if verbose:
        LOG.setLevel(logging.DEBUG)
    click.echo('Creating Models with the following options:\n'
               '  --name:{}\n  --columns:{}\n  --destination:{}\n'
               '  --yaml:{}'.format(name, columns, destination, yaml))
    if destination:
        if destination.endswith('/'):
            destination = destination[:len(destination) - 1]
            click.echo('Trimmed destination to {}'.format(destination))
    try:
        # destination cannot be created or accessed
        destination = check_or_create_models_dir(destination=destination)
    except DirectoryCreationException as e:
        LOG.exception("Couldn't access/create directory", exc_info=True)
        click.echo("An error happened while trying to access/create the 'models' "
                   "directory. Please make sure that you have the "
                   "appropriate ownership and right provided by the os.")
        return
    if not (columns or yaml):
        click.echo("You must provide at least one of --columns or --yaml")
        return
    try:
        # invalid definitions
        if yaml:
            if columns:
                click.echo("Ignoring columns provided through cli since a yaml"
                           " file was also provided")
            try:
                # not found errors
                model_defs = get_model_defs(yaml=yaml)
            except FileNotFound:
                msg = "The yaml file does not exist. Exiting!"
                LOG.error(msg)
                click.echo(msg)
                return
        else:
            if not name:
                click.echo("Invalid Model definition")
                return
            model_defs = get_model_defs(columns=columns, name=name)
    except InvalidModelDefinition:
        click.echo('Invalid Model definition')
        return
    for name, column_defs in model_defs.items():
        model = ModelCompiler(name, column_defs).compiled_model
        filename = "{}/{}.py".format(destination, ModelCompiler.convert_case(name))
        try:
            # file is not writeable
            with open(filename, 'w') as fyle:
                msg = "Writing {} to {}".format(name, filename)
                LOG.info(msg)
                click.echo(msg)
                fyle.write(model)
        except IOError:
            LOG.exception("IOError", exc_info=True)
            click.echo("The following python model was generated:\n\n{}"
                       "Cannot write model  to {}. Make sure the "
                       "destination is writable.\n"
                       .format(name, filename))


if __name__ == '__main__':
    cli()
