'use strict';

define(function (require) {

	var Marionette = require('backbone.marionette');
	var Handlebars = require('handlebars');
	var Template = require('text!./l-application.html');

	var LandingPageView = require('./landingPage/i_landingPage');
	var HeaderView = require('./_shared/header/i-header');
	var DoofView = require('./doof/l-doof');

	return Marionette.LayoutView.extend({

		el: function () {
			return this.options.el ? this.options.el : 'body';
		},

		template: Handlebars.compile(Template),

		regions: {
			header: '.b-doof-header',
			main: '.b-doof-main',
			footer: '.b-doof-footer'
		},

		showLandingPage: function () {
			this.showChildView('main', new LandingPageView({ model: this.model }));
		},

		showApplication: function () {
			this.doofView= new DoofView({ model: this.model });

			this.showChildView('header', new HeaderView({ model: this.model }));
			this.showChildView('main', this.doofView);
		},
		showSinglePickery: function(dish_name, eatery_id) {
			if(!this.doofView) {
				this.doofView= new DoofView({ model: this.model });

				this.showChildView('header', new HeaderView({ model: this.model }));
				this.showChildView('main', this.doofView);
			}
			this.doofView.showSingleEatery(dish_name, eatery_id);
		}
	});
});