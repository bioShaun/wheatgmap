function DeleteSample() {
  var rows = $("#sample-table").bootstrapTable("getSelections");
  if (rows.length == 0) {
    alert("please choose one first.");
    return;
  }
  var ids = "";
  for (var i = 0; i < rows.length; i++) {
    ids += rows[i]["tc_id"] + ",";
  }
  ids = ids.substring(0, ids.length - 1);
  var msg = "are you sure delete those samples.";
  if (confirm(msg) == true) {
    $.ajax({
      url: "/auth/fetch_samples/",
      type: "delete",
      data: { ids: ids },
      success: function (data) {
        if (data.msg == "ok") {
          alert("delete success.");
          $("#sample-table").bootstrapTable("refresh");
        }
      },
      error: function (data) {
        alert("error.");
      },
    });
  }
}

function PubSample() {
  var rows = $("#sample-table").bootstrapTable("getSelections");
  if (rows.length == 0) {
    alert("please choose your data first.");
    return;
  }
  var ids = "";
  for (var i = 0; i < rows.length; i++) {
    ids += rows[i]["tc_id"] + ",";
  }
  ids = ids.substring(0, ids.length - 1);
  var msg = "are you sure public those samples.";
  if (confirm(msg) == true) {
    $.ajax({
      url: "/auth/fetch_samples/",
      type: "post",
      data: { ids: ids, action: "pub" },
      success: function (data) {
        if (data.msg == "ok") {
          alert("public success.");
          $("#sample-table").bootstrapTable("refresh");
        }
      },
      error: function (data) {
        alert("error");
      },
    });
  }
}

function PrSample() {
  var rows = $("#sample-table").bootstrapTable("getSelections");
  if (rows.length == 0) {
    alert("please choose your data first.");
    return;
  }
  var ids = "";
  for (var i = 0; i < rows.length; i++) {
    ids += rows[i]["tc_id"] + ",";
  }
  ids = ids.substring(0, ids.length - 1);
  var msg = "are you sure private those samples.";
  if (confirm(msg) == true) {
    $.ajax({
      url: "/auth/fetch_samples/",
      type: "post",
      data: { ids: ids, action: "private" },
      success: function (data) {
        if (data.msg == "ok") {
          alert("private success.");
          $("#sample-table").bootstrapTable("refresh");
        }
      },
      error: function (data) {
        alert("error");
      },
    });
  }
}

function EditInit() {
  var row = $("#sample-table").bootstrapTable("getSelections");
  if (row.length != 1) {
    alert("edit only allow choose one row.");
    $("#btn_edit").attr("data-toggle", "");
    return;
  }
  $("#btn_edit").attr("data-toggle", "modal");
  $("#myModalLabel").text("Sample: " + row[0]["tc_id"]);
  //$("#scientific_name").val(row[0]['tc_id']);
  return;
}

function EditSample() {
  var row = $("#sample-table").bootstrapTable("getSelections");
  if (row.length > 1) {
    alert("edit only allow choose one row.");
    return;
  }
  var obj = {};
  $("#editForm")
    .find("input")
    .each(function (i, val) {
      if (val.value != "") {
        obj[val.name] = val.value;
      }
    });
  if (Object.keys(obj).length == 0) {
    alert("update sample form is empty.");
    return;
  }
  obj["id"] = row[0]["tc_id"];
  $.ajax({
    url: "/auth/fetch_samples/",
    type: "put",
    data: { data: JSON.stringify(obj) },
    success: function (data) {
      if (data.msg == "ok") {
        $("#editModal").modal("hide");
        $("#sample-table").bootstrapTable("refresh");
        alert("edit success.");
      } else {
        alert("edit failed...");
      }
    },
    error: function (data) {
      alert("error...");
    },
  });
}

function is_legal_name(name, maxLen = 45, iligal_str = "=&") {
  if (name.length > maxLen) {
    return "Maximum request length exceeded";
  }
  var iligal_str_re = new RegExp(`[${iligal_str}]`, "g");
  if (iligal_str_re.test(name)) {
    return `Illegal character [${iligal_str}] in input.`;
  }
}

function is_va_id(name) {
  if (!/^TC-Va-(\d+)/.test(name)) {
    return "Illegal Variety Name, name pattern is: TC-Va-number.";
  }
}

