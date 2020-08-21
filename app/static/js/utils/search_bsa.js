function search_mapping_task() {
  var search_text = $("#bsa-task-id").val();
  if (search_text) {
    window.location.href = "/mapping/bsa/search/" + search_text;
  }
  return;
}

$(document).ready(function () {
  var search_but = $("#bsa-task-btn");
  search_but.on("click", search_mapping_task);
});
