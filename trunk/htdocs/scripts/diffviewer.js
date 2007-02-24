var dh = YAHOO.ext.DomHelper;

CommentDialog = function(el) {
	CommentDialog.superclass.constructor.call(this, el, {
		width: 550,
		height: 450,
		shadow: true,
		minWidth: 400,
		minHeight: 300,
		autoTabs: true,
		proxyDrag: true,
		constraintoviewport: false,
		fixedcenter: true,
	});

	var tabs = this.getTabs();

	this.commentsTab = tabs.getTab("tab-comments");
	this.commentForm = getEl('commentform');
	this.commentForm.enableDisplayMode();

	this.newCommentField = getEl('id_comment');
	this.existingComments = getEl('existing-comments');
	this.inlineEditor = null;

	this.addKeyListener(27, this.closeDlg, this);
	this.setDefaultButton(this.addButton("Close", this.closeDlg, this));
	this.postButton = this.addButton("Save Comment", this.postComment, this);
	this.postButton.hide();
	this.deleteButton = this.addButton("Delete Comment",
	                                   this.deleteComment, this);
	this.deleteButton.hide();

	this.messageDiv = dh.insertBefore(this.deleteButton.getEl().dom,
		{tag: 'div', id: 'comment-status'}, true);

	/* Prevent navigation keypresses in the comments textarea. */
	getEl(el).on("keypress", function(e) {
		YAHOO.util.Event.stopPropagation(e);
	}, this, true);

	tabs.on('tabchange', function() {
		this.updateButtonVisibility();
		this.hideMessage();
	}, this, true);
	this.updateButtonVisibility();

	this.on('resize', this.resizeCommentField, this, true);
	this.on('show', function() {
		if (this.commentForm.isVisible()) {
			this.newCommentField.focus();
		}
	}, this, true);
}