$(document).ready(function () {
  function linkFormatter(value, row, index) {
    if (typeof value === "string") {
      let baseUrl = "/data/samples/";
      if (value.startsWith("TC-Va")) {
        baseUrl = "/variety/detail/";
      }
      return `<a href="${baseUrl}${value}/" target='_blank'>${value}</a>`;
    } else {
      return value;
    }
  }

  function pubFormatter(value) {
    if (typeof value === "boolean") {
      return value ? "Yes" : "No";
    } else {
      return value;
    }
  }

  // 初始化Table
  $("#sample-table").bootstrapTable({
    url: "/auth/fetch_samples/",
    method: "get",
    toolbar: "#toolbar", //工具列
    striped: true, //隔行换色
    cache: false, //禁用缓存
    pagination: true, //关闭分页
    showFooter: false, //是否显示列脚
    showPaginationSwitch: true, //是否显示 数据条数选择框
    sortable: false, //排序
    search: true, //启用搜索
    showFullscreen: true, //全屏按钮
    /* showToggle:true,//显示详细视图和列表 */
    showColumns: true, //是否显示 内容列下拉框
    showRefresh: true, //显示刷新按钮
    //clickToSelect: true, //点击选中checkbox
    pageNumber: 1, //初始化加载第一页，默认第一页
    pageSize: 10, //每页的记录行数
    pageList: [10, 25, 50, 100], //可选择的每页行数
    //paginationPreText: "pre",
    //paginationNextText: "下一页",
    paginationFirstText: "First",
    paginationLastText: "Last",
    showExport: true, //是否显示导出按钮
    buttonsAlign: "right", //按钮位置
    exportTypes: ["excel", "txt", "csv"], //导出文件类型
    Icons: "glyphicon-export",
    columns: [
      {
        title: "全选",
        field: "select",
        checkbox: true,
      },
      {
        field: "tc_id",
        title: "WG ID",
        switchable: true,
        sortable: true,
        formatter: linkFormatter,
      },
      {
        field: "opened",
        title: "Public",
        switchable: true,
        sortable: true,
        formatter: pubFormatter,
        editable: {
          type: "select",
          title: "Type",
          source: [
            { value: "Yes", text: "Yes" },
            { value: "No", text: "No" },
          ],
        },
      },
      {
        field: "sample_name",
        title: "Sample Name",
        switchable: true,
        editable: {
          type: "text",
          title: "Sample Name",
          validate: function (v) {
            if (!v) return "Sample name can not be null";
            return is_legal_name(v);
          },
        },
      },
      {
        field: "type",
        title: "Type",
        switchable: true,
        editable: {
          type: "select",
          title: "Type",
          source: [
            { value: "WES", text: "WES" },
            { value: "WGS", text: "WGS" },
            { value: "RNAseq", text: "RNAseq" },
          ],
        },
      },
      {
        field: "scientific_name",
        title: "Scientific Name",
        switchable: true,
        editable: {
          type: "text",
          title: "Scientific Name",
          validate: function (v) {
            return is_legal_name(v);
          },
        },
      },
      {
        field: "variety_name",
        title: "Variety ID",
        switchable: true,
        //formatter: linkFormatter,
        editable: {
          type: "text",
          title: "Variety ID",
          validate: function (v) {
            if (v) {
              return is_va_id(v);
            }
          },
        },
      },
      {
        field: "tissue",
        title: "Tissue",
        switchable: true,
        editable: {
          type: "text",
          title: "Tissue",
          validate: function (v) {
            return is_legal_name(v);
          },
        },
      },
      {
        field: "age",
        title: "Age",
        switchable: true,
        editable: {
          type: "text",
          title: "Age",
          validate: function (v) {
            return is_legal_name(v);
          },
        },
      },
      {
        field: "bulked_segregant",
        title: "Phenotype",
        switchable: true,
        editable: {
          type: "text",
          title: "Phenotype",
          validate: function (v) {
            return is_legal_name(v, (maxLen = 500));
          },
        },
      },
      {
        field: "mixed_sample",
        title: "Pooled Sample",
        switchable: true,
        editable: {
          type: "text",
          title: "Pooled Sample",
          validate: function (v) {
            return is_legal_name(v, (maxLen = 500));
          },
        },
      },
      {
        field: "dol",
        title: "DOI",
        switchable: true,
        editable: {
          type: "text",
          title: "DOI",
          validate: function (v) {
            return is_legal_name(v, (maxLen = 500));
          },
        },
      },
    ],

    onEditableSave: function (field, row, oldValue, $el) {
      $.ajax({
        type: "post",
        url: "/auth/edit_samples/",
        data: row,
        contentType: "application/json",
        success: function (data, status) {
          if (status == "success") {
            $.confirm({
              boxWidth: "30%",
              backgroundDismiss: true,
              title: "Success!",
              type: "green",
              content: "Date Updated.",
              buttons: { close: function () {} },
            });
          }
        },
        error: function () {
          $.confirm({
            boxWidth: "30%",
            backgroundDismiss: true,
            title: "Failed!",
            type: "red",
            content: "Please Try Again.",
            buttons: { close: function () {} },
          });
        },
        complete: function () {},
      });
    },
  });

  $("#sample-table").on("load-success.bs.table", function (data) {
    const documentHeight = Math.max(
      document.body["scrollHeight"],
      document.documentElement["scrollHeight"]
    );
    const windowHeight = $(window).height();

    if (windowHeight === documentHeight) {
      $("#footer").show();
    } else {
      $("#footer").hide();
    }

    $(window).scroll(function () {
      if (scrollY + windowHeight === documentHeight) {
        $("#footer").fadeIn();
      } else {
        $("#footer").hide();
      }
    });
  });
});
