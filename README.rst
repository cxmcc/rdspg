rdspg
======

Command-line toolkit to help understand information of your RDS Paramter Groups.

Installation
------------

.. code:: bash

    pip install rdspg
    
Usage
-----
Listing Parameter Groups:

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

Getting parameters in parameter group, filtering out default values:

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

Compare differences between two parameter groups:

::

    $ rdspg diff my-replica-a my-replica-b
    ParameterName          my-replica-a  my-replica-b
    -------------------  --------------  ---------------------
    checkpoint_timeout              300  450
    checkpoint_warning               60  <not-set>
    checkpoint_segments             512  32

Export parameter group in terraform template format:

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
