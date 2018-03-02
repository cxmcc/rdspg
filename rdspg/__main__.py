import click
import boto3
import tabulate
import os
import jinja2


def rds_get_parameters(parameter_group_name):
    client = boto3.client('rds')
    paginator = client.get_paginator('describe_db_parameters')
    out = []
    for page in paginator.paginate(DBParameterGroupName=parameter_group_name):
        out += page['Parameters']
    return out


def rds_get_databases():
    client = boto3.client('rds')
    paginator = client.get_paginator('describe_db_instances')
    out = []
    for page in paginator.paginate():
        out += page['DBInstances']
    return out


def rds_get_parameter_groups():
    client = boto3.client('rds')
    paginator = client.get_paginator('describe_db_parameter_groups')
    out = []
    for page in paginator.paginate():
        out += page['DBParameterGroups']
    return out


def rds_list_tags(arn):
    client = boto3.client('rds')
    resp = client.list_tags_for_resource(ResourceName=arn)
    return resp.get('TagList', [])


def rds_get_pg_info(parameter_group_name):
    client = boto3.client('rds')
    resp = client.describe_db_parameter_groups(
        DBParameterGroupName=parameter_group_name
    )
    parameter_group_info = resp['DBParameterGroups'][0]
    return parameter_group_info


def generate_pg_to_db_mapping(pgs, dbs):
    mapping = {}
    for pg in pgs:
        pg_name = pg['DBParameterGroupName']
        mapping[pg_name] = []
    for db in dbs:
        db_name = db['DBInstanceIdentifier']
        pg_name = db['DBParameterGroups'][0]['DBParameterGroupName']
        mapping[pg_name].append(db_name)
    out = []
    for k, v in sorted(mapping.items()):
        if v == []:
            value = '<not-used>'
        else:
            value = ','.join(v)
        out.append((k, value))
    return out


def params_to_kv(params):
    out = {}
    for param in params:
        key = param['ParameterName']
        value = param.get('ParameterValue')
        out[key] = value
    return out


def params_list_to_dict(params, detail=False):
    headers = ['ParameterName', 'ParameterValue', 'ApplyMethod', 'ApplyType']
    if detail:
        headers += ['AllowedValues', 'DataType', 'Source']
    out = []
    for param in params:
        p = list(param.get(h) for h in headers)
        out.append(p)
    return out, headers


def calculate_diff(params_a, params_b):
    params_a = params_to_kv(params_a)
    params_b = params_to_kv(params_b)
    out = []
    for k, v in params_a.iteritems():
        if v != params_b.get(k):
            out.append((k, v, params_b.get(k, '<not-set>')))
        if k in params_b:
            del params_b[k]
    for k, v in params_b.iteritems():
        out.append((k, None, v))
    return out


def only_important_columns_pg(pgs):
    for pg in pgs:
        for k in ('DBParameterGroupArn',):
            if k in pg:
                del pg[k]
    return pgs


def only_user_params(params):
    out = []
    for param in params:
        if param['Source'] not in ('system', 'engine-default'):
            out.append(param)
    return out


def only_important_columns(params):
    columns = ('Description', 'DataType', 'IsModifiable',
               'AllowedValues', 'Source')
    for param in params:
        for k in columns:
            if k in param:
                del param[k]
    return params


def terraform(parameter_group_name, info, params, tags):
    def render(context):
        curr_dir = os.path.dirname(__file__)
        template_file_path = os.path.join(curr_dir, 'terraform.jinja')
        path, filename = os.path.split(template_file_path)
        return jinja2.Environment(
            loader=jinja2.FileSystemLoader(path or './')
        ).get_template(filename).render(context)

    context = {'parameter_group_name': parameter_group_name,
               'params': params, 'info': info, 'tags': tags}
    return render(context)


@click.group()
def cli():
    pass


@cli.command(name='mapping')
@click.option('--no-header', is_flag=True, default=False)
def cmd_mapping(no_header):
    pgs = rds_get_parameter_groups()
    dbs = rds_get_databases()
    mapping = generate_pg_to_db_mapping(pgs, dbs)
    if no_header:
        kwargs = {'tablefmt': 'plain'}
    else:
        headers = ('ParameterGroup', 'DBInstances')
        kwargs = {'tablefmt': 'simple', 'headers': headers}
    output = tabulate.tabulate(mapping, numalign='right', **kwargs)
    click.echo(output)


@cli.command(name='list')
@click.option('--detail', is_flag=True, default=False)
@click.option('--no-header', is_flag=True, default=False)
def cmd_list(detail, no_header):
    pgs = rds_get_parameter_groups()
    if not detail:
        pgs = only_important_columns_pg(pgs)
    if no_header:
        kwargs = {'tablefmt': 'plain'}
    else:
        kwargs = {'tablefmt': 'simple', 'headers': 'keys'}
    output = tabulate.tabulate(pgs, numalign='right', **kwargs)
    click.echo(output)


@cli.command(name='get')
@click.argument('parameter-group')
@click.option('--all-params', is_flag=True, default=False)
@click.option('--detail', is_flag=True, default=False)
@click.option('--no-header', is_flag=True, default=False)
def cmd_get(parameter_group, all_params, detail, no_header):
    params = rds_get_parameters(parameter_group)
    if not all_params:
        params = only_user_params(params)
    if not detail:
        params = only_important_columns(params)
    params, headers = params_list_to_dict(params, detail=detail)
    if no_header:
        kwargs = {'tablefmt': 'plain'}
    else:
        kwargs = {'tablefmt': 'simple', 'headers': headers}
    output = tabulate.tabulate(params, numalign='right', **kwargs)
    click.echo(output)


@cli.command(name='diff')
@click.argument('parameter-group-a')
@click.argument('parameter-group-b')
@click.option('--all-params', is_flag=True, default=False)
@click.option('--no-header', is_flag=True, default=False)
def cmd_diff(parameter_group_a, parameter_group_b, all_params, no_header):
    params_a = rds_get_parameters(parameter_group_a)
    params_b = rds_get_parameters(parameter_group_b)
    if not all_params:
        params_a = only_user_params(params_a)
        params_b = only_user_params(params_b)
    diff = calculate_diff(params_a, params_b)
    headers = ['ParameterName', parameter_group_a, parameter_group_b]
    if no_header:
        kwargs = {'tablefmt': 'plain'}
    else:
        kwargs = {'tablefmt': 'simple', 'headers': headers}
    output = tabulate.tabulate(diff, numalign='right', **kwargs)
    click.echo(output)


@cli.command(name='terraform')
@click.argument('parameter-group')
def cmd_terraform(parameter_group):
    params = rds_get_parameters(parameter_group)
    info = rds_get_pg_info(parameter_group)
    tags = rds_list_tags(info['DBParameterGroupArn'])
    params = only_user_params(params)
    template = terraform(parameter_group, info, params, tags)
    click.echo(template)


def main():
    cli()


if __name__ == '__main__':
    main()
