function check_info(info) {
  samples = info["group"];
  if (samples.length > 4) {
    layer.alert("You can choose at most 4 Samples.");
    return false;
  } else if (samples.length < 1) {
    layer.alert("You should choose at least 1 Samples.");
    return false;
  }
  var_alt_freq = info["var_alt_freq"];
  if (var_alt_freq < 0 || var_alt_freq >= 1) {
    layer.alert("Alt Allele Frequency should between 0 to 1.");
    return false;
  }
  return true;
}

function get_input_data() {
  var group = [];
  $("#multi_d_to option").each(function () {
    group.push($(this).text());
  });
  var var_window = $("#var-density-window").val() || 1000 * 1000;
  var var_depth = $("#var-density-depth").val() || 1;
  var var_alt_freq = Number($("#var-alt-freq").val()) || 0;
  var all_info = {
    group: group,
    var_window: var_window,
    var_depth: var_depth,
    var_alt_freq: var_alt_freq,
  };
  return all_info;
}

$(document).ready(function () {
  select_plugin();
  clear_select_plugin();
  $("#submit").click(function () {
    var info = get_input_data();
    if (check_info(info)) {
      info = JSON.stringify(info);
      var hint = $(
        '<span><img src="/static/images/hint.gif" />' +
          "  under processing, please wait...</span>"
      );
      hint.appendTo("#query_hint");
      $("#results").empty();
      ajaxSend(
        "/variants/variant-density/plot/",
        { info: info },
        function (data) {
          if (data.msg != "ok") {
            layer.alert(data.msg);
            return;
          } else {
            $("#query_hint").empty();
            var downloadBtn = $(
              `<a href="${data.outdir}.zip"><button type="button" class="btn btn-success mb-20" aria-label="Left Align" style="margin-top: 10px;">Download Full Results<span class="iconfont icon-decline-filling download-mark" aria-hidden="true"></span></button></a>`
            );
            var plot = $(
              `<div><img class="var-density" src="${data.outdir}/variant-density.plot.png" /></div>`
            );
            plot.appendTo("#results");
            downloadBtn.appendTo("#results");
            console.log(data.outdir);
            return;
          }
        },
        "post"
      );
    }
  });
});
