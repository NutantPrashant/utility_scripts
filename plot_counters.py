# Author : prashant.chouhan@nutanix.com
# Description: This script can be used to plot counters or subcounters data
# using the periodic counter values files that are saved by the QA cron jobs.

import os
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import argparse
import random

parser = argparse.ArgumentParser()
parser.add_argument('-s', '--start-date', required=True, type=lambda d: datetime.datetime.strptime(d, '%Y%m%d'), help='Start date argument in YYYYMMDD format')
parser.add_argument('-e', '--end-date', required=True, type=lambda d: datetime.datetime.strptime(d, '%Y%m%d'), help='End date argument in YYYYMMDD format')
parser.add_argument('-c', '--counters', nargs="+", required=True, type=str, help='Provide a list of counter or subcounter name. Subcounters can have an optional index separated by a colon. For example, --counters counter1 subcounter1:100')
parser.add_argument('-f', type=str, help='Save the plot in a file with the name: counter_plot_[current date and time].png')

args = parser.parse_args()

start_date = args.start_date
end_date = args.end_date

if args.f:
  save_to_file = True
else:
  save_to_file = False

counter_name_to_index_map = {}
for i, value in enumerate(args.counters):
  if ":" in value:
    counter, index = value.split(':')
    counter_name_to_index_map[counter + "[" + index + "]"] = i
  else:
    counter_name_to_index_map[value] = i

# List of all the files in the current directory
files = sorted(os.listdir())

# Initialize empty lists for each variable
job_ids = []
time_list = []

counter_value_list = []
for i in range(0, len(counter_name_to_index_map)):
  counter_value_list.append([])

# Loop through each file
for file in files:
  # Check if the file is within the time range
  file_time = datetime.datetime.strptime(file.split(".")[0], "%Y%m%d-%H%M%S")
  if start_date <= file_time <= end_date:
    # Open the file for reading
    with open(file, "r") as f:
      # Read the contents of the file
      contents = f.read()

    time_list.append(file_time)
    # Split the contents of the file into lines
    lines = contents.split("\n")
    # Loop through each line.
    for i, line in enumerate(lines):
      # Skip the first 5 and the last line.
      if i < 6 or i == len(lines) - 1:
        continue
      # Continue if this line does not contain any of the counters we are
      # interested in.
      if not any(counter_name in line for counter_name in counter_name_to_index_map.keys()):
        continue

      # Split the line into its components
      components = line.split("|")

      key = components[1].strip()
      value = int(components[2].strip())

      # Get the job_id and variable name
      subcomponents = key.split(".")
      job_id = subcomponents[0]
      counter_name = subcomponents[1]
      for counter in counter_name_to_index_map.keys():
        if counter in counter_name:
          counter_index = counter_name_to_index_map[counter]

      # Append the values to their respective lists
      job_ids.append(int(job_id))
      if len(counter_value_list[counter_index]) < len(time_list):
        counter_value_list[counter_index].append(value)
      else:
        counter_value_list[counter_index][len(time_list) - 1] += value

    for index in counter_name_to_index_map.values():
      if len(counter_value_list[index]) < len(time_list):
        counter_value_list[index].append(0)


if not counter_value_list:
  print("Didn't find any data to plot")
  exit(0)

colors = plt.colormaps['tab20'].colors
markers = ['o', 'v', '^', '<', '>', 's', 'p', '*', 'h', 'H', 'D', 'd']

# Plot the values over time
fig, ax = plt.subplots()
for i, key in enumerate(counter_name_to_index_map.keys()):
  plt.plot(time_list, counter_value_list[counter_name_to_index_map[key]], label=key, color=colors[i], marker=markers[i], markersize=4z)

ax.set_xlabel("Time")
ax.set_ylabel("Counter value")
ax.set_title("Counter Trend Over Time")
ax.grid()
ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))
ax.legend(title="Data Series", loc="upper right", fontsize=8)
fig.autofmt_xdate()

now = datetime.datetime.now()
formatted_datetime = now.strftime("%Y%m%d_%H%M%S")
figManager = plt.get_current_fig_manager()
figManager.full_screen_toggle()

if save_to_file:
  plt.savefig(f"counters_plot_{formatted_datetime}.png")
plt.show()
