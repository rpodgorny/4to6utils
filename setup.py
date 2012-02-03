from distutils.core import setup
import py2exe

from ipv6listen import __version__ as version

setup(
	windows = ['ipv6listen.py', ],
	version = version,
	zipfile = None,
	options = {'py2exe': {'bundle_files': 1}}
)
