import wx
import xmlrpclib

import logging
logger = logging.getLogger()

_exit = False

class Tray(wx.TaskBarIcon):
	def CreatePopupMenu(self):
		menu = wx.Menu()
		menu.Append(123, 'exit')
		self.Bind(wx.EVT_MENU, self.on_exit, id=123)
		return menu
	#enddef

	def on_exit(self, e):
		logger.debug('clicked exit')
		
		_s.exit()
	#enddef
#endclass

def main():
	logger.info('starting ipv6listen tray')

	global _s
	_s = xmlrpclib.ServerProxy('http://localhost:8888')

	app = wx.App(0)

	tb = Tray()

	logger.debug('loading icon')
	icon = wx.Icon('ipv6listen.png', wx.BITMAP_TYPE_PNG)
	tb.SetIcon(icon, 'dummy text')

	logger.info('starting MainLoop')
	app.MainLoop()
#enddef

if __name__ == '__main__':
	main()
#endif