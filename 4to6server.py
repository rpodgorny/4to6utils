#!/usr/bin/python

from version import __version__

import sys
from utils import *

import logging
sys.excepthook = lambda type, value, traceback: logging.critical('unhandled exception', exc_info=(type, value, traceback))


def main():
	logging_setup('INFO', '4to6server.log')

	logging.info('*' * 40)
	logging.info('starting 4to6server v%s' % __version__)

	ml = MainLoop()

	try:
		ml.run()
	except KeyboardInterrupt:
		logging.debug('keyboard interrupt!')


if __name__ == '__main__':
	main()
