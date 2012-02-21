from distutils.core import setup
import py2exe

from ipv6listen import __version__

setup(
	console = ['ipv6listen.py', ],
	version = __version__,
	zipfile = None,
	options = {'py2exe': {'bundle_files': 1}}
)

setup(
	windows = ['ipv6listen_tray.py', ],
	version = __version__,
	zipfile = None,
	options = {'py2exe': {'bundle_files': 1}}
)
