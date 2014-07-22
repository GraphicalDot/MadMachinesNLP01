
/* This is a javascript file to open an indexedd db and storing data in it
*/

(function(){

           var menu_list = [{"menu_item": "Home", "value": {"configuration" : ["no opitions"]}},

            { "menu_item": "Purchase", "value": {"orders": ["create", "receive order", "due", "overdue", "received", "cancelled", "view all"], 
                                        "purchase return": ["create", "view all"], 
                                             "suppliers":  ["create", "view all"], 
                                               "expenses": ["add expenses", "refund expenses", "view all"], 
                                           "make_payment": ["no options"], 
                                            "credit note": ["accept", "view all"]} },
            
            {"menu_item":"Sales", "value": {"invoices": ["create", "unpaid", "paid", "view all"],
                                              "orders": ["create", "due", "overdue", "invoiced", "cancelled", "view all"],
                                           "customers": ["create", "view all"], 
                                     "receive payment": ["no options"], 
                                             "returns": ["create", "view all"],
                                                 "pos": ["create", "view all"], }},

                                    
            {"menu_item": "Money", "value": {"bank account": ["create", "view all"],
                                                 "payments": ["make payment", "receive payment", "transfer funds", "view all"],
                                                 "balances": ["receivables", "payables", "all party balances"],
                                         "all transactions": ["no opitions"], }},

            {"menu_item": "Reports", "value": {"financial": ["balance sheet", "cash flow statement", "income statement", "cash flow cycle"],
                                           "sales reports": ["by products", "by data range", "by month", "by pos", "by supplier"], 
                                        "purchase reports": ["by products", "by data range", "by supplier"],
                                        "company snapshot": ["no options"]}},

            {"menu_item": "Settings", "value": {"tax settings": ["no opitions"],
                                           "invoice templates": ["no opitions"],
                                                "company info": ["no opitions"],
                                                "payment mode": ["no opitions"],
                                                    "settings": ["no opitions"],
                                                 "app settings":["no opitions"],} },

            {"menu_item": "Help", "value": {"documentation": ["no opitions"],
                                                "tutorials": ["no opitions"],
                                           "contact suport": ["no opitions"],
                                                    "about": ["no opitions"],
                                             "license info": ["no opitions"],}}, 

            {"menu_item" : "Users", "value": {"create user": ["no opitions"], 
                                             "manage users": ["no opitions"],
                                               "user roles": ["no opitions"],
                                          "user permissons": ["no opitions"],
                                       "user activity role": ["no opitions"], }},

            {"menu_item": "Tools", "value": {"import": ["no opitions"],
                                            "export": ["no opitions"],}}, ]


	var EasySales = new Object();
	EasySales.db = null;

	EasySales.open = function(){
		window.indexedDB = window.indexedDB || window.mozIndexedDB || window.webkitIndexedDB || window.msIndexedDB;
		if (!window.indexedDB) {
			window.alert("Your browser doesn't support a stable version of IndexedDB. Such and such feature will not be available.");
					}
		else{
			console.log("We have the required version of index db to use")
		}
        
		var db_request = window.indexedDB.open("Canworks", 1);
		
		db_request.onsuccess = function(e){
			EasySales.db = e.target.result;

		db_request.onupgradeneeded = function(event) { 
			var db = event.target.result;
			var objectStore = db.createObjectStore("menu_items", {keyPath: "menu_item", autoIncrement: true});
    
			var transaction = db.transaction(["menu_items"], "readwrite");
			var Store = transaction.objectStore("menu_items");
		    
			for (var i in menu_items) {
				var request = objectStore.add(menu_items[i]);
				request.onsuccess = function(event){
				// event.target.result == customerData[i].menu_item;
								};
						}
    						};
				}
)




