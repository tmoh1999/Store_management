const $ = id => document.getElementById(id);
console.log(999);
function updatesupplier(){
	 const supp_id=$("supplier_id").value
	console.log(`/supplier/${supp_id}/edit`)
     //let currentStatus = parseInt($("status").textContent);
      fetch(`/supplier/${supp_id}/edit`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
               supplier_name:$("supplier_name").value,
               supplier_email: $("supplier_email").value,
               supplier_phone: $("supplier_phone").value,
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