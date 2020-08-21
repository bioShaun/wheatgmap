$(document).ready(function () {
  function connResult() {
    taskId = $("#result").attr("task-id");
    ajaxSend(
      "/task/result/",
      { task_id: taskId },
      function (data) {
        if (data.msg == "ok") {
          layer.close(index);
          clearInterval(status);
          //$("#task-state").text('task state:success');
          layer.msg("task done...");
          if (data.task == "vcf_upload") {
            uploadTask(data.result);
            return;
          }
          if (data.task == "vcf_ann") {
            annTask(data.result);
            return;
          }
          if (data.task == "bsa") {
            bsaTask(data.result);
            return;
          }
          if (data.task == "enrich") {
            enrichTask(data.result);
            return;
          }
          if (data.task == "snp_info" || data.task == "compare_info") {
            snpInfoTask(data.result);
            return;
          }
          layer.alert("no task type: " + data.task);
          return;
        } else if (data.msg == "pending") {
          return;
        } else if (data.msg == "error") {
          layer.close(index);
          clearInterval(status);
          layer.alert("task " + taskId + " failed...");
          //$("#task-state").text("task state:failed");
          return;
        }
      },
      "POST"
    );
  }
  var index = layer.load(1);
  var status = setInterval(connResult, 2000);

  setFooter();
});

function uploadTask(result) {
  layer.alert(result);
  return;
}

function annTask(result) {
  $("#result").empty();
  $("#result").html(
    "<p><a class='btn btn-lg btn-primary' href='/static/download/vcf_ann/" +
      result +
      "' role='button'>download annotation zip files &raquo; </a></p>"
  );
  return;
}

function bsaTask(result) {
  $("#result").empty();
  var plotStr = createPlot(result.files, result.path, result.params);
  $("#result").html(plotStr);
  $("a.snp-index").fancybox({
    overlayShow: true,
    transitionIn: "elastic",
    transitionOut: "elastic",
  });
  $("a[rel=example_group]").fancybox({
    transitionIn: "none",
    transitionOut: "none",
    titlePosition: "over",
    titleFormat: function (title, currentArray, currentIndex, currentOpts) {
      return (
        '<span id="fancybox-title-over">Image ' +
        (currentIndex + 1) +
        " / " +
        currentArray.length +
        (title.length ? " &nbsp; " + title : "") +
        "</span>"
      );
    },
  });
  $("div.albumSlider").albumSlider();
}

function enrichTask(result) {
  $("#result").empty();
  if (result.body.length == 0) {
    layer.alert("no enrich on your gene list.");
    return;
  }
  var tableStr = createTable(result.header, result.body, result.href);
  $("#result").html(tableStr);
  $(".table").DataTable({
    dom: "Bfrtip",
    scrollX: true,
    buttons: ["copy", "csv", "excel", "pdf", "print"],
  });
}

function snpInfoTask(result) {
  $("#result").empty();
  if (result.header.length == 0) {
    layer.alert("backend: query empty");
    return;
  }
  var tableStr = createTable(result.header, result.body, (href = ""));
  $("#result").html(tableStr);
  $(".table").DataTable({
    dom: "Bfrtip",
    scrollX: true,
    buttons: ["copy", "csv", "excel", "pdf", "print"],
  });
}

function createTable(headData, bodyData, href) {
  var htmlBuffer = [];
  htmlBuffer.push("<table class='table table-strip table-bordered'>");
  htmlBuffer.push("<thead>\n<tr>");
  for (var i = 0; i < headData.length; i++) {
    htmlBuffer.push("<th>" + headData[i] + "</th>");
  }
  htmlBuffer.push("</tr>\n</thead>");
  htmlBuffer.push("<tbody>");
  for (var i = 0; i < bodyData.length; i++) {
    htmlBuffer.push("<tr>");
    for (var j = 0; j < bodyData[i].length; j++) {
      if (j == 0 && href.length != 0) {
        href_str = createHref(bodyData[i][j], href[i]);
        htmlBuffer.push("<td>" + href_str + "</td>");
      } else {
        htmlBuffer.push("<td>" + bodyData[i][j] + "</td>");
      }
    }
    htmlBuffer.push("</tr>");
  }
  htmlBuffer.push("</tbody>");
  htmlBuffer.push("</table>");
  tableStr = htmlBuffer.join("\n");
  return tableStr;
}

function createHref(term, href) {
  href_str = "<a target='_blank' href='" + href + "'>" + term + "</a>";
  return href_str;
}
