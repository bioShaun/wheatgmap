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
  }else{
      return true;
  }
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
    var groupA = [];
    var groupB = [];
    $("#multi_d_to option").each(function(){
      groupA.push($(this).text());
    });
    $("#multi_d_to_2 option").each(function(){
      groupB.push($(this).text());
    });
    var info = {'gene_name': gene_name,
                'gene_upstream': gene_upstream,
                'gene_downstream': gene_downstream,
                'groupA': groupA,
                'groupB': groupB,
                'search': 'gene'}
    if(check_gene(info)){
      info = JSON.stringify(info);
      $("#query_hint").empty();
      var hint = $('<span><img src="../../static/images/hint.gif" />' + 'loading data, please wait...</span>');
      hint.appendTo('#query_hint');
      ajaxSend('#',{'info': info}, function(data){
        $('#query_hint').empty();
	$('.results-tables').empty();
        if(data.msg != 'ok'){
          // alert(data.msg);
            createAlert(data.msg);
          return;
        }else{
            if(data.split2[1].length != 0){
                var tableStr = createTable(data.split2[0], data.split2[1], tableType='snp');
                $("#results-table2").html(tableStr);
            };
            if(data.split3[1].length != 0){
                var tableStr = createTable(data.split3[0], data.split3[1], tableType='snp');
                $("#results-table3").html(tableStr);
            };
            if(data.split4[1].length != 0){
                var tableStr = createTable(data.split4[0], data.split4[1], tableType='snp');
                $("#results-table4").html(tableStr);
            };
            if(data.splitn[1].length != 0) {
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
    }else{
      return;
    }
    });
});
