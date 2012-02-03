#!/usr/bin/python

__version__ = '0.0'

import sys
import socket
import select

port1 = int(sys.argv[1])
remote = sys.argv[2]
remote_port = int(sys.argv[3])

def main():
	sock_pairs = []

	sock = socket.socket(socket.AF_INET)
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	sock.bind(('127.0.0.1', port1))
	sock.listen(10)

	while 1:
		rlist = [sock, ]
		wlist = []
		xlist = [sock, ]

		for s1,s2 in sock_pairs:
			rlist.append(s1)
			rlist.append(s2)
			xlist.append(s1)
			xlist.append(s2)
		#endfor

		rlist, wlist, xlist = select.select(rlist, wlist, xlist)

		if sock in rlist:
			print 'accept'
			conn, addr = sock.accept()
			print addr
			s2 = socket.socket(socket.AF_INET6)
			s2.connect((remote, remote_port))
			sock_pairs.append((conn, s2))
		#endif

		if sock in xlist:
			print 'sock in xlist'
			break
		#endif

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
			#endif

			if s2 in xlist:
				print 's2 in xlist'
			#endif
		#endfor
	#endwhile
#enddef

if __name__ == '__main__': main()
