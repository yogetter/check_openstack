# coding: utf-8
from keystone_auth import OSClient
import requests, sys


def check_args(argv):
	if argv[1] != '-c' or argv[3] != '-w':
		print "args format error"
		sys.exit(1)
	else:
		return int(argv[2]), int(argv[4])

critical, warning = check_args(sys.argv)
#print critical, warning

#Get Openstack auth token
token = OSClient().get_token()

#Get Noava service list
header = {'X-Auth-Token': token}
r = requests.get("http://172.22.131.250:8774/v2.1/os-services", headers=header)
data = r.json()
runningService = 0

for state in data['services']:
 if state['state'] == 'up':
	runningService += 1

if runningService < warning and runningService > critical:
	print "Nova is Warning, running service:", runningService
	sys.exit(1)
elif runningService < critical:
	print "Nova is Critical, running service:", runningService 
	sys.exit(2)
else:
	print "Nova is Ok, running service:", runningService 
	sys.exit(0)