YAHOO.extendX(CommentDialog, YAHOO.ext.BasicDialog, {
	closeDlg: function() {
		this.hide(this.checkEmptyCommentBlock.createDelegate(this));
	},

	checkEmptyCommentBlock: function() {
		if (this.commentBlock && this.commentBlock.count == 0) {
			var commentBlock = this.commentBlock;
			this.commentBlock = null;

			commentBlock.el.hide(true, .35, function() {
				commentBlock.el.remove();
				commentBlock = null;
			});
		}
	},

	resizeCommentField: function(b, w, h) {
		if (this.commentForm.isVisible()) {
			this.newCommentField.setSize(w - 50,
				(this.commentBlock.count == 0 ? h - 200 : 100));
		} else {
			this.inlineEditor.field.setWidth(w - 50);
		}
	},

	setCommentBlock: function(commentBlock) {
		if (this.commentBlock != commentBlock) {
			this.checkEmptyCommentBlock();
		}

		this.commentBlock = commentBlock;
		this.updateCommentsList();
		this.newCommentField.dom.value = this.commentBlock.localComment;
		getEl('id_num_lines').dom.value = 1; // XXX
	},

	updateCommentsList: function() {
		var url = "comments/" + this.commentBlock.filediffid + "/" +
		         this.commentBlock.linenum + "/";
		YAHOO.util.Connect.asyncRequest("GET", url, {
			success: function(res) {
				this.hideMessage();
				this.populateComments(res.responseText);
			}.createDelegate(this),

			failure: function(res) {
				this.showError(res.statusText);
			}.createDelegate(this),
		});
	},

	populateComments: function(html) {
		this.existingComments.dom.innerHTML = html;
		this.updateCommentCount();

		var inlineCommentField = document.getElementById('id_yourcomment');
		if (inlineCommentField) {
			this.postButton.disable();
			this.deleteButton.disable();

			this.inlineEditor = new RB.widgets.InlineEditor({
				el: inlineCommentField,
				multiline: true,
				cls: 'inline-comment-editor',
				showEditIcon: true,
				stripTags: true,
				hideButtons: true,
			});

			this.inlineEditor.on('beginedit', function(editor) {
				this.postButton.enable();
				this.deleteButton.enable();
				getEl(inlineCommentField).scrollIntoView(
					this.commentsTab.bodyEl.dom.parentNode);
			}, this, true);

			this.commentForm.hide();
		} else {
			this.postButton.enable();
			this.deleteButton.disable();
			this.inlineEditor = null;
			this.commentForm.show();
		}

		this.resizeCommentField(null, this.width, this.height);

		// Scroll to the bottom.
		var scrollNode = this.commentsTab.bodyEl.dom.parentNode;
		scrollNode.scrollTop = scrollNode.scrollHeight;
	},

	updateCommentCount: function() {
		var count = this.existingComments.getChildrenByClassName("comment",
		                                                         "li").length;
		this.commentBlock.setCount(count);
		this.commentsTab.setText("Comments (" + count + ")");
	},

	updateButtonVisibility: function() {
		var activeTab = this.getTabs().getActiveTab();

		if (activeTab == this.commentsTab) {
			this.postButton.show();
			this.deleteButton.show();
		} else {
			this.postButton.hide();
			this.deleteButton.hide();
		}
	},

	postComment: function() {
		var commentEl = getEl("id_comment");

		if (this.inlineEditor) {
			commentEl.dom.value = this.inlineEditor.getValue();
			this.inlineEditor.completeEdit();
		}

		var text = commentEl.dom.value;

		if (text.strip() == "") {
			this.showError("Please fill out the comment text.");
			return;
		}

		getEl('id_action').dom.value = "set";

		var url = "comments/" + this.commentBlock.filediffid + "/" +
		         this.commentBlock.linenum + "/";
		YAHOO.util.Connect.setForm(this.commentForm.dom);
		YAHOO.util.Connect.asyncRequest("POST", url, {
			success: function(res) {
				this.hideMessage();
				this.commentBlock.localComment = "";
				this.commentBlock.setHasDraft(true);
				this.populateComments(res.responseText);
				this.closeDlg();
			}.createDelegate(this),

			failure: function(res) {
				this.showError(res.statusText);
			}.createDelegate(this),
		});
	},

	deleteComment: function() {
		getEl('id_action').dom.value = "delete";

		var url = "comments/" + this.commentBlock.filediffid + "/" +
		         this.commentBlock.linenum + "/";
		YAHOO.util.Connect.setForm(this.commentForm.dom);
		YAHOO.util.Connect.asyncRequest("POST", url, {
			success: function(res) {
				this.hideMessage();
				this.commentBlock.localComment = "";
				this.commentBlock.setHasDraft(false);
				this.newCommentField.dom.value = "";
				this.existingComments.dom.innerHTML = res.responseText;
				this.updateCommentCount();
				this.closeDlg();
			}.createDelegate(this),

			failure: function(res) {
				this.showError(res.statusText);
			}.createDelegate(this),
		});
	},

	showError: function(text) {
		this.showMessage(text, "error");
	},

	showMessage: function(message, className) {
		this.messageDiv.dom.innerHTML = message

		if (className) {
			this.messageDiv.dom.className = className;
		}

		this.messageDiv.show();
	},

	hideMessage: function() {
		this.messageDiv.dom.className = "";
		this.messageDiv.hide();
	},
});


CommentBlock = function(fileid, lineNumCell, linenum, comments) {
	this.setCount = function(count) {
		this.count = count;
		this.el.dom.innerHTML = this.count;
	};

	this.setHasDraft = function(hasDraft) {
		if (hasDraft) {
			this.el.addClass("draft");
		} else {
			this.el.removeClass("draft");
		}
	};

	this.showCommentDlg = function() {
		if (gCommentDlg == null) {
			gCommentDlg = new CommentDialog("comment-dlg");
		}

		gCommentDlg.setCommentBlock(this);
		gCommentDlg.show(this.el);
	};

	this.fileid = fileid;
	this.filediffid = gFileAnchorToId[fileid];
	this.comments = comments;
	this.linenum = linenum;
	this.localComment = "";

	this.el = dh.append(lineNumCell, {
		tag: 'span',
		cls: 'commentflag',
	}, true);

	for (comment in comments) {
		if (comments[comment].localdraft) {
			this.localComment = comments[comment].text;
			this.setHasDraft(true);
			break;
		}
	}

	this.el.setTop(getEl(lineNumCell).getY());
	this.el.on('click', function(e) {
		YAHOO.util.Event.stopEvent(e);
		this.showCommentDlg();
	}, this, true);

	this.setCount(comments.length);
};


