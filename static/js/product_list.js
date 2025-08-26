function viewRow(btn) {
  let row = btn.closest("tr"); // get the row of the clicked button
  let name = row.cells[1].textContent;
  alert("Viewing product: " + name);
}
function editRow(btn) {
  let row = btn.closest("tr"); // get the row of the clicked button
  let name = row.cells[0].textContent;
  alert("Viewing product: " + name);
}

