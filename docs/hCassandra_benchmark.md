# Hydra Cassandra Scale Test

---

The **hCassandra** Scaling Test allows to spawn thousands of Cassandra clients in an effort to assess the performance of a Cassandra Cluster. The Cassandra Client strongly relies on the *cassandra-stress* tool---a Java-based testing utility which is natively provided along with Cassandra.

Next, we present the performance results for the hCassandra Scaling Test as the number of clients writing and reading to the database increases. We have run the tests for two scenarios both against a 3-Node Cluster. In the *first* scenario, we deployed 10 Mesos Slaves to host Cassandra stress clients, which will concurrently read/write into the 3-Node Cassandra Cluster (**Scale Test 1**). In the *second* scenario, clients are hosted by the same nodes that belong to the 3-Node Cassandra Cluster (**Scale Test 2**), in other words, Cassandra nodes are Mesos slaves at the same time. We certainly must consider the performance penalty that this second scenario may imply due to (for example) resource contention. However, it is an scenario of interest as it resembles relevant real use cases.

For each test we have measured the number of *operations per second* and *latency* as the number of clients increases, for *write* and *read* operations.  

**Note:** the results herein presented can be easily reproduced on any physical or cloud setup by executing the hCassandra_runtests.ipynb (found in the root of the hCassandra project).



## Scale Test 1: Stress clients hosted on EXTERNAL nodes

---

As previously stated this test was run over 10 slave nodes (on Google Cloud) to host multiple instances of the Cassandra Stress Client. Next, we provide software and hardware specifications of the tested scenario., for both the Cassandra Cluster and the Hydra Infra.

#### Software & Hardware Specs

The tests were executed on Google Cloud Servers, with the following specs:

- **Cassandra Cluster**

  - 3 Node Cluster, each with the following specs:
   - 32 vCPUs
   - RAM: 208 GB
   - Disk: 60 GB (SSD persistent disk) + local SSD Scratch Disk: 375 GB
   - OS: Ubuntu 14.04
   - (n1-highmem-32)

  - Cassandra + Cassandra-Tools Version: 3.0.6

- **Hydra Infra**

  - **MASTER**: 1 Server
   - 4 vCPUs
   - RAM: 15 GB
   - OS: Ubuntu 14.04
   - *NOTE*: For the performance tests maximum file open limit (ulimit) had to be increased for the Master Node.

  - **SLAVES**: 10 Servers (hosts to the cassandra stress clients)
    - 16 vCPUs
    - RAM: 60 GB
    - Disk: 60 GB
    - OS: Debian 3.16.7-ckt25-2


#### Performance Results

In this section we present performance metrics for both WRITE and READ operations, separately. The performance metrics include: total number of operations, operation rate (op/s), median latency, 95 and 99 percentile latency (i.e., 95% / 99% of the time the latency was less than the number displayed in the column.), max latency (ms) and operation time.

It is important to point out that each cassandra-stress client (process) is multi-threaded (total of 20 threads per process). As the number of clients increases we can notice that the rate of write operations fluctuates around 310000 ops/sec.


*Table 1. "Cassandra Performance over WRITE Operation - Scenario 1"*

<table><tr><td># Clients</td><td>total_ops</td><td>op/s</td><td>med</td><td>.95</td><td>.99</td><td>max</td><td>op_time</td></tr><tr><td>10</td><td>5610699</td><td>18702</td><td>0.4</td><td>0.8</td><td>1.3</td><td>203.7</td><td>00:05:00</td></tr><tr><td>100</td><td>88201737</td><td>147001</td><td>0.5</td><td>1.0</td><td>1.3</td><td>165.8</td><td>00:10:00</td></tr><tr><td>200</td><td>132617034</td><td>221027</td><td>0.7</td><td>1.455</td><td>2.819</td><td>202.8</td><td>00:10:00</td></tr><tr><td>400</td><td>172053376</td><td>286750</td><td>0.9</td><td>2.8</td><td>5.281</td><td>398.3</td><td>00:10:00</td></tr><tr><td>800</td><td>192706739</td><td>321178</td><td>1.3</td><td>5.305</td><td>9.9</td><td>10228.2</td><td>00:10:00</td></tr><tr><td>1600</td><td>198542059</td><td>330896</td><td>2.0</td><td>11.1</td><td>23.205</td><td>7952.4</td><td>00:10:00</td></tr><tr><td>3200</td><td>573617864</td><td>318781</td><td>3.5</td><td>19.7</td><td>45.005</td><td>12904.2</td><td>00:29:59</td></tr><tr><td>5000</td><td>580920345</td><td>322734</td><td>5.8</td><td>31.7</td><td>64.302</td><td>13338.4</td><td>00:30:00</td></tr><tr><td>6000</td><td>1137540200</td><td>316007</td><td>6.8</td><td>33.2</td><td>70.101</td><td>15280.4</td><td>01:00:00</td></tr><tr><td>7000</td><td>1146288352</td><td>318415</td><td>7.9</td><td>39.28</td><td>75.156</td><td>14498.7</td><td>01:00:00</td></tr><tr><td>8000</td><td>1141405644</td><td>317034</td><td>9.2</td><td>45.6</td><td>88.91</td><td>26445.9</td><td>00:59:59</td></tr><tr><td>9000</td><td>1492160316</td><td>310850</td><td>10.1</td><td>51.8</td><td>98.869</td><td>28970.3</td><td>01:20:00</td></tr><tr><td>10000</td><td>1518306852</td><td>316316</td><td>11.5</td><td>55.15</td><td>101.715</td><td>29907.5</td><td>01:20:00</td></tr></table>





