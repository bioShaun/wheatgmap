var tissueArr = [
  "Pistils",
  "Anther",
  "Shell",
  "Leaf",
  "Root",
  "Stem",
  "Embryo-2",
  "Embryo-3",
  "Embryo-4",
  "Embryo-5",
  "Embryo-6",
  "Embryo-7",
  "Embryo-8",
  "Embryo-10",
  "Embryo-12",
  "Embryo-14",
  "Embryo-16",
  "Embryo-18",
  "Embryo-20",
  "Embryo-22",
  "Embryo-24",
  "Embryo-26",
  "Embryo-28",
  "Embryo-30",
  "Embryo-32",
  "Embryo-34",
  "Embryo-36",
  "Embryo-38",
];

var mrna_lnc_pair = null;

function echarts_width_height(sample, genes) {
  var sample_num = sample.length;
  var gene_num = genes.length;
  return {
    width: 150 + sample_num * 40,
    height: 80 + 30 * gene_num,
  };
}

function prepare_echarts_container(width, height) {
  $("#exp-plot").empty();
  var exp_box = $(
    `<div id="results-plot" style="width: ${width}px; height: ${height}px; margin: 0 auto;"></div>`
  );
  exp_box.appendTo("#exp-plot");
}

function expr_heatmap(tissues, genes, data) {
  var expr_plot = echarts.init(document.getElementById("results-plot"));
  option = create_expr(tissues, genes, data);
  expr_plot.setOption(option);
}

function create_expr(tissues, genes, data) {
  var expArr = data.map((val) => val[2]);
  var expMax = Math.ceil(Math.max(...expArr));

  option = {
    tooltip: {
      position: "top",
    },
    animation: false,
    grid: {
      top: "10%",
      left: 150,
      bottom: 80,
    },
    xAxis: {
      axisLabel: {
        interval: 0,
        rotate: 45,
      },
      type: "category",
      data: tissues,
      splitArea: {
        show: true,
      },
    },
    yAxis: {
      type: "category",
      data: genes,
      splitArea: {
        show: true,
      },
    },
    visualMap: {
      calculable: true,
      max: expMax,
      orient: "horizontal",
      left: "center",
      bottom: "15%",
      inRange: {
        color: [
          "#006837",
          "#0A7C41",
          "#15904B",
          "#2DA154",
          "#4CB05C",
          "#6BBF63",
          "#86CB66",
          "#A0D669",
          "#B7E075",
          "#CCE982",
          "#DFF193",
          "#EFF8A9",
          "#FFFFBF",
          "#FEF2A9",
          "#FEE593",
          "#FDD380",
          "#FDBE6E",
          "#FCA85E",
          "#F88D51",
          "#F47245",
          "#EA5839",
          "#DE3F2E",
          "#CE2726",
          "#B91326",
          "#A50026",
        ],
      },
      show: false,
    },
    series: [
      {
        name: "log2(tpm + 1)",
        type: "heatmap",
        data: data,
        label: {
          show: false,
        },
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowColor: "rgba(0, 0, 0, 0.5)",
          },
        },
      },
    ],
  };
  return option;
}

function extract_mrna_lnc_pair(data) {
  mrna_lnc_pair = [
    ...new Set(data.map((val) => `${val.mRNA_gene}-${val.lncRNA_gene}`)),
  ];
}

