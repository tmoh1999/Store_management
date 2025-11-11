function openScanner() {
	console.log(1990);
      // open scan page in popup
      window.open("/products/scanner", "scanner", "width=500,height=400");
    }

    // called by scanner page after detection
function setBarcode(value) {
	
      document.getElementById("product_brcode").value = value;
   
}
