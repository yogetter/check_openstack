import sys

def helpMsg():
        print ''
        print 'OpenStack check program for Nagios'
        print ''
        print 'Usage: check_PROGRAM.py [flags]'
        print ''
        print 'Flags:'
        print '  -H  openstack endpoint address ex: 192.168.0.1'
        print '  -p  openstack admin password'
        print '  -w  <number> : Global Warning level for service'
        print '  -c  <number> : Global Critical level for service'
        print '  --help  Show this page'
        print ''

def checkArgs(argv):
        if len(argv) == 2 and '--help' in argv:
                helpMsg()
                sys.exit(0)
        if len(argv) != 9:
                print 'Too many or few args'
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
