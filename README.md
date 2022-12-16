# mcs_plotter

MCS Plotter is a extremly simple tool that monitors WiFi-related values and correlates them over time. I wanted to see how MCS values change when oyu are stationary, when you walk around etc. Then I added in RSSI values and iperf performance benchmarking to see if and how they affect eachother.

This is a very quikck-and-dirty 200 rows-ish of python, only works on Linux (Windows does not seem to allow you to view MCS values at all) and relies on output from the iw tool, something the doc on iw clearly does not recommend. You have been warned. :)
