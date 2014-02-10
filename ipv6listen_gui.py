#!/usr/bin/python3

from version import __version__

from ipv6listen import *
from PySide.QtCore import *
from PySide.QtGui import *
import threading

import logging
sys.excepthook = lambda type, value, traceback: logging.critical('unhandled exception', exc_info=(type, value, traceback))


class MyTray(QSystemTrayIcon):
	def __init__(self, app, ml):
		icon = QIcon('ipv6listen.png')
		super().__init__(icon)

		self.app = app
		self.ml = ml

		self.setToolTip('ipv6listen_gui v%s' % __version__)

		menu = QMenu()
		menu.addAction('Force refresh', self.on_refresh)
		menu.addAction('Exit', self.on_exit)
		self.setContextMenu(menu)

		self.show()
	#enddef

	def on_refresh(self):
		logging.info('forced refresh')

		self.ml.refresh()
	#enddef

	def on_exit(self):
		self.app.quit()
	#enddef
#endclass


def main():
	logging_setup('DEBUG', 'ipv6listen_gui.log')

	logging.info('*' * 40)
	logging.info('starting ipv6listen tray v%s' % __version__)

	ml = MainLoop()
	thr = threading.Thread(target=ml.run)
	thr.start()

	app = QApplication(sys.argv[1:])

	tray = MyTray(app, ml)

	app.exec_()

	ml.stop()
	thr.join()

	logging.info('exit')
#enddef


if __name__ == '__main__':
	main()
#endif