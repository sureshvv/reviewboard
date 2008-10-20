<?php
    require "html.inc.php";

    site_start();
?>
<blockquote class="testimonial">
 <div class="quote">
  Review Board has changed the way we review code changes, enforce high quality
  coding standards and styles, and generally mentor new developers.  Every
  time you visit <a href="http://search.yahoo.com/">search.yahoo.com</a>
  you use code that has been reviewed on review board. We're great fans of
  your work!
 </div>
 <div class="source">&mdash; Yahoo! Web Search</div>
</blockquote>

<div><a href="/donate/"><img src="https://www.paypal.com/en_US/i/btn/btn_donate_LG.gif" /></a></div>

<p>
 For too long, code reviews have been too much of a chore. This is largely
 due to the lack of quality tools available, leaving developers to resort to
 e-mail and bug tracker-based solutions.
</p>
<p>
 At <a href="http://www.vmware.com/">VMware</a>, we've traditionally done
 code reviews over e-mail. A significant amount of time was wasted in forming
 review requests, switching between the diff and the e-mail, and trying to
 understand what parts of the code the reviewer was referring to. We decided
 to fix all that.
</p>
<p>
 Review Board is a powerful web-based code review tool that offers
 developers an easy way to handle code reviews. It scales well from small
 projects to large companies and offers a variety of tools to take much
 of the stress and time out of the code review process.
</p>
<table id="overviewshots">
 <tr>
  <td><a href="http://flickr.com/photos/chipx86/525300364/in/set-72157600297790516/"><img src="http://review-board.org/images/screenshots/reviewrequest_thumb.png" width="342" height="297" /></a></td>
  <td>
   <h1>Detailed review requests</h1>
   <p>
    All the information on a change is available at a glance. Authors can
    modify the information quickly and easily through the web UI. Screenshots
    can be added and commented on.
   </p>
   <p>
    Review requests can be created through the "New Review Request" page,
    or updated through the post-review tool on compatible revision control
    systems, making it easy to file new review requests.
   </p>
  </td>
 </tr>
 <tr>
  <td><a href="http://flickr.com/photos/chipx86/525300334/in/set-72157600297790516/"><img src="http://review-board.org/images/screenshots/diffviewer_thumb.png" width="342" height="297" /></a></td>
  <td>
   <h1>Powerful diff viewer</h1>
   <p>
    Diffs are no longer something you just read. Now you can interact with
    them, commenting directly on the lines you're reviewing. The comments,
    along with the lines of the diff, will appear on the review.
   </p>
   <p>
    Keyboard shortcuts make it easy to jump around the diff. For example,
    pressing "n" will jump to the next changed chunk, while "p" will jump
    to the previous.
   </p>
   <p>
    To improve readability, we display syntax highlighting in the diff
    and show the changes within a lines in a "replace" block.
   </p>
   <p>
    Every revision of a diff is stored. This allows the user to look at any
	revision of the diff and also to see the differences between revisions.
    This is especially valuable when there are several iterations of large
	diffs.
   </p>
  </td>
 </tr>
 <tr>
  <td><a href="http://flickr.com/photos/chipx86/525300318/in/set-72157600297790516/"><img src="http://review-board.org/images/screenshots/commentdlg_thumb.png" width="342" height="297" /></a></td>
  <td>
   <h1>Comment and review dialog</h1>
   <p>
    Reviews of code are made in the Comment dialog on the diff viewer page.
    Clicking a line or a comment flag will take you here, allowing you to
    comment on the review. When finished, the review can be finalized and
    published on the Review tab.
   </p>
  </td>
 </tr>
 <tr>
  <td><a href="http://flickr.com/photos/chipx86/525300366/in/set-72157600297790516/"><img src="http://review-board.org/images/screenshots/reviews_thumb.png" width="342" height="297" /></a></td>
  <td>
   <h1>Contextual discussions and reviews</h1>
   <p>
    You already know that comments can be made directly on lines in the diff.
    Following that contextual model, we display discussions, comments, and
    lines of the diff inline on reviews. This allows people to read top to
    bottom and know exactly what people are talking about.
   </p>
   <p>
    We even display clips of commented regions of screenshots!
   </p>
  </td>
 </tr>
 <tr>
  <td><a href="http://flickr.com/photos/chipx86/525300328/in/set-72157600297790516/"><img src="http://review-board.org/images/screenshots/dashboard_thumb.png" width="342" height="297" /></a></td>
  <td>
   <h1>The dashboard</h1>
   <p>
    Every user gets a dashboard, which displays the list of outgoing and
    incoming reviews. You'll never miss a review request again.
   </p>
   <p>
    The dashboard is customizable. Columns can be rearranged, new columns
    can be added and unwanted columns can be removed. The dashboard
    can be sorted using two-level sorting.
   </p>
 </tr>
</table>
<?php
    site_end();
?>