function extract_target() {
  var geneArr1 = $("#genes").val().split(",");
  var geneArr2 = $("#genes").val().split(/\s+/);
  var geneArr = geneArr1.length > geneArr2.length ? geneArr1 : geneArr2;

  if (geneArr.length > 10) {
    $.alert({
      title: "Gene Number Error!",
      content: "At most 10 genes were allowed.",
    });
    return;
  }

  var chr = $("#select-chr").find("option:selected").text();
  var startPos = Number($("#pos-start").val());
  var endPos = Number($("#pos-end").val());
  if (chr || startPos || endPos) {
    const posMsg = check_location({
      chromsome: chr,
      "start-position": startPos,
      "end-position": endPos,
    });
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
  var info = { genes: geneArr, chrom: chr, start: startPos, end: endPos };
  return info;
}

function extract_exp() {
  var tissue = $("#select-tissue").val();
  var mrna = $("#select-mrna").val();
  var lncrna = $("#select-lnc").val();
  var exp_info = { tissue, mrna, lncrna, mrna_lnc_pair };
  return exp_info;
}

function prepare_table_container() {
  $(".lnc-pcg-pair").empty();
  var plot = $(
    `
    <div class="small-datatable card-body">
        <table id="lncRNA" class="table table-striped table-bordered table-hover" cellspacing="0"></table>
    </div>    
    `
  );
  plot.appendTo(".lnc-pcg-pair");
  $(".lnc-pcg-pair").fadeIn();
}

function prepare_exp_table_container() {
  $(".exp-table").empty();
  var exp_table_container = $(
    ` 
    <div class="small-datatable card-body">
        <table id="expression" class="table table-striped table-bordered table-hover" cellspacing="0"></table>
    </div> 
    `
  );
  exp_table_container.appendTo(".exp-table");
  $(".exp-table").fadeIn();
}

function prepare_cor_table_container() {
  $(".exp-cor").empty();
  var exp_table_container = $(
    ` 
      <div class="small-datatable card-body">
          <table id="pearson" class="table table-striped table-bordered table-hover" cellspacing="0"></table>
      </div> 
      `
  );
  exp_table_container.appendTo(".exp-cor");
  $(".exp-cor").fadeIn();
}

function reset_select(id) {
  document.getElementById(id).options.selectedIndex = 0;
  $(`#${id}`).selectpicker("refresh");
}

function reset_query() {
  $("input[type='text']").val("");
  $("#genes").val("");
  reset_select("select-chr");
  reset_select("select-mrna");
  reset_select("select-lnc");
  reset_select("select-tissue");
  $("#exp-plot").empty();
  $(".exp-cor").fadeOut();
  $(".exp-table").fadeOut();
  $(".expression").hide();
  $(".lnc-pcg-pair").empty();
  $(".lnc-pcg-pair").fadeOut();
}

function addOption(id, genes) {
  $(`#${id}`).empty();
  for (let gene of genes) {
    $(`<option value="${gene}">${gene}</option>`).appendTo(`#${id}`);
  }
  $(`#${id}`).selectpicker("refresh");
  $(`#${id}`).selectpicker("render");
}

function initTable(gene_info) {
  prepare_table_container();
  const tableColumns = [
    { data: "chrom", bSortable: true, title: "chrom" },
    { data: "mRNA_start", bSortable: true, title: "mRNA_start" },
    { data: "mRNA_end", bSortable: true, title: "mRNA_end" },
    { data: "mRNA_strand", bSortable: true, title: "mRNA_strand" },
    { data: "mRNA_transcript", bSortable: true, title: "mRNA_transcript" },
    { data: "mRNA_gene", bSortable: true, title: "mRNA_gene" },
    { data: "lncRNA_start", bSortable: true, title: "lncRNA_start" },
    {
      data: "lncRNA_end",
      bSortable: true,
      title: "lncRNA_end",
    },
    { data: "lncRNA_strand", bSortable: true, title: "lncRNA_strand" },
    { data: "lncRNA_transcript", bSortable: true, title: "lncRNA_transcript" },
    { data: "lncRNA_gene", bSortable: true, title: "lncRNA_gene" },
    { data: "direction", bSortable: true, title: "direction" },
    { data: "type", bSortable: true, title: "type" },
    { data: "distance", bSortable: true, title: "distance" },
    { data: "subtype", bSortable: true, title: "subtype" },
    { data: "location", bSortable: true, title: "location" },
  ];
  var lnc_table = $("#lncRNA").DataTable({
    columns: tableColumns,
    dom: "Bfrtip",
    buttons: [
      { extend: "csv", filename: "mRNA-neighbor-lncRNA" },
      { extend: "colvis", postfixButtons: ["colvisRestore"] },
    ],
    scrollX: true,
    columnDefs: [
      {
        targets: 0,
        visible: false,
      },
      {
        targets: 1,
        visible: false,
      },
      {
        targets: 2,
        visible: false,
      },
      {
        targets: 3,
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
    ],
    ajax: function (data, callback) {
      $.ajax({
        type: "POST",
        url: "/tools/fetch-lncRNA/",
        data: { data: JSON.stringify(gene_info) },
        success: function (res) {
          callback({ data: res });

          initExpression(res);
          extract_mrna_lnc_pair(res);
        },
        error: function () {
          console.log("error");
        },
      });
    },
  });

  lnc_table.buttons().container().appendTo("#lncRNA_filter");
}

function initExpTable(exp_info) {
  prepare_exp_table_container();
  const tableColumns = [
    { data: "gene_id", bSortable: true, title: "Gene" },
    { data: "tissue", bSortable: true, title: "Tissue" },
    { data: "tpm", bSortable: true, title: "Tpm" },
  ];
  var exp_table = $("#expression").DataTable({
    columns: tableColumns,
    dom: "Bfrtip",
    buttons: [{ extend: "csv", filename: "mRNA-lncRNA-expression" }],
    ajax: function (data, callback) {
      $.ajax({
        type: "POST",
        url: "/tools/fetch-lncRNA-expression/",
        data: { data: JSON.stringify(exp_info) },
        success: function (res) {
          callback({ data: res["exp"] });
          if (exp_info.tissue.length >= 5) {
            initCorTable(res["pcc"]);
          }
          var echarts_size = echarts_width_height(
            exp_info.tissue,
            res["heatmap_y"]
          );
          prepare_echarts_container(echarts_size.width, echarts_size.height);
          expr_heatmap(exp_info.tissue, res["heatmap_y"], res["heatmap_data"]);
        },
        error: function () {
          console.log("error");
        },
      });
    },
  });

  exp_table.buttons().container().appendTo("#expression_filter");
}

function initCorTable(data) {
  prepare_cor_table_container();
  const tableColumns = [
    { data: "mRNA", bSortable: true, title: "mRNA" },
    { data: "lncRNA", bSortable: true, title: "lncRNA" },
    { data: "pcc", bSortable: true, title: "PCC" },
    { data: "p-value", bSortable: true, title: "P-value" },
  ];
  var cor_table = $("#pearson").DataTable({
    columns: tableColumns,
    dom: "Bfrtip",
    buttons: [{ extend: "csv", filename: "mRNA-lncRNA-correlation" }],
    data: data,
  });

  cor_table.buttons().container().appendTo("#pearson_filter");
}

function initExpression(data) {
  $(".expression").fadeIn();
  var mrna_arr = [...new Set(data.map((val) => val.mRNA_gene))];
  var lnc_arr = [...new Set(data.map((val) => val.lncRNA_gene))];

  addOption("select-mrna", mrna_arr);
  addOption("select-lnc", lnc_arr);
  addOption("select-tissue", tissueArr);
}

$(document).ready(function () {
  addExample();
  $("#submit").click(function () {
    var gene_info = extract_target();
    initTable(gene_info);
  });

  $("#reset").click(function () {
    reset_query();
  });

  $("#query-exp").click(function () {
    var exp_info = extract_exp();
    initExpTable(exp_info);
  });
});
