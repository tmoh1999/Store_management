const $ = id => document.getElementById(id);

function addsupplier(){
	
     //let currentStatus = parseInt($("status").textContent);
      fetch("/suppliers/insert", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
               supplier_name:$("supplier_name").value,
               supplier_email:$("supplier_email").value,
               supplier_phone:$("supplier_phone").value,

        })
      })
      .then(r => r.json())
      .then(data => {
      	//for future responses from back end
         alert(JSON.stringify(data));
       });
}