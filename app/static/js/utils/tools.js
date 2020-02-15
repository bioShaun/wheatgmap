$(document).ready(function(){
  $('#submit').click(function(){
    var genes = $("#genes").val();
    var info = {'genes': genes}
    info = JSON.stringify(info);
    ajaxSend('/tools/blast/table/',{'info': info}, function(data){
      $('results-table').empty();
        if(data.msg != 'ok'){
            createAlert(data.msg);
          return;
        }else{
          var headData = ['GENE_ID', 'Description', 'Pfam_Description', 'Interpro_Description', 'GO_Description'];
          var tableStr = createTable(headData, data.result, 'expr');
          $("#results-table").html(tableStr);
          $(".table").DataTable({
            "ordering": false,
            dom: 'Bfrtip',
            buttons: [
            'copy', 'csv', 'excel', 'pdf', 'print'
            ]
          });
	}
      }, 'POST');
});
})
