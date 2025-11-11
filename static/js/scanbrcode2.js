function openScanner() {
	console.log(1991);
      // open scan page in popup
      window.open("/products/scanner", "scanner", "width=500,height=400");
    }

    // called by scanner page after detection
function setBarcode(value) {
	
      document.getElementById("search_q").value=value;
      document.getElementById("search_form").submit();
}
