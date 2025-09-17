function CreateTransactionsList(data){

let table = document.getElementById("transactions_table");
console.log(table.rows.length)
while (table.rows.length > 1) {
  table.deleteRow(1);
}
console.log(table.rows.length);

for (let i=0;i<data["results"].length;i++){
                    // insert new row at the end
                    let row = table.insertRow(-1);

                  // insert cells into the new row
                  let cell1 = row.insertCell(0);
                  let cell2 = row.insertCell(1);
                  let cell3 = row.insertCell(2);
                  let cell4 = row.insertCell(3);
                  let cell5 = row.insertCell(4);
  
  // set content
  cell1.innerHTML = data["results"][i]["id"] // auto ID (row number)
  cell2.innerHTML = data["results"][i]["date"];
  cell3.innerHTML = data["results"][i]["type"];
  cell4.innerHTML = data["results"][i]["amount"];
  let button = document.createElement("button");
let transId=data["results"][i]["id"]
button.textContent = "Remove";
button.addEventListener("click", function () {
  window.open(`/transaction/${transId}/remove`, '_blank', 'width=600,height=400');
});
 cell5.appendChild(button)

 }
 
}


function updatelist(d){
	console.log(15);
	fetch("/transactions/list/update", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
        	   filter:d,
        })
      })
      .then(r => r.json())
      .then(data => {
      	 
          if (data["results"].length>=0){
  CreateTransactionsList(data);
  document.getElementById("caption_balance").innerHTML="Transactions: "+String(data["balance"]);
  
  }
       });
}
