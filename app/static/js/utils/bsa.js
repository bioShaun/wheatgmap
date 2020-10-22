function get_input_data() {
  var windows_by_chr_length = $("#w-chr-len").val();
  var windows_by_snp_number = $("#w-snp-num").val();
  var step_by_chr_length = $("#s-chr-len").val();
  var step_by_snp_number = $("#s-snp-num").val();
  var min_depth = $("#min_depth").val();
  var qtlseqr_min_depth = $("#qtlseqr_min_depth").val();
  var wild_bulk = [];
  var mutant_bulk = [];
  var wild_parent = [];
  var mutant_parent = [];
  var background = [];
  var ed = "ed";
  var qtlseqr = "qtlseqr";
  var ref_freq = $("#ref_freq").val();
  var p_ref_freq = $("#p_ref_freq").val();
  var background_ref_freq = $("#background_ref_freq").val();
  var pop_stru = $("input[name='pop_stru']:checked").val();
  var qtlseqr_ref_freq = $("#qtlseqr_ref_freq").val();

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
  $("#multi_d_to_5 option").each(function () {
    background.push($(this).text());
  });

  var all_info = {
    genome_window: windows_by_chr_length,
    snp_number_window: windows_by_snp_number,
    genome_step: step_by_chr_length,
    snp_number_step: step_by_snp_number,
    wild: wild_bulk,
    mutant: mutant_bulk,
    wild_parent: wild_parent,
    mutant_parent: mutant_parent,
    background: background,
    ed: ed,
    qtlseqr: qtlseqr,
    ref_freq: ref_freq,
    p_ref_freq: p_ref_freq,
    background_ref_freq: background_ref_freq,
    min_depth: min_depth,
    qtlseqr_min_depth: qtlseqr_min_depth,
    pop_stru: pop_stru,
    qtlseqr_ref_freq: qtlseqr_ref_freq,
  };
  return all_info;
}

function check_input_data(info) {
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
  return "";
}

function connResult(taskId) {
  ajaxSend(
    "/mapping/bsa/result/",
    { task_id: taskId },
    function (data) {
      if (data.msg == "ok") {
        window.location.href = "/mapping/bsa/" + taskId + "/";
        return;
      } else if (data.msg == "pending") {
        return;
      } else if (data.msg == "error") {
        layer.msg("task " + taskId + " failed...");
        return;
      }
    },
    "POST"
  );
}

$(document).ready(function () {
  select_plugin();
  clear_select_plugin();
  $("#submit").bind("click", function () {
    var info = get_input_data();
    console.log(info);
    var compare = "Compare: " + info.mutant + "|" + info.wild;
    var parents = "Parents: " + info.mutant_parent + "|" + info.wild_parent;
    var background = "Background: " + info.background;
    var jobName = compare + ";" + parents + ";" + background;
    error_msg = check_input_data(info);
    if (error_msg.length > 0) {
      alert(error_msg);
      return;
    }
    info = JSON.stringify(info);
    ajaxSend(
      "/mapping/bsa/run/",
      { info: info, jobName: jobName },
      function (data) {
        console.log(data);
        if (data.msg == "ok") {
          if (data.username !== "anonymous") {
            window.location.href = "/auth/tasks/";
          } else {
            window.location.href = "/mapping/bsa/launched/" + data.task_id;
          }
          return;
        } else {
          alert(data.msg);
          return;
        }
      },
      "POST"
    );
  });
  $('[data-toggle="tooltip"]').tooltip();
});
