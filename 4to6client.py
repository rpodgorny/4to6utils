#!/usr/bin/python3

from version import __version__

import sys
import socket
import select
import logging


def logging_setup(level, fn=None):
	logger = logging.getLogger()
	logger.setLevel(logging.DEBUG)

	formatter = logging.Formatter('%(asctime)s: %(levelname)s: %(message)s')

	sh = logging.StreamHandler()
	sh.setLevel(level)
	sh.setFormatter(formatter)
	logger.addHandler(sh)

	if fn:
		fh = logging.FileHandler(fn)
		fh.setLevel(level)
		fh.setFormatter(formatter)
		logger.addHandler(fh)
	#endif
#enddef


def main():
	logging_setup('DEBUG', '4to6client.log')

	logging.info('*' * 40)
	logging.info('starting 4to6client v%s' % __version__)

	triplet = sys.argv[1].split(':')
	local_port, remote, remote_port = triplet
	local_port = int(local_port)
	remote_port = int(remote_port)

	logging.info('%s %s %s' % (local_port, remote, remote_port))

	sock_pairs = []

	sock = socket.socket(socket.AF_INET)
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	sock.bind(('127.0.0.1', local_port))
	sock.listen(10)  # TODO: hard-coded shit

	while 1:
		rlist = [sock, ]
		wlist = []
		xlist = [sock, ]

		for s1, s2 in sock_pairs:
			rlist.append(s1)
			rlist.append(s2)
			xlist.append(s1)
			xlist.append(s2)
		#endfor

		# this a workaround for windows because it can't handle when all lists are empty
		# note: this actually never happens here but i've just cut-n-pasted it from ipv6listen
		if not rlist and not wlist and not xlist:
			time.sleep(0.1)
			rlist, wlist, xlist = [], [], []
		else:
			rlist, wlist, xlist = select.select(rlist, wlist, xlist, 1)
		#endif

		if sock in rlist:
			logging.debug('accept')
			conn, addr = sock.accept()
			logging.debug('addr: %s' % str(addr))

			s2 = socket.socket(socket.AF_INET6)
			s2.connect((remote, remote_port))
			sock_pairs.append((conn, s2))
		#endif

		if sock in xlist:
			logging.debug('sock in xlist')
			break
		#endif

		for s1,s2 in sock_pairs:
			if s1 in rlist:
				buf = s1.recv(100000)  # TODO: hard-coded shit
				if len(buf) == 0:
					s1.shutdown(socket.SHUT_RDWR)
					s2.shutdown(socket.SHUT_RDWR)
					s1.close()
					s2.close()
					sock_pairs.remove((s1, s2))
					logging.debug('shutdown1')
				else:
					s2.send(buf)
				#endif
			#endif

			if s2 in rlist:
				buf = s2.recv(100000)  # TODO: hard-coded shit
				if len(buf) == 0:
					s2.shutdown(socket.SHUT_RDWR)
					s1.shutdown(socket.SHUT_RDWR)
					s2.close()
					s1.close()
					sock_pairs.remove((s1, s2))
					logging.debug('shutdown2')
				else:
					s1.send(buf)
				#endif
			#endif

			if s1 in xlist:
				logging.debug('s1 in xlist')
			#endif

			if s2 in xlist:
				logging.debug('s2 in xlist')
			#endif
		#endfor
	#endwhile

	logging.debug('exited loop')

	logging.info('shutting down listening sockets')
	for s in listen_socks:
		s.close()
	#endfor

	logging.info('shutting down socket pairs')
	for s1, s2 in sock_pairs:
		socket_shutdown(s1)
		socket_shutdown(s2)
	#endfor
#enddef


if __name__ == '__main__':
	main()
#endif
