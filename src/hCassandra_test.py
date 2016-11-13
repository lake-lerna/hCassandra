#!/usr/bin/env python
__author__ = 'annyz'

from sys import path
# Append 'hydra' directory to Python path
path.append("hydra/src/main/python")

import sys
import logging
import math
import ast
import copy
import json
import threading
import time
import random
import paramiko

from datetime import datetime, timedelta
from optparse import OptionParser
from pprint import pformat  # NOQA
from hydra.lib import util
from hydra.lib.h_analyser import HAnalyser
from hydra.lib.hydrabase import HydraBase
from cassandra.cluster import Cluster

try:
    # Python 2.x
    from ConfigParser import ConfigParser
except ImportError:
    # Python 3.x
    from configparser import ConfigParser

l = util.createlogger('hCassandra', logging.DEBUG)


class RunTestCassandra(HydraBase):
    def __init__(self, options, runtest=True, mock=False):
        self.options = options
        self.config = ConfigParser()
        HydraBase.__init__(self, 'CassandraStressTest', self.options, self.config, startappserver=runtest, mock=mock,
                           app_dirs=['src', 'hydra'])
        self.stress_client = '/stress-client'
        self.add_appid(self.stress_client)
        if runtest:
            self.run_test()
            self.stop_appserver()

    def rerun_test(self, options):
        self.options = options
        self.reset_all_app_stats(self.stress_client)
        # Signal message sending
        l.info("Sending signal to Cassandra Stress client to start sending all messages..")
        # Force start-time for ALL clients +60 seconds from current time
        start_time = datetime.now() + timedelta(seconds=60)
        l.debug("Current Time: %s, Start Time: %s" % (datetime.now(), start_time))
        task_list = self.all_task_ids[self.stress_client]
        ha_list = []
        for task_id in task_list:
            info = self.apps[self.stress_client]['ip_port_map'][task_id]
            port = info[0]
            ip = info[1]
            ha_stress = HAnalyser(ip, port, task_id)
            # Signal ALL clients to start sending data, blocks until clients respond with "DONE" after sending all data
            ha_stress.start_test(start_time=start_time)
            ha_list.append(ha_stress)
        l.info('Waiting for test(s) to end...')
        if self.options.sim_failure:
            l.debug("Simulate Cassandra Node Failure. Init.")
            # Thread Event to indicate tests have been completed
            tests_completed = threading.Event()
            # Launch parallel Thread to simulate cassandra node failure.
            l.debug("Launch separate thread to simulate node failure and rejoin.")
            failure_thread = threading.Thread(target=simulate_node_failure, args=(self.options.cluster_ips.split(','),
                                                                 self.options.test_duration, tests_completed))
            failure_thread.start()
        for idx, ha_stress in enumerate(ha_list):
            l.debug('Waiting for task [%s] in [%s:%s] test to END. Iteration: %s' % (ha_stress.task_id, ha_stress.server_ip, ha_stress.port, idx))
            ha_stress.wait_for_testend()
        if self.options.sim_failure:
            l.debug("ALL tests are COMPLETED.")
            tests_completed.set()
        l.info('Fetch App Stats')
        self.fetch_app_stats(self.stress_client)

        return self.result_parser()

    def run_test(self, first_run=True):
        # Get Mesos/Marathon Clients
        self.start_init()
        # Reset (drop) Cassandra DB for cassandra-stress tool default 'keyspace1'
        self.reset_db()
        # Create Table(s) & Triggers for stress Test
        # self.create_triggers()
        # Launch Cassandra Stress-Client(s)
        self.launch_stress_client()
        # Rerun the test
        res = self.rerun_test(self.options)
        # Return Test Results
        return res

    def create_triggers(self):
        try:
            cluster_ips = self.options.cluster_ips.split(',')
            cluster = Cluster(cluster_ips)
            l.debug("Connecting to Cassandra Cluster: [%s]" % (cluster_ips))
            session = cluster.connect()
            l.info("Create keyspace [keyspace1]...")
            # Create Keyspace
            session.execute("CREATE KEYSPACE keyspace1 WITH replication = {'class': 'SimpleStrategy', "
                            "'replication_factor': '1'}  AND durable_writes = true;")
            l.info("Create tables [standard1] & [counter1]...")
            table_create = "CREATE TABLE keyspace1.standard1 ( " \
                           "key blob PRIMARY KEY," \
                            "\"C0\" blob," \
                            "\"C1\" blob," \
                            "\"C2\" blob," \
                            "\"C3\" blob," \
                            "\"C3\" blob" \
                            ") WITH COMPACT STORAGE" \
                            "AND bloom_filter_fp_chance = 0.01" \
                            "AND caching = {'keys': 'ALL', 'rows_per_partition': 'NONE'}" \
                            "AND comment = ''" \
                            "AND compaction = {'class': " \
                            "'org.apache.cassandra.db.compaction.SizeTieredCompactionStrategy', 'max_threshold': '32'," \
                            " 'min_threshold': '4'}" \
                            "AND compression = {'enabled': 'false'}" \
                            "AND crc_check_chance = 1.0" \
                            "AND dclocal_read_repair_chance = 0.1" \
                            "AND default_time_to_live = 0" \
                            "AND gc_grace_seconds = 864000" \
                            "AND max_index_interval = 2048" \
                            "AND memtable_flush_period_in_ms = 0" \
                            "AND min_index_interval = 128" \
                            "AND read_repair_chance = 0.0" \
                            "AND speculative_retry = '99PERCENTILE';"
            l.info("Create standard1 Table")
            # Create 'standard1' & 'counter1' default Tables
            session.execute(table_create)
            l.info('Succeeded to create keyspace1 and standard1 Table.')
            # Create Trigger
            trigger_jar = 'org.apache.cassandra.triggers.AuditTrigger'
            trigger_cql = "CREATE TRIGGER pushTrigger ON keyspace1.standard1 USING " + trigger_jar
            session.execute(trigger_cql)
        except Exception as e:
            l.error('FAILED to create trigger. Error: %s' % str(e))

    def reset_db(self):
        try:
            ips = self.options.cluster_ips.split(',')
            cluster = Cluster(ips)
            l.debug("Connecting to Cassandra Cluster: [%s]" % (ips))
            session = cluster.connect()
            l.info("dropping [keyspace1] (default) keyspace...")
            # session.execute("DROP KEYSPACE keyspace1")
            # Instead of 'dropping' the complete keyspace, let's delete all rows in Tables, so they remain created for subsequent tests
            session.execute("TRUNCATE keyspace1.counter1;")
            session.execute("TRUNCATE keyspace1.standard1;")
            l.info('Succeeded to delete DB.')
        except Exception as e:
            l.error('Failed to reset Cassandra DB. Error: %s' % str(e))

    def stop_and_delete_all_apps(self):
        self.delete_all_launched_apps()

    def result_parser(self):
        result = {
            'total ops': [],     # Running total number of operations during the run.
            'op/s': [],          # Number of operations per second performed during the run.
            'pk/s': [],          # Number of partition operations per second performed during the run.
            'row/s': 0,          # Number of row operations per second performed during the run.
            'mean': 0,           # Average latency in milisecond for each operation during that run.
            'med': [],           # Median latency in miliseconds for each operation during that run.
            '.95': [],           # 95% of the time the latency was less than this number.
            '.99': [],           # 99% of the time the latency was less than this number.
            'max': [],           # Maximum latency in miliseconds.
            'gc_num': 0,         # Number of garbage collections.
            'max_ms': [],        # Longest garbage collection in miliseconds.
            'sum_ms': 0,         # Total of garbage collection in miliseconds.
            'sdv_ms': [],        # Standard deviation in miliseconds.
            'mb': 0,             # Size of the garbage collection in megabytes.
            'op_time': []        # Total Operation Time per client
        }
        cassandra_results = {
            'write': copy.deepcopy(result),
            'read': copy.deepcopy(result)
        }
        # Get stats for Cassandra Stress Client
        stats = self.get_app_stats(self.stress_client)
        # num_clients = self.options.total_client_count
        db_ops = ['write', 'read']
        for client in stats.keys():
            info = stats[client]
            for db_op in db_ops:
                if db_op in info:
                    try:
                        info[db_op] = ast.literal_eval(info[db_op])
                        cassandra_results[db_op]['total ops'].append(int(info[db_op]['Total partitions']))
                        cassandra_results[db_op]['op/s'].append(int(info[db_op]['op rate']))
                        cassandra_results[db_op]['pk/s'].append(int(info[db_op]['partition rate']))
                        cassandra_results[db_op]['.95'].append(float(info[db_op]['latency 95th percentile']))
                        cassandra_results[db_op]['.99'].append(float(info[db_op]['latency 99th percentile']))
                        cassandra_results[db_op]['gc_num'] += int(info[db_op]['total gc count'])
                        cassandra_results[db_op]['sdv_ms'].append(float(info[db_op]['stdev gc time(ms)']))
                        cassandra_results[db_op]['max'].append(float(info[db_op]['latency max']))
                        cassandra_results[db_op]['med'].append(float(info[db_op]['latency median']))
                        cassandra_results[db_op]['op_time'].append((info[db_op]['Total operation time']).replace(' ', ''))
                    except Exception as e:
                        l.error("Failed to parse stats from Client: " + pformat(client) + " DATA = " + pformat(info[db_op]))
                        l.error("ERROR: %s" % str(e))

        return cassandra_results

    def launch_stress_client(self):
        max_threads_per_client = 20
        l.info("Launching the Cassandra Stress Client(s). Total clients = %s" % (self.options.total_client_count))
        # Determine number of threads per Cassandra Stress Client
        if self.options.total_client_count > max_threads_per_client:
            threads_per_client = max_threads_per_client
        else:
            threads_per_client = self.options.total_client_count
        l.debug("Number of Threads per Cassandra-Stress Client, set to: %s" % (threads_per_client))
        self.create_binary_app(name=self.stress_client, app_script='./src/stress_client.py %s %s %s %s %s %s'
                                                                   % (self.options.total_ops_count,
                                                                      threads_per_client,
                                                                      self.options.cluster_ips,
                                                                      self.options.test_duration,
                                                                      self.options.cl,
                                                                      self.options.profile),
                               cpus=0.2, mem=600, ports=[0])
        if self.options.total_client_count > max_threads_per_client:
            client_count = math.ceil(self.options.total_client_count / max_threads_per_client)
            l.info("Number of Cassandra-Stress Clients to launch = %s" % (client_count))
            self.scale_and_verify_app(self.stress_client, client_count)

    def delete_all_launched_apps(self):
        l.info("Deleting Stress Clients")
        self.delete_app(self.stress_client)


