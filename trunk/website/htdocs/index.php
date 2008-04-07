<?php
    require "html.inc.php";

    site_start();
?>
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
<table id="overviewshots">
 <tr>
  <td><img src="http://review-board.org/images/screenshots/reviewrequest_thumb.png" width="342" height="297" /></td>
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
  <td><img src="http://review-board.org/images/screenshots/diffviewer_thumb.png" width="342" height="297" /></td>
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
   <p>
    Every revision of a diff is stored. In the future, this will allow us
    to show the differences between revisions of the diff. This is especially
    valuable when there are several iterations of large diffs.
   </p>
  </td>
 </tr>
 <tr>
  <td><img src="http://review-board.org/images/screenshots/commentdlg_thumb.png" width="342" height="297" /></td>
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
  <td><img src="http://review-board.org/images/screenshots/reviews_thumb.png" width="342" height="297" /></td>
  <td>
   <h1>Contextual discussions and reviews</h1>
   <p>
    You already know that comments can be made directly on lines in the diff.
    Following that contextual model, we display discussions, comments, and
    lines of the diff inline on reviews. This allows people to read top to
    bottom and know exactly what people are talking about.
   </p>
  </td>
 </tr>
 <tr>
  <td><img src="http://review-board.org/images/screenshots/dashboard_thumb.png" width="342" height="297" /></td>
  <td>
   <h1>The dashboard</h1>
   <p>
    Every user gets a dashboard, which displays the list of outgoing and
    incoming reviews. You'll never miss a review request again.
   </p>
 </tr>
</table>
<?php
    site_end();
?>
