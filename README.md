
# Exploring MTA Turnstile Data
The Metropolitan Transportation Authority (MTA), which serves around 11 million passengers in New York State daily,  routinely publishes their Turnstile Data showing the number of entries and exits at each turnstile, per hour. In this notebook, we're going to explore that data and identify:

* How traffic at Grand Central Terminal varies over time
* The Stations with the highest commuter traffic
* The Stations with the lowest commuter traffic

![Turnstile](https://github.com/lucasastorian/MTA-Turnstile-Analysis/blob/master/images/turnstile.jpg)

# Data Cleansing and Preprocessing
The first step is importing the required python libraries, and helper functions into the notebook. Turnstile data from the specified date range is directly downloaded from the MTA website, and subjected to various preprocessing, including
* Stripping leading and trailing spaces from the column names, and alphanumeric columns
* Creating a DateTime column
* Disaggregating the entries and exits, which are recorded cumulatively
* Dropping rows with outliers or NaN values
* Adding station coordinates queried using the Google Maps API

```python
import datetime
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# import local helper functions
from import_data import import_data
from preprocessing import cleanse_data
from utils import weekday_weekend_traffic_differences
```


```python
# set display options
pd.set_option('display.max_columns', 30)
pd.set_option('display.max_rows', 500)
plt.rcParams["figure.figsize"] = (16,8)
```


```python
# The import_data function downloads data from the date range directly from the MTA Website.
# You can replace the start_date and end_date with any date range.
start_date = datetime.datetime(2019, 6, 16)
end_date = datetime.datetime(2019, 7, 16)

turnstile_df = import_data(start_date, end_date)
```

```python
# I've written a couple of functions to do all the data cleansing,
# and feature engineering to declutter the notebook
turnstile_df = cleanse_data(turnstile_df)
```


```python
# entries and exits are no longer cumulative
turnstile_df.head(3)
```




<div>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>C/A</th>
      <th>UNIT</th>
      <th>SCP</th>
      <th>STATION</th>
      <th>LINENAME</th>
      <th>DIVISION</th>
      <th>DATE</th>
      <th>TIME</th>
      <th>DESC</th>
      <th>DATETIME</th>
      <th>TURNSTILE_ID</th>
      <th>ENTRIES</th>
      <th>EXITS</th>
      <th>WDAY</th>
      <th>WEEKDAY</th>
      <th>WEEK</th>
      <th>HOUR</th>
      <th>LATITUDE</th>
      <th>LONGITUDE</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>A002</td>
      <td>R051</td>
      <td>02-00-00</td>
      <td>59 ST</td>
      <td>NQR456W</td>
      <td>BMT</td>
      <td>06/15/2019</td>
      <td>04:00:00</td>
      <td>REGULAR</td>
      <td>2019-06-15 04:00:00</td>
      <td>A002_R051_02-00-00_59 ST</td>
      <td>29</td>
      <td>3</td>
      <td>5</td>
      <td>Saturday</td>
      <td>24</td>
      <td>4</td>
      <td>40.766185</td>
      <td>-73.977304</td>
    </tr>
    <tr>
      <th>1</th>
      <td>A002</td>
      <td>R051</td>
      <td>02-00-00</td>
      <td>59 ST</td>
      <td>NQR456W</td>
      <td>BMT</td>
      <td>06/15/2019</td>
      <td>08:00:00</td>
      <td>REGULAR</td>
      <td>2019-06-15 08:00:00</td>
      <td>A002_R051_02-00-00_59 ST</td>
      <td>33</td>
      <td>26</td>
      <td>5</td>
      <td>Saturday</td>
      <td>24</td>
      <td>8</td>
      <td>40.766185</td>
      <td>-73.977304</td>
    </tr>
    <tr>
      <th>2</th>
      <td>A002</td>
      <td>R051</td>
      <td>02-00-00</td>
      <td>59 ST</td>
      <td>NQR456W</td>
      <td>BMT</td>
      <td>06/15/2019</td>
      <td>12:00:00</td>
      <td>REGULAR</td>
      <td>2019-06-15 12:00:00</td>
      <td>A002_R051_02-00-00_59 ST</td>
      <td>99</td>
      <td>87</td>
      <td>5</td>
      <td>Saturday</td>
      <td>24</td>
      <td>12</td>
      <td>40.766185</td>
      <td>-73.977304</td>
    </tr>
  </tbody>
</table>
</div>

# Explore Traffic at a Grand Central Turnstile
After cleansing and preprocessing the turnstile data, we're first going to analyze the traffic at a single turnstile in Grand Central Terminal for a Week in June 2019. We're going to resample the data at four hour intervals so that it can be clearly graphed. In the carts below, one can see that
* Exits tend to peak in the morning, while entries peak in the afternoon and evenings
* There is significantly less traffic on the weekend than during the week
* The number of entries late on Friday is significantly less than during other week days, implying that commuters may go home relatively early
* There is a also a huge peak in exits around 9am on Monday


```python
# Show Data from a Turnstile at Grand Central Terminal for a Week in June 2019
date_mask = (turnstile_df["DATETIME"] > datetime.datetime(2019,6,17)) & \
            (turnstile_df["DATETIME"] < datetime.datetime(2019, 6,24)) & \
            (turnstile_df["TURNSTILE_ID"] == 'R236_R045_00-00-00_GRD CNTRL-42 ST')

grand_central_turnstile = turnstile_df.loc[date_mask]

# resample data at four hour intervals
new_gct = grand_central_turnstile.resample("4H", base=1, on="DATETIME", label="left").sum()
```



```python
sns.set()
days_of_the_week = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun", ""]
ax = new_gct.plot.line(y="ENTRIES", use_index=False)
new_gct.plot.line(ax=ax, y="EXITS", style='g', use_index=False)

ax.set_ylabel("Number of People", fontsize=15)
ax.set_xlabel("")
ax.set_title("A Turnstile's Traffic at a Grand Central Turnstile in Late June 2019", fontsize=18)
ax.set_xticklabels(days_of_the_week)
ax.set_xticks(np.linspace(0, 41, 8))
plt.yticks(fontsize=12)
plt.xticks(fontsize=13)
ax.legend(["Entries", "Exits"], prop={'size': 12});
```


![Turnstile Traffic](https://github.com/lucasastorian/MTA-Turnstile-Analysis/blob/master/charts/1.svg)



```python
sns.set()
xtick_times = "1:00 5:00 09:00 13:00 17:00 21:00".split()

# Traffic at a Turnstile on Monday
ax = new_gct[0:6].plot.line(y='ENTRIES', use_index=False)

# Traffic at a Turnstile Tuesday through Sunday
for x in range(6, 42, 6):
    new_gct[x:x+6].plot.line(ax=ax, y="ENTRIES", use_index=False)

ax.set_xticks(np.arange(6))
ax.set_xticklabels(xtick_times)
ax.legend(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
ax.set_xlabel("Time", fontsize=14)
ax.set_ylabel("Number of Entries", fontsize=14)
ax.set_title("Number of Entries at a Grand Central Turnstile Every Four Hours", fontsize=18)
plt.yticks(fontsize=11)
plt.xticks(fontsize=12);
```


![Turnstile Entries](https://github.com/lucasastorian/MTA-Turnstile-Analysis/blob/master/charts/2.svg)

```python
sns.set()
xtick_times = "1:00 5:00 09:00 13:00 17:00 21:00".split()

# Traffic at a Turnstile on Monday
ax = new_gct[0:6].plot.line(y='EXITS', use_index=False)

# Traffic at a Turnstile Tuesday through Sunday
for x in range(6, 42, 6):
    new_gct[x:x+6].plot.line(ax=ax, y="ENTRIES", use_index=False)

ax.set_xticks(np.arange(6))
ax.set_xticklabels(xtick_times)
ax.legend(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
ax.set_xlabel("Time", fontsize=15)
ax.set_ylabel("Number of Exits", fontsize=15)
ax.set_title("Number of Exits at a Grand Central Tirnstile Every Four Hours", fontsize=18)
plt.yticks(fontsize=13)
plt.xticks(fontsize=13);
```
![Turnstile Exits](https://github.com/lucasastorian/MTA-Turnstile-Analysis/blob/master/charts/10.svg)

# Explore Traffic Throughout Grand Central Terminal

Next, we aggregate all entries and exits for every turnstile in Grand Central Terminal for a week in June 2019.



```python
# Group all the Turnstiles in Grand Central Terminal for a Week in June 2019

grouped_turnstiles = turnstile_df.groupby(["STATION", "DATETIME"]).sum().reset_index()

mask = (grouped_turnstiles["DATETIME"] > datetime.datetime(2019,6,17)) \
& (grouped_turnstiles["DATETIME"] < datetime.datetime(2019, 6,24)) \
& (grouped_turnstiles["STATION"] == 'GRD CNTRL-42 ST')

gct_tirnstiles = grouped_turnstiles.loc[mask].resample('4H', base=1, on='DATETIME', label='left').sum()

```


```python
# Look at all traffic in Grand Central Terminal for a Week in 2019
days_of_the_week = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun", ""]
ax = gct_tirnstiles.plot.line(y="ENTRIES", use_index=False)
gct_tirnstiles.plot.line(ax=ax, y="EXITS", style='g', use_index=False)

ax.set_ylabel("Number of People", fontsize=15)
ax.set_xlabel("")
ax.set_title("Grand Central Terminal Traffic in Late June 2019", fontsize=18)
ax.set_xticklabels(days_of_the_week)
ax.set_xticks(np.linspace(0, 104, 8))
plt.yticks(fontsize=12)
plt.xticks(fontsize=13)
ax.legend(["Entries", "Exits"], prop={'size': 12})
```


![Turnstile Traffic](https://github.com/lucasastorian/MTA-Turnstile-Analysis/blob/master/charts/3.svg)

# Explore Traffic in Grand Central Terminal

```python
gct_data = turnstile_df.loc[turnstile_df["STATION"] == "GRD CNTRL-42 ST"]
daily_gct_data = gct_data.resample('D', base=0, on="DATETIME", label='left').sum()\
                        .reset_index().drop(["WDAY", "WEEK", "HOUR"], axis=1)

daily_gct_data.head()
```




<div>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>DATETIME</th>
      <th>ENTRIES</th>
      <th>EXITS</th>
      <th>LATITUDE</th>
      <th>LONGITUDE</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>2019-06-15</td>
      <td>48635</td>
      <td>46598</td>
      <td>11003.236074</td>
      <td>-19973.851938</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2019-06-16</td>
      <td>46290</td>
      <td>41572</td>
      <td>12755.603301</td>
      <td>-23154.872802</td>
    </tr>
    <tr>
      <th>2</th>
      <td>2019-06-17</td>
      <td>139889</td>
      <td>110206</td>
      <td>13326.141467</td>
      <td>-24190.554014</td>
    </tr>
    <tr>
      <th>3</th>
      <td>2019-06-18</td>
      <td>152487</td>
      <td>127585</td>
      <td>13855.926908</td>
      <td>-25152.257996</td>
    </tr>
    <tr>
      <th>4</th>
      <td>2019-06-19</td>
      <td>154566</td>
      <td>121274</td>
      <td>14670.981432</td>
      <td>-26631.802584</td>
    </tr>
  </tbody>
</table>
</div>




```python
# Look at Daily Traffic for Grand Central Terminal
days_of_the_week = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
ax = daily_gct_data[2:9].plot.line(y="ENTRIES", use_index=False)
daily_gct_data[9:16].plot.line(y='ENTRIES', ax=ax, use_index=False)
daily_gct_data[16:23].plot.line(y='ENTRIES', ax=ax, use_index=False)

ax.set_ylabel("Number of People", fontsize=16)
ax.set_xlabel("")
ax.set_title("Grand Central Terminal Traffic in June - July 2019", fontsize=18)
ax.set_xticklabels(days_of_the_week)
ax.set_xticks(np.linspace(0, 6, 7))
plt.yticks(fontsize=15)
plt.xticks(fontsize=15)
ax.get_legend().remove()
ax.legend(["June 17 - 24", "June 25 - July 1", "July 1 - 7"], prop={'size': 13});
```


![GCT Traffic](https://github.com/lucasastorian/MTA-Turnstile-Analysis/blob/master/charts/4.svg)



```python
total_ridership_count = turnstile_df.groupby("STATION").sum().sort_values("ENTRIES", ascending=False)
total_ridership_count.head()
```




<div>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>ENTRIES</th>
      <th>EXITS</th>
      <th>WDAY</th>
      <th>WEEK</th>
      <th>HOUR</th>
      <th>LATITUDE</th>
      <th>LONGITUDE</th>
    </tr>
    <tr>
      <th>STATION</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>34 ST-PENN STA</th>
      <td>3943616</td>
      <td>3553992</td>
      <td>47667</td>
      <td>421754</td>
      <td>172483</td>
      <td>653961.172271</td>
      <td>-1.187405e+06</td>
    </tr>
    <tr>
      <th>GRD CNTRL-42 ST</th>
      <td>3305843</td>
      <td>2609092</td>
      <td>28934</td>
      <td>259330</td>
      <td>106566</td>
      <td>402433.171225</td>
      <td>-7.305251e+05</td>
    </tr>
    <tr>
      <th>34 ST-HERALD SQ</th>
      <td>2832196</td>
      <td>2633129</td>
      <td>25994</td>
      <td>228143</td>
      <td>90085</td>
      <td>353741.182670</td>
      <td>-6.422967e+05</td>
    </tr>
    <tr>
      <th>23 ST</th>
      <td>2594169</td>
      <td>1906092</td>
      <td>30439</td>
      <td>271436</td>
      <td>109400</td>
      <td>421836.156124</td>
      <td>-7.661062e+05</td>
    </tr>
    <tr>
      <th>TIMES SQ-42 ST</th>
      <td>2423024</td>
      <td>2331916</td>
      <td>24314</td>
      <td>214862</td>
      <td>81807</td>
      <td>333545.967242</td>
      <td>-6.055101e+05</td>
    </tr>
  </tbody>
</table>
</div>




```python
ax = total_ridership_count.plot.hist(y="ENTRIES", bins=60)

ax.set_xlabel("Distribution of Total Rides per Station", fontsize=14)
ax.set_ylabel('')
ax.set_title("Total Rides per Station", fontsize=18)
plt.yticks(fontsize=12)
plt.xticks(fontsize=13)
ax.legend(["Entries"]);
```


![Total Rides Per Station](https://github.com/lucasastorian/MTA-Turnstile-Analysis/blob/master/charts/5.svg)



```python
# Calculate the difference between average traffic during the week, and average traffic on Weekends.
traffic_differences = weekday_weekend_traffic_differences(turnstile_df.reset_index(), week=25)
```


```python
traffic_differences.head()
```




<div>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>STATION</th>
      <th>LATITUDE</th>
      <th>LONGITUDE</th>
      <th>Entry_diffs</th>
      <th>Exit_diffs</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>1 AV</td>
      <td>40.763368</td>
      <td>-73.959240</td>
      <td>11471.8</td>
      <td>12123.2</td>
    </tr>
    <tr>
      <th>2</th>
      <td>103 ST</td>
      <td>40.790280</td>
      <td>-73.947599</td>
      <td>18973.2</td>
      <td>10205.0</td>
    </tr>
    <tr>
      <th>4</th>
      <td>103 ST-CORONA</td>
      <td>40.748706</td>
      <td>-73.862884</td>
      <td>6989.2</td>
      <td>4500.4</td>
    </tr>
    <tr>
      <th>6</th>
      <td>104 ST</td>
      <td>40.799797</td>
      <td>-73.967307</td>
      <td>2050.8</td>
      <td>485.7</td>
    </tr>
    <tr>
      <th>8</th>
      <td>110 ST</td>
      <td>40.798268</td>
      <td>-73.952514</td>
      <td>4159.2</td>
      <td>2831.1</td>
    </tr>
  </tbody>
</table>
</div>




```python
# Identify the stations with the highest and lowest differences between average entrances / exits
# between Weekdays and Weekends.
highest_entry_diffs = traffic_differences.sort_values("Entry_diffs", ascending=False).head(7)
high_exit_diffs = traffic_differences.sort_values("Exit_diffs", ascending=False).head(7)

lowest_entry_diffs = traffic_differences.sort_values("Entry_diffs", ascending=True).head(7)
lowest_exit_diffs = traffic_differences.sort_values("Exit_diffs", ascending=True).head(7)
```

# Analyzing Commuter Traffic

Stations with the biggest difference in traffic between Weekdays and Weekends are probably also the stations with the most commuters. The weekday_weekend_traffic_differences function calculates the average difference in traffic between Weekdays and Weekends. Below I've identified that
* Grand Central, 34th Penn Street, and 23rd Street have the highest surplus of entries during the week
* 34th Penn Street, Grand Central Terminal, and Fulton have the highest surplus of exits during the week
* Coney Island has by far the highest surplus of entries on the weekend
* The Mets' baseball stadium has the highest surplus of exits on the weekend


```python
ax = sns.barplot(x="STATION", y="Entry_diffs", data=highest_entry_diffs, palette=('Blues_d'))

ax.set_xlabel("Station Name", fontsize=18)
ax.set_ylabel("Difference in Entries", fontsize=18)
plt.yticks(fontsize=12)
plt.xticks(fontsize=14)
ax.set_title("The Stations with the Highest Commuter Traffic (Entries)", fontsize=18);
```


![Highest Commuter Entries](https://github.com/lucasastorian/MTA-Turnstile-Analysis/blob/master/charts/6.svg)



```python
ax = sns.barplot(x="STATION", y="Exit_diffs", data=high_exit_diffs, palette=('Blues_d'))

ax.set_xlabel("Station Name", fontsize=18)
ax.set_ylabel("Difference in Exits", fontsize=18)
plt.yticks(fontsize=12)
plt.xticks(fontsize=14)
ax.set_title("The Stations with the Highest Commuter Traffic (Exits)", fontsize=18);
```


![Highest Commuter Exits](https://github.com/lucasastorian/MTA-Turnstile-Analysis/blob/master/charts/7.svg)



```python
#These Stations Actually Have More Traffic on the Weekend Than During the Week.
ax = sns.barplot(x="STATION", y="Entry_diffs", data=lowest_entry_diffs, palette=('Blues_d'))

ax.set_xlabel("Station Name", fontsize=18)
ax.set_ylabel("Difference in Entrances", fontsize=18)
plt.yticks(fontsize=12)
plt.xticks(fontsize=14)
ax.set_title("The Stations with the Lowest Commuter Traffic (entries)", fontsize=18);
```


![Lowest Commuter Entries](https://github.com/lucasastorian/MTA-Turnstile-Analysis/blob/master/charts/8.svg)



```python
#These Stations Actually Have More Traffic on the Weekend Than During the Week.
ax = sns.barplot(x="STATION", y="Exit_diffs", data=lowest_exit_diffs, palette=('Blues_d'))

ax.set_xlabel("Station Name", fontsize=18)
ax.set_ylabel("Difference in Entrances", fontsize=18)
plt.yticks(fontsize=12)
plt.xticks(fontsize=14)
ax.set_title("The Stations with the Lowest Commuter Traffic (exits)", fontsize=18);
```


![Lowest Commuter Exits](https://github.com/lucasastorian/MTA-Turnstile-Analysis/blob/master/charts/9.svg)



```python

```
