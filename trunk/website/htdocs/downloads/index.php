<?php
    require "html.inc.php";

    site_start("Downloads");
?>
<h1>Releases</h1>
<p>
 The current release of Review Board is <b>1.0 alpha 1</b>.
</p>
<p>
 New Review Board releases are downloaded and installed automatically through
 our installer. See the <a href="/docs/GettingStarted">Getting Started</a>
 guide for instructions.
</p>
<p>
 All releases can be manually downloaded from our
 <a href="releases/">releases</a> directory.
</p>

<h1>Nightly Builds</h1>
<p>
 People wishing to use the latest and greatest in-development builds of
 Review Board can install our nightly builds. See our
 <a href="/docs/GettingStarted">Getting Started</a> guide for instructions.
</p>
<p>
 Note that these builds can be unstable, so use at your own risk. We do try
 to keep them as bug-free as possible, though.
</p>
<p>
 Nightlies can be manually downloaded from our
 <a href="nightlies/">nightlies</a> directory.
</p>

<h1>Bleeding Edge (SVN)</h1>
<p>
 Review Board SVN can be checked out by typing the following on the
 command line:
</p>
<pre>
 $ svn checkout http://reviewboard.googlecode.com/svn/trunk/reviewboard
</pre>
<p>
 <a href="/docs">Documentation</a> is available to help with the installation.
</p>
<?php
	site_end();
?>
