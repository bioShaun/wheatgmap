function createDownloadHref(tablename) {
    var zip_href = '/static/variation_results/' + tablename + '.zip';
    var testStr = "<div><h3>Snp Variation Table</h3>" +
            "<p><a class='btn btn-primary' href='" + zip_href +
            "' role='button'>Download &raquo;</a></p></div>"
    return testStr;
}

function get_input_data(){
  var table = $("#select_file").find("option:selected").text();
  var groupA_name = $("#groupA-name").val();
  var groupB_name = $("#groupB-name").val();
  var groupBG_name = "BG";
  var groupA = [];
  var groupB = [];
  var groupBG = [];
  var nameOrder = [];
  $("#multi_d_to option").each(function(){
    groupA.push($(this).text());
  });
  $("#multi_d_to_2 option").each(function(){
    groupB.push($(this).text());
  });
  $("#multi_d_to_3 option").each(function(){
    groupBG.push($(this).text());
  });
  var all_info = {
      'table': table,
      'groupA_name': groupA_name,
      'groupB_name': groupB_name,
      'groupBG_name': groupBG_name,
      'groupA': groupA,
      'groupB': groupB,
      'groupBG': groupBG,
      'nameOrder': [groupA_name,groupB_name,groupBG_name]
  };
  return all_info;
}

function check_input_data(info){
  keys = Object.keys(info);
  var msg = '';
  for(var i=0; i<keys.length; i++){
    if(info[keys[i]].length == 0){
      msg = keys[i] + ' is empty!';
      return msg;
    }else if(keys[i] == 'groupA_name' || keys[i] == 'groupB_name'){
        var pattern = /\s+/g;
        if(pattern.test(info[keys[i]])){
            return 'custom group name not allowed includes space.';
        }
    }
  }
  return msg;
}
$(document).ready(function(){
  $("#select_file").change(function(){
    var fileSelect = $(this).find("option:selected").text();
    ajaxSend('/variation/select_file/', {'file': fileSelect}, function(data){
      var msg = data.msg;
      if(msg == 'error'){
        // alert('not find samples!');
          createAlert('not find samples!');
        $("#multi_d").empty();
      }else{
        $("#multi_d").empty();
        samples = data.msg;
        for(var i=0;i<samples.length;i++){
          var tmp = $('<option value="' + samples[i] + '">' + samples[i] + '</option>');
          tmp.appendTo('#multi_d');
        }
      }
    });
  });
  // multiselect plugin
  select_plugin();
  $("#select-table").change(function () {
      var tableSelect = $(this).find("option:selected").text();
      ajaxSend('/variation/select_table/', {'table': tableSelect }, function (data) {
          var msg = data.msg;
          if(msg == 'error'){
              createAlert('you have not generated a divide table!');
              return;
          }else{
              $("#results-table").empty();
              if(data.table.length == 0){
                  createAlert('no table file created! please check your info.');
                  return;
              }else{
                  var tableStr = createDownloadHref(data.table);
                  $("#results-table").html(tableStr);
              }
          }

      })

  })
  $("#submit").bind('click',function() {
      var info = get_input_data();
      var error_msg = check_input_data(info);
      if (error_msg.length > 0) {
          // alert(error_msg);
          createAlert(error_msg);
          return;
      }
      info = JSON.stringify(info);
      ajaxSend('/variation/calculate_snp_variations/', {'info': info}, function (data) {
          if (data.msg == 'error') {
              createAlert(data.msg);
              return;
          } else {
              createAlert(data.msg, type='alert-success');
              return
          }
      }, 'POST');
  });
});
