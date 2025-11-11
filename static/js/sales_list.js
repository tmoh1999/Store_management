
function CreateSalesItemList(data) {
    let table = document.getElementById("sales_table").getElementsByTagName("tbody")[0];

    // Remove all rows except the header (2 rows)
    while (table.rows.length > 0) {
        table.deleteRow(0); // Keep totals row and header row
    }

    let tot = 0;
    let tot2 = 0;

    data["results"].forEach(item => {
        let row = table.insertRow(-1);
        console.log("::::"+row.parentNode.tagName)
        // Insert cells
        let cell1 = row.insertCell(0);
        let cell2 = row.insertCell(1);
        let cell3 = row.insertCell(2);
        let cell4 = row.insertCell(3);
        let cell5 = row.insertCell(4);
        let cell6 = row.insertCell(5);

        // Accumulate totals
        tot += item.total_amount;
        tot2 += item.quantity;

        // Set cell content
        cell1.innerHTML = item.sale_id;
        cell2.innerHTML = item.sale_date;
        cell3.innerHTML = item.quantity;
        cell4.innerHTML = item.total_amount;
        cell5.innerHTML = ''; // empty cell if needed

        // Actions column
        cell6.className = "d-flex flex-column justify-content-center gap-2 h-100";
        cell6.style.position = "sticky";
        cell6.style.right = "0";
        

        // View button
        let btnView = document.createElement("button");
        btnView.className = "btn btn-success btn-sm w-100";
        btnView.textContent = "View";
        btnView.addEventListener("click", () => {
            window.open(`/sales/sales/${item.sale_id}/viewsaleitems`, '_blank', 'width=600,height=400');
        });

        // Remove button
        let btnRemove = document.createElement("button");
        btnRemove.className = "btn btn-danger btn-sm w-100";
        btnRemove.textContent = "Remove";
        btnRemove.addEventListener("click", () => removeSale(item.sale_id));

        // Append buttons
        cell6.appendChild(btnView);
        cell6.appendChild(btnRemove);
    });

    // Update totals in header
    document.getElementById("total_price").innerHTML = tot;
    document.getElementById("total_quantity").innerHTML = tot2;
}

function updatelist(){
	
	 console.log(document.getElementById("sales_filter").value);
     //let currentStatus = parseInt($("status").textContent);
      fetch("/sales/saleslist/update", {
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
	fetch("/sales/saleslist/update", {
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
	fetch("/sales/sale/remove", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
        	   sale_id:sale_id,
        })
      })
      .then(r => r.json())
      .then(data => {
      	 
          alert(JSON.stringify(data));
          window.location.reload();
       });
}