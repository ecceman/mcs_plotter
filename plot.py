#!/usr/bin/env python
# Generates a static PNG image from data in sqlite3 db.

import matplotlib.pyplot as plt
import sqlite3
from sqlite3 import Error

__license__ = "MIT"
__status__ = "Development"

# Info for graph, edit or automate to your liking
wnic = "AX200 (rev 1a)"
driver = "iwlwifi"
uname = "6.0.12-arch1-1"
ap = "Cisco 2802i (AirOS 8.10)"

# Nice colors
rssi_color = "#81b1d2"
mcs_color = "#fa8174"
iperf_color = "#ffed6f"

img_filename = "graph.png"
img_dpi = 300
db_name = "wifidata.db"


def get_mcs_data(conn):
    cur = conn.cursor()
    cur.execute("SELECT id, rssi, mcs, iperf FROM mcs_data")
    rows = cur.fetchall()
    return rows


def sqlite3_con():
    conn = None
    try:
        conn = sqlite3.connect(db_name)
    except Error as e:
        print(e)
        return False
    finally:
        return conn


def graph_data(conn):
    rows = get_mcs_data(conn)

    x = []
    rssi = []
    mcs = []
    iperf = []

    for row in rows:
        print(str(row))
        x.append(int(row[0]))
        rssi.append(int(row[1]))
        mcs.append(int(row[2]))
        iperf.append(float(row[3]))

    plt.style.use('dark_background')
    fig, ax_rssi = plt.subplots()

    ax_rssi.tick_params(axis='y', colors=rssi_color)
    ax_rssi.yaxis.label.set_color(rssi_color)
    ax_rssi.spines['left'].set_color(rssi_color)
    ax_rssi.bar(x, rssi, alpha=0.4, color=rssi_color, width=0.9)
    ax_rssi.grid(visible=True, axis='both', linewidth=0.1)
    ax_rssi.tick_params(axis='both', labelsize=6.0)
    ax_rssi.set_xlabel("Timeline (s)", fontsize=6)
    ax_rssi.set_ylabel("RSSI (dBm)", fontsize=6)
    ax_rssi.set_yticks([-100, -90, -80, -70, -60, -50, -40, -30, -20, -10, 0])

    ax_mcs = ax_rssi.twinx()
    ax_mcs.tick_params(axis='y', colors=mcs_color)
    ax_mcs.yaxis.label.set_color(mcs_color)
    ax_mcs.spines['right'].set_color(mcs_color)
    ax_mcs.tick_params(axis='y', labelsize=6.0)
    ax_mcs.set_ylabel("MCS", fontsize=6)
    ax_mcs.plot(x, mcs, "-", color=mcs_color, label="MCS", linewidth=1.0)
    ax_mcs.set_yticks([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

    ax_iperf = ax_rssi.twinx()
    ax_iperf.tick_params(axis='y', colors=iperf_color)
    ax_iperf.spines.right.set_position(("axes", 1.10))
    ax_iperf.yaxis.label.set_color(iperf_color)
    ax_iperf.spines['right'].set_color(iperf_color)
    ax_iperf.tick_params(axis='y', labelsize=6.0)
    ax_iperf.set_ylabel("Throughput (Mbps)", fontsize=6)
    ax_iperf.plot(x, iperf, "-", color=iperf_color, label="iperf3", linewidth=1.0)
    ax_iperf.set_yticks([0, 20, 40, 60, 80, 100, 120, 140, 160, 180, 200])

    plt.title('Kernel: ' + uname + ', Drv: ' + driver + ', WNIC: ' + wnic + ', AP(s): ' + ap, fontsize=6)

    plt.savefig(img_filename, bbox_inches='tight', dpi=img_dpi)


if __name__ == '__main__':
    print("Generating image file...")
    conn = sqlite3_con()
    if conn:
        graph_data(conn)
        print("Done.")