The next table represents the results for the **READ** Operations:



*Table 2. "Cassandra Performance over READ Operation."*


<table><tr><td># Clients</td><td>total_ops</td><td>op/s</td><td>med</td><td>.95</td><td>.99</td><td>max</td><td>op_time</td></tr><tr><td>10</td><td>5602356</td><td>18674</td><td>0.4</td><td>0.8</td><td>1.5</td><td>70.2</td><td>5</td></tr><tr><td>100</td><td>83973752</td><td>139955</td><td>0.6</td><td>1.08</td><td>1.688</td><td>102.1</td><td>10</td></tr><tr><td>200</td><td>120327348</td><td>200544</td><td>0.8</td><td>1.755</td><td>2.782</td><td>50.1</td><td>10</td></tr><tr><td>400</td><td>146202779</td><td>243669</td><td>1.1</td><td>3.6</td><td>6.4</td><td>792.4</td><td>10</td></tr><tr><td>800</td><td>212690723</td><td>354484</td><td>1.3</td><td>6.3</td><td>12.0</td><td>210.2</td><td>10</td></tr><tr><td>1600</td><td>212281082</td><td>353797</td><td>2.3</td><td>12.6</td><td>27.205</td><td>139.6</td><td>10</td></tr><tr><td>3200</td><td>619437107</td><td>344125</td><td>4.0</td><td>27.505</td><td>46.7</td><td>659.6</td><td>30</td></tr><tr><td>5000</td><td>725438245</td><td>403026</td><td>5.1</td><td>39.6</td><td>65.351</td><td>2469.0</td><td>30</td></tr><tr><td>6000</td><td>1386394809</td><td>385114</td><td>7.9</td><td>43.5</td><td>73.2</td><td>3615.9</td><td>60</td></tr><tr><td>7000</td><td>1389277009</td><td>385907</td><td>3.7</td><td>61.9</td><td>94.4</td><td>4805.6</td><td>60</td></tr><tr><td>8000</td><td>1375211033</td><td>382008</td><td>10.3</td><td>58.15</td><td>89.2</td><td>4582.8</td><td>60</td></tr><tr><td>9000</td><td>1820464408</td><td>379262</td><td>8.2</td><td>66.9</td><td>98.838</td><td>3622.7</td><td>80</td></tr><tr><td>10000</td><td>2110372437</td><td>439654</td><td>11.6</td><td>58.93</td><td>90.526</td><td>26406.0</td><td>80</td></tr></table>



---

<h5 style="text-align: center;" markdown="1">*Figure 1. - Operations per Second vs Client Count (Scenario 1) - Line Graph*</h5>

<div>
    <a href="https://plot.ly/~anny.martinez/256/" target="_blank" title="op/s vs. # Clients" style="display: block; text-align: center;"><img src="https://plot.ly/~anny.martinez/256.png" alt="op/s vs. # Clients" style="max-width: 100%;width: 1139px;"  width="1139" onerror="this.onerror=null;this.src='https://plot.ly/404.png';" /></a>
    <script data-plotly="anny.martinez:256"  src="https://plot.ly/embed.js" async></script>
</div>


---

