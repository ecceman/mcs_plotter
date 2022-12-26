#!/usr/bin/env python
# Generates a static PNG image from data in sqlite3 db.

import matplotlib.pyplot as plt
import sqlite3
from sqlite3 import Error
import numpy as np
import argparse

__license__ = "MIT"
__status__ = "Development"

# Info for graph, edit or automate to your liking
wnic = "AX200 (rev 1a)"
driver = "iwlwifi"
uname = "6.0.12-arch1-1"
ap = "Cisco 2802i (AireOS 8.10)"

# Nice colors
rssi_color = "#81b1d2"
mcs_rx_color = "#fa8174"
mcs_tx_color = "#F8ECFF"
iperf_color = "#ffed6f"
ss_color = '#97EB63'

img_filename = "graph.png"
img_dpi = 300


def get_mcs_data(conn):
    cur = conn.cursor()
    cur.execute("SELECT id, rssi, mcs_rx, mcs_tx, iperf, ss_rx, ss_tx FROM mcs_data")
    rows = cur.fetchall()
    return rows


def sqlite3_con():
    conn = None
    try:
        conn = sqlite3.connect(args.db)
    except Error as e:
        print(e)
        return False
    finally:
        return conn


def graph_data(conn):
    rows = get_mcs_data(conn)

    x = []
    rssi = []
    mcs_rx = []
    mcs_tx = []
    iperf = []
    ss_rx = []

    for row in rows:
        print(str(row))
        x.append(int(row[0]))
        rssi.append(int(row[1]))
        mcs_rx.append(int(row[2]))
        mcs_tx.append(int(row[3]))
        iperf.append(float(row[4]))
        ss_rx.append(int(row[5]))

    plt.style.use('dark_background')
    fig, ax_rssi = plt.subplots()
    lines = []

    # RSSI hanging bars
    if args.rssi:
        ax_rssi.tick_params(axis='y', colors=rssi_color)
        ax_rssi.yaxis.label.set_color(rssi_color)
        ax_rssi.spines['left'].set_color(rssi_color)
        ax_rssi.bar(x, rssi, alpha=0.7, color=rssi_color, width=0.9)
        ax_rssi.grid(visible=True, axis='both', linewidth=0.1)
        ax_rssi.tick_params(axis='both', labelsize=6.0)
        ax_rssi.set_xlabel("Timeline (s)", fontsize=6)
        ax_rssi.set_ylabel("RSSI (dBm)", fontsize=6)
        ax_rssi.set_yticks([-100, -90, -80, -70, -60, -50, -40, -30, -20, -10, 0])

    # MCS
    if args.mcs_rx:
        ax_mcs_rx = ax_rssi.twinx()
        vals_mcs_rx = np.asarray(mcs_rx)
        minval_mcs_rx = np.amin(vals_mcs_rx)
        minval_mcs_rx += np.sign(minval_mcs_rx)
        ax_mcs_rx.tick_params(axis='y', colors=mcs_rx_color)
        ax_mcs_rx.yaxis.label.set_color(mcs_rx_color)
        ax_mcs_rx.spines['right'].set_color(mcs_rx_color)
        ax_mcs_rx.tick_params(axis='y', labelsize=6.0)
        ax_mcs_rx.set_ylabel("MCS", fontsize=6)
        # ax_mcs.plot(x, mcs, ".-", color=mcs_color, label="MCS", linewidth=1.0)
        t = ax_mcs_rx.plot(x, vals_mcs_rx, "o-", color=mcs_rx_color, label="MCS RX", linewidth=1.0)
        lines.append(t[0])
        ax_mcs_rx.set_yticks([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

    # MCS TX
    if args.mcs_tx:
        if args.mcs_rx:
            vals_mcs_tx = np.asarray(mcs_tx)
            t = ax_mcs_rx.plot(x, vals_mcs_tx, ".-", color=mcs_tx_color, alpha=1.0, label="MCS TX", linewidth=1.0)
            lines.append(t[0])
            ax_mcs_rx.set_yticks([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        else:
            ax_mcs_tx = ax_rssi.twinx()
            vals_mcs_tx = np.asarray(mcs_tx)
            minval_mcs_tx = np.amin(vals_mcs_tx)
            minval_mcs_tx += np.sign(minval_mcs_tx)
            ax_mcs_tx.tick_params(axis='y', colors=mcs_rx_color)
            ax_mcs_tx.yaxis.label.set_color(mcs_rx_color)
            ax_mcs_tx.spines['right'].set_color(mcs_rx_color)
            ax_mcs_tx.tick_params(axis='y', labelsize=6.0)
            ax_mcs_tx.set_ylabel("MCS", fontsize=6)
            t = ax_mcs_tx.plot(x, vals_mcs_tx, "o-", color=mcs_rx_color, label="MCS RX", linewidth=1.0)
            lines.append(t[0])
            ax_mcs_tx.set_yticks([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

    # iPerf thoughput
    if args.iperf:
        iperf = [float('nan') if t == 0 else t for t in iperf]  # don't plot zero values
        ax_iperf = ax_rssi.twinx()
        ax_iperf.tick_params(axis='y', colors=iperf_color)
        ax_iperf.spines.right.set_position(("axes", 1.10))
        ax_iperf.yaxis.label.set_color(iperf_color)
        ax_iperf.spines['right'].set_color(iperf_color)
        ax_iperf.tick_params(axis='y', labelsize=6.0)
        ax_iperf.set_ylabel("Throughput (Mbps)", fontsize=6)
        t = ax_iperf.plot(x, iperf, ".-", color=iperf_color, label="Throughput", linewidth=1.0)
        lines.append(t[0])
        ax_iperf.set_yticks([0, 20, 40, 60, 80, 100, 120, 140, 160, 180, 200])

    # SS
    if args.ss_rx:
        ax_ss = ax_rssi.twinx()
        ax_ss.tick_params(axis='y', colors=ss_color)
        ax_ss.spines.right.set_position(("axes", 1.25))
        ax_ss.yaxis.label.set_color(ss_color)
        ax_ss.spines['right'].set_color(ss_color)
        ax_ss.tick_params(axis='y', labelsize=6.0)
        ax_ss.set_ylabel("Spacial streams", fontsize=6)
        t = ax_ss.plot(x, ss_rx, ".-", color=ss_color, label="SS (RX)", linewidth=1.0)
        lines.append(t[0])
        ax_ss.set_yticks([0, 1, 2, 3, 4])

    # Label
    labels = [l.get_label() for l in lines]
    ax_rssi.legend(lines, labels, loc="lower left", prop={'size': 5})

    plt.title('Kernel: ' + uname + ', Drv: ' + driver + ', WNIC: ' + wnic + ', AP(s): ' + ap, fontsize=6)

    plt.savefig(img_filename, bbox_inches='tight', dpi=img_dpi)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='MCS plotter')
    parser.add_argument("--db", help="File for the sqlite3 database. Defaults to mcs_plotter.db", default='mcs_plotter.db')
    parser.add_argument("--mcs_rx", action=argparse.BooleanOptionalAction, help="Plot MCS RX.", default=True)
    parser.add_argument("--mcs_tx", action=argparse.BooleanOptionalAction, help="plot MCS TX.")
    parser.add_argument("--rssi", action=argparse.BooleanOptionalAction, help="Plot RSSI.", default=True)
    parser.add_argument("--iperf", action=argparse.BooleanOptionalAction, help="Plot iperf thoughput.")
    parser.add_argument("--ss_rx", action=argparse.BooleanOptionalAction, help="Plot Spacial Streams (RX).")
    parser.add_argument("--ss_tx", action=argparse.BooleanOptionalAction, help="Plot Spacial Streams (TX).")
    args = parser.parse_args()

    print(str(args))

    print("Generating image file...")
    conn = sqlite3_con()
    if conn:
        graph_data(conn)
        print("Done.")