// Constants
var BACKWARD = -1;
var FORWARD  = 1;
var INVALID  = -1;
var DIFF_SCROLLDOWN_AMOUNT = 100;
var VISIBLE_CONTEXT_SIZE = 5;

var gActions = [
	{ // Previous file
		keys: "aAKP<m",
		onPress: function() { scrollToAnchor(GetNextFileAnchor(BACKWARD)); }
	},

	{ // Next file
		keys: "fFJN>/",
		onPress: function() { scrollToAnchor(GetNextFileAnchor(FORWARD)); }
	},

	{ // Previous diff
		keys: "sSkp,,",
		onPress: function() { scrollToAnchor(GetNextAnchor(BACKWARD)); }
	},

	{ // Next diff
		keys: "dDjn..",
		onPress: function() { scrollToAnchor(GetNextAnchor(FORWARD)); }
	},

	{ // Recenter
		keys: unescape("%0D"),
		onPress: function() { scrollToAnchor(gSelectedAnchor); }
	},

	{ // Go to header
		keys: "gu;",
		onPress: function() {}
	},

	{ // Go to footer
		keys: "GU:",
		onPress: function() {}
	},
];

// State variables
var gSelectedAnchor = INVALID;
var gCurrentAnchor = 0;
var gFileAnchorToId = {};
var gCommentDlg = null;
var gGhostCommentFlag = null;

YAHOO.util.Event.on(window, "load", onPageLoaded);

function onKeyPress(evt) {
	var keyChar = String.fromCharCode(YAHOO.util.Event.getCharCode(evt));

	for (var i = 0; i < gActions.length; i++) {
		if (gActions[i].keys.indexOf(keyChar) != -1) {
			gActions[i].onPress();
			return;
		}
	}
}

function gotoAnchor(name) {
	return scrollToAnchor(GetAnchorByName(name));
}

function GetAnchorByName(name) {
	for (var anchor = 0; anchor < document.anchors.length; anchor++) {
		if (document.anchors[anchor].name == name) {
			return anchor;
		}
	}

	return INVALID;
}

function onPageLoaded(evt) {
	/* Skip over the change index to the first item */
	gSelectedAnchor = 1;
	SetHighlighted(gSelectedAnchor, true)

	YAHOO.util.Event.on(window, "keypress", onKeyPress);
}

function findLineNumCell(table, linenum) {
	var cell = null;
	var found = false;
	var row_offset = 1; // Get past the headers.

	if (table.rows.length - row_offset > linenum) {
		var norm_row = row_offset + linenum;
		var row = table.rows[row_offset + linenum];

		// Account for the "x lines hidden" row.
		if (row != null && row.cells.length > 3) {
			cell = (row.cells.length == 4 ? row.cells[1] : row.cells[0]);

			if (parseInt(cell.innerHTML) == linenum) {
				return cell;
			}
		}
	}

	/* Binary search for this cell. */
	var low = 1;
	var high = table.rows.length;

	if (cell != null) {
		/*
		 * We collapsed the rows (unless someone mucked with the DB),
		 * so the desired row is less than the row number retrieved.
		 */
		high = parseInt(cell.innerHTML);
	}

	console.debug("checking for line...");

	for (var i = Math.round((low + high) / 2);
	     low < high - 1;
		 i = Math.round((low + high) / 2)) {
		var row = table.rows[row_offset + i];
		cell = (row.cells.length == 4 ? row.cells[1] : row.cells[0]);
		var value = parseInt(cell.innerHTML);

		if (!value) {
			// This is a "..." line or some such. Compute with the next highest
			i++;
			row = table.rows[row_offset + i];
			cell = (row.cells.length == 4 ? row.cells[1] : row.cells[0]);
			value = parseInt(cell.innerHTML);
		}

		if (value > linenum) {
			high = i;
		} else if (value < linenum) {
			low = i;
		} else {
			return cell;
		}
	}

	// Well.. damn. Ignore this then.
	return null;
}

