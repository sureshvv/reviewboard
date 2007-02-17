RB = {widgets: {}}

RB.widgets.InlineEditor = function(config) {
	YAHOO.ext.util.Config.apply(this, config);

	var dh = YAHOO.ext.DomHelper;

	this.el = getEl(this.el);
	this.el.setVisibilityMode(YAHOO.ext.Element.DISPLAY);

	this.form = dh.insertBefore(this.el.dom, {
		tag: 'form',
		cls: 'inline-editor-form ' + (this.cls || ''),
	}, true);
	this.form.setVisibilityMode(YAHOO.ext.Element.DISPLAY);

	var saveButton = {
		tag: 'input',
		type: 'submit',
		value: 'Save',
		cls: 'save',
	};

	var cancelButton = {
		tag: 'input',
		type: 'submit',
		value: 'Cancel',
		cls: 'cancel',
	};

	if (this.multiline) {
		this.field = this.form.createChild({
			tag: 'textarea',
			html: this.value || '',
			wrap: 'none',
			rows: this.rows || 10,
			cols: this.cols || 80,
		});

		block = this.form.createChild({tag: 'div'});
		this.saveButton = block.createChild(saveButton);
		this.cancelButton = block.createChild(cancelButton);
	} else {
		this.field = this.form.createChild({
			tag: 'input',
			type: 'text',
		});

		this.saveButton = this.form.createChild(saveButton);
		this.cancelButton = this.form.createChild(cancelButton);
	}

	if (this.showEditIcon) {
		var img = {
			tag: 'img',
			cls: 'editicon',
			src: '/images/edit.png',
			width: 14,
			height: 14,
		};

		if (this.multiline) {
			var labels = this.findLabelForId(this.el.id);

			if (labels.length > 0) {
				this.editicon = dh.append(labels[0], img, true);
			}
		} else {
			this.editicon = dh.insertAfter(this.el.dom, img, true);
		}

		if (this.editicon) {
			this.editicon.setVisibilityMode(YAHOO.ext.Element.DISPLAY);
			this.editicon.on('click', this.startEdit, this, true);
		}
	}

	this.events = {
		'complete': true,
	};

	this.el.on('click', this.startEdit, this, true);
	this.saveButton.on('click', this.save, this, true);
	this.cancelButton.on('click', this.cancel, this, true);

	this.field.addKeyMap([
		{
			key: [10, 13],
			fn: this.onEnter,
			scope: this,
		},
		{
			key: 27,
			fn: this.onEscape,
			scope: this,
		}
	]);

	this.hide();
}

YAHOO.extendX(RB.widgets.InlineEditor, YAHOO.ext.util.Observable, {
	onBlur: function(e) {
		if (this.editing) {
			this.completeEdit();
		}
	},

	onEnter: function(k, e) {
		if (!this.multiline || e.ctrlKey) {
			this.save();
		}
	},

	onEscape: function() {
		this.cancel();
	},

	startEdit: function() {
		var value = this.el.dom.innerHTML;
		this.initialValue = value;
		this.setValue(value);
		this.editing = true;
		this.show();
	},

	completeEdit: function() {
		var value = this.getValue();
		this.hide();

		if (this.initialValue != value) {
			this.el.dom.innerHTML = value;
			this.fireEvent('complete', this, value, this.initialValue);
		}
	},

	save: function(e) {
		if (e) {
			e.preventDefault();
		}

		this.completeEdit();
	},

	cancel: function(e) {
		if (e) {
			e.preventDefault();
		}
		this.el.dom.innerHTML = this.initialValue;
		this.hide();
	},

	show: function() {
		if (this.editicon) {
			this.editicon.hide();
		}

		this.form.show();
		this.autoSize();
		this.el.hide();
		this.field.focus();
	},

	hide: function() {
		this.editing = false;
		this.form.hide();
		this.form.setLeftTop(-10000, -10000);
		this.field.blur();
		this.el.show();

		if (this.editicon) {
			this.editicon.show();
		}
	},

	moveTo: function(xy) {
		this.form.setXY(xy);
	},

	setValue: function(value) {
		this.field.dom.value = value;
	},

	getValue: function() {
		return this.field.dom.value;
	},

	autoSize: function() {
		var parentNode = getEl(this.el.dom.parentNode, true);
		var elWidth = this.el.getWidth();

		if (this.multiline) {
			this.form.setWidth(elWidth);
			this.field.fitToParent();
		} else {
			var parentWidth = parentNode.getWidth();
			this.form.setHeight(this.el.getHeight());
			this.form.setWidth(
				Math.min(elWidth + (parentWidth - elWidth) / 2, parentWidth));

			var buttonsWidth =
				this.cancelButton.getX() - this.saveButton.getX() +
				this.cancelButton.getWidth() +
				this.saveButton.getX() - (this.field.getX() +
				                          this.field.getWidth());
			this.field.setWidth(this.form.getWidth() - buttonsWidth);
		}
	},

	findLabelForId: function(id) {
		var method = function(el) {
			return (el.getAttribute('for') == id);
		};

		return YAHOO.util.Dom.getElementsBy(method, 'label', document);
	},
});
