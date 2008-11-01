_-= wxPostReview =-_

Things that NEED to be Fixed:
 - Make post-review into a lib so it can be used by both the console and gui version
  - ie stop having to use my own hacked version of the console post-review
 - Expand wxPostReview so it can be used with other SCMs then P4
 - Stop using the old post-reviews diff generator

Known bugs:
 - Resizing doesn't always work correctly
 - If something goes wrong, there is no info given to the user as to what is happening
 - Still require a diff util for windows


Usage
 1) You'll need to have wxPython 2.8+ installed on your system
 2) You'll need to have the commandline P4 tool installed
 3) Edit the gui.pyw file
  Change: `REVIEWBOARD_HOST = None` to `REVIEWBOARD_HOST = <your rb server url>`
