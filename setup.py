from cx_Freeze import setup, Executable

from version import __version__

executables = [
	Executable(
		script='4to6server.py',
		#appendScriptToExe=True,
		#appendScriptToLibrary=False,
		#compress=True,
	),
	Executable(
		script='4to6client.py',
		#appendScriptToExe=True,
		#appendScriptToLibrary=False,
		#compress=True,
	),
]

setup(
	name = '4to6utils',
	version = __version__,
	options = {
		'build_exe': {
			'includes': ['re', ],
			#'create_shared_zip': False,
			#'compressed': True,
			'include_msvcr': True,
		},
	},
	executables = executables,
)