<h5 style="text-align: center;" markdown="1">*Figure 2. - Operations per Second vs Client Count (Scenario 1) - Bar Graph*</h5>

<div>
    <a href="https://plot.ly/~anny.martinez/258/" target="_blank" title="Ops/sec" style="display: block; text-align: center;"><img src="https://plot.ly/~anny.martinez/258.png" alt="Ops/sec" style="max-width: 100%;width: 1139px;"  width="1139" onerror="this.onerror=null;this.src='https://plot.ly/404.png';" /></a>
    <script data-plotly="anny.martinez:258"  src="https://plot.ly/embed.js" async></script>
</div>



---

<h5 style="text-align: center;" markdown="1">*Figure 3. - Latency vs Client Count (Scenario 1) - Line Graph*</h5>


<div>
    <a href="https://plot.ly/~anny.martinez/260/" target="_blank" title="Latency vs. Client Count" style="display: block; text-align: center;"><img src="https://plot.ly/~anny.martinez/260.png" alt="Latency vs. Client Count" style="max-width: 100%;width: 1139px;"  width="1139" onerror="this.onerror=null;this.src='https://plot.ly/404.png';" /></a>
    <script data-plotly="anny.martinez:260"  src="https://plot.ly/embed.js" async></script>
</div>



---

<h5 style="text-align: center;" markdown="1">*Figure 4. - Latency vs Client Count (Scenario 1) - Line Graph*</h5>


<div>
    <a href="https://plot.ly/~anny.martinez/262/" target="_blank" title="Latency" style="display: block; text-align: center;"><img src="https://plot.ly/~anny.martinez/262.png" alt="Latency" style="max-width: 100%;width: 1139px;"  width="1139" onerror="this.onerror=null;this.src='https://plot.ly/404.png';" /></a>
    <script data-plotly="anny.martinez:262"  src="https://plot.ly/embed.js" async></script>
</div>




## Scenario/Test 2: Stress clients hosted on CASSANDRA nodes

---

As previously stated this test runs the stress clients on the same nodes belonging to the Cassandra Cluster.  


#### Software & Hardware Specs


The tests were executed on Google Cloud Servers, with the following specs:

- **Cassandra Cluster**

  - 3 Node Cluster, each with the following specs:
   - 32 vCPUs
   - RAM: 208 GB
   - Disk: 60 GB (SSD persistent disk) + local SSD Scratch Disk: 375 GB
   - OS: Ubuntu 14.04
   - (n1-highmem-32)

  - Cassandra + Cassandra-Tools Version: 3.0.6

- **Hydra Cluster**

  - **MASTER**: 1 Server
   - 4 vCPUs
   - RAM: 15 GB
   - OS: Ubuntu 14.04

  - **SLAVES**: Cassandra Cluster Nodes (all 3)


#### Performance Results

  In this section we present performance metrics for both WRITE and READ operations, separately. The performance metrics include: total number of operations, operation rate (op/s), median latency, 95 and 99 percentile latency (i.e., 95% / 99% of the time the latency was less than the number displayed in the column.), max latency (ms) and operation time.

  It is important to point out that each cassandra-stress client (process) is multi-threaded (total of 20 threads per client). When comparing these results to previous wherein cassandra stress clients are run on dedicated servers, we notice that performance drops **50%** approximately due to resource contention.


*Table 3. "Cassandra Performance over WRITE Operation."*

<table><tr><td># Clients</td><td>total_ops</td><td>op/s</td><td>med</td><td>.95</td><td>.99</td><td>max</td><td>op_time</td></tr><tr><td>10</td><td>6691246</td><td>22304</td><td>0.4</td><td>0.6</td><td>0.8</td><td>166.5</td><td>00:05:00</td></tr><tr><td>100</td><td>63265931</td><td>105443</td><td>0.9</td><td>1.6</td><td>2.4</td><td>148.0</td><td>00:09:59</td></tr><tr><td>200</td><td>79812349</td><td>133020</td><td>1.1</td><td>3.1</td><td>5.291</td><td>178.9</td><td>00:09:59</td></tr><tr><td>400</td><td>89365204</td><td>148940</td><td>1.7</td><td>6.4</td><td>12.062</td><td>251.0</td><td>00:10:00</td></tr><tr><td>800</td><td>98738676</td><td>164558</td><td>2.9</td><td>12.105</td><td>20.561</td><td>231.4</td><td>00:09:59</td></tr><tr><td>1600</td><td>98825855</td><td>164708</td><td>5.1</td><td>26.71</td><td>45.254</td><td>2201.4</td><td>00:10:00</td></tr><tr><td>3200</td><td>296251663</td><td>164580</td><td>9.5</td><td>52.91</td><td>87.792</td><td>2601.5</td><td>00:30:00</td></tr><tr><td>5000</td><td>285984387</td><td>158861</td><td>12.8</td><td>91.3</td><td>145.457</td><td>1827.5</td><td>00:30:00</td></tr><tr><td>6000</td><td>560550496</td><td>155692</td><td>18.9</td><td>102.0</td><td>165.301</td><td>2413.6</td><td>00:59:59</td></tr><tr><td>7000</td><td>554087432</td><td>153884</td><td>14.9</td><td>137.2</td><td>205.651</td><td>3794.7</td><td>01:00:00</td></tr></table>


