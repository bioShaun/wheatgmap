$(document).ready(function () {
  $("#submit").click(function () {
    var genes = $("#genes").val();
    var chr = $("#select-chr").find("option:selected").text();
    var startPos = $("#pos-start").val();
    var endPos = $("#pos-end").val();
    if (chr || startPos || endPos) {
      const posMsg = check_location(
        {
          chromsome: chr,
          "start-position": startPos,
          "end-position": endPos,
        },
        (maxRange = null)
      );
      if (posMsg) {
        $.alert({
          title: "Location Error!",
          content: posMsg,
        });
        return;
      }
    } else {
      if (!genes) {
        $.alert({
          title: "Empty Input!",
          content: "[Gene IDs]/[Genome region] is needed.",
        });
        return;
      }
    }
    var info = { genes: genes, chrom: chr, start: startPos, end: endPos };

    info = JSON.stringify(info);
    ajaxSend(
      "/tools/blast/table/",
      { info: info },
      function (data) {
        $("results-table").empty();
        if (data.msg != "ok") {
          createAlert(data.msg);
          return;
        } else {
          var headData = [
            "GENE_ID",
            "Description",
            "Pfam_Description",
            "Interpro_Description",
            "GO_Description",
          ];
          var tableStr = createTable(headData, data.result, "expr");
          $("#results-table").html(tableStr);
          $(".table").DataTable({
            ordering: false,
            dom: "Bfrtip",
            buttons: ["copy", "csv", "excel", "pdf", "print"],
          });
        }
      },
      "POST"
    );
  });

  $("#reset").click(function () {
    $("input[type='text']").val("");
    $("#genes").val("");
    document.getElementById("select-chr").options.selectedIndex = 0;
    $("#select-chr").selectpicker("refresh");
    $("results-table").empty();
  });
});
