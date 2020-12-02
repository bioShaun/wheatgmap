function check_gene(info) {
  var keys = Object.keys(info);
  for (var i = 0; i < keys.length; i++) {
    if (info[keys[i]].length == 0) {
      createAlert(keys[i] + " is empty!");
      return false;
    } else if (info[keys[i]] == "group" && info[keys[i]].length > 20) {
      createAlert("samples number have to < 20!");
      return false;
    }
  }
  return true;
}

function expr_line(head, data) {
  var expr_plot = echarts.init(document.getElementById("results-plot"));
  var series = [];
  var keys = Object.keys(data);
  for (var i = 0; i < keys.length; i++) {
    series.push({
      name: keys[i],
      type: "line",
      data: data[keys[i]].map((val) => Math.log2(val + 1)),
    });
  }
  console.log(series);
  option = create_expr(head, Object.keys(data), series);
  expr_plot.setOption(option);
}

function create_expr(head, genes, series) {
  option = {
    tooltip: {
      trigger: "axis",
    },
    dataZoom: {
      show: true,
      realtime: true,
    },
    grid: { bottom: "55%" },
    legend: {
      //right: '15%',
      data: genes,
    },
    toolbox: {
      show: true,
      feature: {
        mark: { show: true },
        dataView: { show: true, readOnly: false },
        magicType: { show: true, type: ["line", "bar", "stack", "tiled"] },
        restore: { show: true },
        saveAsImage: { show: true },
      },
    },
    xAxis: [
      {
        axisLabel: {
          interval: 0,
          rotate: 75,
        },
        type: "category",
        data: head,
      },
    ],
    yAxis: [
      {
        type: "value",
        scale: true,
        name: "log2(TPM + 1)",
      },
    ],
    series: series,
  };
  return option;
}

function initSampleTable() {
  const tableColumns = [
    { data: "sample_name", bSortable: true, title: "Sample" },
    { data: "tissue", bSortable: true, title: "Tissue" },
    { data: "age", bSortable: true, title: "Age" },
    { data: "variety", bSortable: true, title: "Variety" },
    { data: "stress_disease", bSortable: true, title: "Stress Disease" },
    { data: "high_level_tissue", bSortable: true, title: "High Level Tissue" },
    { data: "high_level_age", bSortable: true, title: "High Level Age" },
    {
      data: "high_level_variety",
      bSortable: true,
      title: "High Level Variety",
    },
    {
      data: "high_level_stress_disease",
      bSortable: true,
      title: "High Level Stress Disease",
    },
    { data: "study_title", bSortable: true, title: "Study Title" },
    { data: "doi", bSortable: true, title: "DOI" },
  ];
  var table = $("#sample").DataTable({
    columns: tableColumns,
    dom: "Bfrtip",
    buttons: [
      {
        extend: "colvis",
        postfixButtons: ["colvisRestore"],
      },
    ],
    columnDefs: [
      {
        targets: 5,
        visible: false,
      },
      {
        targets: 6,
        visible: false,
      },
      {
        targets: 7,
        visible: false,
      },
      {
        targets: 8,
        visible: false,
      },
      {
        targets: 9,
        visible: false,
      },
      {
        targets: 10,
        visible: false,
      },
    ],
    ajax: function (data, callback) {
      $.ajax({
        type: "GET",
        url: "/expression/exp-sample/",
        success: function (res) {
          callback({ data: res });
        },
        error: function () {
          console.log("error");
        },
      });
    },
  });

  table.buttons().container().appendTo(".dataTables_filter");
}

$(document).ready(function () {
  // multiselect plugin
  select_plugin();
  clear_select_plugin();
  initSampleTable();
  addExample();
  $("#submit").click(function () {
    var gene_name = $("#genes").val();
    var group = [];

    var hint = $(
      '<span><img src="/static/images/hint.gif" />' +
        "  under processing, please wait...</span>"
    );
    hint.appendTo("#query_hint");
    $("#multi_d_to option").each(function () {
      group.push($(this).text());
    });
    var info = { gene_name: gene_name, group: group };
    if (check_gene(info)) {
      info = JSON.stringify(info);
      $("#expression-echart-container").empty();
      var exp_box = $(
        '<div id="results-plot" class="expression-echart-canvas"></div>'
      );
      exp_box.appendTo("#expression-echart-container");
      $("#results-box").fadeOut();
      ajaxSend(
        "/expression/search/result/",
        { info: info },
        function (data) {
          $("#query_hint").empty();
          if (data.msg != "ok") {
            createAlert(data.msg);
            return;
          } else {
            expr_line(group, data.data);
            $("#results-box").fadeIn();
            /*
          generate_plot(createPlotData(groupA, groupB, data.bodyData));
          tableStr = createTable(data.headData, data.bodyData, tableType='expr');
          $("#results-table").html(tableStr);
          $("#results_table").DataTable({
            dom: 'lBfrtip',
            "scrollX": true,
            buttons: [
              'csv'
            ]
          }); */
          }
        },
        "POST"
      );
    } else {
      return;
    }
  });
});
