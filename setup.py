import sys
from version import __version__


if sys.platform == 'win32':
	from cx_Freeze import setup, Executable

	executables = [
		Executable(
			script='4to6server.py',
			appendScriptToExe=True,
			appendScriptToLibrary=False,
			compress=True,
		),
		Executable(
			script='4to6client.py',
			appendScriptToExe=True,
			appendScriptToLibrary=False,
			compress=True,
		),
	]

	setup(
		name = '4to6utils',
		version = __version__,
		options = {
			'build_exe': {
				'includes': ['re', ],
				'create_shared_zip': False,
				'compressed': True,
				'include_msvcr': True,
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
