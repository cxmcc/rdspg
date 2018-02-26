import click
import boto3
import tabulate
import os
import jinja2

def rds_get_parameters(parameter_group_name):
    client = boto3.client('rds')
    resp = client.describe_db_parameters(DBParameterGroupName=parameter_group_name)
    return resp['Parameters']


def rds_get_parameter_groups():
    client = boto3.client('rds')
    resp = client.describe_db_parameter_groups()
    return resp['DBParameterGroups']


def rds_get_pg_info(parameter_group_name):
    client = boto3.client('rds')
    resp = client.describe_db_parameter_groups(DBParameterGroupName=parameter_group_name)
    info = {}
    info['family'] = resp['DBParameterGroups'][0]['DBParameterGroupFamily']
    info['description'] = resp['DBParameterGroups'][0]['Description']
    return info


def only_important_columns_pg(pgs):
    for pg in pgs:
        for k in ('DBParameterGroupArn', ):
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
    for param in params:
        for k in ('Description', 'DataType', 'IsModifiable', 'AllowedValues', 'Source'):
            if k in param:
                del param[k]
    return params


def terraform(parameter_group_name, info, params):
    def render(context):
        curr_dir = os.path.dirname(__file__)
        template_file_path = os.path.join(curr_dir, 'terraform.jinja')
        path, filename = os.path.split(template_file_path)
        return jinja2.Environment(
            loader=jinja2.FileSystemLoader(path or './')
        ).get_template(filename).render(context)
    context = {'parameter_group_name': parameter_group_name, 'params': params, 'info': info}
    return render(context)


@click.group()
def cli():
    pass


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
    output = tabulate.tabulate(pgs, **kwargs)
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
    if no_header:
        kwargs = {'tablefmt': 'plain'}
    else:
        kwargs = {'tablefmt': 'simple', 'headers': 'keys'}
    output = tabulate.tabulate(params, **kwargs)
    click.echo(output)


@cli.command(name='terraform')
@click.argument('parameter-group')
def cmd_terraform(parameter_group):
    params = rds_get_parameters(parameter_group)
    info = rds_get_pg_info(parameter_group)
    params = only_user_params(params)
    template = terraform(parameter_group, info, params)
    click.echo(template)


def main():
    cli()
    

if __name__ == '__main__':
    main()
