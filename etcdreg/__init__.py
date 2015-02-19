#!/usr/bin/env python

# params :
# - advertised ip
# - service name
# - service ports
# - etcd path
# - etcd address <ip>:<port>
# - etcd ttl
# - loop time
#
# will register key at etcd: /<etcd_path>/<service_name>_<service_port>/<public_ip>:<docker_port>

import sys, time, requests, getopt, socket, select, json


# potentially run multiple checks in parallel
def healthchecks():
    return True

def getetcdurl(opt, port):
    return 'http://'+opt['etcd_address']+'/v2/keys/'+opt['etcd_path']+'/'+opt['service_name']+':'+port+'/'+opt['hostname']+'?ttl='+opt['etcd_ttl']

def register(opt):
    for port in opt['service_ports'].split(','):
        mapport = opt['portmap'][port+'/tcp']
        url = getetcdurl(opt, port)
        payload = { "ip" : opt['advertised_ip'], "port" : mapport, "hostname" : opt['hostname'] }
        requests.put(url, data = { "value" : json.dumps(payload) })
        if(opt['debug']):
            print "register "+port+" on "+url+" : "+str(payload)

def deregister(opt):
    print "deregister"

def main(argv):
    settings = { 
	'hostname' : socket.gethostname(),
        'advertised_ip': '127.0.0.1',
        'service_name': 'undefined',
        'service_ports': '80,443',
        'etcd_path': 'services',
        'etcd_address': '172.17.42.1:4001',
        'etcd_ttl': '15',
        'frequency': 10,
	'debug': False,
	'portmap': {}
    }

    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.connect('/var/run/docker.sock')
    s.sendall("GET /containers/"+settings['hostname']+"/json HTTP/1.0\r\n\r\n")
#    s.sendall("GET /containers/54d4297572a9/json HTTP/1.0\r\n\r\n")
    response = s.recv(4096)
    s.close()
    (headers, js) = response.split("\r\n\r\n")
    data = json.loads(js)
    for port, mapped in data['NetworkSettings']['Ports'].iteritems():
	# multiple ports can be mapped to the same internal port, pick first
	settings['portmap'][port] = mapped[0]['HostPort']

    try:
        opts, args = getopt.getopt(argv,"i:s:p:P:e:t:f:hd",["service=","ip=","ttl="])
    except getopt.GetoptError:
        print 'registrator.py -i <advertised_ip> -s <service_name> -p <ports> -P <etcd_path> -e <etcd_address> -t <ttl> -f <freqency>'
    for opt, arg in opts:
    	if opt == '-h':
	    print 'registrator.py -i <advertised_ip> -s <service_name> -p <ports> -P <etcd_path> -e <etcd_address> -t <ttl> -f <freqency>'
    	    sys.exit()
        elif opt in ("-d"):
            settings['debug'] = True
        elif opt in ("-i", "--ip"):
            settings['advertised_ip'] = arg
	elif opt in ("-s", "--service"):
	    settings['service_name'] = arg
	elif opt in ("-p", "--ports"):
	    settings['service_ports'] = arg
	elif opt in ("-P", "--path"):
	    settings['etcd_path'] = arg
	elif opt in ("-e", "--etcd"):
	    settings['etcd_address'] = arg
	elif opt in ("-t", "--ttl"):
	    settings['etcd_ttl'] = arg
	elif opt in ("-f", "--freq"):
	    settings['frequency'] = arg

    while True:
	if healthchecks() :
	    register(settings)
        else :
	    deregister(settings)
	# should sleep for a defined time minus check execution time to get stable update intervals
	time.sleep(0.5)

