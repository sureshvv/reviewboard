<?php
    require "html.inc.php";

    site_start("Downloads");
?>
<p>
 Review Board is still in development, but is approaching an official release.
 We'll be releasing once <a href="http://www.djangoproject.com/">Django</a>
 provides a new official release.
</p>
<p>
 For time being, we recommend you use Review Board SVN. We work to keep
 SVN stable and usable in production environments.
</P>
<p>
 Review Board SVN can be checked out by typing the following on the
 command line:
</p>
<pre>
 $ svn checkout http://reviewboard.googlecode.com/svn/trunk/reviewboard
</pre>
<p>
 <a href="http://code.google.com/p/reviewboard/wiki/Documentation">Documentation</a>
 is available to help with the installation.
</p>
<?php
	site_end();
?>
