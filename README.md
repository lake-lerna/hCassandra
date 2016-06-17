# hCassandra: <sub> *A Cassandra Stress Test*



The **hCassandra** project holds a test case of the [Hydra](https://github.com/lake-lerna/hydra) Platform---a scale testing infra using Mesos and Marathon. **hCassandra** evaluates the performance of a Cassandra Cluster in an automated fashion. Overall, it automatically scales the number of clients writing and reading into the database (as per users specification), while providing stats and graphs along the run.

**Disclaimer:** This is still *WORK IN PROGRESS* and will be progressively updated.

## Requirements

- **Cassandra Cluster**

  We assume a Cassandra Cluster is already configured. For guidelines on how to install Cassandra, please refer to:

  - Cassandra Installation: http://docs.datastax.com/en/cassandra/3.0/cassandra/install/installDeb.html
  - Cluster Configuration: https://www.digitalocean.com/community/tutorials/how-to-configure-a-multi-node-cluster-with-cassandra-on-a-ubuntu-vps


  In order to enable communication from any other node in the network to the Cassandra Cluster nodes, relevant configuration(s) are:

**Configuration Tips**

    # Open & Edit /etc/cassandra/cassandra.yaml
    vim /etc/cassandra/cassandra.yaml

    # Change the following attributes to the cluster node's IP
    rpc_address=<node_ip>
    listen_address=<node_ip>
    seeds:<seeds_ips>

- **Cassandra-Tools**

    The Cassandra Client (stress client) developed in this test case is largely based in the *cassandra-stress* tool available along the Cassandra-Tools. For installation:

      sudo apt-get install openjdk-8-jdk
      echo "deb http://debian.datastax.com/community stable main" | sudo tee -a /etc/apt/sources.list.d/cassandra.sources.list
      curl -L https://debian.datastax.com/debian/repo_key | sudo apt-key add -
      sudo apt-get update
      sudo apt-get install cassandra-tools
      sudo service cassandra stop

- **IMPORTANT**

  - To avoid any performance penalty (e.g., resource contention), stress clients should run in DIFFERENT machines from those in the Cassandra Cluster. In other words, 'slave' nodes of the Hydra Infra should be different from the nodes in the Cassandra Cluster.

## Running the Test

- From the Command-Line:

      python hCassandra_test.py --cluster_ips='10.10.3.20,10.10.3.113,10.10.3.119' --total_client_count=30

  Where:
  - ***cluster_ips***: comma separated IPs of nodes in the Cassandra Cluster. (default: 127.0.0.1)
  - ***total_client_count***: total number of clients to launch. (default = 20)
  - ***total_ops_count***: total number of operations (write/read) to be performed (default: 1000000).
  - ***profile***: filename (.YAML) specifying keyspace, table definition and/or query definitions. If not specified 'default' keyspace, table and queries will be used for the stress test.
  - ***test_duration***: (optional) either test duration or total ops count should be specified.
  - ***consistency_level***: Cassandra database consistency level (default: LOCAL_ONE)
  - ***config_file***: hydra config file (default: hydra.ini) located in the root folder.
