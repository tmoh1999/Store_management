const $ = id => document.getElementById(id);
console.log(999);
function updateproduct(){
	 const prod_id=$("product_id").value
	console.log(`/product/${prod_id}/edit`)
     //let currentStatus = parseInt($("status").textContent);
      fetch(`/product/${prod_id}/edit`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
               product_name:$("product_name").value,
               product_price: parseFloat($("product_price").value),
               product_brcode: $("product_brcode").value,
        })
      })
      .then(r => r.json())
      .then(data => {
      	//for future responses from back end
         if (data["success"]==true){
         	if (window.opener) {
        window.opener.location.reload();
    }

                window.close();
                //alert(JSON.stringify(data["success"]));
                
          }
       });
}