#!/usr/bin/env python
__author__ = 'annyz'

from sys import path
# Append 'hydra' directory to Python path
path.append("hydra/src/main/python")

import logging
import os
import psutil
import json
import time
import subprocess
import re
import sys

from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from hydra.lib import util
from hydra.lib.hdaemon import HDaemonRepSrv
from pprint import pformat   # NOQA

l = util.createlogger('StressClient', logging.DEBUG)


class HDCStressRepSrv(HDaemonRepSrv):
    """
        HDaemon Cassandra Stress REP Server (to control and collect stats from stress client)
    """
    def __init__(self, port, run_data, stress_metrics):
        self.run_data = run_data
        self.stress_metrics = stress_metrics
        self.init_stress_metrics()
        HDaemonRepSrv.__init__(self, port)
        # Register Functions
        self.register_fn('teststart', self.test_start)
        self.register_fn('getstats', self.get_stats)
        self.register_fn('teststatus', self.test_status)
        self.register_fn('updateconfig', self.update_config)

    def test_start(self, start_time):
        """
           Signal Stress Client to START test
        """
        l.info('Scheduling Test to start %s.' % (start_time))
        start_time = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S.%f")
        self.run_data['test_status'] = 'running'
        self.run_data['stats']['msg_cnt'] = self.stress_metrics['ops_count']
        # If time to start has passed, start immediately
        if start_time < datetime.now():
            time_to_start(self.run_data)
        else:
            test_scheduler = BackgroundScheduler()
            test_scheduler.add_job(lambda: time_to_start(self.run_data), next_run_time=start_time)
            test_scheduler.start()
        # Report Status
        return ('ok', None)

    def get_stats(self):
        """
            Retrieve Test Stats
        """
        l.info("Sending Cassandra Stress Test Stats:" + pformat(self.run_data['stats']))
        return ('ok', self.run_data['stats'])

    def reset_stats(self):
        self.run_data['stats'] = {}
        return('ok', None)

    def test_status(self):
        """
            Retrieve Test Status: 'stopped', 'stopping' or 'running'
        """
        return ('ok', self.run_data['test_status'])

    def init_stress_metrics(self):
        l.info("Initialize Cassandra Stress Test metrics...")
        self.ops_count = self.stress_metrics['ops_count']       # Number of Operations to run

    def update_config(self, ops_count):
        self.ops_count = ops_count
        l.info("Stress Client updated metrics to: ops_count=%s" % self.ops_count)
        # Return Status of 'update'
        return ('ok', None)


def time_to_start(run_data):
    l.info('Starting Cassandra Stress Test at: %s' % (datetime.utcnow()))
    # Initialize test data collection
    run_data['start'] = True
    return


def parse_results(stdout, run_data):
    try:
        l.info('Start parsing cassandra-stress output.')
        index_start = stdout.find('op rate')
        index_end = stdout.find('END')
        if (index_start and index_end) != -1:
            results = stdout[index_start:index_end]
            # find 'matches' of the type att_name:value
            matches = re.findall(r'.+\:{1}.+', results)
            # partition each match at ':'
            matches = [m.split(':', 1) for m in matches]
            # Remove extra whitespaces
            for pair in matches:
                for idx, m in enumerate(pair):
                    pair[idx] = re.sub(r'\s{2,}', '', m)
            # Build dictionary of results
            result_dict = dict(matches)
            # Remove [] in results
            for key, value in result_dict.iteritems():
                result_dict[key] = re.sub(r'\[{1}.{1,}\]{1}', '', value)
            run_data.update(result_dict)
    except Exception, e:
        l.error("ERROR while parsing Cassandra-Stress OUTPUT. Error: %s" % str(e))


def check_user_queries(data_profile):
    """
    Check if 'user' queries are defined in YAML Profile.
    :param data_profile: .yaml profile
    :return: True if custom user queries are defined in profile, otherwise, False
    """
    # TODO: Analyze 'profile' and set 'user_queries'
    return False


