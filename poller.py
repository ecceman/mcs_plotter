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

__license__ = "MIT"
__status__ = "Development"

wnic = 'wlan0'
interval = 2 # Less than 2 will probably make iperf fail
db_name = './wifidata.db'
iperf_server = '192.168.10.20'


def sqlite3_con():
    if os.path.isfile(db_name):
        os.remove(db_name)
    conn = None
    try:
        conn = sqlite3.connect(db_name)

        sql = """ CREATE TABLE IF NOT EXISTS mcs_data (
                id integer PRIMARY KEY,
                ssid text,
                rssi text,
                mcs text,
                rtt text,
                iperf text
                ); """

        cur = conn.cursor()
        cur.execute(sql)
    except Error as e:
        print(e)
        return False
    finally:
        return conn


def sqlite3_insert(conn, data):
    sql = """INSERT INTO mcs_data (ssid, rssi, mcs, rtt, iperf) VALUES (?, ?, ?, ?, ?)"""
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
    data = {'ssid': '', 'rssi': '', 'mcs': '', 'rtt': '', 'iperf': '0'}

    cmd_ssid = "iw dev " + wnic + " link | grep SSID | awk '{print $2, $3, $4}'"
    data['ssid'] = run_cmd(cmd_ssid).strip()

    cmd_rssi = "iw dev " + wnic + " link | grep signal | awk '{print $2}'"
    data['rssi'] = run_cmd(cmd_rssi)

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
            data['mcs'] = mcs

    # cmd_rtt = "fping ..." but fping seems to use weird output and connot be grep'ed
    data['rtt'] = 0

    cmd_iperf = "iperf3 -c " + iperf_server + " -t 1 --connect-timeout 200 -P 2 | grep SUM | head -n 1 | awk '{print $6}'"
    t = run_cmd(cmd_iperf).strip()
    if 'error' in t:
        print("iperf error.")
    if t.isnumeric() or isfloat(t):
        data['iperf'] = t

    return data['ssid'], data['rssi'], data['mcs'], data['rtt'], data['iperf']


if __name__ == '__main__':
    print("Opening SQLite3 DB: " + db_name)
    conn = sqlite3_con()
    if conn:
        print("Polling WiFi data. CTRL+C to stop.")
        while True:
            data = get_mcs_data()
            print("Got data! " + str(data))
            sqlite3_insert(conn, data)
            time.sleep(interval)
