import argparse
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime

scan_type_data = {}

def calculate_scan_time(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()
    total_scan_time = 0
    scan_times = []
    start_times = []
    for line in lines:
        data = line.strip().split()
        # print("Data: ", data)
        scan_type = data[1] + data[2]
        if scan_type not in scan_type_data:
            scan_type_data[scan_type] = ([],[])
        start_time = datetime.datetime.strptime(data[4] + ' ' + data[5] + ' ' + data[6], '%b %d %H:%M:%S%z')
        end_time = datetime.datetime.strptime(data[7] + ' ' + data[8] + ' ' + data[9], '%b %d %H:%M:%S%z')
        scan_time = end_time - start_time
        start_times, scan_times = scan_type_data[scan_type]
        scan_times.append(scan_time.total_seconds())
        start_times.append(start_time)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Calculate total scan time.')
    parser.add_argument('file_path', type=str, help='Path to the file containing scan data.')
    args = parser.parse_args()

    calculate_scan_time(args.file_path)
    # print(scan_type_data)

    #print(scan_type_data["FullScan"])
    colors = plt.colormaps['tab20'].colors
    markers = ['o', 'v', '^', '<', '>', 's', 'p', '*', 'h', 'H', 'D', 'd']

    # Plot the values over time
    fig, ax = plt.subplots()
    for i, key in enumerate(scan_type_data.keys()):
      plt.plot(scan_type_data[key][0], scan_type_data[key][1], label = key, color=colors[i], marker = markers[i], markersize = 2)

    ax.set_xlabel("Time")
    ax.set_ylabel("Scan time (secs)")
    ax.grid()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))
    ax.xaxis.set_major_locator(mdates.HourLocator(interval=10))
    ax.legend(title="Data Series", loc="upper right", fontsize=8)
    fig.autofmt_xdate()

    now = datetime.datetime.now()
    formatted_datetime = now.strftime("%Y%m%d_%H%M%S")
    figManager = plt.get_current_fig_manager()
    figManager.full_screen_toggle()
    plt.savefig(f"scan_times_plot_{formatted_datetime}.png")
    plt.show()
