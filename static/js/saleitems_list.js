function CreateSalesItemList(data){

let table = document.getElementById("sales_table").getElementsByTagName("tbody")[0];

while (table.rows.length > 0) {
  table.deleteRow(0);
}

let tot=0,tot2=0,tot3=0;
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
                  let cell7 = row.insertCell(6);
                  let cell8 = row.insertCell(7);
                  
  
  // set content
  cell1.innerHTML = data["results"][i]["sale_id"] // auto ID (row number)
  cell2.innerHTML = data["results"][i]["date"];
  cell3.innerHTML = data["results"][i]["unit_price"];
  cell4.innerHTML = data["results"][i]["product"];
  cell5.innerHTML = parseFloat(data["results"][i]["profit"])*parseFloat(data["results"][i]["quantity"]);
  cell6.innerHTML = data["results"][i]["quantity"];
  cell7.innerHTML = data["results"][i]["total"];
  cell8.innerHTML = data["results"][i]["description"];
  console.log("profit:"+data["results"][i]["profit"])
  tot+=parseFloat(data["results"][i]["total"]);
tot2+=parseFloat(data["results"][i]["quantity"]);
tot3+=parseFloat(data["results"][i]["profit"])*parseFloat(data["results"][i]["quantity"]);
  }
  document.getElementById("total_sum").innerHTML=tot;
 document.getElementById("total_quantity").innerHTML=tot2;
 document.getElementById("total_profit").innerHTML=tot3;
}


function updatelist2(){
	fetch("/saleitemslist/update", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
        	   date_start:document.getElementById("date_input_start").value,
        date_end:document.getElementById("date_input_end").value,
        filter2:document.getElementById("search_q").value,
        })
      })
      .then(r => r.json())
      .then(data => {
      	 
          if (data["results"].length>=0){
  CreateSalesItemList(data);
  
  }
       });
}


