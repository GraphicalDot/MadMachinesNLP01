/* global Materialize */
'use strict';

define(function (require) {

	var $ = require('jquery');
	var Handlebars = require('handlebars');
	var Marionette = require('backbone.marionette');
	var Template = require('text!./i-header.html');
	var Radio = require('backbone.radio');

	return Marionette.ItemView.extend({
		className: 'navbar-fixed',
		initialize: function () {
			this.applicationChannel = Radio.channel('application');
			this.doofChannel= Radio.channel('doof');
		},
		templateHelpers: {
			isUserPresent: function () {
				return this.third_party_id;
			},
			facebookPictureUrl: function () {
				return this.picture.data.url;
			}
		},
		template: Handlebars.compile(Template),
		events: {
			'click .logoutButton': 'doLogout',

			'click #facebookLoginLink': 'doLogin',
			'click #feedback_nav': 'onClickFeedback',
			'click #how_it_works_nav': 'onClickHowItWorks',
			'click #enter_your_query_nav': 'onClickEnterYourQuery',
			'click #pick_eatery_nav': 'onClickPickEatery',
		},
		modelEvents: {
			'change': 'render'
		},

		doLogout: function (e) {
			e.preventDefault();

			var self = this;
			this.model.logout().then(function (success) {
				self.applicationChannel.trigger("showLandingPage");
			});
		},

		doLogin: function (e) {
			e.preventDefault();

			var self = this;
			this.model.promiseLogin().then(function (success) {
				self.applicationChannel.trigger("showApplicationPage");
			});
		},

		onClickFeedback: function (e) {
			e.preventDefault();
			this.doofChannel.trigger("feedback");
		},
		onClickHowItWorks: function (e) {
			e.preventDefault();
			this.applicationChannel.trigger("how_it_works");
		},
		onClickEnterYourQuery: function (e) {
			e.preventDefault();
			this.applicationChannel.trigger("enterYourQuery");
		},

		onClickPickEatery: function (e) {
			e.preventDefault();
			this.applicationChannel.trigger('pick_eatery');
		},
		onShow: function () {
			if (this.model.get('third_party_id')) {
				$(".dropdown-button").dropdown({
					hover: true,
					belowOrigin: true
				});
			}
		}
	});
});