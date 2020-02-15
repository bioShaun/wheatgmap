function get_input_data(){
  var table = $("#select_file").find("option:selected").text();
  var chr = $("#select-chr").find("option:selected").text();
  var startPos = $("#pos-start").val();
  var endPos = $("#pos-end").val();
  var groupA = [];
  var groupB = [];
  var groupBG = [];
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
    'chr': chr,
    'start_pos': startPos,
    'end_pos': endPos,
    'groupA': groupA,
    'groupB': groupB,
    'groupBG': groupBG,
    'search': 'regin'
  };
  return all_info;
}

function check_input_data(info){
  var pos_max = 1000000;
  keys = Object.keys(info);
  var msg = '';
  for(var i=0; i<keys.length; i++){
    if(info[keys[i]].length == 0){
      msg = keys[i] + ' is empty!';
      return msg;
    }
  }
  if(info['end_pos'] - info['start_pos'] > pos_max){
    msg = 'range length not allowed > 1000kb!';
    return msg;
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
  /*
  $("#search-button").bind('click', function(){
    var searchSample = $("#search-sample").val();
    var table = $("#select_file").find("option:selected").text();
    ajaxSend('/search_sampe', {'table': table, 'sample': searchSample}, function(data){
      var msg = data.msg;
      if(msg == 'error'){
        alert('没有找到相应的样品名称!');
      }else{
        sample = data.msg;
        var tmp = $('<div class="col-xs-2"><div class="checkbox"><label><input type="checkbox" name="dispop" value="' + sample +'">' + sample + '</label></div></div>');
        tmp.appendTo('.show-samples');
      }
    });
  });
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
      ajaxSend('/variation/get_snp_info/', {'info': info}, function (data) {
          $('#query_hint').empty();
	  $('.results-tables').empty();
          if (data.msg == 'error') {
              createAlert(data.msg);
              return;
          } else {
              if (data.split2[1].length != 0) {
                  var tableStr = createTable(data.split2[0], data.split2[1], tableType = 'snp');
                  $("#results-table2").html(tableStr);
              };
              if (data.split3[1].length != 0) {
                  var tableStr = createTable(data.split3[0], data.split3[1], tableType = 'snp');
                  $("#results-table3").html(tableStr);
              };
              if (data.split4[1].length != 0) {
                  var tableStr = createTable(data.split4[0], data.split4[1], tableType = 'snp');
                  $("#results-table4").html(tableStr);
              };
              if (data.splitn[1].length != 0) {
                  var tableStr = createTable(data.splitn[0], data.splitn[1], tableType = 'snp');
                  $("#results-tablen").html(tableStr);
              }
              $(".region_table").DataTable({
                  dom: 'lBfrtip',
                  "scrollX": true,
                  buttons: [
                      'csv'
                  ]
              });
          }
      }, 'POST');
  });
});
