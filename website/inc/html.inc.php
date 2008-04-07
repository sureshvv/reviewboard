<?php
	function site_start($title = "") {
		if ($title == "") {
			$title = "Review Board";
		} else {
			$title = "Review Board | " . $title;
		}
?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
 "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">

<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
 <head>
  <title><?php print $title; ?></title>
  <link rel="stylesheet" type="text/css" href="/css/site.css" />
  <link rel="icon" href="/favicon.ico" type="image/png" />
  <link rel="SHORTCUT ICON" href="/favicon.ico" type="image/png" />
 </head>
 <body>
  <div class="box-container">
   <div class="box pageheader">
    <div class="box-inner">
     <h1>Review Board</h1>
     <h2>Code reviews are fun again! ...almost.</h2>
    </div>
   </div>
  </div>
  <div class="box-container">
   <ul id="navbar">
    <li><a href="/blog/">Blog</a></li>
    <li><a href="http://demo.review-board.org/">Demo</a></li>
    <li><a href="http://flickr.com/photos/chipx86/sets/72157600297790516/detail/">Screen Shots</a></li>
    <li><a href="http://groups.google.com/group/reviewboard">Discuss</a></li>
    <li><a href="/users.php">Who Uses It</a></li>
    <li><a href="http://code.google.com/p/reviewboard/w/list">Wiki</a></li>
    <li><a href="http://code.google.com/p/reviewboard/">Development</a></li>
   </ul>
  </div>
  <div class="box-container">
   <div class="box contentbox">
    <div class="box-inner" id="content">
<?php
	}

	function site_end() {
?>
    </div>
   </div>
  </div>
  <script src="http://www.google-analytics.com/urchin.js" type="text/javascript"></script>
  <script type="text/javascript">
  _uacct = "UA-1584268-3";
  urchinTracker();
  </script>
 </body>
</html>
<?php
	}
?>
