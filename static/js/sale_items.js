const $ = id => document.getElementById(id);
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
  CreateSalesItemList(data);
  }
       });
}
function handleEdit(event){
let input=event.target;
let id=input.id;
parts=id.split('-')
console.log(id,parts);
fetch("/sale/update_item", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
        	   sale_id:$("sale_id").value,
               item_id:parts[1],
               target: parts[0],
               new_value:input.value
        })
      })
      .then(r => r.json())
      .then(data => {
      	              //for future responses from back end
                       $("total").textContent=data["total"];
CreateSalesItemList(data);
  
       });
}
    // called by scanner page after detection
function setBarcode(value) {
	console.log(19999999);
      document.getElementById("search_q").value=value;
      searchquery(value);
}




function addsaleitems(){
	
     //let currentStatus = parseInt($("status").textContent);
      fetch("/sale/add_item", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
        	   sale_id:$("sale_id").value,
               price: parseFloat($("product_price").value),
               quantity: $("product_quantity").value,
               description: $("product_description").value
        })
      })
      .then(r => r.json())
      .then(data => {
      	              //for future responses from back end
                       $("total").textContent=data["total"];
  CreateSalesItemList(data);
  $("product_price").value="";
    $("product_quantity").value="1";
  $("product_description").value="";
       });
}
function SaveSale(){
//let currentStatus = parseInt($("status").textContent);
      fetch("/sale/confirm", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
        	   sale_id:$("sale_id").value,
        })
      })
      .then(r => r.json())
      .then(data => {
      	              //for future responses from back end
                       console.log(data);
                       
                       window.history.back();
       });
}
function CancelSale(){
	
     //let currentStatus = parseInt($("status").textContent);
      fetch("/sale/remove", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
        	   sale_id:$("sale_id").value,
        })
      })
      .then(r => r.json())
      .then(data => {
      	              //for future responses from back end
                       console.log(data);
                       
                       window.history.back();
       });
}
function CreateSalesItemList(data){

let table = document.getElementById("sale_table");
console.log(table.rows.length)
while (table.rows.length > 2) {
  table.deleteRow(2);
}
console.log(table.rows.length)
for (let i=0;i<data["results"].length;i++){
                    // insert new row at the end
                    let row = table.insertRow(2);

                  // insert cells into the new row
                  let cell1 = row.insertCell(0);
                  let cell2 = row.insertCell(1);
                  let cell3 = row.insertCell(2);
                  let cell4 = row.insertCell(3);
                  let cell5 = row.insertCell(4);
                  
  // set content
  cell1.innerHTML = data["results"][i]["name"] // auto ID (row number)
  cell2.innerHTML = data["results"][i]["barcode"]
let input4 = document.createElement("input");
  
  input4.value = data["results"][i]["description"];
  input4.min = 0;
  input4.id="description-"+data["results"][i]["item_id"]
  input4.classList.add("cell-input");
  input4.style.background="lightblue";
  input4.addEventListener("change",handleEdit);
cell3.appendChild(input4);
let input1 = document.createElement("input");
  input1.type = "number";
  input1.value = data["results"][i]["price"];
  input1.min = 0;
  input1.id="price-"+data["results"][i]["item_id"]
  input1.classList.add("cell-input");
  input1.style.background="lightblue";
  input1.addEventListener("change",handleEdit);
cell4.appendChild(input1);
let input2 = document.createElement("input");
  input2.type = "number";
  input2.value = data["results"][i]["quantity"];
  input2.min = 0;
  input2.id="quantity-"+data["results"][i]["item_id"]
  input2.classList.add("cell-input");
  input2.style.background="lightblue";
  input2.addEventListener("change",handleEdit);
  cell5.appendChild(input2);
  }
 $("product_price").focus();
}