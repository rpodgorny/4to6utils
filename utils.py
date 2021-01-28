import os
import time
import socket
import select
import logging
import subprocess


# TODO: this is version for windowed applications
def get_output(cmd):
	import os
	f = os.popen(cmd)
	return f.read()


def get_listening_ports():
	def parse(s):
		for i in s:
			while '  ' in i: i = i.replace('  ', ' ')
			i = i.strip()
			_, local_addr, _ = i.split(' ', 2)
			yield local_addr

	def get_port(s):
		port = s.rsplit(':', 1)[1]
		return int(port)

	ipv4 = get_output('netstat -a -n -p tcp').split('\n')
	ipv4 = [i for i in ipv4 if '0.0.0.0' in i]
	ipv4 = parse(ipv4)
	ipv4 = map(get_port, ipv4)
	ipv4 = sorted(list(set(ipv4)))

	ipv6 = get_output('netstat -a -n -p tcpv6').split('\n')
	ipv6 = [i for i in ipv6 if '[::]' in i]
	ipv6 = parse(ipv6)
	ipv6 = map(get_port, ipv6)
	ipv6 = sorted(list(set(ipv6)))

	return ipv4, ipv6


def find_only():
	ipv4, ipv6 = get_listening_ports()
	logging.debug('ipv4: %s' % ipv4)
	logging.debug('ipv6: %s' % ipv6)
	ret4 = ipv4[:]
	for i in ipv6:
		if i in ret4: ret4.remove(i)
	ret6 = ipv6[:]
	for i in ipv4:
		if i in ret6: ret6.remove(i)
	logging.debug('ipv4_only: %s' % ret4)
	logging.debug('ipv6_only: %s' % ret6)
	return ret4, ret6


def shutdown_socket(sock):
	try:
		sock.shutdown(socket.SHUT_RDWR)
		sock.close()
	except:
		logging.error('socket shutdown failed')


class MainLoop():
	def __init__(self):
		self._run = False
		self._refresh = False

	def run(self):
		sock_pairs = []

		listen_socks = []
		listen_sock_to_port_map = {}

		t_last_check = 0

		self._run = True
		while self._run:
			t = time.monotonic()

			if t - t_last_check > 60 or self._refresh:  # TODO: hard-coded shit
				logging.debug('scanning for listening port changes')

				ipv4_only, ipv6_only = find_only()

				for p in ipv4_only:
					if p in listen_sock_to_port_map.values():
						continue
					logging.info('found new ipv4-only port %s' % p)
					s = socket.socket(socket.AF_INET6)
					s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
					s.bind(('::', p))
					s.listen(10)
					logging.debug('listening on port %s' % p)
					listen_socks.append(s)
					listen_sock_to_port_map[s] = p

				for s, p in listen_sock_to_port_map.copy().items():
					if not p in ipv6_only:
						continue
					logging.info('detected stale ipv6-only port %s' % p)
					listen_socks.remove(s)
					del listen_sock_to_port_map[s]
					s.close()

				self._refresh = False

				t_last_check = t

			rlist, wlist, xlist = listen_socks[:], [], listen_socks[:]

			for s1, s2 in sock_pairs:
				rlist.append(s1)
				rlist.append(s2)
				xlist.append(s1)
				xlist.append(s2)

			# this a workaround for windows because it can't handle when all lists are empty
			if not rlist and not wlist and not xlist:
				time.sleep(0.1)  # TODO: hard-coded shit
				rlist, wlist, xlist = [], [], []
			else:
				rlist, wlist, xlist = select.select(rlist, wlist, xlist, 1)  # TODO: hard-coded shit

			for s in listen_socks:
				if s in rlist:
					conn, addr = s.accept()
					logging.info('accept from %s for socket on port %s' % (addr, listen_sock_to_port_map[s], ))
					s2 = socket.socket(socket.AF_INET)
					try:
						s2.connect(('127.0.0.1', listen_sock_to_port_map[s]))
						sock_pairs.append((conn, s2))
					except socket.error as e:
						logging.error('failed to connect to local ipv4 socket. errno is %s' % e.errno)

				if s in xlist:
					logging.debug('listening socket in xlist')
					# TODO: do something
					#break

			for s1, s2 in sock_pairs[:]:
				shut_it_down = False

				if s1 in rlist:
					try:
						buf = s1.recv(100000)  # TODO: hard-coded shit
					except:
						logging.debug('s1.recv() exception, probably closed by remote end')
						buf = ''

					if len(buf) == 0:
						logging.debug('shutdown1')
						shut_it_down = True
					else:
						try:
							s2.send(buf)
						except:
							logging.exception('s2.send() exception')

				if s2 in rlist:
					try:
						buf = s2.recv(100000)  # TODO: hard-coded shit
					except:
						logging.debug('s2.recv() exception, probably closed by remote end')
						buf = ''

					if len(buf) == 0:
						logging.debug('shutdown2')
						shut_it_down = True
					else:
						try:
							s1.send(buf)
						except:
							logging.exception('s1.send() exception')

				if s1 in xlist:
					logging.debug('s1 in xlist')
					# TODO: do something

				if s2 in xlist:
					logging.debug('s2 in xlist')
					# TODO: do something

				if shut_it_down:
					shutdown_socket(s2)
					shutdown_socket(s1)
					sock_pairs.remove((s1, s2))

		logging.debug('exited loop')

		logging.info('shutting down listening sockets')
		for s in listen_socks:
			s.close()
		listen_socks.clear()

		logging.info('shutting down socket pairs')
		for s1, s2 in sock_pairs:
			socket_shutdown(s1)
			socket_shutdown(s2)
		sock_pairs.clear()

	def refresh(self):
		self._refresh = True

	def stop(self):
		self._run = False


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
