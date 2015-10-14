// Doof Application Starting Point.

'use strict';

define(function (require) {

	var Marionette = require('backbone.marionette');
	var Backbone = require('backbone');
	var FB = require('facebook');
	var AppRouter = require('./router');

	// Create a new app
	var App = new Marionette.Application();

	//Before Starting App, do some setups.
	App.on("before:start", function (opts) {

		opts = opts || {};

		//initialize our Facebook SDK
		FB.init({
			appId: '1605945752959547',
			cookie: true,  // enable cookies to allow the server to access the session
			version: 'v2.5', // use version 2.5
			status: true
		});

		FB.getLoginStatus(function (res) {
			opts.userStatus = res.status;
			// Trigger Start App Event.
			App.vent.trigger('startApp', opts);
		});

	});

	// It will be triggered after FB SDK has initialized..
	App.vent.bind('startApp', function (opts) {
		// Create a application Router
		var appRouter = new AppRouter(opts);

		appRouter.setupApplication().then(function (success) {
			if (Backbone.history) {
				Backbone.history.start();
			}
		}, function (error) {
			console.log(error);
		});
	});

	return App;
});