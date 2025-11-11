function CreateSalesItemList(data) {
    let table = document.getElementById("products_table").getElementsByTagName("tbody")[0];

    // Remove all rows except the header (2 rows)
    while (table.rows.length > 0) {
        table.deleteRow(0); // Keep totals row and header row
    }
   
    

    data["results"].forEach(item => {
        let row = table.insertRow(-1);
        let dmode=document.getElementById("display_mode").value;
        console.log("dmode"+dmode);
        // Insert cells
        let cell1 = row.insertCell(0);
        let cell2 = row.insertCell(1);
        let cell3 = row.insertCell(2);
        let cell4 = row.insertCell(3);
        let cell5 = row.insertCell(4);
        let cell6 = row.insertCell(5);

        // Accumulate totals
        

        // Set cell content
        cell1.innerHTML = item.id;
        cell2.innerHTML = item.name;
        cell3.innerHTML = item.barcode;
        cell4.innerHTML = item.price;
        cell5.innerHTML =item.quantity; 

        // Actions column
        cell6.className = "d-flex flex-column justify-content-center gap-2 h-100";
        cell6.style.position = "sticky";
        cell6.style.right = "0";
        
        if (dmode==1){
        	
        	// View button
        let btnAdd = document.createElement("button");
        
        btnAdd.className = "btn btn-sm btn-success";
        btnAdd.textContent = "Add";
        btnAdd.addEventListener("click", () => {
            window.open(`/products/product/${item.id}/addproducts`, '_blank', 'width=600,height=400');
        });
       cell6.appendChild(btnAdd);
        } else if (dmode==3){
        	
        let type=document.getElementById("display_type").value;
        let row_id=document.getElementById("display_row_id").value;
        let btnSelect= document.createElement("button");
        btnSelect.className = "btn btn-sm btn-success";
        
        btnSelect.textContent = "Select";
        btnSelect.addEventListener("click", () => {
            selectclick(item.id,row_id,type);
        });
        cell6.appendChild(btnSelect);
        } else{
       
        // View button
        let btnView = document.createElement("button");
        btnView.className = "btn btn-sm btn-info";
        btnView.textContent = "View";
        btnView.addEventListener("click", () => {
            window.open(`/products/product/${item.id}/viewsales`, '_blank', 'width=600,height=400');
        });
        // View button
        let btnEdit = document.createElement("button");
        btnEdit.className = "btn btn-sm btn-warning";
        btnEdit.textContent = "Edit";
        btnEdit.addEventListener("click", () => {
            window.open(`/products/product/${item.id}/edit`, '_blank', 'width=600,height=400');
        });
                // View button
        let btnRemove = document.createElement("button");
        btnRemove.className = "btn btn-sm btn-danger";
        btnRemove.textContent = "Remove";
        btnRemove.addEventListener("click", () => {
            window.open(`/products/product/${item.id}/remove`, '_blank', 'width=600,height=400');
        });
        

        // Append buttons
        cell6.appendChild(btnView);
        cell6.appendChild(btnEdit);
        cell6.appendChild(btnRemove);
        }
    });

    
}

function updatelist(){
	
	 
     //let currentStatus = parseInt($("status").textContent);
      fetch("/products/productlist", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
        	   search_q:document.getElementById("search_q").value,
               products_filter:document.getElementById("products_filter").value,
        })
      })
      .then(r => r.json())
      .then(data => {
      	 
          if (data["results"].length>=0){
          	console.log(document.getElementById("products_filter").value)
  CreateSalesItemList(data);
  
  }
       });
}


function selectclick(product_id, row_id, type){
    fetch("/products/product/selected", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ product_id, row_id, type })
    })
    .then(r => r.json())
    .then(data => {
        console.log(JSON.stringify(data));
       if (window.opener && !window.opener.closed) {
       	 console.log(window.opener.location.pathname)
            window.opener.selectResponse(data);
        }
        window.close();
    });
}

function printProducts(){
let query=document.getElementById("search_q").value;
let filt=document.getElementById("products_filter").value;
window.open(`/products/products.pdf/${ filt }/${ query }`, '_blank', 'width=600,height=400')
}