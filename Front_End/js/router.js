/* global FB */
'use strict';

define(function (require) {

	var Marionette = require('backbone.marionette');
	var Promise = require('es6Promises').Promise;
	var Radio= require('backbone.radio');

	var UserModel = require('./models/userModel');
	var ApplicationLayoutView = require('./views/l-application');

	var router = "";
	// Create a Marionette AppRouter
	return Marionette.AppRouter.extend({
		initialize: function (opts) {
			router = this;
			this.opts = opts;

			this.applicationChannel= Radio.channel('application');
		},

		setupApplication: function () {
			var self= this;

			this.applicationChannel.on("showLandingPage", function() {
				router.navigate("");
				self.controller.landingPage();
			});
			this.applicationChannel.on("showApplicationPage", function() {
				router.navigate("application");
				self.controller.application();
			});

			var promise = new Promise(function (resolve, reject) {
				router.userModel = new UserModel({ userStatus: router.opts.userStatus });
				router.userModel.fetchData().then(function (success) {
					router.appLayout = new ApplicationLayoutView({ el: router.opts.el, model: router.userModel });
					router.appLayout.render();
					resolve("success");
				}, function (error) {
					resolve(error);
				});
			});

			return promise;
		},

		appRoutes: {
			"": "landingPage",
			"application": "application",
			"application/:eatery_name/": "singleEatery"
		},

		controller: {
			landingPage: function () {
				router.appLayout.showLandingPage();
			},
			application: function () {
				if (router.userModel.isAuthorized()) {
					router.appLayout.showApplication();
				} else {
					console.log("User is not Authorized. Sorry");
					router.navigate("");
					this.landingPage();
				}
			},
			singleEatery: function(eatery_name) {
				if (router.userModel.isAuthorized()) {
					console.log(eatery_name);
					router.appLayout.showSinglePickery(eatery_name);
				} else {
					console.log("User is not Authorized. Sorry");
					router.navigate("");
					this.landingPage();
				}
			}
		},
	});
});