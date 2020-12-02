/*
function createHref(term, href) {
  href_str = "<a target='_blank' href='" + href + "'>" + term + "</a>";
  return href_str;
}
*/
function createHref(term, href) {
  if (href.search(/amigo.geneontology.org/i) != -1) {
    tmp_href = "http://amigo.geneontology.org/amigo/term/" + href.split("=")[1];
  } else {
    tmp_href = href;
  }
  href_str = "<a target='_blank' href='" + tmp_href + "'>" + term + "</a>";
  return href_str;
}
function createTable(headData, bodyData, href) {
  var htmlBuffer = [];
  htmlBuffer.push(
    '<table id="example" class="table table-striped table-bordered table-hover enrich-table">'
  );
  htmlBuffer.push("<thead>\n<tr>");
  for (var i = 0; i < headData.length; i++) {
    htmlBuffer.push("<th>" + headData[i] + "</th>");
  }
  htmlBuffer.push("</tr>\n</thead>");
  htmlBuffer.push("<tbody>");
  for (var i = 0; i < bodyData.length; i++) {
    htmlBuffer.push("<tr>");
    for (var j = 0; j < bodyData[i].length; j++) {
      if (j == 0) {
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

$(document).ready(function () {
  $("#submit").click(function () {
    var formData = new FormData();
    var specie = $("#species").find("option:selected").text();
    if (specie.length == 0) {
      layer.alert("please choose specie first.", { icon: 0 });
      return;
    }
    formData.append("specie", specie);
    var geneList = $("#gene-list").val();
    if (geneList.length != 0 && geneList.slice(0, 7) != "TraesCS") {
      layer.alert("gene name is TraesCS*.", { icon: 0 });
      return;
    } else if (geneList.length != 0) {
      formData.append("gene_list", geneList);
    } else {
      var fileObj = document.getElementById("gene-file").files;
      if (fileObj.length == 0) {
        layer.alert("no gene list and upload file.", { icon: 0 });
        return;
      }
      formData.append("file", fileObj[0]);
    }
    var index = layer.load(1);
    $.ajax({
      url: "/expression/enrich/table/",
      type: "post",
      data: formData,
      contentType: false,
      processData: false,
      xhr: function () {
        var xhr = new XMLHttpRequest();
        xhr.upload.addEventListener("progress", function (e) {
          var progressRate = (e.loaded / e.total) * 100 + "%";
          $(".progress-bar").css("width", progressRate);
        });
        return xhr;
      },
      success: function (data) {
        layer.close(index);
        if (data.msg == "ok") {
          $(".progress-bar").css("width", "0%");
          $("#result-table").empty();
          var tableStr = createTable(
            data.result.header,
            data.result.body,
            data.result.href
          );
          $("#result-table").html(tableStr);
          var table = $(".enrich-table").DataTable({
            lengthChange: false,
            buttons: ["copy", "csv"],
          });
          table
            .buttons()
            .container()
            .appendTo("#example_wrapper .col-md-6:eq(0)");
          return;
        } else if (data.msg == "async") {
          window.location.href = "/task/result/" + data.task_id + "/";
          return;
        } else {
          layer.close(index);
          layer.alert(data.msg, { icon: 2 });
          return;
        }
      },
    });
  });
});
