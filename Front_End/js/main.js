
/* This is the main javascript file to load the require.js configuration variables
 *
 */

require.config({
    paths: {
        jquery: 'libs/jquery/jquery',
        underscore: 'libs/underscore/underscore',
        backbone: 'libs/backbone/backbone',
        handlebars: 'libs/handlebars/handlebars',
	mustache: 'libs/mustache/mustache',
	jqueryValidate: 'libs/jqueryValidate/jqueryValidate',
	bootstrapForm: 'libs/bootstrap/bootstrap-form',
	bootstrapTransition: 'libs/bootstrap/bootstrap-transition',
	bootstrapAlert: 'libs/bootstrap/bootstrap-alert',
	bootstrapTooltip: 'libs/bootstrap/bootstrap-tooltip',
	bootstrapPopover: 'libs/bootstrap/bootstrap-popover',
	bootstrapDropdown: 'libs/bootstrap/bootstrap-dropdown',
	bootstrapButton: 'libs/bootstrap/bootstrap-button',

    }
});

require(['app'], function(App){
    App.initialize();
});
 


