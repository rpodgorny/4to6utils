from ipv6listen import __version__

import wx
import xmlrpclib

import log
sys.excepthook = log.log_exception
log.filename = 'ipv6listen_tray.log'

_exit = False

class Tray(wx.TaskBarIcon):
	def CreatePopupMenu(self):
		menu = wx.Menu()
		menu.Append(123, 'exit')
		self.Bind(wx.EVT_MENU, self.on_exit, id=123)
		return menu
	#enddef

	def on_exit(self, e):
		log.log('clicked exit')
		
		_s.exit()
	#enddef
#endclass

def main():
	log.log('*' * 40)
	log.log('starting ipv6listen tray v%s' % __version__)

	global _s
	_s = xmlrpclib.ServerProxy('http://localhost:8888')

	app = wx.App(0)

	tb = Tray()

	log.log('loading icon')
	icon = wx.Icon('ipv6listen.png', wx.BITMAP_TYPE_PNG)
	tb.SetIcon(icon, 'dummy text')

	log.log('starting MainLoop')
	app.MainLoop()
#enddef

if __name__ == '__main__':
	main()
#endif