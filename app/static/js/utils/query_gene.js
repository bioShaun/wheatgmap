function check_gene(info){
  var keys = Object.keys(info);
  for(var i = 0; i < keys.length; i++){
    if(info[keys[i]].length == 0){
        createAlert(keys[i] + ' is empty!');
        return false;
    }
  }
  if(Number(info['gene_upstream']) > 2 || Number(info['gene_downstream'] > 2)){
      createAlert('upstream & downstream not allowed > 2');
      return false;
  }
  return true;
}

$(document).ready(function(){
  // multiselect plugin
  select_plugin()
  /*
  $("#select_file").change(function(){
    var fileSelect = $(this).find("option:selected").text();
    ajaxSend('/variation/select_file/', {'file': fileSelect}, function(data){
      var msg = data.msg;
      if(msg == 'error'){
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
  $('#submit').click(function(){
    var gene_name = $("#gene_name").val();
    var gene_upstream = $("#up").val();
    var gene_downstream = $("#down").val();
    //var table = $("#select_file").find("option:selected").text();
    var sample = [];
    $("#multi_d_to option").each(function(){
      sample.push($(this).text());
    });
    var info = {'gene_name': gene_name,
                'gene_upstream': gene_upstream,
                'gene_downstream': gene_downstream,
                'sample': sample,
                'search': 'gene'}
    if(check_gene(info)){
      info = JSON.stringify(info);
      $("#query_hint").empty();
      var hint = $('<span><img src="../../static/images/hint.gif" />' + 'loading data, please wait...</span>');
      hint.appendTo('#query_hint');
      ajaxSend('/variants/get_snp_info/',{'info': info}, function(data){
        $('#query_hint').empty();
	      $('.results-tables').empty();
        if(data.msg != 'ok'){
          // alert(data.msg);
            createAlert(data.msg);
          return;
        }else{
          var tableStr = createTable(data.data.head, data.data.result);
          $("#results-table").html(tableStr);
          $(".region_table").DataTable({
            dom: 'lBfrtip',
            "scrollX": true,
            buttons: [
              'csv'
            ]
          });
        }
      }, 'POST');
    }else{
      return;
    }
    });
});