The next table represents the results for the **READ** Operations:


*Table 4. "Cassandra Performance over READ Operation."*

<table><tr><td># Clients</td><td>total_ops</td><td>op/s</td><td>med</td><td>.95</td><td>.99</td><td>max</td><td>op_time</td></tr><tr><td>10</td><td>6842755</td><td>22809</td><td>0.4</td><td>0.6</td><td>0.8</td><td>83.4</td><td>5</td></tr><tr><td>100</td><td>61405552</td><td>102343</td><td>0.9</td><td>1.78</td><td>2.596</td><td>104.0</td><td>10</td></tr><tr><td>200</td><td>74045140</td><td>123409</td><td>1.2</td><td>3.255</td><td>5.382</td><td>82.6</td><td>10</td></tr><tr><td>400</td><td>81409864</td><td>135680</td><td>1.8</td><td>7.505</td><td>15.981</td><td>166.0</td><td>10</td></tr><tr><td>800</td><td>86891992</td><td>144816</td><td>3.1</td><td>14.405</td><td>25.922</td><td>364.8</td><td>10</td></tr><tr><td>1600</td><td>97038821</td><td>161725</td><td>5.4</td><td>26.9</td><td>46.466</td><td>392.5</td><td>10</td></tr><tr><td>3200</td><td>264755153</td><td>147082</td><td>12.6</td><td>53.2</td><td>110.605</td><td>517.5</td><td>30</td></tr><tr><td>5000</td><td>279667855</td><td>155366</td><td>13.0</td><td>96.055</td><td>167.453</td><td>760.7</td><td>30</td></tr><tr><td>6000</td><td>505423863</td><td>140390</td><td>23.5</td><td>112.2</td><td>194.7</td><td>727.6</td><td>60</td></tr><tr><td>7000</td><td>489950706</td><td>136094</td><td>20.8</td><td>153.255</td><td>237.61</td><td>820.2</td><td>60</td></tr></table>


---

<h5 style="text-align: center;" markdown="1">*Figure 5. - Operations per Second vs Client Count (Scenario 2) - Line Graph*</h5>


<div>
    <a href="https://plot.ly/~anny.martinez/248/" target="_blank" title="op/s vs. # Clients" style="display: block; text-align: center;"><img src="https://plot.ly/~anny.martinez/248.png" alt="op/s vs. # Clients" style="max-width: 100%;width: 1139px;"  width="1139" onerror="this.onerror=null;this.src='https://plot.ly/404.png';" /></a>
    <script data-plotly="anny.martinez:248"  src="https://plot.ly/embed.js" async></script>
</div>


---

<h5 style="text-align: center;" markdown="1">*Figure 6. - Operations per Second vs Client Count (Scenario 2) - Bar Graph*</h5>

<div>
    <a href="https://plot.ly/~anny.martinez/250/" target="_blank" title="Ops/sec" style="display: block; text-align: center;"><img src="https://plot.ly/~anny.martinez/250.png" alt="Ops/sec" style="max-width: 100%;width: 1139px;"  width="1139" onerror="this.onerror=null;this.src='https://plot.ly/404.png';" /></a>
    <script data-plotly="anny.martinez:250"  src="https://plot.ly/embed.js" async></script>
</div>




---

<h5 style="text-align: center;" markdown="1">*Figure 7. - Latency vs Client Count (Scenario 2) - Line Graph*</h5>

