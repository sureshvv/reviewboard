<?php
	require "consts.inc.php";

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
<?php

		site_body_start();
	}

	function site_body_start() {
		global $CURRENT_VERSION;
?>
  <div class="box-container">
   <table class="box pageheader">
    <colgroup>
     <col width="*" />
     <col width="1" />
     <col width="1" />
     <col width="1" />
    </colgroup>
    <tr>
     <td class="titlebox">
      <h1><a href="/">Review Board</a></h1>
      <h2>Code reviews are fun again! ...almost.</h2>
	  <p id="version"><b>Current release:</b> <?php print $CURRENT_VERSION; ?></p>
     </td>
     <td>
      <dl>
       <dt>About</dt>
       <dd><a href="/news/">News</a></dd>
       <dd><a href="/blog/">Developer Blogs</a></dd>
       <dd><a href="/screenshots/">Screenshots</a></dd>
       <dd><a href="/users.php">Happy Users</a></dd>
       <dd><a href="/media/">Media and Links</a></dd>
      </dl>
     </td>
     <td>
      <dl>
       <dt>Using</dt>
       <dd><a href="/downloads/">Downloads</a></dd>
       <dd><a href="http://demo.review-board.org/">Demo</a></dd>
       <dd><a href="/docs/">Documentation</a></dd>
       <dd><a href="http://groups.google.com/group/reviewboard">Mailing List</a></dd>
      </dl>
     </td>
     <td>
      <dl>
       <dt>Contributing</dt>
       <dd><a href="http://reviews.review-board.org/">Code Reviews</a></dd>
       <dd><a href="http://build.review-board.org/waterfall">Build Monitoring</a></dd>
       <dd><a href="/bugs/">Bug Tracker</a></dd>
       <dd><a href="/wiki/">Wiki</a></dd>
       <dd><a href="/donate/">Donate</a></dd>
      </dl>
     </td>
    </tr>
   </table>
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
