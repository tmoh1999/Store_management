

function supplierlist(){
	
     //let currentStatus = parseInt($("status").textContent);
      fetch("/suppliers/select_list", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
        })
      })
      .then(r => r.json())
      .then(data => {
      	
      
      	//for future responses from back end
         

         
        
         
         console.log(data);
         const select = document.getElementById("product_supplier");
         console.log(data["success"]);
  for (let x in data["suppliers"]) {
    const option = document.createElement("option");
    option.value = data["suppliers"][x]["supplier_id"];
    option.textContent = data["suppliers"][x]["name"];
    select.appendChild(option);
    console.log(data["suppliers"][x]["name"]);
  }
       });
}
supplierlist();