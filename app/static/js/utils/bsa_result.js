$(document).ready(function(){
  function connResult() {
    taskId = $("#task-id").text().split(':')[1]; 
    ajaxSend('/mapping/bsa/result/', {'task_id': taskId}, function(data){
      if (data.msg == 'ok'){
        layer.close(index);
        clearInterval(status);
        layer.alert('task done...');
        return;
      }else if (data.msg == 'pending'){
        return;
      }else if (data.msg == 'error'){
        layer.close(index);
        clearInterval(status);
        layer.alert('task ' + taskId + ' failed...');
        return;
      }
    }, 'POST');
  }
 var index = layer.load(1);
 var status = setInterval(connResult, 20000);
});
