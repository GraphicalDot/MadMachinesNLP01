'use strict';

define(function(require) {

  var Backbone= require('backbone');
  var async= require('async');
  var FB= require('facebook');
  var Promise= require('es6Promises').Promise;

	var self;

  return Backbone.Model.extend({
    // defaults
    defaults: {
      id: null,
      third_party_id: null,
      name: null,
      email: null,
      image: null,
      status: 0
    },

    // fetch FB info if avaiable
    initialize: function (opts) {
			self= this;
			this.userStatus= opts.userStatus;
    },

		fetchData: function() {
			var self= this;
			var promise= new Promise(function(resolve, reject) {
				if(self.userStatus=== "connected") {
					async.waterfall([self.getUserdata, self.saveSession], function(err, result) {
						if(err) {
							reject(err);
						}
						resolve(result);
					});
				} else {
					resolve("Facebook user not connected. "+ self.userStatus);
				}
			});

			return promise;
		},

    // Return if user is authorzed.
    isAuthorized: function () {
      /* true if third_party_id exists */
      return Boolean(this.get("third_party_id"));
    },

    // If function gets User Data from FB APi
    getUserdata: function (callback) {
      FB.api('/me?fields=third_party_id,email,name,picture', function (response) {
        if (!response || response.error) {
          callback(true, response.error);
        } else {
          callback(null, response);
        }
      });
    },

    // This function stores the user data in Model
    saveSession: function (user, callback) {
			/* if third_party_id exist its totally okay */
      if (user['third_party_id']) {
				self.set({
          third_party_id: user['third_party_id'],
          name: user['name'],
          email: user['email'],
          picture: user['picture'],
          status: "1"
        }, {
					silent: true
				});

        self.set({
          id: user['id']
        });

        callback(null, "Everything is wonderful.");
      } else {
        callback(true, "third_party_id check failed!");
        return false;
      }
    },

    // This function login user inside.
    login: function (opts, callback) {
      FB.login(function (response) {
        if (response.authResponse) {
          /* Use async.js to run async functions in a row */
          async.waterfall([
            self.getuserdata,
            self.savesession,
            /* optionally here you can include self.save() -> this will push cookies (including auth_token) to the server */
          ], function (err, result) {
            callback(err, result);
          });

        } else {
          self._onERROR('User cancelled login or did not fully authorize.');
        }
      }, {
          scope: 'email,user_likes'
        });
    },

    promiseLogin: function() {
      var promise= new Promise(function(resolve, reject) {
        FB.login(function(response) {
          if(response.authResponse) {
            async.waterfall([self.getUserdata, self.saveSession], function(err, result) {
              if(err) {
                reject(err);
              }
              resolve(result);
            });
          } else {
            reject("User cancelled login or did not fully authorize.");
          }
        }, {scope: 'email, user_likes'});
      });

      return promise;
    },

    // This function logs out user.
    logout: function () {
      var promise= new Promise(function(resolve, reject) {
        FB.logout(function() {
          self.clear();
          resolve('success');
        });
      });
      return promise;
    },
  });
});