rdspg
======

Command-line toolkit to help understand information about your AWS RDS Parameter Groups.

Installation
------------

.. code:: bash

    pip install rdspg
    
Purpose
-------

When it comes to analyzing parameter groups for RDS, AWS suggested in a `blog post <https://aws.amazon.com/premiumsupport/knowledge-center/default-custom-groups/>`_ that it could only be done using `diff`:

    There is no AWS CLI command to compare two parameter groups simultaneously; this feature is only available by using the RDS console.
    You can then compare the plain text files that list the parameter groups using a Linux tool such as the diff command, or a source code editor like Notepad++.

I think we can do better. This tool is to help us make that task a lot easier. Also adding a few other features to help analyzing changes.

Permission Config
-----------------
This tool needs certain IAM permissions in order to work. Example policy:

::

    {
       "Version":"2012-10-17",
       "Statement":[
          {
             "Effect":"Allow",
             "Action":[
                "rds:DescribeDBInstances",
                "rds:DescribeDBParameters",
                "rds:DescribeDBParameterGroups",
                "rds:DescribeDBClusters",
                "rds:DescribeDBClusterParameterGroups",
                "rds:DescribeDBClusterParameters",
                "rds:ListTagsForResource"
             ],
             "Resource":"*"
          }
       ]
    }

Usage
-----
* Listing Parameter Groups:

::

    $ rdspg list
    DBParameterGroupName             DBParameterGroupFamily    Description
    -------------------------------  ------------------------  ----------------------------------------------------------
    default.aurora-postgresql9.6     aurora-postgresql9.6      Default parameter group for aurora-postgresql9.6
    default.aurora5.6                aurora5.6                 Default parameter group for aurora5.6
    default.postgres9.3              postgres9.3               Default parameter group for postgres9.3
    default.postgres9.4              postgres9.4               Default parameter group for postgres9.4
    default.postgres9.5              postgres9.5               Default parameter group for postgres9.5
    default.postgres9.6              postgres9.6               Default parameter group for postgres9.6
    my-parameter-group               postgres9.6               My Parameter Group

* Getting parameters in parameter group, filtering out default values:

::

    $ rdspg get my-replica
    ParameterName                      ParameterValue  ApplyMethod    ApplyType
    -------------------------------  ----------------  -------------  -----------
    autovacuum_analyze_scale_factor               0.1  immediate      dynamic
    checkpoint_segments                           512  immediate      dynamic
    checkpoint_timeout                            300  immediate      dynamic
    checkpoint_warning                             60  immediate      dynamic
    default_statistics_target                     100  immediate      dynamic
    hot_standby_feedback                            1  immediate      dynamic
    log_autovacuum_min_duration                     0  immediate      dynamic
    log_connections                                 1  immediate      dynamic
    log_disconnections                              1  immediate      dynamic

* Getting a mapping of parameter group -> instances:

::

    $ rdspg mapping
    ParameterGroup       DBInstances
    -------------------  ---------------------------------
    default.postgres9.4  <not-used>
    default.postgres9.5  db-replica-9-5-a,db-replica-9-5-b
    default.postgres9.6  db-replica-9-6-a,db-replica-9-6-b

* Compare differences between two parameter groups:

::

    $ rdspg diff my-replica-a my-replica-b
    ParameterName          my-replica-a  my-replica-b
    -------------------  --------------  ---------------------
    checkpoint_timeout              300  450
    checkpoint_warning               60  <not-set>
    checkpoint_segments             512  32

* Export parameter group in terraform template format:

::

    $ rdspg terraform my-parameter-group
    resource "aws_db_parameter_group" "my-parameter-group" {
      name   = "my-parameter-group"
      family = "postgres9.5"
      description = "My awesome parameter group"
    
      parameter {
        name         = "autovacuum_analyze_scale_factor"
        value        = "0.01"
        apply_method = "immediate"
      }
    
      parameter {
        name         = "autovacuum_vacuum_scale_factor"
        value        = "0.01"
        apply_method = "immediate"
      }
    
    }

* All the commands work for db clusters with ``--cluster`` flag

::

    $ rdspg list --cluster
    DBClusterParameterGroupName    DBParameterGroupFamily    Description
    -----------------------------  ------------------------  --------------------------------------------------------
    customers-p-cluster            aurora-postgresql9.6      Managed by Terraform
    default.aurora-postgresql1     aurora-postgresql1        Default cluster parameter group for aurora-postgresql1
    default.aurora-postgresql9.6   aurora-postgresql9.6      Default cluster parameter group for aurora-postgresql9.6
    default.aurora5.6              aurora5.6                 Default cluster parameter group for aurora5.6
