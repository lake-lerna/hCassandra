
# hCassandra runTests

## The Basics

### Objective

   This test aims to **automate**:
   
   (1) The execution of the Hydra Cassandra Stress Test (hCassandra) for increasing client load.
   (2) The generation of a full-report containing performance results in the form of tables and graphs. 
   
   To this end, tests are run for different client loads (defined by the user), i.e., increasing the number of clients writing and reading to the database.

### Customizing the Test

   Modify **total_num_clients** to change the number of clients per run and **total_ops_count** for modifyng the total number of operations per run.
   
   Current tests have been run for a maximum of **X** clients, a fixed number of 1,000,000 operations against a 3-node Cassandra Cluster (for further details on Software & Hardware specs please refer to the *Test Results/Specs* section.
   
### Useful HINTS for running the test

- If test has been previously executed and output is still shown, you can restart (delete former results) by selecting in the top menu Cell -> All Output -> Clear
- To run test, step on top of the code cells and press the 'run cell' button on the top menu.
- When RUN is finished, generate your own report by selecting FILE -> Download as -> Markdown (.md) (or any other preferred format.

---

## hCassandra Test 1: Fixed Number of Stress Clients (Debug Mode) 

---

The following test runs a SINGLE execution of the Cassandra Test for a fixed number of clients and operations. Runs in debug mode: showing logger info during execution. 


```python
!python ./src/hCassandra_test.py --cluster_ips='10.10.3.20,10.10.3.113,10.10.3.119' --total_client_count=10 --total_ops_count=100000
```

---

## hCassandra Test 2: Increasing the Number of stress clients (multiple runs)

---


**IMPORTANT**:

   If you want to change the number of clients and/or number of operations for your test, please set values to desired in the following section:



```python
# Define num Client(s) / Operation(s) 
# total_num_clients = [10, 20, 100, 500, 1000]
total_num_clients = [10, 50, 100, 500, 1000]
total_ops_count = [1000000]
cassandra_cluster_ips = '10.10.3.20,10.10.3.113,10.10.3.119'
```

Next functions are some 'util' functions aimed to ease result processing. 


```python
import json
import ast

def get_result(test_stdout):
    """This Function gets (filters) the Cassandra Test Results from stdout"""
    index_start = test_stdout.find('Cassandra Stress Results: \n')
    index_end = test_stdout.find('Calling Server shutdown')
    if index_start != -1:
        results = test_stdout[(index_start + len('Cassandra Stress Results: \n')):index_end]
        res_dict = ast.literal_eval(results)
        return res_dict
    else:
        return {}
```

The following block of code is the actual **EXECUTION OF THE CASSANDRA SCALE TESTS**. This may take a couple of minutes:


```python
import subprocess
import os
import json

hCassandra_results = dict()

print 'STARTING CASSANDRA STRESS TESTS \n'
# Execute hCassandra_test for given client_count
for idx1, clients in enumerate(total_num_clients):
    for idx2, ops in enumerate(total_ops_count):
        print ('Test (%s/%s) in progress.. Please wait until test is completed..' % ((len(total_ops_count) * idx1) + idx2 + 1,len(total_num_clients) * len(total_ops_count)))
        # Execute hCassandra_test.py (python script for hCassandra Scale Test)
        hcass_cmd = "python ./src/hCassandra_test.py --cluster_ips=%s --total_client_count=%s --total_ops_count=%s" % (cassandra_cluster_ips, clients, ops)
        stress_test = subprocess.Popen(hcass_cmd, stdout=subprocess.PIPE,
                                          stderr=subprocess.PIPE, shell=True, preexec_fn=os.setsid)
        stdout, stderr = stress_test.communicate()
        results_dict = get_result(stdout)
        if len(results_dict) <= 1:
            print ('There was an ERROR while attempting to parse stdout...')
            print 'STDOUT: %s' % stdout
            print 'STDERR: %s' % stderr
        if not str(clients) in hCassandra_results:
            hCassandra_results[str(clients)] = dict()
        hCassandra_results[str(clients)][str(ops)] = results_dict
        print 'Test SUCCESFULLY completed... \n'

print 'END OF TESTS:'
print 'ALL TESTS HAVE BEEN COMPLETED. PLEASE PROCEED TO GENERATE GRAPHS & TABLES WITH PERFORMANCE RESULTS.'
```

   ---
   
   Wait until RESULTS (**hCassandra_results**) are generated for all cases, and then execute the following blocks to generate (1) Tables with results (markdown compatible) and (2) Graphs
   
   The **END OF TEST** is indicated by a message. Please wait...
   
   ---

### RESULT PROCESSING & TABLE/ GRAPH GENERATION

Next, we reorder results per # of operations. In other words, for a fixed number of operations we show how performance changes when the number of clients increases. 


```python
class ListTable(list):
    """ Overridden list class which takes a 2-dimensional list of 
        the form [[1,2,3],[4,5,6]], and renders an HTML Table in 
        IPython Notebook. """
    
    def _repr_html_(self):
        html = ["<table>"]
        for row in self:
            html.append("<tr>")
            
            for col in row:
                html.append("<td>{0}</td>".format(col))
            
            html.append("</tr>")
        html.append("</table>")
        return ''.join(html)
```


```python
results_per_ops = dict()

# Table Format
header = [
            '# ops',
            '# Clients',
            'total_ops',
            'op/s',
            'pk/s',
            'med',
            '.95',
            '.99',
            'max',
            'max_ms',
            'sdv_ms',
            'op_time'
        ]

data_matrix_write = ListTable()
data_matrix_read = ListTable()

data_matrix_write.append(header)
data_matrix_read.append(header)

for ops in total_ops_count:
    results_per_ops[str(ops)] = dict()
    first = True
    for clients in total_num_clients:
        if str(clients) in hCassandra_results:
            res_dict = ast.literal_eval(hCassandra_results[str(clients)][str(ops)])
            results_per_ops[str(ops)][str(clients)] = res_dict
            ops_fixed = ""
            if first:
                ops_fixed = ops
            data_matrix_write.append([ops_fixed, clients, res_dict['write']['total ops'], res_dict['write']['op/s'], res_dict['write']['pk/s'], res_dict['write']['med'], res_dict['write']['.95'], res_dict['write']['.99'], res_dict['write']['max'], res_dict['write']['max_ms'], res_dict['write']['sdv_ms'], res_dict['write']['op_time']])
            data_matrix_read.append([ops_fixed, clients, res_dict['read']['total ops'], res_dict['read']['op/s'], res_dict['read']['pk/s'], res_dict['read']['med'], res_dict['read']['.95'], res_dict['read']['.99'], res_dict['read']['max'], res_dict['read']['max_ms'], res_dict['read']['sdv_ms'], res_dict['read']['op_time']])
            first = False
```

### Result Generation: Table Format

Next, results are displayed in a Table, following the markdown format. Please, copy this table into your readme.results to keep track of results between test executions.  



The next table represents the results for the **WRITE** Operations:

---

*Table 1. "Cassandra Performance over WRITE Operation."*


```python
data_matrix_write
```




<table><tr><td># ops</td><td># Clients</td><td>total_ops</td><td>op/s</td><td>pk/s</td><td>med</td><td>.95</td><td>.99</td><td>max</td><td>max_ms</td><td>sdv_ms</td><td>op_time</td></tr><tr><td>1000000</td><td>10</td><td>[1000000]</td><td>[15639]</td><td>[15639]</td><td>[0.6]</td><td>[0.8]</td><td>[1.0]</td><td>[125.2]</td><td>[]</td><td>[0.0]</td><td>[' 00:01:03']</td></tr><tr><td></td><td>50</td><td>[1000000, 1000000, 1000000, 1000000, 1000000]</td><td>[8515, 8777, 7208, 7183, 8720]</td><td>[8515, 8777, 7208, 7183, 8720]</td><td>[0.8, 0.8, 0.9, 0.9, 0.8]</td><td>[2.2, 2.2, 2.8, 2.9, 2.1]</td><td>[4.0, 4.0, 5.7, 6.2, 3.9]</td><td>[212.1, 211.4, 211.1, 212.9, 219.0]</td><td>[]</td><td>[0.0, 0.0, 0.0, 0.0, 0.0]</td><td>[' 00:01:57', ' 00:01:53', ' 00:02:18', ' 00:02:19', ' 00:01:54']</td></tr><tr><td></td><td>100</td><td>[1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000]</td><td>[5266, 5188, 5176, 5233, 5105, 5137, 5282, 5212, 5194, 5202]</td><td>[5266, 5188, 5176, 5233, 5105, 5137, 5282, 5212, 5194, 5202]</td><td>[1.1, 1.2, 1.2, 1.1, 1.2, 1.2, 1.1, 1.2, 1.2, 1.2]</td><td>[4.3, 4.3, 4.2, 4.4, 4.4, 4.3, 4.3, 4.3, 4.4, 4.2]</td><td>[8.2, 8.9, 8.2, 8.6, 8.4, 8.4, 8.2, 8.9, 9.0, 8.3]</td><td>[229.3, 229.1, 230.3, 228.4, 230.4, 233.6, 228.7, 229.2, 229.2, 235.6]</td><td>[]</td><td>[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]</td><td>[' 00:03:09', ' 00:03:12', ' 00:03:13', ' 00:03:11', ' 00:03:15', ' 00:03:14', ' 00:03:09', ' 00:03:11', ' 00:03:12', ' 00:03:12']</td></tr><tr><td></td><td>500</td><td>[1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 999994, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 999999, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000]</td><td>[1340, 1269, 1249, 1230, 1294, 1087, 1101, 1057, 1275, 1085, 1261, 1094, 1143, 1273, 1288, 1252, 1278, 1084, 1287, 1299, 1114, 1292, 1072, 1269, 1069, 1315, 1242, 1258, 1280, 1252, 1299, 1255, 1261, 1274, 1082, 1276, 1064, 1345, 1291, 1099, 1068, 1051, 1299, 1332, 1076, 1331, 1273, 1086, 1246, 1234]</td><td>[1340, 1269, 1249, 1230, 1294, 1087, 1101, 1057, 1275, 1085, 1261, 1094, 1143, 1273, 1288, 1252, 1278, 1084, 1287, 1299, 1114, 1292, 1072, 1269, 1069, 1315, 1242, 1258, 1280, 1252, 1299, 1255, 1261, 1274, 1082, 1276, 1064, 1345, 1291, 1099, 1068, 1051, 1299, 1332, 1076, 1331, 1273, 1086, 1246, 1234]</td><td>[2.4, 2.4, 2.5, 2.5, 2.2, 3.3, 3.2, 3.4, 2.3, 3.3, 2.4, 3.3, 3.1, 2.4, 2.4, 2.5, 2.3, 3.3, 2.3, 2.4, 3.3, 2.2, 3.3, 2.5, 3.3, 2.3, 2.5, 2.3, 2.4, 2.4, 2.4, 2.4, 2.4, 2.4, 3.3, 2.3, 3.3, 2.2, 2.3, 3.1, 3.3, 3.3, 2.3, 2.4, 3.4, 2.2, 2.4, 3.2, 2.4, 2.5]</td><td>[24.3, 26.4, 27.7, 27.7, 26.0, 29.2, 29.1, 30.4, 26.5, 30.0, 26.3, 29.4, 27.9, 26.7, 26.0, 27.9, 27.0, 29.9, 26.6, 25.6, 29.0, 26.6, 30.8, 27.3, 29.6, 25.7, 27.4, 27.0, 26.5, 27.0, 26.8, 27.0, 27.1, 26.6, 30.3, 26.5, 30.1, 25.1, 26.6, 29.0, 30.0, 29.9, 26.3, 25.2, 30.0, 26.0, 27.0, 29.1, 26.7, 28.1]</td><td>[43.9, 46.7, 49.3, 49.0, 47.2, 50.9, 51.6, 52.4, 47.3, 51.6, 47.5, 51.7, 48.9, 46.6, 47.6, 49.2, 48.8, 52.2, 47.9, 46.1, 51.7, 48.4, 54.5, 49.4, 51.6, 46.2, 49.4, 48.0, 47.3, 49.8, 48.4, 48.5, 48.5, 48.6, 52.7, 48.5, 51.7, 46.2, 47.9, 50.4, 52.4, 52.2, 47.8, 47.6, 52.1, 46.7, 47.1, 50.4, 47.5, 50.5]</td><td>[271.8, 276.9, 271.0, 255.8, 270.3, 276.5, 269.8, 306.3, 300.6, 261.2, 275.4, 288.6, 279.2, 275.4, 271.1, 255.7, 270.2, 277.2, 272.4, 274.2, 261.2, 274.5, 302.5, 250.7, 303.4, 285.2, 276.4, 276.3, 303.1, 274.4, 269.6, 283.2, 302.6, 276.4, 289.3, 282.2, 290.0, 273.2, 260.1, 272.1, 303.1, 302.2, 250.7, 273.7, 270.6, 274.0, 276.3, 261.8, 272.6, 269.6]</td><td>[]</td><td>[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]</td><td>[' 00:12:26', ' 00:13:08', ' 00:13:20', ' 00:13:32', ' 00:12:52', ' 00:15:20', ' 00:15:08', ' 00:15:45', ' 00:13:04', ' 00:15:21', ' 00:13:13', ' 00:15:14', ' 00:14:34', ' 00:13:05', ' 00:12:56', ' 00:13:18', ' 00:13:02', ' 00:15:22', ' 00:12:56', ' 00:12:49', ' 00:14:58', ' 00:12:54', ' 00:15:33', ' 00:13:07', ' 00:15:35', ' 00:12:40', ' 00:13:25', ' 00:13:14', ' 00:13:01', ' 00:13:18', ' 00:12:49', ' 00:13:16', ' 00:13:13', ' 00:13:04', ' 00:15:24', ' 00:13:03', ' 00:15:40', ' 00:12:23', ' 00:12:54', ' 00:15:10', ' 00:15:36', ' 00:15:51', ' 00:12:49', ' 00:12:30', ' 00:15:28', ' 00:12:31', ' 00:13:05', ' 00:15:20', ' 00:13:22', ' 00:13:30']</td></tr><tr><td></td><td>1000</td><td>[1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 999996, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 999993, 1000000, 1000000, 1000000, 1000000, 1000000, 999991, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 999995, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 999995, 1000000, 1000000, 999976]</td><td>[614, 621, 638, 591, 628, 641, 624, 599, 648, 640, 647, 618, 620, 637, 633, 620, 638, 614, 629, 611, 627, 623, 616, 617, 660, 641, 604, 643, 639, 613, 610, 616, 636, 612, 642, 639, 647, 630, 646, 615, 660, 647, 613, 604, 628, 599, 651, 628, 616, 630, 614, 614, 650, 622, 609, 633, 610, 598, 637, 620, 631, 627, 618, 615, 609, 641, 618, 615, 617, 653, 650, 613, 630, 624, 628, 647, 636, 645, 630, 628, 647, 638, 619, 611, 617, 622, 597, 625, 617, 620, 623, 622, 634, 630, 607, 627, 641, 615, 636, 629]</td><td>[614, 621, 638, 591, 628, 641, 624, 599, 648, 640, 647, 618, 620, 637, 633, 620, 638, 614, 629, 611, 627, 623, 616, 617, 660, 641, 604, 643, 639, 613, 610, 616, 636, 612, 642, 639, 647, 630, 646, 615, 660, 647, 613, 604, 628, 599, 651, 628, 616, 630, 614, 614, 650, 622, 609, 633, 610, 598, 637, 620, 631, 627, 618, 615, 609, 641, 618, 615, 617, 653, 650, 613, 630, 624, 628, 647, 636, 645, 630, 628, 647, 638, 619, 611, 617, 622, 597, 625, 617, 620, 623, 622, 634, 630, 607, 627, 641, 615, 636, 629]</td><td>[3.8, 3.6, 3.9, 3.9, 3.6, 3.4, 3.6, 3.5, 3.1, 3.7, 3.3, 3.4, 3.7, 3.5, 3.6, 3.7, 3.5, 3.6, 3.7, 3.7, 3.4, 3.6, 3.6, 3.5, 3.4, 3.7, 3.5, 3.4, 3.6, 3.4, 3.6, 3.6, 3.8, 3.5, 3.5, 3.3, 3.7, 3.7, 3.7, 3.8, 3.5, 3.1, 3.9, 3.7, 3.2, 3.6, 3.4, 3.4, 3.6, 3.5, 3.7, 3.6, 3.3, 3.6, 3.3, 3.5, 3.5, 3.7, 3.3, 3.4, 3.7, 3.8, 3.8, 3.6, 3.5, 3.4, 3.3, 3.7, 3.6, 3.5, 3.4, 3.8, 3.6, 3.5, 3.5, 3.5, 3.6, 3.4, 3.6, 3.2, 3.3, 3.4, 3.8, 3.7, 3.9, 3.3, 3.8, 3.6, 3.7, 3.5, 3.8, 3.9, 3.7, 3.6, 3.5, 3.6, 3.9, 3.5, 3.7, 3.3]</td><td>[54.5, 53.7, 51.9, 56.3, 54.4, 52.4, 54.3, 56.6, 53.2, 51.9, 52.8, 54.4, 54.6, 54.4, 53.4, 53.5, 53.2, 54.6, 54.1, 54.9, 54.4, 54.9, 54.7, 54.7, 51.3, 52.7, 56.7, 52.7, 52.7, 55.8, 54.9, 54.6, 53.3, 55.1, 53.0, 53.9, 52.0, 52.6, 50.6, 54.3, 51.1, 53.5, 54.6, 55.3, 54.5, 55.9, 51.6, 53.9, 54.5, 53.0, 53.8, 54.9, 52.2, 54.6, 56.1, 53.4, 54.6, 55.4, 54.0, 54.1, 52.7, 52.9, 54.4, 54.8, 55.0, 53.4, 56.3, 55.4, 54.4, 51.4, 52.1, 54.9, 53.6, 54.0, 54.5, 52.2, 52.8, 52.2, 53.8, 54.8, 52.4, 53.5, 54.6, 55.6, 54.5, 54.8, 56.4, 55.3, 53.9, 55.2, 53.3, 53.6, 53.2, 53.6, 55.9, 53.0, 51.4, 54.9, 52.6, 53.9]</td><td>[82.7, 82.3, 78.7, 84.2, 82.5, 80.4, 81.3, 85.5, 81.2, 78.8, 78.3, 82.9, 82.9, 81.5, 80.6, 79.8, 79.5, 82.0, 83.1, 83.0, 82.1, 80.9, 83.2, 83.0, 77.0, 80.2, 84.9, 79.9, 78.6, 83.4, 83.1, 81.8, 79.0, 81.8, 80.6, 81.9, 77.9, 79.5, 77.3, 83.1, 78.4, 81.1, 81.9, 84.7, 81.3, 84.3, 78.0, 81.2, 83.0, 80.2, 82.0, 82.9, 79.8, 81.3, 85.3, 80.5, 82.1, 85.1, 81.5, 81.9, 79.5, 80.5, 81.3, 83.4, 83.0, 79.3, 84.2, 84.2, 80.5, 79.6, 78.9, 82.6, 81.4, 80.8, 81.9, 77.9, 78.8, 78.8, 81.1, 83.0, 80.5, 81.0, 81.5, 83.2, 81.6, 82.0, 84.7, 84.5, 81.3, 83.3, 79.8, 81.8, 81.0, 79.9, 84.3, 80.7, 78.4, 83.7, 79.7, 81.4]</td><td>[319.0, 321.6, 315.5, 320.1, 316.5, 310.2, 343.2, 327.3, 315.9, 315.7, 311.8, 321.5, 325.3, 312.4, 312.1, 395.7, 312.6, 382.6, 294.9, 320.3, 323.5, 313.1, 342.2, 306.0, 313.4, 340.4, 314.8, 318.4, 325.0, 395.8, 320.5, 323.0, 320.5, 394.3, 313.9, 320.0, 318.8, 314.4, 302.6, 319.8, 313.7, 318.8, 316.7, 317.6, 319.5, 315.6, 319.9, 318.1, 319.1, 306.1, 320.8, 319.0, 299.1, 309.5, 326.1, 313.1, 315.9, 322.4, 317.5, 311.6, 319.4, 317.5, 321.8, 323.9, 321.6, 317.4, 319.6, 347.8, 306.5, 343.2, 342.4, 317.5, 319.1, 342.3, 320.4, 316.6, 319.5, 315.2, 314.1, 319.8, 322.0, 318.9, 318.1, 396.0, 313.9, 316.8, 324.3, 393.0, 294.3, 324.7, 324.3, 301.4, 312.0, 320.0, 321.8, 307.7, 320.7, 334.8, 337.0, 313.8]</td><td>[]</td><td>[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]</td><td>[' 00:27:07', ' 00:26:49', ' 00:26:07', ' 00:28:11', ' 00:26:31', ' 00:26:00', ' 00:26:42', ' 00:27:50', ' 00:25:44', ' 00:26:01', ' 00:25:46', ' 00:26:56', ' 00:26:53', ' 00:26:10', ' 00:26:19', ' 00:26:53', ' 00:26:08', ' 00:27:09', ' 00:26:29', ' 00:27:16', ' 00:26:35', ' 00:26:45', ' 00:27:04', ' 00:26:59', ' 00:25:14', ' 00:26:00', ' 00:27:36', ' 00:25:54', ' 00:26:04', ' 00:27:11', ' 00:27:18', ' 00:27:02', ' 00:26:11', ' 00:27:14', ' 00:25:58', ' 00:26:05', ' 00:25:45', ' 00:26:28', ' 00:25:47', ' 00:27:04', ' 00:25:16', ' 00:25:46', ' 00:27:12', ' 00:27:34', ' 00:26:31', ' 00:27:49', ' 00:25:37', ' 00:26:31', ' 00:27:02', ' 00:26:26', ' 00:27:09', ' 00:27:07', ' 00:25:37', ' 00:26:47', ' 00:27:23', ' 00:26:19', ' 00:27:19', ' 00:27:52', ' 00:26:10', ' 00:26:53', ' 00:26:25', ' 00:26:35', ' 00:26:59', ' 00:27:06', ' 00:27:21', ' 00:25:59', ' 00:26:57', ' 00:27:05', ' 00:27:01', ' 00:25:31', ' 00:25:39', ' 00:27:11', ' 00:26:26', ' 00:26:41', ' 00:26:31', ' 00:25:45', ' 00:26:11', ' 00:25:50', ' 00:26:27', ' 00:26:31', ' 00:25:46', ' 00:26:08', ' 00:26:56', ' 00:27:15', ' 00:27:01', ' 00:26:47', ' 00:27:55', ' 00:26:40', ' 00:27:01', ' 00:26:54', ' 00:26:45', ' 00:26:48', ' 00:26:16', ' 00:26:27', ' 00:27:26', ' 00:26:34', ' 00:26:00', ' 00:27:07', ' 00:26:12', ' 00:26:29']</td></tr></table>



The next table represents the results for the **READ** Operations:

---

*Table 1. "Cassandra Performance over READ Operation."*


```python
data_matrix_read
```




<table><tr><td># ops</td><td># Clients</td><td>total_ops</td><td>op/s</td><td>pk/s</td><td>med</td><td>.95</td><td>.99</td><td>max</td><td>max_ms</td><td>sdv_ms</td><td>op_time</td></tr><tr><td>1000000</td><td>10</td><td>[1000000]</td><td>[15883]</td><td>[15883]</td><td>[0.6]</td><td>[0.8]</td><td>[1.0]</td><td>[46.6]</td><td>[]</td><td>[0.0]</td><td>[' 00:01:02']</td></tr><tr><td></td><td>50</td><td>[1000000, 1000000, 1000000, 1000000, 1000000]</td><td>[7202, 7204, 7973, 7809, 7101]</td><td>[7202, 7204, 7973, 7809, 7101]</td><td>[0.9, 0.9, 0.9, 0.9, 1.0]</td><td>[2.9, 3.0, 2.6, 2.8, 3.0]</td><td>[4.9, 5.4, 4.9, 5.1, 5.3]</td><td>[63.4, 59.2, 56.0, 62.5, 59.0]</td><td>[]</td><td>[0.0, 0.0, 0.0, 0.0, 0.0]</td><td>[' 00:02:18', ' 00:02:18', ' 00:02:05', ' 00:02:08', ' 00:02:20']</td></tr><tr><td></td><td>100</td><td>[1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000]</td><td>[4438, 4472, 4540, 4382, 4621, 4533, 4547, 4433, 4474, 4415]</td><td>[4438, 4472, 4540, 4382, 4621, 4533, 4547, 4433, 4474, 4415]</td><td>[1.3, 1.3, 1.3, 1.4, 1.2, 1.3, 1.3, 1.3, 1.3, 1.3]</td><td>[5.4, 5.5, 5.3, 5.5, 5.4, 5.4, 5.4, 5.3, 5.2, 5.3]</td><td>[11.7, 11.3, 11.2, 11.0, 10.9, 11.1, 11.2, 11.1, 10.6, 10.7]</td><td>[83.6, 91.7, 84.0, 79.5, 84.4, 81.3, 78.1, 87.8, 93.0, 84.5]</td><td>[]</td><td>[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]</td><td>[' 00:03:45', ' 00:03:43', ' 00:03:40', ' 00:03:48', ' 00:03:36', ' 00:03:40', ' 00:03:39', ' 00:03:45', ' 00:03:43', ' 00:03:46']</td></tr><tr><td></td><td>500</td><td>[1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000]</td><td>[971, 983, 993, 995, 956, 1081, 1080, 1107, 966, 1082, 976, 1078, 1049, 975, 963, 979, 974, 1081, 973, 955, 1059, 956, 1078, 976, 1093, 967, 999, 972, 988, 981, 971, 973, 990, 976, 1072, 956, 1100, 972, 959, 1072, 1110, 1116, 969, 954, 1086, 972, 973, 1076, 988, 1007]</td><td>[971, 983, 993, 995, 956, 1081, 1080, 1107, 966, 1082, 976, 1078, 1049, 975, 963, 979, 974, 1081, 973, 955, 1059, 956, 1078, 976, 1093, 967, 999, 972, 988, 981, 971, 973, 990, 976, 1072, 956, 1100, 972, 959, 1072, 1110, 1116, 969, 954, 1086, 972, 973, 1076, 988, 1007]</td><td>[2.4, 2.2, 2.0, 2.1, 2.6, 2.0, 2.2, 2.3, 2.4, 2.2, 2.3, 2.0, 1.9, 2.5, 2.4, 2.4, 2.4, 2.4, 2.3, 2.5, 2.2, 2.5, 2.3, 2.3, 2.3, 2.4, 2.0, 2.3, 2.1, 2.3, 2.3, 2.3, 2.0, 2.3, 2.1, 2.7, 2.4, 2.4, 2.6, 2.1, 2.3, 2.2, 2.3, 2.5, 2.2, 2.4, 2.3, 2.3, 2.1, 1.8]</td><td>[37.4, 37.5, 36.9, 36.3, 37.4, 35.0, 35.2, 34.5, 36.1, 35.1, 36.3, 35.2, 35.8, 36.6, 37.2, 36.7, 36.3, 34.8, 37.3, 36.8, 35.3, 37.1, 34.8, 35.5, 34.5, 37.0, 37.1, 37.1, 37.3, 36.8, 36.8, 37.1, 37.0, 36.5, 35.3, 36.5, 34.3, 36.4, 36.8, 35.2, 33.4, 34.5, 37.4, 37.1, 34.7, 36.9, 37.3, 34.7, 37.1, 36.4]</td><td>[58.8, 58.5, 58.0, 58.6, 59.4, 54.8, 56.0, 56.2, 57.0, 56.0, 58.1, 57.0, 56.8, 57.5, 58.0, 57.1, 57.5, 55.8, 58.7, 58.2, 57.5, 58.2, 56.0, 56.3, 55.8, 58.1, 58.2, 58.2, 58.4, 57.7, 57.6, 58.1, 58.2, 58.5, 56.3, 58.1, 55.8, 56.7, 58.4, 56.8, 55.1, 56.6, 59.2, 59.1, 56.5, 57.8, 58.4, 56.6, 59.0, 57.1]</td><td>[237.8, 191.3, 180.0, 180.8, 188.3, 184.2, 159.7, 207.1, 189.9, 436.2, 195.4, 199.9, 187.1, 190.8, 245.4, 196.1, 261.2, 176.6, 189.3, 245.1, 178.7, 181.3, 178.8, 176.3, 175.0, 310.0, 220.8, 193.9, 191.3, 182.8, 189.7, 191.2, 212.0, 188.8, 163.7, 240.2, 180.0, 182.1, 178.2, 210.2, 171.0, 232.0, 195.6, 179.8, 167.5, 183.8, 196.4, 212.0, 201.9, 167.7]</td><td>[]</td><td>[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]</td><td>[' 00:17:09', ' 00:16:57', ' 00:16:47', ' 00:16:45', ' 00:17:26', ' 00:15:25', ' 00:15:26', ' 00:15:03', ' 00:17:14', ' 00:15:24', ' 00:17:04', ' 00:15:27', ' 00:15:53', ' 00:17:05', ' 00:17:18', ' 00:17:01', ' 00:17:07', ' 00:15:25', ' 00:17:07', ' 00:17:26', ' 00:15:43', ' 00:17:25', ' 00:15:27', ' 00:17:04', ' 00:15:14', ' 00:17:13', ' 00:16:40', ' 00:17:08', ' 00:16:51', ' 00:16:59', ' 00:17:10', ' 00:17:07', ' 00:16:50', ' 00:17:04', ' 00:15:32', ' 00:17:26', ' 00:15:08', ' 00:17:08', ' 00:17:22', ' 00:15:32', ' 00:15:01', ' 00:14:56', ' 00:17:12', ' 00:17:28', ' 00:15:20', ' 00:17:09', ' 00:17:07', ' 00:15:29', ' 00:16:52', ' 00:16:32']</td></tr><tr><td></td><td>1000</td><td>[1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 999993, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 999992, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 999999, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 999982, 1000000, 999996, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 999315, 1000000, 1000000, 1000000]</td><td>[518, 523, 521, 537, 518, 521, 526, 527, 515, 527, 519, 520, 519, 514, 510, 517, 515, 524, 512, 525, 513, 513, 516, 521, 505, 519, 534, 515, 504, 522, 526, 520, 509, 527, 508, 516, 519, 507, 506, 519, 509, 527, 515, 528, 515, 529, 511, 521, 520, 510, 521, 519, 498, 521, 523, 519, 525, 535, 506, 523, 513, 520, 519, 521, 522, 522, 521, 523, 522, 512, 507, 539, 513, 514, 514, 515, 512, 518, 510, 512, 498, 529, 527, 520, 520, 518, 537, 514, 520, 520, 520, 520, 510, 506, 527, 509, 514, 520, 510, 524]</td><td>[518, 523, 521, 537, 518, 521, 526, 527, 515, 527, 519, 520, 519, 514, 510, 517, 515, 524, 512, 525, 513, 513, 516, 521, 505, 519, 534, 515, 504, 522, 526, 520, 509, 527, 508, 516, 519, 507, 506, 519, 509, 527, 515, 528, 515, 529, 511, 521, 520, 510, 521, 519, 498, 521, 523, 519, 525, 535, 506, 523, 513, 520, 519, 521, 522, 522, 521, 523, 522, 512, 507, 539, 513, 514, 514, 515, 512, 518, 510, 512, 498, 529, 527, 520, 520, 518, 537, 514, 520, 520, 520, 520, 510, 506, 527, 509, 514, 520, 510, 524]</td><td>[4.0, 3.9, 3.7, 3.5, 3.3, 4.6, 4.0, 3.4, 3.8, 3.5, 3.4, 4.1, 3.5, 3.9, 4.1, 4.2, 4.4, 3.6, 4.4, 3.5, 4.1, 4.0, 3.5, 4.4, 3.6, 3.6, 3.3, 3.4, 4.0, 3.9, 3.5, 4.4, 4.1, 3.6, 3.7, 3.8, 3.6, 4.2, 4.6, 4.0, 3.9, 3.5, 3.5, 3.8, 4.4, 3.7, 3.9, 4.1, 3.8, 4.1, 3.9, 3.8, 4.6, 3.2, 3.3, 3.4, 3.9, 3.8, 4.3, 3.6, 3.9, 3.7, 4.0, 3.9, 3.8, 3.2, 3.9, 3.6, 3.5, 3.8, 4.3, 3.1, 4.0, 3.9, 4.1, 3.7, 3.9, 3.6, 4.5, 4.6, 4.8, 3.4, 3.2, 4.1, 3.8, 3.6, 3.5, 4.0, 4.2, 4.0, 3.6, 3.4, 4.1, 3.9, 3.7, 4.0, 3.4, 4.0, 3.5, 3.6]</td><td>[63.8, 62.5, 63.0, 63.2, 64.4, 62.4, 63.2, 63.4, 63.5, 62.6, 64.2, 62.6, 63.4, 64.2, 64.5, 63.5, 62.4, 63.6, 63.8, 65.1, 64.8, 64.0, 66.3, 62.3, 66.6, 62.9, 62.7, 63.9, 64.7, 62.7, 63.3, 63.5, 65.2, 63.1, 65.7, 64.0, 63.5, 65.3, 63.5, 63.7, 64.3, 62.3, 65.2, 64.0, 63.4, 65.3, 63.6, 62.1, 64.8, 64.5, 63.7, 63.8, 64.6, 64.3, 64.1, 63.5, 63.5, 63.6, 64.7, 63.0, 63.8, 63.3, 64.2, 63.5, 63.7, 64.2, 63.6, 63.3, 64.1, 63.6, 64.1, 62.7, 63.9, 65.2, 64.2, 63.2, 64.1, 64.0, 62.9, 62.9, 65.3, 63.0, 63.5, 64.7, 63.0, 63.4, 65.3, 64.3, 63.6, 63.3, 64.0, 64.3, 63.6, 64.7, 63.7, 64.3, 65.0, 64.3, 65.3, 62.6]</td><td>[89.9, 89.4, 90.3, 90.3, 90.4, 88.0, 89.7, 89.6, 90.1, 87.9, 90.7, 89.5, 88.7, 90.4, 91.9, 90.9, 88.9, 89.7, 92.1, 91.4, 93.1, 90.9, 93.4, 89.6, 92.4, 89.5, 89.3, 91.4, 93.0, 89.2, 89.5, 90.3, 91.3, 89.2, 92.2, 91.0, 89.5, 91.5, 90.1, 90.8, 90.4, 89.4, 92.8, 91.2, 89.1, 92.2, 90.2, 88.4, 92.2, 91.0, 90.6, 90.1, 91.0, 92.0, 90.5, 89.3, 90.4, 90.9, 92.3, 89.8, 90.9, 88.7, 90.4, 89.7, 89.1, 90.3, 90.4, 89.5, 90.3, 90.8, 89.1, 89.8, 91.1, 92.2, 90.8, 88.6, 90.9, 89.6, 88.9, 90.0, 93.8, 88.5, 89.4, 91.6, 88.9, 91.1, 92.8, 91.2, 90.2, 89.5, 90.2, 90.6, 89.9, 91.1, 89.3, 91.0, 92.0, 91.6, 92.6, 88.1]</td><td>[235.4, 214.5, 222.7, 237.2, 215.5, 210.8, 232.3, 240.3, 215.8, 217.6, 230.1, 237.6, 228.6, 233.7, 231.1, 232.1, 244.1, 230.3, 251.9, 256.3, 215.2, 231.6, 249.8, 226.5, 237.7, 225.0, 220.6, 231.6, 211.8, 255.7, 238.2, 227.0, 210.4, 223.6, 233.9, 223.6, 231.5, 221.2, 241.4, 221.5, 216.9, 247.1, 240.4, 226.4, 221.9, 231.7, 231.9, 230.7, 228.4, 232.0, 231.7, 252.1, 239.4, 219.3, 222.3, 232.7, 226.3, 213.7, 212.0, 246.9, 220.5, 229.7, 238.2, 231.1, 231.7, 211.7, 236.6, 228.9, 216.4, 241.2, 215.3, 210.7, 214.7, 231.5, 239.0, 231.5, 229.0, 221.6, 234.7, 212.7, 218.5, 231.4, 219.2, 232.1, 231.4, 244.5, 212.1, 229.3, 227.4, 234.4, 231.6, 210.3, 215.8, 244.4, 214.9, 231.3, 224.6, 199.3, 230.2, 220.4]</td><td>[]</td><td>[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]</td><td>[' 00:32:09', ' 00:31:52', ' 00:31:58', ' 00:31:01', ' 00:32:09', ' 00:31:59', ' 00:31:41', ' 00:31:37', ' 00:32:23', ' 00:31:35', ' 00:32:08', ' 00:32:01', ' 00:32:04', ' 00:32:24', ' 00:32:41', ' 00:32:14', ' 00:32:23', ' 00:31:48', ' 00:32:31', ' 00:31:44', ' 00:32:28', ' 00:32:30', ' 00:32:16', ' 00:32:00', ' 00:33:00', ' 00:32:06', ' 00:31:11', ' 00:32:22', ' 00:33:05', ' 00:31:57', ' 00:31:39', ' 00:32:04', ' 00:32:45', ' 00:31:37', ' 00:32:50', ' 00:32:17', ' 00:32:06', ' 00:32:51', ' 00:32:56', ' 00:32:06', ' 00:32:44', ' 00:31:35', ' 00:32:22', ' 00:31:33', ' 00:32:21', ' 00:31:30', ' 00:32:36', ' 00:31:58', ' 00:32:01', ' 00:32:42', ' 00:31:57', ' 00:32:07', ' 00:33:27', ' 00:31:58', ' 00:31:53', ' 00:32:06', ' 00:31:45', ' 00:31:10', ' 00:32:55', ' 00:31:50', ' 00:32:29', ' 00:32:03', ' 00:32:06', ' 00:31:59', ' 00:31:54', ' 00:31:54', ' 00:32:00', ' 00:31:53', ' 00:31:55', ' 00:32:32', ' 00:32:50', ' 00:30:54', ' 00:32:29', ' 00:32:25', ' 00:32:27', ' 00:32:23', ' 00:32:32', ' 00:32:10', ' 00:32:42', ' 00:32:34', ' 00:33:29', ' 00:31:30', ' 00:31:36', ' 00:32:03', ' 00:32:04', ' 00:32:10', ' 00:31:03', ' 00:32:26', ' 00:32:04', ' 00:32:04', ' 00:32:02', ' 00:32:01', ' 00:32:41', ' 00:32:55', ' 00:31:35', ' 00:32:44', ' 00:32:22', ' 00:32:04', ' 00:32:40', ' 00:31:46']</td></tr></table>



### Result Generation: Graphs

Next, results are displayed in Graphs. 

--- 

**IMPORTANT**

Please, MODIFY the graphs name in order to avoid OVERWRITING previous results.



---


```python
ops_second_graph_filename = "hCassandra_ops_sec_002"
median_latency_graph_filename = "hCassandra_med_002"
```


```python
import plotly.plotly as py
from plotly.graph_objs import *
import operator
import numpy

data_matrix = [['# ops', '# Clients', 'total_ops', 'op/s', 'pk/s', 'med', '.95', '.99', 'max', 'max_ms', 'sdv_ms', 'op_time']]


traces_plot1 = []
traces_plot2 = []

# For each trace = client count
for ops_count, tests_per_trace in results_per_ops.iteritems():
    
    total_ops = []
    op_s = []
    op_s_r = []
    pk_s = []
    med = []
    med_r = []
    p95 = []
    p99 = []
    max_lat = []
    max_ms = []
    sdv_ms = []
    op_time = []
    
    for num_clients, res_dict in tests_per_trace.iteritems():
        op_s.append(sum((ops for ops in res_dict['write']['op/s'])))
        med.append(numpy.median(res_dict['write']['med']))
        op_s_r.append(sum((ops for ops in res_dict['read']['op/s'])))
        med_r.append(numpy.median(res_dict['read']['med']))
        # Un-Comment for any other feature you want to depict...
        
        #total_ops.append(sum((ops for ops in res_dict['write']['total ops'])))
        #pk_s.append(res_dict['write']['pk/s'])
        #p95.append(res_dict['write']['.95'])
        #p99.append(res_dict['write']['.99'])
        #max_lat.append(res_dict['write']['max'])
        #max_ms.append(res_dict['write']['max_ms'])
        #sdv_ms.append(res_dict['write']['sdv_ms'])
        #op_time.append(res_dict['write']['op_time'])
        
        
    trace_plot1 = Scatter(
          x=total_num_clients,
          y=op_s, 
          mode = 'lines+markers',
          name = 'ops_count = ' + str(ops_count) + '[WRITE]',
          line=dict(
            shape='spline'
            )
        )
    
    trace_plot2 = Scatter(
          x=total_num_clients,
          y=op_s_r, 
          mode = 'lines+markers',
          name = 'ops_count = ' + str(ops_count) + '[READ]',
          line=dict(
            shape='spline'
            )
        )
        
    trace_plot3 = Scatter(
          x=total_num_clients,
          y=med, 
          mode = 'lines+markers',
          name = 'ops_count = ' + str(ops_count) + '[WRITE]', 
          line=dict(
            shape='spline'
            )
        )

    trace_plot4 = Scatter(
          x=total_num_clients,
          y=med_r, 
          mode = 'lines+markers',
          name = 'ops_count = ' + str(ops_count) + '[READ]', 
          line=dict(
            shape='spline'
            )
        )
    
    traces_plot1.append(trace_plot1)
    traces_plot1.append(trace_plot2)
    traces_plot2.append(trace_plot3)
    traces_plot2.append(trace_plot4)

```

### Result Generation: operations per second vs. client count

The following graph illustrates how, the number of operations per second changes while the number of clients increases 


```python
data = Data(traces_plot1)
# Edit the layout
layout = dict(title = 'op/s vs. # Clients',
              xaxis = dict(title = '# clients'),
              yaxis = dict(title = 'op/s'),
              )

# Plot and embed in notebook
fig = dict(data=data, layout=layout)
py.iplot(fig, filename = ops_second_graph_filename)
```

    /home/annyz/venv/local/lib/python2.7/site-packages/requests/packages/urllib3/util/ssl_.py:122: InsecurePlatformWarning:
    
    A true SSLContext object is not available. This prevents urllib3 from configuring SSL appropriately and may cause certain SSL connections to fail. You can upgrade to a newer version of Python to solve this. For more information, see https://urllib3.readthedocs.org/en/latest/security.html#insecureplatformwarning.
    

<div>
    <a href="https://plot.ly/~anny.martinez/61/" target="_blank" title="op/s vs. # Clients" style="display: block; text-align: center;"><img src="https://plot.ly/~anny.martinez/61.png" alt="op/s vs. # Clients" style="max-width: 100%;width: 1030px;"  width="1030" onerror="this.onerror=null;this.src='https://plot.ly/404.png';" /></a>
    <script data-plotly="anny.martinez:61"  src="https://plot.ly/embed.js" async></script>
</div>



### Result Generation: median latency vs. client count

The following graph illustrates median latency in miliseconds for each operation during that run as the number of clients increases. 


```python
data = Data(traces_plot2)
# Edit the layout
layout = dict(title = 'Median Latency vs. Client Count',
              xaxis = dict(title = '# Clients'),
              yaxis = dict(title = 'Median Latency [ms]'),
              )

# Plot and embed in notebook
fig = dict(data=data, layout=layout)
py.iplot(fig, filename = median_latency_graph_filename)
```

    /home/annyz/venv/local/lib/python2.7/site-packages/requests/packages/urllib3/util/ssl_.py:122: InsecurePlatformWarning:
    
    A true SSLContext object is not available. This prevents urllib3 from configuring SSL appropriately and may cause certain SSL connections to fail. You can upgrade to a newer version of Python to solve this. For more information, see https://urllib3.readthedocs.org/en/latest/security.html#insecureplatformwarning.
    


<div>
    <a href="https://plot.ly/~anny.martinez/63/" target="_blank" title="Median Latency vs. Client Count" style="display: block; text-align: center;"><img src="https://plot.ly/~anny.martinez/63.png" alt="Median Latency vs. Client Count" style="max-width: 100%;width: 1030px;"  width="1030" onerror="this.onerror=null;this.src='https://plot.ly/404.png';" /></a>
    <script data-plotly="anny.martinez:63"  src="https://plot.ly/embed.js" async></script>
</div>




```python

```
