# RouterMonitor
Monitoring script to check internet connectivity and reboot Huawei mobile router if needed.
Performs periodic ping to a host in internet and if the ping fails for too long time, the router is rebooted.

The monitoring script is executed in a Linux machine that is in the LAN network behind the router, so that it can access the router's management interface that by default is 192.168.1.1. 

The script uses https://pypi.org/project/huawei-lte-api/ as API to command the router.

Tested with Huawei B715s-23c as the router and Raspberry PI as the monitoring device.
Used python version 3.7 but should work also with older python3 versions.

## Installation
- Clone repository to /home/pi/RouterMonitor
- Edit the global variables in routermonitor.py to match with your environment, at least G_ROUTER_PASSWORD needs to be changed, possibly also G_ROUTER_IP.
- Install python modules: sudo pip3 install requests typing huawei-lte-api
- Make sure the latest requests library is used: sudo pip3 install requests -U
- Tip: If you face runtime failures in some of those libraries, try upgrading it by "pip3 install xxxxx -U"
- Copy routermonitor.service to /etc/systemd/system/
- sudo systemctl daemon-reload
- sudo systemctl enable routermonitor
- sudo systemctl start routermonitor
- Check status: systemctl status routermonitor
- The script writes logs to /var/log/syslog

## Testing and troubleshooting

Initially it is good to run the script manually in test mode to verify connectivity to the router API.
Running this command should print information about the router:
python3 routermonitor.py --test

If that works, you can start the service. If you want to verify that router reboot logic works, a good method to cause
an artificial break in the internet connection is to disable mobile network connection from
the router management GUI front page and then observe from /var/log/syslog of the monitoring machine when routermonitor
detects the break and eventually reboots the router.
