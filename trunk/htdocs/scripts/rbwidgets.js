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

	this.saveButton.setVisibilityMode(YAHOO.ext.Element.DISPLAY);
	this.cancelButton.setVisibilityMode(YAHOO.ext.Element.DISPLAY);

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

	YAHOO.ext.EventManager.onWindowResize(this.fitWidthToParent, this, true);

	this.hide();
}

YAHOO.extendX(RB.widgets.InlineEditor, YAHOO.ext.util.Observable, {
	onEnter: function(k, e) {
		if (!this.multiline || e.ctrlKey) {
			this.save();
		}
	},

	onEscape: function() {
		this.cancel();
	},

	startEdit: function() {
		var value = this.html2text(this.el.dom.innerHTML);
		this.initialValue = value;
		this.setValue(value);
		this.editing = true;
		this.show();
	},

	completeEdit: function() {
		var value = this.text2html(this.getValue());
		this.el.dom.innerHTML = value;

		this.hide();
		this.editing = false;

		if (this.initialValue != value) {
			this.fireEvent('complete', this, value, this.initialValue);
		}
	},

	html2text: function(str) {
		str = str.replace(/&amp;/g, "&");
		str = str.replace(/&lt;/g, "<");
		str = str.replace(/&gt;/g, ">");
		return str;
	},

	text2html: function(str) {
		str = str.replace(/&/g, "&amp;");
		str = str.replace(/</g, "&lt;");
		str = str.replace(/>/g, "&gt;");
		return str;
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
		this.editing = false;
	},

	show: function() {
		if (this.editicon) {
			this.editicon.hide();
		}

		this.saveButton.show();
		this.cancelButton.show();
		this.form.show();
		this.fitWidthToParent();

		if (this.multiline) {
			var elHeight = this.el.getHeight();
			this.field.setHeight(elHeight);
			var attrs = { height: {to: elHeight + 100} };
			var anim = new YAHOO.util.Anim(this.field.dom, attrs, 0.5,
			                               YAHOO.util.Easing.easeOut);
			anim.animate();
		}

		this.el.hide();
		this.field.focus();
	},

	hide: function() {
		this.saveButton.hide();
		this.cancelButton.hide();

		if (this.multiline && this.editing) {
			this.el.beginMeasure();
			var box = this.el.getBox(true, true);
			var elHeight = box.height;
			this.el.endMeasure();

			var attrs = { height: {to: elHeight} };
			var anim = new YAHOO.util.Anim(this.field.dom, attrs, 0.5,
			                               YAHOO.util.Easing.easeOut);
			anim.onComplete.subscribe(this.finishHide, this, true);
			anim.animate();
		} else {
			this.finishHide();
		}
	},

	finishHide: function() {
		this.el.show();
		this.form.hide();
		this.field.blur();

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

	fitWidthToParent: function() {
		if (this.editing) {
			if (this.multiline) {
				this.form.setWidth(getEl(this.form.dom.parentNode).getWidth());
				this.field.setWidth(this.form.getWidth());
			} else {
				var parentWidth = getEl(this.el.dom.parentNode).getWidth();
				var elWidth = this.el.getWidth();

				this.form.setWidth(
					Math.min(elWidth + (parentWidth - elWidth) / 2,
							 parentWidth));

				var saveButtonX = this.saveButton.getX();
				var buttonsWidth =
					this.cancelButton.getX() - saveButtonX +
					this.cancelButton.getWidth() +
					saveButtonX - (this.field.getX() + this.field.getWidth());
				this.field.setWidth(this.form.getWidth() - buttonsWidth);
			}
		}
	},

	findLabelForId: function(id) {
		var method = function(el) {
			return (el.getAttribute('for') == id);
		};

		return YAHOO.util.Dom.getElementsBy(method, 'label', document);
	},
});
