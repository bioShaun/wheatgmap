function check_gene(info){
  var keys = Object.keys(info);
  for(var i = 0; i < keys.length; i++){
    if(info[keys[i]].length == 0){
      createAlert(keys[i] + ' is empty!');
      return false;
    }else if(info[keys[i]] == 'group' && info[keys[i]].length > 20){
      createAlert('samples number have to < 20!');
      return false;
    }
  } 
  return true;
}

function expr_line(head, data){
  var expr_plot = echarts.init(document.getElementById('results-plot'));
  var series = [];
  var keys = Object.keys(data);
  for(var i = 0; i < keys.length; i++){
    series.push({'name': keys[i],
                 'type':'line',
                 'data': data[keys[i]]});
  }
  console.log(series);
  option = create_expr(head, Object.keys(data), series);
  expr_plot.setOption(option);
}

function create_expr(head, genes, series) {
        option = {
          tooltip : {
            trigger: 'axis'
            },
            dataZoom: {
              show: true,
              start : 30,
              end : 70,
              realtime: true
            },
            legend: {
                //right: '15%',
                data: genes
            },
            toolbox: {
                show: true,
                feature: {
                    mark: {show: true},
                    dataZoom: {show: true},
                    dataView: {show: true, readOnly: false},
                    magicType : {show: true, type: ['line', 'bar', 'stack', 'tiled']},
                    restore: {show: true},
                    saveAsImage: {show: true}
                }
            },
            xAxis: [
                {
                   axisLabel: {
                              interval: 0,
                              rotate: 25
                    },
                    type: 'category',
                    data: head
                }
            ],
            yAxis: [
                {
                    type: 'value',
                    scale: true
                }
            ],
            series: series 
        };
        return option;
}

$(document).ready(function(){
  // multiselect plugin
  select_plugin()
  clear_select_plugin()
  $('#submit').click(function(){
    var gene_name = $("#gene_name").val();
    var group = [];
    $("#multi_d_to option").each(function(){
      group.push($(this).text());
    });
    var info = {'gene_name': gene_name,
                'group': group}
    if(check_gene(info)){
      info = JSON.stringify(info);
      $("#query_hint").empty();
      var hint = $('<span><img src="/static/images/hint.gif" />' + 'loading data, please wait...</span>');
      hint.appendTo('#query_hint');
      ajaxSend('/expression/search/result/',{'info': info}, function(data){
        if(data.msg != 'ok'){
          createAlert(data.msg);
          $("#query_hint").empty();
          return;
        }else{
          $("#results-plot").empty();
          $("#query_hint").empty();
          expr_line(group, data.data);
          /*
          generate_plot(createPlotData(groupA, groupB, data.bodyData));
          tableStr = createTable(data.headData, data.bodyData, tableType='expr');
          $("#results-table").html(tableStr);
          $("#results_table").DataTable({
            dom: 'lBfrtip',
            "scrollX": true,
            buttons: [
              'csv'
            ]
          }); */
        }
      }, 'POST');
    }else{
      return;
    }
    });
});
