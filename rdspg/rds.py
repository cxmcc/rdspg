import boto3


def get_api(cluster=False):
    if cluster:
        return RDSClusterAPI()
    else:
        return RDSInstanceAPI()


class RDSAPI:
    def __init__(self):
        self.client = boto3.client('rds')

    def get_parameters(self, name):
        raise NotImplementedError

    def get_dbs(self):
        raise NotImplementedError

    def get_parameter_groups(self):
        raise NotImplementedError

    def get_pg_info(self):
        raise NotImplementedError

    def generate_pg_to_db_mapping(self):
        pgs = self.get_parameter_groups()
        dbs = self.get_dbs()
        mapping = {}
        for pg in pgs:
            pg_name = pg[self.FIELD_PARAMETER_GROUP_NAME]
            mapping[pg_name] = []
        for db in dbs:
            db_name = db[self.FIELD_DB_ID]
            pg_list = db[self.FIELD_PARAMETER_GROUP]
            pg_name = pg_list[0][self.FIELD_PARAMETER_GROUP_NAME]
            mapping[pg_name].append(db_name)
        out = []
        for k, v in sorted(mapping.items()):
            if v == []:
                value = '<not-used>'
            else:
                value = ','.join(v)
            out.append((k, value))
        return out

    def list_tags(self, arn):
        resp = self.client.list_tags_for_resource(ResourceName=arn)
        return resp.get('TagList', [])


class RDSInstanceAPI(RDSAPI):
    FIELD_PARAMETER_GROUP_NAME = 'DBParameterGroupName'
    FIELD_DB_ID = 'DBInstanceIdentifier'
    FIELD_PARAMETER_GROUP = 'DBParameterGroups'

    def get_parameters(self, name):
        paginator = self.client.get_paginator('describe_db_parameters')
        out = []
        for page in paginator.paginate(DBParameterGroupName=name):
            out += page['Parameters']
        return out

    def get_dbs(self):
        paginator = self.client.get_paginator('describe_db_instances')
        out = []
        for page in paginator.paginate():
            out += page['DBInstances']
        return out

    def get_parameter_groups(self):
        paginator = self.client.get_paginator('describe_db_parameter_groups')
        out = []
        for page in paginator.paginate():
            out += page['DBParameterGroups']
        return out

    def get_pg_info(self, name):
        resp = self.client.describe_db_parameter_groups(
            DBParameterGroupName=name
        )
        info = resp['DBParameterGroups'][0]
        return info


class RDSClusterAPI(RDSAPI):
    FIELD_PARAMETER_GROUP_NAME = 'DBClusterParameterGroupName'
    FIELD_DB_ID = 'DBClusterIdentifier'
    FIELD_PARAMETER_GROUP = 'DBClusterParameterGroups'

    def get_parameters(self, name):
        # Can't be paginated
        resp = self.client.describe_db_cluster_parameters(
            DBClusterParameterGroupName=name,
        )
        return resp['Parameters']

    def get_dbs(self):
        # Can't be paginated
        resp = self.client.describe_db_clusters()
        return resp['DBClusters']

    def get_parameter_groups(self):
        # Can't be paginated
        resp = self.client.describe_db_cluster_parameter_groups()
        return resp['DBClusterParameterGroups']

    def get_pg_info(self, name):
        resp = self.client.describe_db_cluster_parameter_groups(
            DBClusterParameterGroupName=name
        )
        info = resp['DBClusterParameterGroups'][0]
        return info
