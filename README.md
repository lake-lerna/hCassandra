# hCassandra: <sub> *A Cassandra Stress Test*



The **hCassandra** project holds a test case of the [Hydra](https://github.com/lake-lerna/hydra) Platform---a scale testing infra using Mesos and Marathon. **hCassandra** evaluates the performance of a Cassandra Cluster in an automated fashion. Overall, it automatically scales the number of clients writing and reading into the database (as per users specification), while providing stats and graphs along the run.

**Disclaimer:** This is still *WORK IN PROGRESS* and will be progressively updated.

## Requirements

- **Cassandra Cluster**

  We assume a Cassandra Cluster is already configured. If a Cassandra Cluster is already in place you can skip this section. Otherwise follow the instructions to bring up your own Cassandra Cluster:

  - For our tests we set a 3-Node Cluster on Google Cloud Servers. However, you may set up a N-Node Cluster according to your own requirements or test scenario.
  - Software & Hardware Specs:
    - OS: Debian (Debian 3.16.7-ckt25-2 (2016-04-08) x86_64 GNU/Linux)
    - n1-standard-16 (16 vCPUs; 16GB of memory)
    - Python 2.7

```
# Install Latest Version of OpenJDK
$ sudo apt-get install openjdk-8-jdk

# Check which version of Java is installed by running the following command:
$ java -version
# It is recommended to use the latest version of Oracle Java 8 or OpenJDK 8 on all nodes.

# Add the repository to the /etc/apt/sources.list.d/cassandra.sources.list
$ echo "deb http://debian.datastax.com/community stable main" | sudo tee -a /etc/apt/sources.list.d/cassandra.sources.list

# Add the DataStax repository key to your aptitude trusted keys.
$ curl -L https://debian.datastax.com/debian/repo_key | sudo apt-key add -

# Install the latest package:
$ sudo apt-get update
$ sudo apt-get install dsc30
$ sudo apt-get install cassandra-tools

# Because the Debian packages start the Cassandra service automatically, you must stop the server and clear the data:
Doing this removes the default cluster_name (Test Cluster) from the system table. All nodes must use the same cluster name.
$ sudo service cassandra stop
$ sudo rm -rf /var/lib/cassandra/*
```

Repeat this process for each node.


Once, Cassandra has been installed on all nodes. you'll need to edit your configuration file for each node. To do so, open on your preferred text editor:

```
vim ~/etc/cassandra/cassandra.yaml
```


The information you'll need to edit for each node will be (cluster_name, seed_provider, rpc_address and listen_address). Choose a node to be your seed one (or any other number, in our case we selected 2 out of our 3 nodes to be seeds), and look in the configuration file for the lines that refer to each of these attributes, and modify them to your needs:

```
cluster_name: 'Name'
seed_provider:
      - seeds:  "Seed IP"
listen_address: <current_node_IP>
rpc_address: <current_node_IP>
```

To illustrate this, consider the following 3 node cluster example, with: n1 (10.10.0.155), n2 (10.10.2.218) and n3 (10.10.3.116). Assuming we take n1 and n2 as seed nodes. The configuration for n1, would look like:

```
cluster_name: 'dev-Test' (same in all nodes)
seed_provider:
      - seeds:  "10.10.0.155,10.10.2.218"  (IPs for seed nodes / same in all nodes)
listen_address: 10.10.0.155    (current node's IP Address)
rpc_address: 10.10.0.155    (current node's IP Address)
```

To run, simply type the following on the seed node and when it's finished, replicate this process on the other nodes. If you don't see any errors, your multi-node Cassandra setup should be successfully deployed..

```
$ sudo sh ~/cassandra/bin/cassandra

```


To verify that DataStax Distribution of Apache Cassandra is running:


```
$ nodetool status

```


For further guidelines on how to install Cassandra, please refer to:

- Cassandra Installation: http://docs.datastax.com/en/cassandra/3.0/cassandra/install/installDeb.html
- Cluster Configuration: https://www.digitalocean.com/community/tutorials/how-to-configure-a-multi-node-cluster-with-cassandra-on-a-ubuntu-vps


**IF...**

If a node in the cluster shows to be down (DN, when running `nodetool status` on the nodes that are UP) despite the efforts to restart it, start the service as follows:


```
  sudo cassandra -f &

```


- **Cassandra-Tools**

    The Cassandra Client (stress client) developed in this test case is largely based in the *cassandra-stress* tool available along the Cassandra-Tools. You will need to make sure cassandra tools is installed in each slave node of your Hydra setup.

     For installation:

```
sudo apt-get install openjdk-8-jdk
echo "deb http://debian.datastax.com/community stable main" | sudo tee -a /etc/apt/sources.list.d/cassandra.sources.list
curl -L https://debian.datastax.com/debian/repo_key | sudo apt-key add -
sudo apt-get update
sudo apt-get install cassandra-tools
sudo service cassandra stop
```


- **IMPORTANT**

  - To avoid any performance penalty (e.g., resource contention), stress clients should run in DIFFERENT machines from those in the Cassandra Cluster. In other words, 'slave' nodes of the Hydra Infra should be different from the nodes in the Cassandra Cluster.

## Running the Test

In order to run the test, you require:

(1) Setup Hydra (follow the instructions in the [Hydra](https://github.com/lake-lerna/hydra) README)

(2) Git clone the hCassandra Project into your Hydra Master from: https://github.com/lake-lerna/hCassandra

(3) Put your hydra.ini configuration file in the project's root (~/hCassandra)
- Properly set Mesos and Marathon IPs to your Hydra Setup IP.

### **OPTION 1**

To automatically run the tests for a given set of clients use the IPython Notebook located in the root of the project (hCassandra_runtests.ipynb), which will ease the execution of all tests and present performance results in tables and graphs.

*REQUIREMENT*: You must install jupyter notebook[INSTALL](http://jupyter.readthedocs.io/en/latest/install.html)

Next, to run the notebook execute from ~/hCassandra:

```
  jupyter notebook
```

The Jupyter Notebook is running at: http://localhost:8888/, open in a browser and follow instructions in the notebook.

FOR REMOTE ACCESS TO YOUR NOTEBOOK:

```
# CREATE A CONFIG FILE
$ jupyter notebook --generate-config

# Open config File
$ vim ~/.jupyter/jupyter_notebook_config.py

# Uncomment and change the follwoing lines:
c.NotebookApp.ip = '*'
# Set fixed port for server access
c.NotebookApp.port = 8888
```

### **OPTION 2**


- From the Command-Line:

      python ~/src/hCassandra_test.py --cluster_ips='10.10.3.20,10.10.3.113,10.10.3.119' --total_client_count=30

  Where:
  - ***cluster_ips***: comma separated IPs of nodes in the Cassandra Cluster. (default: 127.0.0.1)
  - ***total_client_count***: total number of clients to launch. (default = 20)
  - ***total_ops_count*** (optional): total number of operations (write/read) to be performed (default: 1000000).
  - ***profile***: filename (.YAML) specifying keyspace, table definition and/or query definitions. If not specified 'default' keyspace, table and queries will be used for the stress test (still not supported)
  - ***test_duration***: (optional) either test duration or total ops count should be specified.
  - ***consistency_level***: (optional) Cassandra database consistency level (default: LOCAL_ONE)
  - ***config_file***: hydra config file (default: hydra.ini) located in the root folder.
