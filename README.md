To run:

In one terminal window:
- cd device/
- make build
- ./device [port]

In another terminal window:
- cd ui/
- run python3 main.py

In "Connect to Device" fields: type 0 for IP Address and whatever port number you specified for port
In "Test Duration" fields: specify test duration in seconds, and optionally frequency (default will be 1000ms, i.e. 1s)

Click "Discover" to get model # and Serial (IP Address and Port field must be filled out)
Click "Start Test" to start test and begin seeing live plot

You can start multiple devices at once by running ./device [port] on multiple terminals
You can also record data from multiple devices sequentially if you record from one, save that graph to PDF, and then
change the port number in the port field and hit "Start Test" (a new live graph will begin generating)

Test results are saved in test_results (a sample is included)