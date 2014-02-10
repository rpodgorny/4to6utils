import sys
from version import __version__


if sys.platform == 'win32':
	from cx_Freeze import setup, Executable

	base = 'Win32GUI'

	executables = [
		Executable(
			script='ipv6listen.py',
			appendScriptToExe=True,
			appendScriptToLibrary=False,
			compress=True,
		),
		Executable(
			script='ipv6listen_gui.py',
			appendScriptToExe=True,
			appendScriptToLibrary=False,
			compress=True,
			base=base
		),
		Executable(
			script='4to6.py',
			appendScriptToExe=True,
			appendScriptToLibrary=False,
			compress=True,
		),
	]

	setup(
		name = 'ipv6utils',
		version = __version__,
		options = {
			'build_exe': {
				'includes': ['re', ],
				'create_shared_zip': False,
				'compressed': True,
				'include_msvcr': True,
				'include_files': ['ipv6listen.png', ]
			},
		},
		executables = executables,
	)
else:
	'''
	from setuptools import setup, find_packages

	setup(
		name = 'faddns',
		version = __version__,
		options = {
			'build_exe': {
				'compressed': True,
				'include_files': ['faddns.png', 'faddnsc.ini']
			},
		},
		scripts = ['faddnsc'],
		#packages = find_packages(),
		py_modules = ['cfg', 'faddns', 'version'],
	)'''
	pass
#endif
