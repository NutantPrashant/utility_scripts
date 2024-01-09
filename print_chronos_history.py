import os
import datetime
import argparse
import pandas as pd
import sys
from bs4 import BeautifulSoup

parser = argparse.ArgumentParser()
parser.add_argument('-s', '--start-date', required=True, type=lambda d: datetime.datetime.strptime(d, '%Y%m%d'), help='Start date argument in YYYYMMDD format')
parser.add_argument('-e', '--end-date', required=True, type=lambda d: datetime.datetime.strptime(d, '%Y%m%d'), help='End date argument in YYYYMMDD format')
parser.add_argument('-t', '--job-type', nargs="+", required=True, type=str, help='Background job type')
args = parser.parse_args()

start_date = args.start_date
end_date = args.end_date

# List of all the files in the current directory
files = sorted(os.listdir())

all_filtered_tables = []
job_type = "UpdateRefcount"
# Loop through each file
for file in files:
  # Check if the file is within the time range
  file_time = datetime.datetime.strptime(file.split(".")[0], "%Y%m%d-%H%M%S")
  if start_date <= file_time <= end_date:
    # Open the file for reading
    with open(file, "r") as f:
      soup = BeautifulSoup(f, 'html.parser')
      tables = soup.find_all('table')
      for i, table in enumerate(tables):
        # Only save the 4th table.
        if i != 4:
          continue
        df = pd.read_html(str(table), header=0)[0]
        all_filtered_tables.append(df)

if not all_filtered_tables:
  print("Nothing to display")

result = pd.DataFrame(columns=all_filtered_tables[0].columns)
for table in all_filtered_tables:
  print(table.to_string())


# This needs to be fixed
# job_type = "UpdateRefcount"
# for table in all_filtered_tables:
#   for i, row in table.iterrows():
#     if row.isna().any():
#       continue
#     if job_type in row["Job Name"]:
#       result.append(row)
#
# print(result)
