const $ = id => document.getElementById(id);

function addproduct(){
	
     //let currentStatus = parseInt($("status").textContent);
      fetch("/insertproduct", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
               product_name:$("product_name").value,
               product_price: parseFloat($("product_price").value),
               product_brcode: $("product_brcode").value,
               product_quantity: $("product_quantity").value,
               product_purchase_price:$("product_purchase_price").value,
               purchase_id:$("purchase_id").value,
        })
      })
      .then(r => r.json())
      .then(data => {
      	//for future responses from back end
         alert(JSON.stringify(data));
       });
}
function SavePurchase(){
//let currentStatus = parseInt($("status").textContent);
      fetch("/purchase/confirm", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
        	   purchase_id:$("purchase_id").value,
        })
      })
      .then(r => r.json())
      .then(data => {
      	              //for future responses from back end
                       console.log(data);
                       
                       window.history.back();
       });
}
