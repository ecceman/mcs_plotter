# mcs_plotter

MCS Plotter is a extremly simple CLI tool that monitors WiFi-related values and correlates them over time. I wanted to see how MCS values change when you are stationary, when you walk around etc. Then I added in RSSI values and iperf performance benchmarking to see if and how they affect eachother.

This is a very quikck-and-dirty 200 rows-ish of python, only works on Linux (Windows does not seem to allow you to view MCS values at all) and relies on output from the `iw` tool, something the doc on iw clearly does not recommend. You have been warned. :)

## Usage:
Change the variables in the `poller.py` and `plot.py` file to fit your needs and simply run the poller first for a while. The CTRL+C to abort the polling and run `plot.py` to generate a static PNG image.

![alt text](https://github.com/ecceman/mcs_plotter/blob/main/mcs_graph_draft1.png)
