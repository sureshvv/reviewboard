from distutils.core import setup
try:
  import py2exe
  print "Running on Windows"
except ImportError:
  print "Not Running on Windows"
try:
  import py2app
  print "Running on OSX"
except ImportError:
  print "Not Running on OSX"

setup(
windows=[
	{
		"script": "gui.pyw",
		"icon_resources": [(1, "favicon.ico")],
	}
	],
app=[
	{
		"script": "gui.pyw",
	}
	],
	)