def simulate_node_failure(node_ips, max_duration, tests_completed):
    """
        Simulate random cassandra node failure and 'rejoin' into cluster
    """
    run = True
    l.info("START Cassandra Node Failure Simulation. Entering.")
    while run:
        # If stress-tests are still running continue with node failure simulation
        if not tests_completed.isSet():
            # Select 'random' node from Cassandra Cluster
            node_ip = select_random_node(node_ips)
            # Determine delay before stopping cassandra node (to simulate failure / node down)
            duration_secs = max_duration*60
            time_next_stop = random.randint(1, duration_secs/4)
            l.debug("STOP programmed in %s seconds" % time_next_stop)
            # Wait
            time.sleep(time_next_stop)
            ssh_fail = False
            # Stop Cassandra Node (simulate failure / stop the service)
            stop_cmd = "sudo service cassandra stop"
            l.debug("STOP Cassandra Node: %s"%node_ip)
            try:
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(str(node_ip))
                l.debug("[Simulate Cassandra Node Failure] Connected to host: %s" % node_ip)
            except paramiko.AuthenticationException as e:
                l.error("Authentication failed when connecting to %s. ERROR: %s" % (node_ip, e))
                ssh_fail = True
            except:
                l.error("Could not SSH to %s, waiting for it to start" % node_ip)
                ssh_fail = True
            if not ssh_fail:
                # Send the command to STOP cassandra node
                ssh.exec_command(stop_cmd)
                # Determine delay before starting cassandra node (to simulate rejoin to the cluster)
                time_next_rejoin = random.randint(1, duration_secs/4)
                l.debug("START programmed in %s seconds" % time_next_rejoin)
                time.sleep(time_next_rejoin)
                # Start Cassandra Node (simulate rejoin / start the service)
                start_cmd = "sudo service cassandra start"
                l.debug("START Cassandra Node: %s"%node_ip)
                # Send the command (non-blocking)
                ssh.exec_command(start_cmd)
                # Disconnect from the host
                l.debug("Closing SSH connection to host: %s" % node_ip)
                ssh.close()
                run=False
        else:
            # Tests Complete has been signaled
            run=False
            l.info("END node failure simulation. Exiting.")

