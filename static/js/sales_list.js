function CreateSalesItemList(data){

let table = document.getElementById("sales_table");
console.log(table.rows.length)
while (table.rows.length > 1) {
  table.deleteRow(1);
}
console.log(table.rows.length);
tot=0;
tot2=0;
for (let i=0;i<data["results"].length;i++){
                    // insert new row at the end
                    let row = table.insertRow(-1);

                  // insert cells into the new row
                  let cell1 = row.insertCell(0);
                  let cell2 = row.insertCell(1);
                  let cell3 = row.insertCell(2);
                  let cell4 = row.insertCell(3);
                  let cell5 = row.insertCell(4);
                  let cell6 = row.insertCell(5);
  tot+=data["results"][i]["total_amount"];
  tot2+=data["results"][i]["quantity"];
  // set content
  cell1.innerHTML = data["results"][i]["sale_id"] // auto ID (row number)
  cell2.innerHTML = data["results"][i]["sale_date"];
  cell3.innerHTML = data["results"][i]["quantity"];
  cell4.innerHTML = data["results"][i]["total_amount"];
  
  
let button = document.createElement("button");
let saleId=data["results"][i]["sale_id"]
button.textContent = "View";
button.addEventListener("click", function () {
  window.open(`/sales/${saleId}/viewsaleitems`, '_blank', 'width=600,height=400');
});
cell5.appendChild(button)
let button2 = document.createElement("button");
button2.textContent = "Remove";
button2.addEventListener("click", () => removeSale(data["results"][i]["sale_id"]));
cell6.appendChild(button2);
  }
 console.log(tot);
 document.getElementById("total_price").innerHTML=tot;
 document.getElementById("total_quantity").innerHTML=tot2;
}

function updatelist(){
	
	 console.log(document.getElementById("sales_filter").value);
     //let currentStatus = parseInt($("status").textContent);
      fetch("/saleslist/update", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
        	   filter:document.getElementById("sales_filter").value,
        })
      })
      .then(r => r.json())
      .then(data => {
      	 
          if (data["results"].length>=0){
  CreateSalesItemList(data);
  
  }
       });
}
function updatelist2(d){
	fetch("/saleslist/update", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
        	   filter:d,
        })
      })
      .then(r => r.json())
      .then(data => {
      	 
          if (data["results"].length>=0){
  CreateSalesItemList(data);
  
  }
       });
}
function updatetotal(val){
	
	
	x=parseFloat(document.getElementById("total_price").innerHTML);
	
	
	y=x+parseFloat(val);
	

	document.getElementById("remain").innerHTML=y;

}

function removeSale(sale_id){
	fetch("/sale/remove", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
        	   sale_id:sale_id,
        })
      })
      .then(r => r.json())
      .then(data => {
      	 
          alert(JSON.stringify(data));
       });
}