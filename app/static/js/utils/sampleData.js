$(document).ready(function () {
  var $container = $("#userData");
  var handsontable;
  var updateInfo = {};

  $container.handsontable({
    startRows: 8,
    startCols: 6,
    rowHeaders: true,
    colHeaders: [
      "WG ID",
      "Public",
      "Sample Name",
      "Type",
      "Scientific Name",
      "Variety ID",
      "Tissue",
      "Age",
      "Phenotype",
      "Pooled Sample",
      "DOI",
    ],
    columns: [
      { data: "tc_id", type: "text" },
      { data: "opened", type: "checkbox" },
      { data: "sample_name", type: "text" },
      { data: "type", type: "text" },
      { data: "scientific_name", type: "text" },
      { data: "variety_name", type: "text" },
      { data: "tissue", type: "text" },
      { data: "age", type: "text" },
      { data: "bulked_segregant", type: "text" },
      { data: "mixed_sample", type: "text" },
      { data: "dol", type: "text" },
    ],
    minSpareRows: 1,
    stretchH: "all",
    contextMenu: true,
    autoWrapRow: true,
    maxRows: 20,
    width: "100%",
    height: 500,
    exportFile: true,
    columnSorting: {
      indicator: true,
    },
    autoColumnSize: {
      samplingRatio: 23,
    },

    filters: true,
    dropdownMenu: true,
    licenseKey: "non-commercial-and-evaluation",
    afterChange: function (change, source) {
      if (handsontable) {
        const fullData = handsontable.getData();
        if (fullData && change) {
          change.map((val) => {
            const tcId = fullData[val[0]][0];
            const field = val[1];
            const newVal = val[3];
            updateInfo[tcId] = { ...updateInfo[tcId], [field]: newVal };
            saveButton.removeAttr("disabled");
            cancelButton.removeAttr("disabled");
            const tableStats = getTableStats(fullData);
            setTableStats(tableStats);
          });
        }
      }
    },
    bindRowsWithHeaders: "strict",
  });

  var handsontable = $container.data("handsontable");

  function loadFromDb() {
    $.ajax({
      url: "/auth/fetch_samples/",
      dataType: "json",
      type: "GET",
      success: function (res) {
        ori_data = res.map((val) => val);
        handsontable.loadData(res);
        const tableStats = getTableStats(res);
        setTableStats(tableStats);
      },
    });
  }

  function getTableStats(data) {
    const stats_obj = {};
    data.map((val) => {
      const pub_stats = val["opened"] ? "pub" : "pri";
      const data_type = val["type"] ? val["type"].toLowerCase() : "unknown";
      const col_id = `${pub_stats}-${data_type}`;
      stats_obj[col_id] = stats_obj[col_id] ? stats_obj[col_id] + 1 : 1;
    });
    console.log(stats_obj);
    return stats_obj;
  }

  function setTableStats(stats) {
    for (let col_i in stats) {
      $(`#${col_i}`).text(stats[col_i]);
    }
  }

  function updateTable(data) {
    $.ajax({
      url: "/auth/hot_edit_samples/",
      dataType: "application/json",
      type: "POST",
      data: JSON.stringify(data),
      success: function (res) {
        console.log(res);
      },
      error: function (res) {
        console.log(res);
      },
    });
  }

  loadFromDb();

  var button1 = document.getElementById("export-file");
  var saveButton = $("#save-change");
  var cancelButton = $("#save-cancel");
  var exportPlugin1 = handsontable.getPlugin("exportFile");
  button1.addEventListener("click", function () {
    exportPlugin1.downloadFile("csv", {
      bom: false,
      columnDelimiter: ",",
      columnHeaders: true,
      exportHiddenColumns: true,
      exportHiddenRows: true,
      fileExtension: "csv",
      filename: "Handsontable-CSV-file_[YYYY]-[MM]-[DD]",
      mimeType: "text/csv",
      rowDelimiter: "\r\n",
      rowHeaders: false,
    });
  });

  function resetUpdate() {
    updateInfo = {};
    saveButton.attr("disabled", true);
    cancelButton.attr("disabled", true);
  }

  cancelButton.on("click", () => {
    loadFromDb();
    resetUpdate();
  });

  saveButton.on("click", () => {
    updateTable(updateInfo);
    resetUpdate();
  });
});