def select_random_node(cluster_ips):
    """
        Select a random cassandra node from a list of IPs
    """
    return random.choice(cluster_ips)

class RunTest(object):
    def __init__(self, argv):
        usage = ('python %prog --test_duration=<time to run test> --total_ops_count=<Total Operations>'
                 '--total_client_count=<Total clients to launch> --cluster_ips=<cassandra node list ips>'
                 '--consistency_level=<cassandra consistency level> --profile=<yaml profile>'
                 '--config_file=<path_to_config_file> --sim_failure=<simulate node failure>')
        parser = OptionParser(description='cassandra scale test master',
                              version="0.1", usage=usage)
        parser.add_option("--test_duration", dest='test_duration', type='int', default=5)
        parser.add_option("--total_ops_count", dest='total_ops_count', type='int', default=1000000)
        parser.add_option("--total_client_count", dest='total_client_count', type='int', default=20)
        parser.add_option("--cluster_ips", dest='cluster_ips', type='string', default='127.0.0.1')
        parser.add_option("--consistency_level", dest='cl', type='string', default='LOCAL_ONE')
        parser.add_option("--profile", dest='profile', type='string', default='hydra_profile.yaml')
        parser.add_option("--config_file", dest='config_file', type='string', default='hydra.ini')
        parser.add_option("--sim_failure", dest='sim_failure', action="store_true", default=False)


        (options, args) = parser.parse_args()
        # Check NO list of positional arguments leftover after parsing options
        if ((len(args) != 0)):
            parser.print_help()
            sys.exit(1)

        # Run Cassandra Test
        r = RunTestCassandra(options, False)
        r.start_appserver()
        res = r.run_test()
        r.delete_all_launched_apps()
        # Cassandra-Stress Test Results
        result_json = json.dumps(res)
        print("Cassandra Stress Results: \n%s" % pformat(result_json))
        r.stop_appserver()

if __name__ == "__main__":
    RunTest(sys.argv)
