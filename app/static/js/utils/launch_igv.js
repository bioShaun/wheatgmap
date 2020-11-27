function setIgv(sampleArry) {
  var igvDiv = document.getElementById("igv-div");

  var wheat_ann = [
    {
      name: "Genes",
      format: "gtf",
      url: "/static/reference/wheat_anno/sorted.hclc.gtf.gz",
      indexURL: "/static/reference/wheat_anno/sorted.hclc.gtf.gz.csi",
      order: 1000000,
      visibilityWindow: 1000000,
      height: 150,
    },
  ];

  var wheat_ref = {
    name: "Chinese Spring",
    fastaURL: "/static/reference/Chinese_Spring_v1.0.fasta",
    indexURL: "/static/reference/Chinese_Spring_v1.0.fasta.fai",
  };

  var vcf_tracks = sampleArry.map((sampleId, idx) => {
    return {
      type: "variant",
      format: "vcf",
      url: `/static/vcf_private_sample/${sampleId}.vcf.gz`,
      indexURL: `/static/vcf_private_sample/${sampleId}.vcf.gz.csi`,
      name: sampleId,
      squishedCallHeight: 1,
      expandedCallHeight: 4,
      visibilityWindow: 1000000,
      order: (idx + 2) * 1000000,
    };
  });

  console.log(vcf_tracks);

  const all_tracks = wheat_ann.concat(vcf_tracks);

  var options = {
    reference: wheat_ref,
    tracks: all_tracks,
  };

  igv.createBrowser(igvDiv, options).then(function (browser) {
    console.log("Created IGV browser");
  });
}

function get_input_data() {
  var group = [];
  $("#multi_d_to option").each(function () {
    group.push($(this).text());
  });
  var all_info = {
    group: group,
  };
  return all_info;
}

function check_info(info) {
  samples = info["group"];
  if (samples.length > 4) {
    layer.alert("You can choose at most 4 Samples.");
    return false;
  } else if (samples.length < 1) {
    layer.alert("You should choose at least 1 Samples.");
    return false;
  }
  return true;
}

$(document).ready(function () {
  select_plugin();
  clear_select_plugin();

  var igvBox = $("#igv-box");
  var queryBox = $("#query-box");

  $("#submit").click(function () {
    console.log("submit");
    console.log(igvBox);
    var info = get_input_data();
    if (check_info(info)) {
      queryBox.hide();
      igvBox.fadeIn();
      setIgv(info["group"]);
    }
  });

  $("#reset-btn").click(function () {
    console.log("reset");
    igvBox.hide();
    queryBox.fadeIn();
    igv.removeAllBrowsers();
  });
});
