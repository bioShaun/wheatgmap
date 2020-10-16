var VAR_FILTER_LIMIT = {
  afd: [0.5, 1],
  afd_deviation: [0, 0.3],
  p_afd: [0.5, 1],
  p_afd_deviation: [0, 0.3],
  wild_freq: [0, 0.5],
  mut_freq: [0, 0.5],
  p_wild_freq: [0, 0.5],
  p_mut_freq: [0, 0.5],
};

var VAR_FILTER_FIELD_NAME = {
  afd: "AFD",
  afd_deviation: "AFD deviation",
  p_afd: "parent AFD",
  p_afd_deviation: "parent AFD deviation",
  wild_freq: "Wild Max Heterozygosity ratio",
  mut_freq: "Mutant Max Heterozygosity ratio",
  p_wild_freq: "Wild Parent Max Heterozygosity ratio",
  p_mut_freq: "Mutant Parent Max Heterozygosity ratio",
};

function check_value(val, name, lower, upper) {
  if ((val < lower) | (val > upper)) {
    return `${name} should between ${lower} and ${upper}`;
  }
}

function check_info(info) {
  if (info["wild"].length == 0) {
    return "no wild bulk.";
  }
  if (info["mutant"].length == 0) {
    return "no mutant bulk.";
  }
  if (info["wild_parent"].length != 0) {
    if (info["mutant_parent"].length == 0) {
      return "wild parent and mutant parent must be paired.";
    }
  }
  if (info["mutant_parent"].length != 0) {
    if (info["wild_parent"].length == 0) {
      return "wild parent and mutant parent must be paired.";
    }
  }
  if (!info["afd"]) {
    return "AFD is required.";
  }
  for (let field in VAR_FILTER_LIMIT) {
    var msg = check_value(
      info[field],
      VAR_FILTER_FIELD_NAME[field],
      VAR_FILTER_LIMIT[field][0],
      VAR_FILTER_LIMIT[field][1]
    );
    if (msg) {
      return msg;
    }
  }
  return "";
}

function get_input_data() {
  var wild_bulk = [];
  var mutant_bulk = [];
  var wild_parent = [];
  var mutant_parent = [];
  $("#multi_d_to option").each(function () {
    wild_bulk.push($(this).text());
  });
  $("#multi_d_to_2 option").each(function () {
    mutant_bulk.push($(this).text());
  });
  $("#multi_d_to_3 option").each(function () {
    wild_parent.push($(this).text());
  });
  $("#multi_d_to_4 option").each(function () {
    mutant_parent.push($(this).text());
  });
  var afd = $("#afd").val();
  var afd_deviation = $("#afd_deviation").val() || 0.05;
  var p_afd = $("#p_afd").val() || 1;
  var p_afd_deviation = $("#p_afd_deviation").val() || 0.05;
  var wild_freq = $("#wild_freq").val() || 0.4;
  var mut_freq = $("#mut_freq").val() || 0.4;
  var p_wild_freq = $("#p_wild_freq").val() || 0;
  var p_mut_freq = $("#p_mut_freq").val() || 0;
  var min_depth = $("#min_depth").val() || 5;
  var all_info = {
    wild: wild_bulk,
    mutant: mutant_bulk,
    wild_parent: wild_parent,
    mutant_parent: mutant_parent,
    afd: afd,
    afd_deviation: afd_deviation,
    p_afd: p_afd,
    p_afd_deviation: p_afd_deviation,
    wild_freq: wild_freq,
    mut_freq: mut_freq,
    p_wild_freq: p_wild_freq,
    p_mut_freq: p_mut_freq,
    min_depth: min_depth,
  };
  return all_info;
}

$(document).ready(function () {
  select_plugin();
  clear_select_plugin();
  $("#submit").click(function () {
    var info = get_input_data();
    error_msg = check_info(info);
    if (error_msg) {
      $.alert({
        title: "Input Error!",
        content: error_msg,
      });
      return;
    }
    console.log(info);
    info = JSON.stringify(info);
    var hint = $(
      '<span><img src="/static/images/hint.gif" />' +
        "  under processing, please wait...</span>"
    );
    hint.appendTo("#query_hint");
    $("#results").empty();
    ajaxSend(
      "/mapping/var-filter/launch/",
      { info },
      function (data) {
        if (data.msg != "ok") {
          layer.alert(data.msg);
          return;
        } else {
          $("#query_hint").empty();
          var downloadBtn = $(
            `<a href="${data.out_file}"><button type="button" class="btn btn-success mb-20" aria-label="Left Align" style="margin-top: 10px;">Download Full Results<span class="iconfont icon-decline-filling download-mark" aria-hidden="true"></span></button></a>`
          );
          var plot = $(
            `<div><img class="var-density" src="${data.out_plot}" /></div>`
          );
          plot.appendTo("#results");
          downloadBtn.appendTo("#results");
          console.log(data.outdir);
          return;
        }
      },
      "post"
    );
  });
});
