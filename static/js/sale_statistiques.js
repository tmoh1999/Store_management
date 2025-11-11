function CreateSalesItemList(data){

let table = document.getElementById("sales_stat_table").getElementsByTagName("tbody")[0];

while (table.rows.length > 0) {
  table.deleteRow(0);
}


for (let i=0;i<data["results"].length;i++){
                    // insert new row at the end
                    let row = table.insertRow(-1);

                  // insert cells into the new row
                  let cell1 = row.insertCell(0);
                  let cell2 = row.insertCell(1);
                  let cell3 = row.insertCell(2);
                  let cell4 = row.insertCell(3);
                  
                  
                  
  
  // set content
  cell1.innerHTML = data["results"][i]["date"];
  cell2.innerHTML = data["results"][i]["nbsales"];
  cell3.innerHTML = data["results"][i]["nbitems"];
  cell4.innerHTML = data["results"][i]["total"];
  }
  
}


function updatelist2(){
	fetch("/sales/sale/statistiques", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
        	   date_start:document.getElementById("date_input_start").value,
        date_end:document.getElementById("date_input_end").value
        })
      })
      .then(r => r.json())
      .then(data => {
      	 
          if (data["results"].length>=0){
  CreateSalesItemList(data);
  
  }
       });
}


