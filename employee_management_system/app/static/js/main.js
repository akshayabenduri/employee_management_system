// Fill the delete-confirmation modal with the selected employee's details
document.addEventListener("DOMContentLoaded", function () {
  const modal = document.getElementById("deleteModal");
  if (!modal) return;
  modal.addEventListener("show.bs.modal", function (event) {
    const btn = event.relatedTarget;
    document.getElementById("deleteName").textContent = btn.getAttribute("data-name");
    document.getElementById("deleteForm").action = btn.getAttribute("data-url");
  });
});
