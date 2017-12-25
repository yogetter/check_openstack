# coding: utf-8
from keystone_auth import OSClient
import requests, sys

def helpMsg():
        print ''
        print 'OpenStack nova check program for Nagios'
        print ''
        print 'Usage: check_nova.py [flags]'
        print ''
        print 'Flags:'
	print '  -H  openstack endpoint address ex: 192.168.0.1'
	print '  -p  openstack admin password'
        print '  -w  <number> : Global Warning level for nova service'
        print '  -c  <number> : Global Critical level for nova service'
        print '  -h  Show this page'
        print ''

def checkArgs(argv):
	if len(argv) == 2 and '-h' in argv:
		helpMsg()
		sys.exit(0)
	if len(argv) != 9:
		print 'args format error'
		sys.exit(1)
	else:
		if '-H' not in argv:
			print 'Need Openstack endpoint address'
			sys.exit(1)
		elif '-p' not in argv:
			print 'Need Openstack admin password'
			sys.exit(1)
		elif '-c' not in argv or '-w' not in argv:
			print 'args format error'
			sys.exit(1)
		else:
			return {'endpoint': argv[argv.index('-H')+1], 'passwd': argv[argv.index('-p')+1], 
				'warning': int(argv[argv.index('-c') + 1]), 'critical': int(argv[argv.index('-w') + 1])}

def checkError(data):
	if 'error' in data:
		print 'Error response code', data['error']['code']
		sys.exit(1)
	
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
