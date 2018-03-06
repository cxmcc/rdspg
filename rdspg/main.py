import click
import rds
import tabulate
import os
import jinja2


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
        for k in ('DBParameterGroupArn', 'DBClusterParameterGroupArn'):
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


def terraform(parameter_group_name, info, params, tags, cluster=False):
    if cluster:
        template_file = 'terraform_cluster.jinja'
    else:
        template_file = 'terraform_instance.jinja'

    def render(context):
        curr_dir = os.path.dirname(__file__)
        template_file_path = os.path.join(curr_dir, template_file)
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
@click.option('--cluster', is_flag=True, default=False)
@click.option('--no-header', is_flag=True, default=False)
def cmd_mapping(cluster, no_header):
    api = rds.get_api(cluster=cluster)
    mapping = api.generate_pg_to_db_mapping()
    if no_header:
        kwargs = {'tablefmt': 'plain'}
    else:
        headers = ('ParameterGroup', 'DBInstances')
        kwargs = {'tablefmt': 'simple', 'headers': headers}
    output = tabulate.tabulate(mapping, numalign='right', **kwargs)
    click.echo(output)


@cli.command(name='list')
@click.option('--cluster', is_flag=True, default=False)
@click.option('--detail', is_flag=True, default=False)
@click.option('--no-header', is_flag=True, default=False)
def cmd_list(cluster, detail, no_header):
    api = rds.get_api(cluster=cluster)
    pgs = api.get_parameter_groups()
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
@click.option('--cluster', is_flag=True, default=False)
@click.option('--all-params', is_flag=True, default=False)
@click.option('--detail', is_flag=True, default=False)
@click.option('--no-header', is_flag=True, default=False)
def cmd_get(cluster, parameter_group, all_params, detail, no_header):
    api = rds.get_api(cluster=cluster)
    params = api.get_parameters(parameter_group)
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
@click.option('--cluster', is_flag=True, default=False)
@click.option('--all-params', is_flag=True, default=False)
@click.option('--no-header', is_flag=True, default=False)
def cmd_diff(cluster, parameter_group_a, parameter_group_b,
             all_params, no_header):
    api = rds.get_api(cluster=cluster)
    params_a = api.get_parameters(parameter_group_a)
    params_b = api.get_parameters(parameter_group_b)
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
@click.option('--cluster', is_flag=True, default=False)
@click.argument('parameter-group')
def cmd_terraform(cluster, parameter_group):
    api = rds.get_api(cluster=cluster)
    params = api.get_parameters(parameter_group)
    info = api.get_pg_info(parameter_group)
    if cluster:
        arn = info['DBClusterParameterGroupArn']
    else:
        arn = info['DBParameterGroupArn']
    tags = api.list_tags(arn)
    params = only_user_params(params)
    template = terraform(parameter_group, info, params, tags)
    click.echo(template)


def main():
    cli()


if __name__ == '__main__':
    main()
