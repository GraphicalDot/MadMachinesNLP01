/* global Materialize */
'use strict';

define(function (require) {

	var $ = require('jquery');
	var Handlebars = require('handlebars');
	var Marionette = require('backbone.marionette');
	var Template = require('text!./landingPage.html');
	var Radio = require('backbone.radio');

	var initialize_method = "Previous User Detected. Continue with Same User?";
	var fb_login_success_message = "Successfully Logged In";
	var fb_login_error_message = "Cant Login. Some Issue with Facebook Login";

	return Marionette.ItemView.extend({
		initialize: function () {
			if (this.model.get('third_party_id')) {
				this.alert_msg(initialize_method, 4000, "");
			}

			this.applicationChannel = Radio.channel('application');
		},

		className: 'lander-page',
		template: Handlebars.compile(Template),

		templateHelpers: {
			isUserPresent: function () {
				return this.third_party_id;
			},
			userName: function () {
				return this.name;
			},
			facebookPictureUrl: function () {
				return this.picture.data.url;
			}
		},

		events: {
			'click .lander-facebook_login': 'login',
			'click .lander-logout_user': 'logout'
		},

		onShow: function () {
			$(".slider").slider({ full_width: true });
			if (this.model.isAuthorized()) {
				$('.user_dropdown-button').dropdown();
			}
			$('.b-doof-header').empty();
		},

		login: function (e) {
			e.preventDefault();
			var self = this;
			this.model.promiseLogin().then(function (success) {
				self.alert_msg(fb_login_success_message, 3000, "");
				self.applicationChannel.trigger("showApplicationPage");
			}, function (error) {
				self.alert_msg(fb_login_error_message, 3000, "");
			});
		},

		logout: function (e) {
			e.preventDefault();

			var self = this;
			this.model.logout().then(function (success) {
				self.applicationChannel.trigger("showLandingPage");
			});
		},

		alert_msg: function (msg, time, options) {
			Materialize.toast(msg, time, options);
		}
	});
});