<div>
    <a href="https://plot.ly/~anny.martinez/252/" target="_blank" title="Latency vs. Client Count" style="display: block; text-align: center;"><img src="https://plot.ly/~anny.martinez/252.png" alt="Latency vs. Client Count" style="max-width: 100%;width: 1139px;"  width="1139" onerror="this.onerror=null;this.src='https://plot.ly/404.png';" /></a>
    <script data-plotly="anny.martinez:252"  src="https://plot.ly/embed.js" async></script>
</div>



---

<h5 style="text-align: center;" markdown="1">*Figure 8. - Latency vs Client Count (Scenario 2) - Bar Graph*</h5>


<div>
    <a href="https://plot.ly/~anny.martinez/254/" target="_blank" title="Latency" style="display: block; text-align: center;"><img src="https://plot.ly/~anny.martinez/254.png" alt="Latency" style="max-width: 100%;width: 1139px;"  width="1139" onerror="this.onerror=null;this.src='https://plot.ly/404.png';" /></a>
    <script data-plotly="anny.martinez:254"  src="https://plot.ly/embed.js" async></script>
</div>







---
### Cassandra-Stress Tool READ Issue



When running **MULTIPLE** instances of the cassandra-stress tool with the 'default' settings, we have encountered an error when attempting to perform the READ operation.

These are the commands executed (for both, write and read operations), where the number of **threads** per process has been changed in an effort to determine a failing pattern:

```
# WRITE Operation
 cassandra-stress write duration=1m -rate threads=10 -node 10.10.0.71,10.10.0.45,10.10.0.61

# READ Operation
cassandra-stress read duration=1m -rate threads=10 -node 10.10.0.71,10.10.0.45,10.10.0.61

```

The error we find is the following:

**ERROR**:

```
java.io.IOException: Operation x0 on key(s) [33335030363730503230]: Data returned was not validated

	at org.apache.cassandra.stress.Operation.error(Operation.java:135)
	at org.apache.cassandra.stress.Operation.timeWithRetry(Operation.java:113)
	at org.apache.cassandra.stress.operations.predefined.CqlOperation.run(CqlOperation.java:98)
	at org.apache.cassandra.stress.operations.predefined.CqlOperation.run(CqlOperation.java:106)
	at org.apache.cassandra.stress.operations.predefined.CqlOperation.run(CqlOperation.java:258)
	at org.apache.cassandra.stress.StressAction$Consumer.run(StressAction.java:321)
java.io.IOException: Operation x0 on key(s) [4f4e374d4b5050333631]: Data returned was not validated
```

We first attempted to determine if the reading error was due to the number of threads per process. However, this did not convey to any pattern. We finally figured out that as the number of clients increased he duration of the test had to increase as well, otherwise the error was raised. The following table shows the duration in minutes we had to perform per test as a function of the number of clients in an effort to avoid hitting this error.

total_num_clients = [10, 100, 200, 400, 800, 1600, 3200, 5000, 6000, 7000, 8000, 9000, 10000]
total_ops_count = [1000000]
duration_array = [5, 10, 10, 10, 10, 10, 30, 30, 60, 60, 60, 80, 80]


*Table 5. "Cassandra-Stress Duration per Client Count to avoid READ error"*

| Duration [m]     | # Clients     |
| :-------| :-------------|
| 5       | 10            |
| 10      | 100           |
| 10      | 200           |
| 10      | 400           |
| 10      | 800           |
| 10      | 1600          |
| 30      | 3200          |
| 30      | 5000          |
| 60      | 6000          |
| 60      | 7000          |
| 60      | 8000          |
| 80      | 9000          |
| 80      | 10000         |



---

The following graphs depict he READ failure when the test duration is fixed to the same time (10m or 5m) for all client count.


<h5 style="text-align: center;" markdown="1">*Figure 5(2). - Operations per Second vs Client Count (Scenario 2) - Line Graph DURATION: 10m*</h5>


<div>
    <a href="https://plot.ly/~anny.martinez/238/" target="_blank" title="op/s vs. # Clients" style="display: block; text-align: center;"><img src="https://plot.ly/~anny.martinez/238.png" alt="op/s vs. # Clients" style="max-width: 100%;width: 1139px;"  width="1139" onerror="this.onerror=null;this.src='https://plot.ly/404.png';" /></a>
    <script data-plotly="anny.martinez:238"  src="https://plot.ly/embed.js" async></script>
</div>



<h5 style="text-align: center;" markdown="1">*Figure 5(3). - Operations per Second vs Client Count (Scenario 2) - Line Graph DURATION: 5m*</h5>


