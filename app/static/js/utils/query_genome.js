function createDownloadHref(tablename) {
    var zip_href = '/static/variation_results/' + tablename + '.zip';
    var testStr = "<div><h3>Snp Variation Table</h3>" +
            "<p><a class='btn btn-primary' href='" + zip_href +
            "' role='button'>Download &raquo;</a></p></div>"
    return testStr;
}

function get_input_data(){
  //var table = $("#select_file").find("option:selected").text();
  //var sample = $("samples").val();
  //var groupB_name = $("#groupB-name").val();
  var sample = [];
  //var groupB = [];
  $("#multi_d_to option").each(function(){
    sample.push($(this).text());
  });
  /*
  $("#multi_d_to_2 option").each(function(){
    groupB.push($(this).text());
  });
  */
  var all_info = {
      'sample': sample,
      'search': 'all'
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
    }
  }
  return msg;
}
$(document).ready(function(){
  /*
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
  */
  // multiselect plugin
  select_plugin();
  /*
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
  */
  $("#submit").bind('click',function() {
      var info = get_input_data();
      var error_msg = check_input_data(info);
      if (error_msg.length > 0) {
          // alert(error_msg);
          createAlert(error_msg);
          return;
      }
      info = JSON.stringify(info);
      $("#query_hint").empty();
      var hint = $('<span><img src="../../static/images/hint.gif" />' + 'loading data, please wait...</span>');
      hint.appendTo('#query_hint');
      ajaxSend('/variants/get_snp_info/', {'info': info}, function (data) {
          $('#query_hint').empty();
          if (data.msg != 'ok') {
              createAlert(data.msg);
              return;
          } else {
            var tableStr = createDownloadHref(data.data.result);
            $("#results-table").html(tableStr);
            return
          }
      }, 'POST');
  });
});
