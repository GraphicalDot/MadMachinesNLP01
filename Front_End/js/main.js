// Require JS Configuration

'use strict';

// Set Requirejs Configuration
require.config({
	// Set burst to prevent any kind of cache
	urlArgs: new Date().getTime(),
	waitSeconds: 0,

	paths: {
		// backbone dependencies
		'jquery': './../components/jquery/jquery-1.11.3.min',
		'underscore': './../components/marionette/underscore/underscore',
		'backbone': './../components/marionette/backbone-min',
		'backbone.marionette': './../components/marionette/backbone.marionette',
		'backbone.radio': './../components/marionette/backbone.radio',
		'backbone.service': './../components/marionette/marionette-service',
		'handlebars': './../components/handlebars-v4.0.2',
		// End of backbone dependencies

		// Require JS Plugins

		'text': './../components/requirejs/plugins/text',
		'hbs': './../components/requirejs/plugins/require-handlebars',
		'require-async': './../components/requirejs/plugins/require-async',
		// End of Require JS Plugins

		// Materialaze CSS dependencies
		'picker': './../components/materialize/js/date_picker/picker',
		'picker.date': './../components/materialize/js/date_picker/picker.date',
		'animation': './../components/materialize/js/animation',
		'buttons': './../components/materialize/js/buttons',
		'cards': './../components/materialize/js/cards',
		'character_counter': './../components/materialize/js/character_counter',
		'chips': './../components/materialize/js/chips',
		'collapsible': './../components/materialize/js/collapsible',
		'dropdown': './../components/materialize/js/dropdown',
		'forms': './../components/materialize/js/forms',
		'global': './../components/materialize/js/global',
		'hammerjs': './../components/materialize/js/hammer.min',
		'jquery.easing': './../components/materialize/js/jquery.easing.1.3',
		'jquery.hammer': './../components/materialize/js/jquery.hammer',
		'jquery.timeago': './../components/materialize/js/jquery.timeago.min',
		'leanModal': './../components/materialize/js/leanModal',
		'materialbox': './../components/materialize/js/materialbox',
		'parallax': './../components/materialize/js/parallax',
		'prism': './../components/materialize/js/prism',
		'pushpin': './../components/materialize/js/pushpin',
		'scrollFire': './../components/materialize/js/scrollFire',
		'scrollspy': './../components/materialize/js/scrollspy',
		'sideNav': './../components/materialize/js/sideNav',
		'slider': './../components/materialize/js/slider',
		'tabs': './../components/materialize/js/tabs',
		'toasts': './../components/materialize/js/toasts',
		'tooltip': './../components/materialize/js/tooltip',
		'transitions': './../components/materialize/js/transitions',
		'velocity': './../components/materialize/js/velocity.min',
		'waves': './../components/materialize/js/waves',
		// end of materialize css dependencies

		// Others

		'facebook': '//connect.facebook.net/en_US/sdk',
		'gridalicious': './../components/gridalicious',
		'async': './../components/async',
		'jquery.bootpag': './../components/jquery.bootpag.min',

		// d3
		'd3': './../components/d3/d3.min',
		'd3.tips': './../components/d3/d3.tips',
		'radialGraph': './../components/d3/radialGraph',

		'typeahead': './../components/typeahead/typeahead.bundle',
		'tablesorter': './../components/typeahead/jquery.tablesorter',
		// 'masonry': './../components/masonry.min',

		'es6Promises': './../components/es6-promises'
	},
	shim: {
		'jquery': {
			exports: '$'
		},

		// backbone shim configuration & dependencies
		'underscore': {
			exports: '_'
		},

		'backbone': {
			deps: ['underscore', 'jquery'],
			exports: 'Backbone'
		},

		'backbone.marionette': {
			deps: ['backbone'],
			exports: 'Marionette'
		},

		'backbone.radio': {
			deps: ['backbone.marionette'],
			exports: 'Radio'
		},

		'backbone.service': {
			deps: ['backbone.marionette', 'backbone.radio'],
		},
		// end of backbone shim configuration

		// materialize css shim configuration
		'velocity': {
			deps: ['jquery'],
			exports: 'Vel'
		},

		'jquery.easing': {
			deps: ['jquery']
		},

		'animation': {
			deps: ['jquery']
		},

		'hammerjs': {
			exports: 'Hammer'
		},

		'jquery.hammer': {
			deps: ['jquery', 'hammerjs', 'waves']
		},

		'global': {
			deps: ['jquery']
		},

		'toasts': {
			deps: ['hammerjs', 'velocity']
		},

		'collapsible': {
			deps: ['jquery']
		},

		'dropdown': {
			deps: ['jquery']
		},

		'leanModal': {
			deps: ['jquery']
		},

		'materialbox': {
			deps: ['jquery']
		},

		'parallax': {
			deps: ['jquery']
		},

		'tabs': {
			deps: ['jquery']
		},

		'tooltip': {
			deps: ['jquery']
		},

		'sideNav': {
			deps: ['jquery']
		},

		'scrollspy': {
			deps: ['jquery']
		},

		'forms': {
			deps: ['jquery', 'global']
		},

		'slider': {
			deps: ['jquery']
		},

		'cards': {
			deps: ['jquery']
		},

		'pushpin': {
			deps: ['jquery']
		},

		'buttons': {
			deps: ['jquery']
		},

		'transitions': {
			deps: ['jquery', 'scrollFire']
		},

		'scrollFire': {
			deps: ['jquery', 'global']
		},

		'waves': {
			exports: 'Waves'
		},

		'character_counter': {
			deps: ['jquery']
		},

		'chips': {
			deps: ['jquery']
		},

		'jquery.timeago': {
			deps: ['jquery']
		},
		// end of materialize css shim configuration

		'facebook': {
			exports: 'FB'
		},


		'gridalicious': {
			deps: ['jquery']
		},

		'jquery.bootpag': {
			deps: ['jquery']
		},


		'typeahead': {
			deps: ['jquery'],
			init: function ($) {
				return require.s.contexts._.registry['typeahead.js'].factory($);
			}
		},

		'tablesorter': {
			deps: ['jquery']
		},

		'handlebars': {
			exports: 'Handlebars'
		},

		'd3.tips': {
			deps: ['d3']
		},

		'radialGraph': {
			deps: ['d3', 'd3.tips']
		}
	}
});



//Include Materialize JS Dependencies.
require(['jquery.easing', 'animation', 'velocity', 'hammerjs', 'jquery.hammer', 'global', 'collapsible', 'dropdown', 'leanModal', 'materialbox', 'parallax', 'tabs', 'tooltip', 'waves', 'toasts', 'sideNav', 'scrollspy', 'forms', 'slider', 'cards', 'pushpin', 'buttons', 'scrollFire', 'transitions', 'picker', 'picker.date', 'character_counter', 'chips', 'jquery.timeago'], function () {

	//Start our application
	require(['jquery', 'backbone', './app', './global_variables'], function ($, Backbone, App) {

		$.fn.enterKey = function (fnc) {
			return this.each(function () {
				$(this).keypress(function (ev) {
					var keycode = (ev.keyCode ? ev.keyCode : ev.which);
					if (keycode == '13') {
						fnc.call(this, ev);
					}
				});
			});
		}

		// Backbone.emulateJSON= true;
		// start our application
		App.start({ el: '.doof-container' });
	});
});
