
$(document).ready(function(){
    console.log("Template loadeded")
    Admin = {};
    window.Admin = Admin
   

/*This is the backbone adapter for indexed db, where id is the name of the database under indexe db and two object stores were created with the name of merchants and credentials */
var databasev1 = {
    id: "EasyAdminversion2",
    description: "The database for the Admin",
    migrations : [
        {
            version: "1.0",
            migrate: function(transaction, next) {
		var merchantStore = transaction.db.createObjectStore("merchants");
		var credentialsStore = transaction.db.createObjectStore("credentials");
               	next();
            }
        }, 
	   {
            version: "1.1",
            migrate: function(transaction, next) {
                var merchantStore = transaction.objectStore("merchants");
		merchantStore.createIndex("emailIndex", "email", { unique: true}); 
                next();
            },
        }
    ]
}



/*This is the function to create hash from username and password to create a basic authentication token
 */
function make_base_auth(username, password){
	var token = username+ ":" + password;
	var hash = btoa(token);
	return "Basic " + hash ; 
}	


function make_request(endpoint, type, data, headers){
	url =  "http://54.254.97.167:5000/" + endpoint
//	url =  "http://192.168.1.3:5000/" + endpoint
	$.ajaxSetup({
		beforeSend: function(request){
		request.setRequestHeader("Authorization", make_base_auth("ankitgoyal", "ankitgoyal"));
		request.setRequestHeader("Access-Type", "superadmin");
		}});

	if (type == "GET"){
		return 	$.ajax({
			url: url,
			type: type,
			statusCode: {
				404: function() {
					bootbox.alert("page not found");
					},
				401: function(){
					bootbox.alert("Error loading Page, Please try again");
				}},
	  		dataType: 'json',
	  		async: false,
			});
		}
	else {
		return 	$.ajax({
			headers: {"Content-Type": 'application/json'},
			url: url,
			type: type,
			data: data,
			statusCode: {
				404: function() {
					bootbox.alert("page not found");
					},
				401: function(){
					bootbox.alert("Error loading Page, Please try again");
				},
				400: function(){
					bootbox.alert("This has already been deactivated");
				},
			},
			dataType: 'json',
	  		async: false,
	});
		}
};

/*This is the template object which uses name as an argument to return handlebar compiled template from the the html
 */
var template = function(name){
    return Mustache.compile($("#"+name+"-template").html());
};


	/*________View corresponds to /admin/see_merchant ______________*/
/* This is the ManageMerchant view of the backbone, WHat this does is, It populates all the users present in the merchant
 * database,This is Done by Caling another view 
 */
Admin.ListMerchants = Backbone.Model.extend({
	database: databasev1,
	storeName: "merchants",
});

Admin.ListMerchants.Collection = Backbone.Collection.extend({
	database: databasev1,
	storeName: "merchants",
	model: Admin.ListMerchants,

});


Admin.ListMerchants.View = Backbone.View.extend({
	tagName: "table",
	className: "table table-hover table-bordered table-condensed",
	template: template("manage-merchants"),

	initialize: function(){
	},
	render: function(){
		var self = this;
		this.$el.html(this.template(this));
		var jqhr = make_request("accounts/merchants?rpp=100", "GET");
		jqhr.done(function(data){
			$.each(data.merchants, function(iter, merchant){
				self.populateMerchant(merchant);
			});
		});	
		$("table").tablecloth({theme: "paper", bordered: true, condensed: true, striped: true, sortable: true, clean: true, }); 
		return this;
		},
	
	populateMerchant: function(merchant){
		/*this function is being called on every mrechant present in the merchant collection, Which in 
		 turn appends a each merchant view to this view */
		var view = new Admin.ListMerchants.Merchant({model: merchant});
		this.$el.append(view.render().el);
			},
	});


Admin.ListMerchants.Merchant = Backbone.View.extend({
	tagName: "tr",
	template: template("merchantadd"),
	Company_name: function() {return this.model.company_name },
	Contact_name: function() {return this.model.contact_name },
	Email: function() {return this.model.email},
	Deactivated: function() {return this.model.deactivated},
	Mobile_number: function(){ return this.model.mobile_number},
	Plan_Details: function(){return this.model.plan_details},
	Plan_name: function(){ return this.Plan_Details().plan.name },
	Plan_pricing_name: function(){ return this.Plan_Details().plan_pricing.name},
	Merchant_id: function(){ return this.model.merchant_id},

	events: {
		/* These actions are initated when the user clicks on the delte button with id="deleteMechant" and
		 * id="editMerchant" present in this view */
		"click #deleteMerchant" : "deactivate",
		"click #editMerchant": "edit",
	},

	render: function(){
		this.$el.html(this.template(this));
		return this;
		},

	deactivate: function(e){
		e.preventDefault();
		var self = this;
		this.url = "accounts/merchants/" + this.Merchant_id() + "/deactivate";
		bootbox.confirm("Are you sure", function(result){
			if(result){
				var jqhr = make_request(self.url, "POST");
				jqhr.done(function(data){
					if(data.status == 200){
						bootbox.alert("The Merchant has been deactivated");
					}
					else{
						bootbox.alert("The Merchant has already been deactivated");
					}
				});
				}	
		});
			},

	edit: function(event){
		event.preventDefault();
		/* This function is being called on when the user clicks on the edit button of this view, ON clicking 
		 * on this button a new view will be called which displays the details of the merchant to be edited, if 
		 * needed, which will be updatedd to the mechant collection */
		var subview = new Admin.ListMerchants.EditMerchant({model: this.model})
		$(".dynamic_display").html(subview.render().el);		
		return false;
	},

});

/* Called by the view mentioned above, and renders all details of a particular merchant present in the merchant collection
 * and provides a save button to save all the edits done to the merchant to the collection merchants */
Admin.ListMerchants.EditMerchant = Backbone.View.extend({
	tagName: "form",
	className: "form-horizontal",
	template: _.template($("#manage-merchants-details-template").html()),
	initialize: function(options){
	//	$(".dynamic_display").html($('#loadingImage').show());
		this.model = options.model;
		this.merchantId = this.model.merchant_id;
		console.log("Hit man");
	},

	render: function(){
		this.plan = "";
		this.pricing = "";
		var self = this;
		this.$el.append(this.template(this));


		/*This part populates the #plan by reching out on the api end point /plans/plans */
		url = "accounts/merchants/" + this.merchantId;
		var jqhr = make_request(url, "GET");
		jqhr.done(function(data){
			$.each(self.$("input"), function(iter, value){
				var value = $(this).attr("name");
				$(this).val(data.merchant[value]);
				});
			self.plan = data.merchant.plan_details.plan;
			self.pricing = data.merchant.plan_details.plan_pricing;
		})
		var k = make_request("plans/plans", "GET");
		k.done(function(data){
			$.each(data.plans, function(iter, plan){
				var subView = new Admin.CreateMerchantChangePlanView({model: plan});
				self.$("#plan").append(subView.render().el);		
			})
		})
		/* This parts implements the change function on the #plan which changes #pricing on the basis of plan selected */
		this.$("select#plan").change(function(){
			var endpoint = "plans/plans/" + $(this).children(":selected").attr("id") 
			var k = make_request(endpoint, "GET")
			k.done(function(data){
				$("#pricing").empty();
				$.each(data.plan.pricings, function(iter, pricing){
					var subView = new Admin.CreateMerchantChangeOptionView({model: pricing});
					$("#pricing").append(subView.render().el)
				})
			})
		});
		this.$("select#plan").val(this.plan.name); //This selects the plan stored under the merchant 
		/*This populates the #pricing based upon the plan selected everytime from the #plan */
		url = "plans/plans/" + this.plan.plan_id;
		var jqhr = make_request(url, "GET");
		jqhr.done(function(data){
			self.$("pricing").empty();
			$.each(data.plan.pricings, function(iter, pricing){
				var subView = new Admin.CreateMerchantChangeOptionView({model: pricing});
				self.$("#pricing").append(subView.render().el)
				console.log(data);	
			});
			});
		this.$("select#pricing").val(this.pricing.name)
		/* This part fills out the formdetails under the account etail section of this view by reching out on the api-endpoint
		 * /plans/merchant_plan/merchant_id */
		var url = "plans/merchant_plan/" + this.merchantId;
		var jqhr = make_request(url, "GET");
		jqhr.done(function(data){
			self.$("#lastDeductionDate").val(data.merchant_plan.last_deduction_date);
			self.$("#nextDeductionDate").val(data.merchant_plan.next_deduction_date);
			$.each(data.merchant_plan_usage, function(iter, quota){
				var subView = new Admin.ListMerchants.EditMerchantAddQuotas({model: quota});
				self.$("#addQuotas").append(subView.render().el)
			});
		});
		return this;
		},

	events: {
		"click #default" : "default",
		"click #update": "update",	
		"click #receivePayment": "receivePayment",	
		"click #paymentHistory": "paymentHistory",	
		},

	receivePayment: function(event){
		event.preventDefault();
		var subView = new Admin.ListMerchants.ReceivePayment({model: this.model});
		this.$el.html(subView.render().el);
	},

	paymentHistory: function(event){
		event.preventDefault();
		var subView = new Admin.ListMerchants.PaymentHistory({model: this.model});
		this.$el.html(subView.render().el);
		$("table").tablecloth({theme: "paper", bordered: true, condensed: true, striped: true, sortable: true, clean: true, }); 
	},
	default: function(event){
		event.preventDefault();
	},

	update: function(event){
		/*This function saves all the changes made to the merchant into the collection */
		event.preventDefault()
		var self = this;
		this.formObject = {};
		$.each($("form").serializeArray(), function(iter, data){
			self.formObject[data.name] = data.value
		});
		var url = "accounts/merchants/" + this.merchantId;	
		var jqhr = make_request(url, "PUT", JSON.stringify(this.formObject))
		console.log(JSON.stringify(this.formObject))
		jqhr.done(function(data){
			if(data.status == 204){
				bootbox.alert("Merchaant has been edited")
			}
			else{
				bootbox.alert("There is some editing Merchant")
			}
		});
		return this;
	},

});

Admin.ListMerchants.EditMerchantAddQuotas = Backbone.View.extend({
	template: template("edit-merchant-quota-row"),
	className: "control-group",
	name: function(){return this.model.name},
	value: function(){return this.model.usage_value},
	intialize: function(options){
		this.model = options.model;
	},
	render: function(){
		this.$el.append(this.template(this));
		return this;
	},
});

/* This view is being called upon when the user clicks on the receive payment button present in the edit merchant form.This view calls the Api
 * enpoint /plans/merchant_plan with get paramaeter as merchant id 
 */

Admin.ListMerchants.ReceivePayment = Backbone.View.extend({
	template: template("merchant-receive-payment"),
	merchant_name: function(){ return this.model.contact_name},
	merchant_id: function(){ return this.model.merchant_id},
	initialize: function(options){
		this.model = options.model;
	},

	render: function(){
		var self = this;
		this.$el.append(this.template(this));
		url = "plans/merchant_plan/" + this.merchant_id()
		var jqhr = make_request(url, "GET");
		jqhr.done(function(data){
			self.$("#currentBalance").val(data.merchant_plan.current_balance);
			console.log(self.current_balance);
		})
		return this;
	},

	events: {
		"click #done": "done",
	},
	done: function(event){
		event.preventDefault();
		var self = this;
		this.formObject = {};
		$.each($("form").serializeArray(), function(iter, data){
			self.formObject[data.name] = data.value
		});	
		this.formObject["merchant_id"] = parseInt($("#merchantName").attr("merchant_id"));
		var jqhr = make_request("plans/payments", "POST", JSON.stringify(this.formObject))
		console.log(JSON.stringify(this.formObject))
		jqhr.done(function(data){
			if(data.status == 201){
				bootbox.alert("Payment Has Been Added")
			}
			else{
				bootbox.alert("There is some error posting Payment")
			}
		});
		return this
			},
})

/* This view is being displayed when the user clicks on the payment history button on the edit merchant form, It uses the template 
 * merchant-payment-history-template and it turns call the api end point plans/payments with ( rpp = 100, right now) and 
 * merchant id , based upon the elements present in the response under payments call the PaymentHistoryAddRowView */
Admin.ListMerchants.PaymentHistory = Backbone.View.extend({
	tagName: "table",
	className: "table table-hover table-bordered table-condensed",
	template: template("merchant-payment-history"),
	initialize: function(options){
		this.model = options.model
	},

	render: function(){
		var self = this;
		this.$el.append(this.template(this));
		url = "plans/payments" + "?rpp=100" + "&" + "merchant_id=" + this.model.merchant_id
		var jqhr = make_request(url,"GET") //Need to add rpp to get the full ressults;
		console.log(url)
		jqhr.done(function(data){
			$.each(data.payments, function(iter, payment){
				var subView = new Admin.ListMerchants.PaymentHistoryAddRowView({model: payment})
				self.$("#addPayments").append(subView.render().el)
			});
		console.log(data);
		});
		return this;
	},

});


Admin.ListMerchants.PaymentHistoryAddRowView  = Backbone.View.extend({
	tagName: "tr",
	template: template("merchant-payment-history-row"),
	date: function(){return this.model.recieve_date},
	amount: function(){return this.model.amount},
	keyInTime: function(){return this.model.date_time.substr(17,9)},
	initialize: function(options){
		this.model = options.model;
		console.log(this.model);
		console.log(this.amount());
	},

	render: function(){
		this.$el.append(this.template(this));
		return this;
		},
});

	/*________   #/admin/create_user _______*/
/* THis is the view which will be called when the user clicks on the #/admin/create_user .This view populates the Mrchants
 * collection*/
Admin.CreateMerchant = Backbone.Model.extend({
	database: databasev1,
	storeName: "merchants",
});

Admin.CreateMerchant.Collection = Backbone.Collection.extend({
	model: Admin.CreateMerchant,
	database: databasev1,
	storeName: "merchants",
	});

Admin.CreateMerchant.View = Backbone.View.extend({
	tagName: "form",
	className: "form-horizontal merchant-form",
	template: template("form"),
	initialize: function(){
		this.model = new Admin.CreateMerchant()
		this.collection = new Admin.CreateMerchant.Collection();
		this.collection.on("all", this.render, this);
		this.collection.fetch();
		console.log("Intialize function initiated");	
	},
		
	events: {
            'submit': "add",
            },

	render: function(){
		var self = this;
		this.$el.html(this.template(this))
		$("#confirmPassword").change(function(){
		 	if($("#confirmPassword").val() != $("#password").val()){
				$("#confirmPassword").val("");
				$("#passwordMessege").empty();
				$("#passwordMessege").append("** Password does not Match")
			}
			else {
				$("#passwordMessege").empty();
			}
			})	
		var k = make_request("plans/plans", "GET");
		k.done(function(data){
			$.each(data.plans, function(iter, plan){
				var subView = new Admin.CreateMerchantChangePlanView({model: plan});
				self.$("#plan").append(subView.render().el);		
			})
		})

		//This caters with the change in the value in the #plans id
		this.$("select#plan").change(function(){
			var endpoint = "plans/plans/" + $(this).children(":selected").attr("id") 
			var k = make_request(endpoint, "GET")
			k.done(function(data){
				$("#pricing").empty();
				$.each(data.plan.pricings, function(iter, pricing){
					var subView = new Admin.CreateMerchantChangeOptionView({model: pricing});
					$("#pricing").append(subView.render().el)
				})
			})
		})
		return this;
                    },

	add: function(event){
		event.preventDefault();
		var self = this;
		this.formObject = {};
		$.each($("form").serializeArray(), function(iter, data){
			self.formObject[data.name] = data.value
		});	
		this.formObject["plan_id"] = parseInt($("select#plan").children(":selected").attr("id"));
		this.formObject["plan_pricing_id"] = parseInt($("select#pricing").children(":selected").attr("pricing_id"));
		var jqhr = make_request("accounts/merchants", "POST", JSON.stringify(this.formObject))
		console.log(JSON.stringify(this.formObject))
		jqhr.done(function(data){
			if(data.status == 201){
				bootbox.alert("Merchant has been Added")
			}
			else{
				bootbox.alert("There is some error creating merchant")
			}
		});
		$.each($("form input"), function(iter, value){$(this).val("")})	
		return this
			},

	});

Admin.CreateMerchantChangeOptionView = Backbone.View.extend({
	tagName: "option",
	template: Mustache.compile("{{name}}"),
	initialize: function(options){
		this.model = options.model;
		this.name = this.model.name;
		this.$el.attr({"pricing_id": this.model.pricing_id});
	},
	render: function(){
		this.$el.append(this.template(this));
		return this;
	},
});
Admin.CreateMerchantChangePlanView = Backbone.View.extend({
	tagName: "option",
	template: Mustache.compile("{{name}}"),
	initialize: function(options){
		this.model = options.model;
		this.name = this.model.name;
		this.$el.attr({"value": this.model.name,  "id": this.model.plan_id});
	},
	render: function(){
		this.$el.append(this.template(this));
		return this;
	},
});


/* This is the login view of Admin console which handles whether the user is logged in or not, This works in this way;
 * the intialize function of this view waits for the collection to be fetched and then calls the viewrender function of 
 * this view  instead of the default render method.
 * The view render method checks in the collection whether the auth param is boolean false or true.if its false, it fetches
 * the login view and if its true it fetches the logout view.
 * The model binds with the change in the value, so that if the value of the any model changes prresent in the collection
 * the view renders itself again*/

Admin.AdminAccess = Backbone.Model.extend({
		database: databasev1,
		storeName: "credentials",
});

Admin.AdminAccess.Collection = Backbone.Collection.extend({
		model: Admin.AdminAccess,
		database: databasev1,
		storeName: "credentials",

});

Admin.AdminAccess.View = Backbone.View.extend({
	initialize: function(){
		console.log("Initialize of admin acces view has been called");
		this.model = new Admin.AdminAccess();
		this.collection = new Admin.AdminAccess.Collection();
		var self = this;
		},

	render: function(){
		var self = this;
		this.collection.fetch({success: function(){	
		if(self.collection.get("username") != undefined && self.collection.get("username").get("value") == "ankitgoyal" && self.collection.get("password").get("value") == "ankitgoyal"){
			var view = new Admin.AdminAccessLogoutView({model: self.model, collection: self.collection})
			$("#header-bar").html(view.render().el);
		}
		
		else {
			var subView = new Admin.AdminAccessLoginView({model: self.model, collection: self.collection});
			$(".dynamic_display").html(subView.render().el);
			}
		}});
		return this;
	},

});

Admin.AdminAccessLoginView = Backbone.View.extend({
	tagName: "form",
	className: "form-horizontal",
	template: template("login"),
	template2: template("login-header"),
	initialize: function(options){
		this.model = options.model;
		this.collection = options.collection;
		this.collection.fetch();
	},
	render: function(){
		console.log("Render function of adminAccesLoginView has been called");
		$("#header-bar").html(this.template2(this))
		this.$el.append(this.template(this));
		return this;
	},

	events: {
		"click #login": "login",
	},

	login: function(event){
		event.preventDefault();
		var self = this;
		this.username = $("#username").val();
		this.password = $("#password").val();
		console.log(this.username, this.password)
		$.ajax({
			headers: {"Access-Type": "superadmin", "Authorization": make_base_auth(this.username, this.password)},
			url: "http://54.254.97.167:5000/accounts/superadmin_login_check",
			type: "GET",
	  		dataType: 'json',
	  		async: false,
			statusCode: {
				400: function() {
					bootbox.alert("Username and password combination you have provided is incorrect", function(){
						$("#username").val("");
						$("#password").val("");
					});
				}},
		}).done(function(data){
			if(data.error == false){	
				bootbox.alert("You have logged in successfully, Press OK to continue", function(){
					self.model.save({id: "username", value: $("#username").val()});
					self.collection.add(this.model, {merge: true});
					self.model.save({id: "password", value: $("#password").val()});
					self.collection.add(this.model, {merge: true});
				var subView = new Admin.AdminAccessLogoutView({model: self.model, collection: self.collection});
					$("#header-bar").html(subView.render().el);
				})
			}
			else{	
				}
			})
	},
});


Admin.AdminAccessLogoutView = Backbone.View.extend({
	tagName: "ul",
	className: "nav header-nav",
	template: template("after-login"),
	initialize: function(options){
		this.model = options.model;
		this.collection = options.collection;
		this.collection.fetch();
	},

	render: function(){
		console.log("logout view")
//		var subView = new Admin.WelcomeView({"message": "Press any tab to Continue"})
//		$(".dynamic_display").html(subView.render().el);
		this.$el.append(this.template(this))
		return this;
		},

	events: {
		"click #logout": "logoutsubmit",
		},

	logoutsubmit: function(event){
		event.preventDefault();
		this.model.save({id: "username", value: null});
		this.collection.add(this.model, {merge: true});
		this.model.save({id: "password", value: null});
		this.collection.add(this.model, {merge: true});
		var str = new Admin.AdminAccessLoginView({model: this.model, collection: this.collection});
		$(".dynamic_display").html(str.render().el);
	},
});


/*This is the welcome view of the admin which has welcom-template as its template and takes message as the parameter
 */
Admin.WelcomeView = Backbone.View.extend({
	template: template("welcome"),
	templateHeader: template("before-login"),
	initialize: function(options){
		this.message = options.message;
			},

	render: function(){
		this.$el.append(this.template(this))
		//$("#header-bar").append(this.templateHeader(this))
		return this;
		},
});


Admin.PlanView = Backbone.View.extend({
	tagName: "form",
	className: "form-horizontal",
	template: template("plan-view"),
	initialize: function(){
		var self = this;
		console.log("The PlanView has been intiliazed");
		var k = make_request("plans/quotas", "GET");
		k.done(function(data){
			self.plans = data.quotas;
		})
	},

	render: function(){
		var self = this;
		this.$el.append(this.template(this));
		$.each(this.plans, function(iter, value){
			var subView = new Admin.PlanAddMorePluginsView({model: value})
			self.$("#populatePlugins").append(subView.render().el);
			
		})
		var subView = new Admin.PlanAddMorePricingView();
		this.$("#populatePlans").append(subView.render().el);
		return this;
	},

	events:{
		"click #addPlan": "addPlan",
		"click #addMore": "addMore",
	},

	addPlan:function(event){
		event.preventDefault();
		var self = this;
		this.pricingList = [];
		this.quotaList = [];
		$.each($("#populatePlans #plan"), function(iter, plan){
			self.pricingList.push({"name": plan.name.value,  "value": parseInt(plan.value.value), "period":  parseInt(plan.period.value)})
		})
		$.each($("#populatePlugins input"), function(){
			self.quotaList.push({"quota_id": $(this).attr("id"), "value": parseInt($(this).attr("value"))})
		});
		console.log(JSON.stringify({"name": $("#planName").val(), "quotas": this.quotaList, "pricings": this.pricingList}))

		var k = make_request("plans/plans", "POST", JSON.stringify({"name": $("#planName").val(), "quotas": this.quotaList, "pricings": this.pricingList}))
		k.done(function(data){
			if(data.status == 201 ){
				bootbox.alert("Plan has been Added");
			}
			else{
				bootbox.alert("Some error has occurred and the Plan cannot be addedd");
			}
		})

	},

	addMore: function(event){
		event.preventDefault();
		var subView = new Admin.PlanAddMorePricingView();
		$("#populatePlans").append(subView.render().el);
	},
});

Admin.PlanAddMorePluginsView = Backbone.View.extend({
	templateCheckBox: template("checkbox"),
	templateTextBox: template("textbox"),
	initialize: function(options){
		this.model = options.model;
		this.name = this.model.name; 
		this.quotaId = this.model.quota_id; 
	
		console.log(this.model.name , this.model.is_boolean)	
	},

	render: function(){
		if( this.model.is_boolean == false){
			this.$el.append(this.templateTextBox(this));
			return this;
		}
		else{
			this.$el.append(this.templateCheckBox(this));
			return this;
		}
	},

});


Admin.PlanAddMorePricingView = Backbone.View.extend({
	tagName: "form",
	className: "form-horizontal",
	template: template("plan-add-more-pricing"),
	render: function(){
		this.$el.append(this.template(this));
		this.$el.attr("id", "plan");
		return this;
	},

	events: {
		"click #editPlan" : "editPlan",
		"click #deletePlan" : "deletePlan",
	},

	editPlan: function(event){
		event.preventDefault();
		console.log("edit has ben licked");
	},

	deletePlan: function(event){
		event.preventDefault();
		this.remove();
	},
});


	/* This will be used to when a user clicks on /viewplans end point */
Admin.PlanViewAllView = Backbone.View.extend({
	tagName: "table",
	className: "table table-hover table-bordered table-condensed",
	template: template("view-all-plans"),

	initialize: function(){
		console.log("Intialize function of the plan view all has been called")	
	},

	render: function(){
		var self = this;
		this.$el.append(this.template(this));
		var k = make_request("plans/plans", "GET");
		k.done(function(data){
			$.each(data.plans, function(iter, plan){
			var subView = new Admin.PlanViewAllRowView({model: plan});
			self.$("#populateRow").append(subView.render().el);
			});
                $("table").tablecloth({
			theme: "paper",
			bordered: true,
			condensed: true,
			striped: true,    
			sortable: true,
			clean: true, 
		}); 
		});
		return this;
	},

	events: {
		"click #addPlan": "addPlan",
	},	

	addPlan: function(event){
		event.preventDefault();		
		var subView = new Admin.PlanView();
		this.$el.html(subView.render().el);
		return;
	},
});

Admin.PlanViewAllRowView = Backbone.View.extend({
	tagName: "tr",
	template: template("view-all-plans-row"),
	initialize: function(options){
		this.model = options.model;
		this.name = this.model.name;
	},
	render: function(){
		this.$el.append(this.template(this));
		return this;
	},
	events: {
		"click #deletePlan": "deletePlan",
	},

	deletePlan: function(event){
		event.preventDefault();
		this.remove();
		//Right now, tis delete only the view but not deletes the plan from the server, Need to integrate this
	},

});
/*This is router of the user dropdown menu
 */
Admin.Router = Backbone.Router.extend({
	initialize: function(options){
		this.el =  options.el ;
		console.log("Hey man!!");
		this.Login();
	},

	routes: {
		"":  "welcome",
		"merchant/createmerchant": "createMerchant",	
		"merchant/viewallmerchants": "listMerchants",
		"plans/addplan": "addPlan",	
		"plans/viewplans": "viewPlans",
	},
	
	welcome: function(){
		console.log("HOME view called");
		var str = new Admin.WelcomeView({message: "HOME"})
		this.el.html(str.render().el);
	},
	
	createMerchant: function(){
		console.log("HOME view called");
		var createMerchant = new Admin.CreateMerchant.View();
		this.el.html(createMerchant.render().el);
    	},
	
	listMerchants: function(){
		console.log("HOME view called");
		var listMerchants = new Admin.ListMerchants.View();
		this.el.html(listMerchants.render().el);
		$("table").tablecloth({theme: "paper", bordered: true, condensed: true, striped: true, sortable: true, clean: true, }); 
	},

	addPlan: function(){
		var str = new Admin.PlanView();
		this.el.empty();
		this.el.append(str.render().el)
	},
	viewPlans: function(){
		var str = new Admin.PlanViewAllView();
		this.el.empty();
		this.el.append(str.render().el)
		$("table").tablecloth({theme: "paper", bordered: true, condensed: true, striped: true, sortable: true, clean: true, }); 
	},
	Login: function(){
		var str = new Admin.AdminAccess.View();
		this.el.append(str.render().el)	
	},	
});

Admin.boot = function(container){
	console.log("User boot function loaded");
	container = $(container);
	this.el = container;
	var str = new Admin.AdminAccess.View();
	this.el.append(str.render().el)	
	var router = new Admin.Router({el: container});
	Backbone.history.start();
}
});