def run(argv):
    """
        Cassandra Stress Client Exec Entry
    """
    l.info("Starting Cassandra Stress Client.")
    user_queries = False

    # Parse Inputs
    if len(argv) >= 6:
        ops_count = argv[1]             # number of Operations (e.g., n=1000000 insert/read one million rows)
        client_count = argv[2]          # client count (client threads)
        cluster_ips = argv[3]           # C*-Cluster IPs
        duration = argv[4]
        consistency_level = argv[5]     # consistency level, default='LOCAL_ONE'
    if len(argv) >= 7:
        stress_profile = argv[6]        # (optional) .yaml profile (defines data model & queries)
        user_queries = check_user_queries(stress_profile)

    # Initialize 'run_data'
    run_data = {'start': False,
                'stats': {'write': {},
                          'read': {},
                          'msg_cnt': ops_count},
                'test_status': 'stopped'}
    client_metrics = {'ops_count': ops_count}

    # Start HDaemon Reply Server (background process to control test & collect stats)
    client_rep_port = os.environ.get('PORT0')
    l.info("Starting Cassandra Stress Client REP server at port [%s]", client_rep_port)
    hd = HDCStressRepSrv(client_rep_port, run_data, client_metrics)
    hd.run()

    while True:
        if not hd.run_data['start']:
            l.debug("Cassandra Client WAITING FOR SIGNAL...")
            time.sleep(1)
            continue
        l.info("START SIGNAL received. Cassandra Client initiating Stress Test...")

        process = psutil.Process()
        hd.run_data['stats']['write'] = {'net:start': json.dumps(psutil.net_io_counters()),
                                         'cpu:start': json.dumps(process.cpu_times()),
                                         'mem:start': json.dumps(process.memory_info()),
                                         'time:start': json.dumps(time.time())
                                        }

        # The cluster must be first populated by a 'write' test
        base_cmd = 'cassandra-stress %s duration=%sm -rate threads=%s -node %s'
        write_cmd = base_cmd % ('write', duration, client_count,
                                cluster_ips)

        # Initiate Subprocess Call (WRITE OPERATION)
        l.info('Execute command: %s' % (write_cmd))
        stress_process = subprocess.Popen(write_cmd, stdout=subprocess.PIPE,
                                          stderr=subprocess.PIPE, shell=True, preexec_fn=os.setsid)
        stdout_w, stderr_w = stress_process.communicate()
        cmd_status_w = stress_process.returncode
        if cmd_status_w != 0:
            l.error('Error while running Cassandra-Stress WRITE Operation. Return Code: %s' % (cmd_status_w))
        l.debug('Output of Cassandra-Stress Test WRITE operation: %s' % (stdout_w))
        l.debug('stderr of Cassandra-Stress Test WRITE operation: %s' % (stderr_w))

        # Write stats to 'run_data'
        hd.run_data['stats']['write']['time:end'] = json.dumps(time.time())
        hd.run_data['stats']['write']['net:end'] = json.dumps(psutil.net_io_counters())
        hd.run_data['stats']['write']['cpu:end'] = json.dumps(process.cpu_times())
        hd.run_data['stats']['write']['mem:end'] = json.dumps(process.memory_info())
        parse_results(stdout_w, hd.run_data['stats']['write'])
        l.debug("Updated RUN_DATA: \n%s" % pformat(hd.run_data))

        # Initiate Subprocess Call (READ/QUERY OPERATION)
        if not user_queries:
            query_cmd = base_cmd % ('read', duration, client_count,
                                    cluster_ips)
        else:
            query_cmd = base_cmd % ('user', duration, client_count,
                                    cluster_ips)
            query_cmd += 'profile=%s' % (stress_profile)

        hd.run_data['stats']['read'] = {}
        q_start_time = time.time()
        l.debug('Execute command: %s' % (query_cmd))
        stress_process = subprocess.Popen(query_cmd, stdout=subprocess.PIPE,
                                          stderr=subprocess.PIPE, shell=True, preexec_fn=os.setsid)
        stdout_q, stderr_q = stress_process.communicate()
        cmd_status_q = stress_process.returncode
        if cmd_status_q != 0:
            l.error('Error while running Cassandra-Stress READ Operation. Return Code: %s' % (cmd_status_q))
        l.debug('Output of Cassandra-Stress Test READ operation: %s' % (stdout_q))
        l.debug('stderr of Cassandra-Stress Test READ operation: %s' % (stderr_q))

        # Write stats to 'run_data'
        hd.run_data['stats']['read']['time:start'] = json.dumps(q_start_time)
        hd.run_data['stats']['read']['time:end'] = json.dumps(time.time())
        hd.run_data['stats']['read']['net:end'] = json.dumps(psutil.net_io_counters())
        hd.run_data['stats']['read']['cpu:end'] = json.dumps(process.cpu_times())
        hd.run_data['stats']['read']['mem:end'] = json.dumps(process.memory_info())
        parse_results(stdout_q, hd.run_data['stats']['read'])
        hd.run_data['test_status'] = 'stopping'
        hd.run_data['start'] = False
        hd.run_data['msg_cnt'] = ops_count
        l.info('Cassandra Stress Test COMPLETED.')
        break

if __name__ == "__main__":
    run(sys.argv)