function isLineNumCell(cell) {
	var content = cell.innerHTML;

	return (cell.tagName == "TH" &&
	        cell.parentNode.parentNode.tagName == "TBODY" &&
	        cell.className != "controls" && content != "..." &&
		    parseInt(content) != NaN);
}

function addComments(fileid, lines) {
	var table = getEl(fileid);

	table.on('click', function(e) {
		var node = e.target;
		if (isLineNumCell(node)) {
			YAHOO.util.Event.stopEvent(e);
			var commentBlock = new CommentBlock(fileid, node,
			                                    parseInt(node.innerHTML), []);
			commentBlock.showCommentDlg();
		} else {
			var tbody = null;

			if (node.tagName == "PRE") {
				tbody = getEl(node.parentNode.parentNode.parentNode);
			} else if (node.tagName == "TD") {
				tbody = getEl(node.parentNode.parentNode);
			}

			if (tbody &&
			    (tbody.hasClass("delete") || tbody.hasClass("insert") ||
				 tbody.hasClass("replace"))) {
				gotoAnchor(tbody.dom.getElementsByTagName("A")[0].name);
			}
		}
	});

	table.on('mouseover', function(e) {
		var node = e.target;
		if (isLineNumCell(node) && node.childNodes.length == 1) {
			if (!gGhostCommentFlag) {
				gGhostCommentFlag = dh.append(document.body, {
					tag: 'img',
					src: '/images/comment-ghost.png',
				}, true);
				gGhostCommentFlag.enableDisplayMode();
				gGhostCommentFlag.setAbsolutePositioned();
				gGhostCommentFlag.setX(2);
			}

			getEl(node).setStyle("cursor", "pointer");

			gGhostCommentFlag.setTop(getEl(node).getY() - 1);
			gGhostCommentFlag.show();
		}
	});

	table.on('mouseout', function(e) {
		var relTarget = e.relatedTarget || e.toElement;
		if (gGhostCommentFlag && relTarget != gGhostCommentFlag.dom) {
			gGhostCommentFlag.hide();
		}
	});

	for (linenum in lines) {
		linenum = parseInt(linenum);
		var cell = findLineNumCell(table.dom, linenum);

		if (cell != null) {
			new CommentBlock(fileid, cell, linenum, lines[linenum]);
		}
	}
}

function scrollToAnchor(anchor) {
	if (anchor == INVALID) {
		return false;
	}

	window.scrollTo(0,
		getEl(document.anchors[anchor]).getY() - DIFF_SCROLLDOWN_AMOUNT);
	SetHighlighted(gSelectedAnchor, false);
	SetHighlighted(anchor, true);
	gSelectedAnchor = anchor;

	return true;
}

function GetNextAnchor(dir) {
	for (var anchor = gSelectedAnchor + dir; ; anchor = anchor + dir) {
		if (anchor < 0 || anchor >= document.anchors.length) {
			return INVALID;
		}

		var name = document.anchors[anchor].name;

		if (name == "index_header" || name == "index_footer") {
			return INVALID;
		} else if (name.substr(0, 4) != "file") {
			return anchor;
		}
	}
}

function GetNextFileAnchor(dir) {
	var fileId = document.anchors[gSelectedAnchor].name.split(".")[0];
	var newAnchor = parseInt(fileId) + dir;
	return GetAnchorByName(newAnchor);
}

function SetHighlighted(anchor, highlighted) {
	var anchorNode = document.anchors[anchor];
	var node = anchorNode.parentNode;
	var nextNode = anchorNode.nextSibling.nextSibling;
	var controlsNode;

	if (node.tagName == "TD" || node.tagName == "TH") {
		controlsNode = node.parentNode.getElementsByTagName('th')[0].firstChild.nextSibling;
	}
	else if (nextNode.className == "sidebyside") {
		controlsNode = nextNode.getElementsByTagName('th')[0].firstChild;
	}
	else {
		return;
	}

	controlsNode.nodeValue = (highlighted ? "▶" : "");
}
