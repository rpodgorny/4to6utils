#!/usr/bin/python

__version__ = '0.1'

import sys
import socket
import select
import logging

# TODO: this is version for windowed applications
def get_output(cmd):
	import os
	f = os.popen(cmd)
	return f.read()
#enddef

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

	ipv4 = get_output('netstat -a -n -p tcp').split('\n')
	ipv4 = [i for i in ipv4 if 'LISTENING' in i]
	ipv4 = parse(ipv4)
	ipv4 = map(get_port, ipv4)
	ipv4 = list(set(ipv4))

	ipv6 = get_output('netstat -a -n -p tcpv6').split('\n')
	ipv6 = [i for i in ipv6 if 'LISTENING' in i]
	ipv6 = parse(ipv6)
	ipv6 = map(get_port, ipv6)
	ipv6 = list(set(ipv6))
	
	logging.debug('ipv4: %s', ipv4)
	logging.debug('ipv6: %s', ipv6)

	ret = ipv4
	for i in ipv6:
		if i in ret: ret.remove(i)
	#endfor

	return ret
#enddef

def main():
	logging.basicConfig(level=logging.DEBUG)

	logging.info('*' * 40)
	logging.info('starting ipv6listen v%s', __version__)
	
	if sys.platform == 'win32':
		logging.info('detected win32')

		import tray
		tray.run('ipv6listen.png', 'ipv6listen v%s' % __version__)
	#endif

	ports = map(int, sys.argv[1:])
	if not ports:
		logging.info('no ports specified, using autodetection')
		ports = find_ipv4_only()
		logging.info('found ports: %s', ports)
	#endif

	sock_pairs = []

	listen_socks = []
	listen_sock_to_port_map = {}
	for p in ports:
		s = socket.socket(socket.AF_INET6)
		s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		s.bind(('::', p))
		s.listen(10)
		logging.info('listening on port %s', p)
		listen_socks.append(s)
		listen_sock_to_port_map[s] = p
	#endfor

	try:
		run = True
		while run and not tray._exit:
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
					logging.info('accept from %s', addr)
					s2 = socket.socket(socket.AF_INET)
					s2.connect(('127.0.0.1', listen_sock_to_port_map[s]))
					sock_pairs.append((conn, s2))
				#endif

				if s in xlist:
					logging.warrning('listening socket in xlist')
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
						logging.info('shutdown1')
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
						logging.info('shutdown2')
					else:
						s1.send(buf)
					#endif
				#endif

				if s1 in xlist:
					logging.warning('s1 in xlist')
					# TODO: do something
				#endif

				if s2 in xlist:
					logging.warning('s2 in xlist')
					# TODO: do something
				#endif
			#endfor
		#endwhile
	except KeyboardInterrupt:
		logging.info('keyboard interrupt!')
	#endtry

	logging.info('shutting down listening sockets')
	for s in listen_socks:
		s.close()
	#endfor

	logging.info('shutting down socket pairs')
	for s1,s2 in sock_pairs:
		s1.shutdown(socket.SHUT_RDWR)
		s2.shutdown(socket.SHUT_RDWR)
		s1.close()
		s2.close()
	#endfor

	if sys.platform == 'win32':
		tray.exit()
	#endif
#enddef

if __name__ == '__main__': main()
