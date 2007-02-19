RB = {utils: {}}

RB.utils.String = function() {};
RB.utils.String.prototype = {
	strip: function() {
		return this.replace(/^\s+/, '').replace(/\s+$/, '');
	},

	stripTags: function() {
		return this.replace(/<\/?[^>]+>/gi, '');
	},
};

YAHOO.augment(String, RB.utils.String);