<div>
    <a href="https://plot.ly/~anny.martinez/230/" target="_blank" title="op/s vs. # Clients" style="display: block; text-align: center;"><img src="https://plot.ly/~anny.martinez/230.png" alt="op/s vs. # Clients" style="max-width: 100%;width: 1139px;"  width="1139" onerror="this.onerror=null;this.src='https://plot.ly/404.png';" /></a>
    <script data-plotly="anny.martinez:230"  src="https://plot.ly/embed.js" async></script>
</div>

---

<h5 style="text-align: center;" markdown="1">*Figure 6(2). - Operations per Second vs Client Count (Scenario 2) - Bar Graph DURATION:10m*</h5>

<div>
    <a href="https://plot.ly/~anny.martinez/240/" target="_blank" title="Ops/sec" style="display: block; text-align: center;"><img src="https://plot.ly/~anny.martinez/240.png" alt="Ops/sec" style="max-width: 100%;width: 1139px;"  width="1139" onerror="this.onerror=null;this.src='https://plot.ly/404.png';" /></a>
    <script data-plotly="anny.martinez:240"  src="https://plot.ly/embed.js" async></script>
</div>



<h5 style="text-align: center;" markdown="1">*Figure 6(3). - Operations per Second vs Client Count (Scenario 2) - Bar Graph DURATION:5m*</h5>

<div>
    <a href="https://plot.ly/~anny.martinez/232/" target="_blank" title="Ops/sec" style="display: block; text-align: center;"><img src="https://plot.ly/~anny.martinez/232.png" alt="Ops/sec" style="max-width: 100%;width: 1139px;"  width="1139" onerror="this.onerror=null;this.src='https://plot.ly/404.png';" /></a>
    <script data-plotly="anny.martinez:232"  src="https://plot.ly/embed.js" async></script>
</div>

---

<h5 style="text-align: center;" markdown="1">*Figure 7(2). - Latency vs Client Count (Scenario 2) - Line Graph DURATION:10m*</h5>


<div>
    <a href="https://plot.ly/~anny.martinez/242/" target="_blank" title="Latency vs. Client Count" style="display: block; text-align: center;"><img src="https://plot.ly/~anny.martinez/242.png" alt="Latency vs. Client Count" style="max-width: 100%;width: 1139px;"  width="1139" onerror="this.onerror=null;this.src='https://plot.ly/404.png';" /></a>
    <script data-plotly="anny.martinez:242"  src="https://plot.ly/embed.js" async></script>
</div>



<h5 style="text-align: center;" markdown="1">*Figure 7(3). - Latency vs Client Count (Scenario 2) - Line Graph DURATION:5m*</h5>


<div>
    <a href="https://plot.ly/~anny.martinez/234/" target="_blank" title="Latency vs. Client Count" style="display: block; text-align: center;"><img src="https://plot.ly/~anny.martinez/234.png" alt="Latency vs. Client Count" style="max-width: 100%;width: 1139px;"  width="1139" onerror="this.onerror=null;this.src='https://plot.ly/404.png';" /></a>
    <script data-plotly="anny.martinez:234"  src="https://plot.ly/embed.js" async></script>
</div>

---

<h5 style="text-align: center;" markdown="1">*Figure 8(2). - Latency vs Client Count (Scenario 2) - Bar Graph DURATION:10m*</h5>

<div>
    <a href="https://plot.ly/~anny.martinez/244/" target="_blank" title="Latency" style="display: block; text-align: center;"><img src="https://plot.ly/~anny.martinez/244.png" alt="Latency" style="max-width: 100%;width: 1139px;"  width="1139" onerror="this.onerror=null;this.src='https://plot.ly/404.png';" /></a>
    <script data-plotly="anny.martinez:244"  src="https://plot.ly/embed.js" async></script>
</div>



<h5 style="text-align: center;" markdown="1">*Figure 8(3). - Latency vs Client Count (Scenario 2) - Bar Graph DURATION:5m*</h5>

<div>
    <a href="https://plot.ly/~anny.martinez/236/" target="_blank" title="Latency" style="display: block; text-align: center;"><img src="https://plot.ly/~anny.martinez/236.png" alt="Latency" style="max-width: 100%;width: 1139px;"  width="1139" onerror="this.onerror=null;this.src='https://plot.ly/404.png';" /></a>
    <script data-plotly="anny.martinez:236"  src="https://plot.ly/embed.js" async></script>
</div>
