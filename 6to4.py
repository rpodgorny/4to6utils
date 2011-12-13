#!/usr/bin/python

__version__ = '0.0'

import sys
import socket
import select
import subprocess

def find_ipv4_only():
	def parse(s):
		for i in s:
			while '  ' in i: i = i.replace('  ', ' ')
			i = i.strip()
			_, local_addr, _ = i.split(' ', 2)
			yield local_addr
	#enddef
	
	def get_port(s):
		port = s.rsplit(':', 1)[1]
		return int(port)
	#enddef

	ipv4 = subprocess.check_output('netstat -a -n -p tcp', shell=True).split('\n')
	ipv4 = [i for i in ipv4 if 'LISTENING' in i]
	ipv4 = parse(ipv4)
	ipv4 = map(get_port, ipv4)

	ipv6 = subprocess.check_output('netstat -a -n -p tcpv6', shell=True).split('\n')
	ipv6 = [i for i in ipv6 if 'LISTENING' in i]
	ipv6 = parse(ipv6)
	ipv6 = map(get_port, ipv6)
	
	#print ipv4
	#print ipv6

	ret = ipv4
	for i in ipv6: ret.remove(i)
	return ret
#enddef

def main():
	# TODO: for automatic mode
	#print find_ipv4_only()
	
	ports = map(int, sys.argv[1:])
	if not ports:
		print 'no ports specified!'
		return
	#endif

	sock_pairs = []

	listen_socks = []
	listen_sock_to_port_map = {}
	for p in ports:
		s = socket.socket(socket.AF_INET6)
		s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		s.bind(('::', p))
		s.listen(10)
		print 'listening on port %s' % p
		listen_socks.append(s)
		listen_sock_to_port_map[s] = p
	#endfor

	while 1:
		rlist = listen_socks[:]
		wlist = []
		xlist = listen_socks[:]

		for s1,s2 in sock_pairs:
			rlist.append(s1)
			rlist.append(s2)
			xlist.append(s1)
			xlist.append(s2)
		#endfor

		rlist, wlist, xlist = select.select(rlist, wlist, xlist, 1)

		for s in listen_socks:
			if s in rlist:
				conn, addr = s.accept()
				print 'accept from %s' % addr
				s2 = socket.socket(socket.AF_INET)
				s2.connect(('127.0.0.1', listen_sock_to_port_map[s]))
				sock_pairs.append((conn, s2))
			#endif

			if s in xlist:
				print 'sock in xlist'
				# TODO: do something
				#break
			#endif
		#endfor

		for s1,s2 in sock_pairs:
			if s1 in rlist:
				buf = s1.recv(100000)
				if len(buf) == 0:
					s1.shutdown(socket.SHUT_RDWR)
					s2.shutdown(socket.SHUT_RDWR)
					s1.close()
					s2.close()
					sock_pairs.remove((s1, s2))
					print 'shutdown1'
				else:
					s2.send(buf)
				#endif
			#endif

			if s2 in rlist:
				buf = s2.recv(100000)
				if len(buf) == 0:
					s2.shutdown(socket.SHUT_RDWR)
					s1.shutdown(socket.SHUT_RDWR)
					s2.close()
					s1.close()
					sock_pairs.remove((s1, s2))
					print 'shutdown2'
				else:
					s1.send(buf)
				#endif
			#endif

			if s1 in xlist:
				print 's1 in xlist'
				# TODO: do something
			#endif

			if s2 in xlist:
				print 's2 in xlist'
				# TODO: do something
			#endif
		#endfor
	#endwhile
#enddef

if __name__ == '__main__': main()
