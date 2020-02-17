function get_input_data(){
    var gene_id = $("#gene_list").val();
    var chrom = $("#select-chr").val();
    var chrom_start = $("#pos-start").val();
    var chrom_end = $("#pos-end").val();
    var group_name1 = $("#g1").val();
    var group_name2 = $("#g2").val();
    var group_name3 = $("#g3").val();
    var group_name4 = $("#g4").val();
    var group_name5 = $("#g5").val();
    var group1 = [];
    var group2 = [];
    var group3 = [];
    var group4 = [];
    var group5 = [];
    $("#multi_d_to option").each(function(){
      group1.push($(this).text());
    });
    $("#multi_d_to_2 option").each(function(){
      group2.push($(this).text());
    });
    $("#multi_d_to_3 option").each(function(){
      group3.push($(this).text());
    });
    $("#multi_d_to_4 option").each(function(){
      group4.push($(this).text());
    });
    $("#multi_d_to_5 option").each(function(){
      group5.push($(this).text());
    });
    
    var all_info = {
        'gene_id': gene_id,
        'chrom': chrom,
        'chrom_start': chrom_start,
        'chrom_end': chrom_end,
        'group_name1': group_name1,
        'group_name2': group_name2,
        'group_name3': group_name3,
        'group_name4': group_name4,
        'group_name5': group_name5,
        'group1': group1,
        'group2': group2,
        'group3': group3,
        'group4': group4,
        'group5': group5
    };
    return all_info;
}
  
function check_input_data(info, params){
  if(info['group_name1'].length != 0){
    if(info['group1'].length == 0){
      layer.alert(info['group_name1'] + ' sample list is empty.');
      return false;
    }
    params[info['group_name1']] = info['group1'];
  }
  if(info['group_name2'].length != 0){
    if(info['group2'].length == 0){
      layer.alert(info['group_name2'] + ' sample list is empty.');
      return false;
    }
    params[info['group_name2']] = info['group2'];
  }
  if(info['group_name3'].length != 0){
    if(info['group3'].length == 0){
      layer.alert(info['group_name3'] + ' sample list is empty.');
      return false;
    }
    params[info['group_name3']] = info['group3'];
  }
  if(info['group_name4'].length != 0){
    if(info['group4'].length == 0){
      layer.alert(info['group_name4'] + ' sample list is empty.');
      return false;
    }
    params[info['group_name4']] = info['group4'];
  }
  if(info['group_name5'].length != 0){
    if(info['group5'].length == 0){
      layer.alert(info['group_name5'] + ' sample list is empty.');
      return false;
    }
    params[info['group_name5']] = info['group5'];
  }
  if(Object.keys(params).length == 0){
    layer.alert('no group input.');
    return false;
  }
  params['group_names'] = Object.keys(params);
  if(info['gene_id'].length != 0){
    params['gene_id'] = info['gene_id'];
    return true;
  }
  if(info['chrom'].length != 0){
    if(info['chrom_start'].length == 0){
      layer.alert('chrom start is empty.');
      return false;
    }
    if(info['chrom_end'].length == 0){
      layer.alert('chrom end is empty.');
      return false;
    }
    if(Number(info['chrom_end']) < Number(info['chrom_start'])){
      layer.alert('end must bigger than start.');
      return false;
    }
    if(Number(info['chrom_end']) - Number(info['chrom_start']) > 1000000){
      layer.alert('regin too long (regin < 1M).');
      return false;
    }
    params['chrom'] = info['chrom'];
    params['chrom_start'] = info['chrom_start'];
    params['chrom_end'] = info['chrom_end'];
    return true;
  }
}
  
$(document).ready(function(){
  select_plugin();
  clear_select_plugin();
  $("#submit").bind('click',function() {
        var params = {};
        var info = get_input_data();
        if(check_input_data(info, params)){
          params = JSON.stringify(params);
          ajaxSend('/mapping/compare/run/', {'info': params}, function (data) {
            if (data.msg == 'ok') {
                layer.msg('task alreay commit, please waitting a second...');
                window.location.href='/task/result/' + data.task_id + '/';
                return;
            } else {
                alert(data.msg);
                return;
            }
          }, 'POST');
    }else{
      return;
    };
  });
});
  
  
