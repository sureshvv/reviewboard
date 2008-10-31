from distutils.core import setup
import py2exe

setup(windows=[
	{
		"script": "gui.pyw",
		"icon_resources": [(1, "favicon.ico")],
	}
	],)
