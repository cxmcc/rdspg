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
