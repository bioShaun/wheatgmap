function check_info(info){
   var keys = Object.keys(info);
   var pos_start = 0;
   var pos_end = 0;
   for(var i = 0; i < keys.length; i++){
     if(info[keys[i]].length == 0){
         layer.alert(keys[i] + ' is empty!');
         return false;
     }
     if(keys[i] == 'pos_start'){
        pos_start = Number(info[keys[i]]);
     }
     if(keys[i] == 'pos_end'){
        pos_end = Number(info[keys[i]]);
     }
   }
   if (pos_end < pos_start){
      layer.alert('end must bigger than start.');
      return false;
   }
   if (pos_end - pos_start > 5000000){
      layer.alert('regin too long (regin < 5M).');
      return false;
   }
   return true;
 }

function get_input_data(){
   var gene_list = $("#gene_list").val();
   var chr = $("#select-chr").val();
   var pos_start = $("#pos-start").val();
   var pos_end = $("#pos-end").val();
   var group = [];
   $("#multi_d_to option").each(function(){
     group.push($(this).text());
   });
   var all_info = {
      "group": group
   }
   if (gene_list.length != 0){
      all_info['gene_list'] = gene_list;
      return all_info;
   }
   all_info['chr'] = chr;
   all_info['pos_start'] = pos_start;
   all_info['pos_end'] = pos_end;
   return all_info;
 }

$(document).ready(function(){
   select_plugin();
   clear_select_plugin();
   $("#submit").click(function(){
      var info = get_input_data();  
      if(check_info(info)){
         info = JSON.stringify(info);
         var hint = $('<span><img src="/static/images/hint.gif" />' + 'loading data, please wait...</span>');
         hint.appendTo('#query_hint');
         ajaxSend('/variants/query/result/', {'info': info}, function(data){
            if(data.msg != 'ok'){
               layer.alert(data.msg);
               return;
            }else{
               layer.msg('task already commit, please waitting a second...');
               window.location.href='/task/result/' + data.task_id + '/';
               return;
            }
         },'post');
      }
   });
});
