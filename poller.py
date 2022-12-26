#!/usr/bin/env python
# Very dirty way to poll wifi data by screenscaping CLI output and storing it in sqlite3
# The DB is created if it des not exist and removed first if it exists
# Populate data with this script and generate a static image with plot.py

import subprocess
import re
import time
import sqlite3
from sqlite3 import Error
import os
import argparse
import ipaddress

__license__ = "MIT"
__status__ = "Development"

wnic = 'wlan0'
interval = 2 # Less than 2 will probably make iperf fail
db_name = './wifidata.db'
iperf_server = '192.168.10.20'


def sqlite3_con(db_file: str):
    if os.path.isfile(db_file):
        os.remove(db_file)
    conn = None
    try:
        conn = sqlite3.connect(db_file)

        sql = """ CREATE TABLE IF NOT EXISTS mcs_data (
                id integer PRIMARY KEY,
                ssid text,
                rssi text,
                mcs_rx text,
                mcs_tx text,
                rtt text,
                iperf text,
                ss_rx text,
                ss_tx text
                ); """

        cur = conn.cursor()
        cur.execute(sql)
    except Error as e:
        print(e)
        return False
    finally:
        return conn


def sqlite3_insert(conn, data):
    sql = """INSERT INTO mcs_data (ssid, rssi, mcs_rx, mcs_tx, rtt, iperf, ss_rx, ss_tx) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"""
    cur = conn.cursor()
    cur.execute(sql, data)
    conn.commit()


def run_cmd(cmd: str) -> str:
    s = subprocess.Popen([cmd], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    return s.stdout.read().decode('utf-8').strip('\n').strip('\t')


def isfloat(num):
    try:
        float(num)
        return True
    except ValueError:
        return False


# Let's screenscrape iw although it clearly advises against this
def get_mcs_data() -> tuple:
    data = {'ssid': '', 'rssi': '', 'mcs_rx': '', 'mcs_tx': '', 'rtt': '', 'iperf': '0', 'ss_rx': '', 'ss_tx': ''}

    cmd_ssid = "iw dev " + wnic + " link | grep SSID | awk '{print $2, $3, $4}'"
    data['ssid'] = run_cmd(cmd_ssid).strip()

    if args.rssi:
        cmd_rssi = "iw dev " + wnic + " link | grep signal | awk '{print $2}'"
        data['rssi'] = run_cmd(cmd_rssi)

    if args.mcs_rx:
        cmd_mcs = "iw dev " + wnic + " link | grep 'rx bitrate' | grep MCS"
        line = run_cmd(cmd_mcs).split()
        if mcs_element := list(filter(re.compile(".*MCS").match, line)):
            mcs = ""
            try:
                mcs = line[line.index(mcs_element[0])+1]
            except ValueError:
                pass
            finally:
                if mcs == '':
                    mcs = 0
                data['mcs_rx'] = mcs

    if args.mcs_tx:
        cmd_mcs = "iw dev " + wnic + " link | grep 'tx bitrate' | grep MCS"
        line = run_cmd(cmd_mcs).split()
        if mcs_element := list(filter(re.compile(".*MCS").match, line)):
            mcs = ""
            try:
                mcs = line[line.index(mcs_element[0])+1]
            except ValueError:
                pass
            finally:
                if mcs == '':
                    mcs = 0
                data['mcs_tx'] = mcs

    # cmd_rtt = "fping ..." but fping seems to use weird output and connot be grep'ed
    data['rtt'] = 0

    try:
        if args.iperf and ipaddress.ip_address(args.iperf_server):
            cmd_iperf = "iperf3 -c " + iperf_server + " -t 1 --connect-timeout 200 -P 2 | grep SUM | head -n 1 | awk '{print $6}'"
            t = run_cmd(cmd_iperf).strip()
            if 'error' in t:
                print("iperf error.")
            if t.isnumeric() or isfloat(t):
                data['iperf'] = t
    except ValueError:
        pass

    if args.ss_rx:
        cmd_ss_rx = "iw dev " + wnic + " link | grep 'rx bitrate'"
        t = run_cmd(cmd_ss_rx).strip()
        pos = t.find('NSS')
        data['ss_rx'] = t[pos+3:].strip()
        pass

    return data['ssid'], data['rssi'], data['mcs_rx'], data['mcs_tx'], data['rtt'], data['iperf'], data['ss_rx'], data['ss_tx']


def main():
    print(str(args))
    if args.db:
        print("Opening SQLite3 DB: " + args.db)
        conn = sqlite3_con(args.db)
        if conn:
            print("Polling WiFi data. CTRL+C to stop.")
            while True:
                data = get_mcs_data()
                if args.cli_output:
                    print("Got data! " + str(data))
                sqlite3_insert(conn, data)
                time.sleep(interval)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='MCS plotter')
    parser.add_argument("--db", help="File for the sqlite3 database. Defaults to mcs_plotter.db", default='mcs_plotter.db')
    parser.add_argument("--mcs_rx", help="Collect MCS RX Values.", action="store_true", default=True)
    parser.add_argument("--mcs_tx", help="Collect MCS TX Values.", action="store_true", default=True)
    parser.add_argument("--rssi", help="Plot RSSI values", action="store_true", default=True)
    parser.add_argument("--iperf", action=argparse.BooleanOptionalAction)
    parser.add_argument("--iperf_server", type=str, help="IPv4 address of iperf3 server")
    parser.add_argument("--ss_rx", action=argparse.BooleanOptionalAction, help="Collect Spacial Streams data (RX).")
    parser.add_argument("--ss_tx", action=argparse.BooleanOptionalAction, help="Collect Spacial Streams data (TX).")
    parser.add_argument("--cli-output", help="Show polling output in CLI", action="store_true", default=True)
    args = parser.parse_args()

    main()


