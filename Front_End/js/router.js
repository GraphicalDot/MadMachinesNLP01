
/*This javascript files defines the router for our applications*/

define([
		'jquery',
		'undescore',
		'backbone',
		'views/users/create_user',
		'views/users/manage_users',
		'views/users/user_roles',
		'views/users/user_permisissions',
		'views/users/user_activity_log', ], function



EasysalesRouter = Backbone.Router.extend({

    routes: {
        "", "index",
        "create_user": "create_user",
        "manage_users": "manage_users",
        "user_roles": "user_roles", 
        "user_permissions": "user_permissions",
        "usr_activity_log": "user_activity_log",
    },
        index: function(){/*main page for the index.html*/ } , 
        create_user: function() { /* html fiel for the create user



