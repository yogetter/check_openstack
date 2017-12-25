# coding: utf-8
from keystone_auth import OSClient
from tool import checkArgs, checkError, helpMsg
import requests, sys

#Get endpoint, passwd, critical, warning
args = checkArgs(sys.argv)
#print args

#Get Openstack auth token
token = OSClient('admin', args['passwd'], 'admin', 'http://'+args['endpoint']+':5000/v2.0').get_token()

#Get Nova service list
header = {'X-Auth-Token': token}
r = requests.get('http://' + args['endpoint'] + ':8774/v2.1/os-services', headers=header)
data = r.json()
checkError(data)
runningService = 0
#print data

#Check Nova service state
for state in data['services']:
 if state['state'] == 'up':
	runningService += 1

if runningService < args['warning']  and runningService > args['critical']:
	print 'Nova is Warning, running service:', runningService
	sys.exit(1)
elif runningService < args['critical']:
	print 'Nova is Critical, running service:', runningService 
	sys.exit(2)
else:
	print 'Nova is Ok, running service:', runningService 
	sys.exit(0)
