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
		high = cell.innerHTML;
	}

	for (var i = Math.round((low + high) / 2);
	     low < high - 1;
		 i = Math.round((low + high) / 2)) {
		var row = table.rows[row_offset + i];
		cell = (row.cells.length == 4 ? row.cells[1] : row.cells[0]);
		var value = parseInt(cell.innerHTML);

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

function addComments(fileid, lines) {
	var table = document.getElementById(fileid);

	for (linenum in lines) {
		var cell = findLineNumCell(table, parseInt(linenum));

		if (cell != null) {
			cell.innerHTML = "<span class=\"commentflag\" style=\"top: " +
							 getEl(cell).getY() + "px;\">" +
							 lines[linenum].length + "</span>" +
							 "<a name=\"" + fileid + ".line" + linenum +
							 "\">" + linenum + "</a>";
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
