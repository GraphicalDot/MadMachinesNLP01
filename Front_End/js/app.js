
/*This is app.js file which is t be passed into the main require.js file
 */

define([
        'jquery',
        'underscore',
        'backbone',
        'router',
       	], 
	function($, _, Backbone, Router){
            var initialize = function(){
                Router.initialize();

            }

            return { initialize: initialize
            };
        });
