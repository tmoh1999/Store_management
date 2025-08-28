function openScanner() {
	console.log(1991);
      // open scan page in popup
      window.open("/scanner", "scanner", "width=500,height=400");
    }
function searchquery(query){
	
     //let currentStatus = parseInt($("status").textContent);
      fetch("/search2", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
        	   query:query,
               sale_id:$("sale_id").value,
        })
      })
      .then(r => r.json())
      .then(data => {
      	 
          if (data["results"].length>0){
      	console.log(data["total"]);
                 $("total").textContent=data["total"]
                 let table = document.getElementById("sale_table");

                    // insert new row at the end
                    let row = table.insertRow(2);

                  // insert cells into the new row
                  let cell1 = row.insertCell(0);
                  let cell2 = row.insertCell(1);
                  let cell3 = row.insertCell(2);
                  let cell4 = row.insertCell(3);
  // set content
  cell1.innerHTML = data["results"][0]["name"]; // auto ID (row number)
  cell2.innerHTML = data["results"][0]["barcode"];
 let input = document.createElement("input");
  input.type = "number";
  input.value = data["results"][0]["price"]; ;
  input.min = 0;
  input.classList.add("cell-input");
  cell3.appendChild(input);
  
 let input1 = document.createElement("input");
  input1.type = "number";
  input1.value = 1;
  input1.min = 0;
  input1.classList.add("cell-input");
  cell4.appendChild(input1);
  }
       });
}
    // called by scanner page after detection
function setBarcode(value) {
	console.log(19999999);
      document.getElementById("search_q").value=value;
      searchquery(value);
}


const $ = id => document.getElementById(id);

function addsaleitems(){
	
     //let currentStatus = parseInt($("status").textContent);
      fetch("/sale/add_item", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
        	   sale_id:$("sale_id").value,
               price: parseFloat($("product_price").value),
               quantity: $("product_quantity").value
        })
      })
      .then(r => r.json())
      .then(data => {
      	              //for future responses from back end
                       $("total").textContent=data["total"]
                      let table = document.getElementById("sale_table");

                    // insert new row at the end
                    let row = table.insertRow(2);

                  // insert cells into the new row
                  let cell1 = row.insertCell(0);
                  let cell2 = row.insertCell(1);
                  let cell3 = row.insertCell(2);
                  let cell4 = row.insertCell(3);
  // set content
  cell1.innerHTML = ""; // auto ID (row number)
  cell2.innerHTML = "";
let input1 = document.createElement("input");
  input1.type = "number";
  input1.value = data["price"];
  input1.min = 0;
  input1.classList.add("cell-input");
cell3.appendChild(input1);
let input2 = document.createElement("input");
  input2.type = "number";
  input2.value = data["quantity"];;
  input2.min = 0;
  input2.classList.add("cell-input");
  cell4.appendChild(input2);
       });
}

