const $ = id => document.getElementById(id);

function addtransaction(){
	
     //let currentStatus = parseInt($("status").textContent);
      fetch("/transaction/add", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
               transaction_amount: parseFloat($("transaction_amount").value),
               transaction_type: $("transaction_type").value,
               transaction_date: $("transaction_date").value
        })
      })
      .then(r => r.json())
      .then(data => {
      	//for future responses from back end
         alert(JSON.stringify(data));
       });
}