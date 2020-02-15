$(document).ready(function(){
  $('#submit').click(function(){
    var index = layer.load(1);
    var formData = new FormData();
    var database = $("#database").find("option:selected").text();
    if(database.length == 0){
      alert('please choose database first.');
      return;
    };
    formData.append('annotation_database', database);
    var fileObj = document.getElementById('file').files;
    if(fileObj.length == 0){
        alert('no upload file.');
        return;
    }
    if(fileObj[0].name.substring(fileObj[0].name.indexOf('.')) != '.vcf.gz'){
      alert('upload file have to *.vcf.gz.');
      return;
    }
    formData.append('file', fileObj[0]);
    $.ajax({
    url: "/tools/vcf/result/",
    type: "post",
    data: formData,
    contentType: false,
    processData: false,
    xhr: function () {
      var xhr = new XMLHttpRequest();
          xhr.upload.addEventListener('progress', function (e) {
              var progressRate = (e.loaded / e.total) * 100 + '%';
              $('.progress-bar').css('width', progressRate);
          })
          return xhr;
    },
    success: function (data) {
      if (data.msg == "ok") {
        layer.close(index);
        $('.progress-bar').css('width', "0%");
        $('#result').empty();
        $('#result').html(
          "<p><a class='btn btn-lg btn-primary' href='/static/download/vcf_ann/" + data.result + "' role='button'>download annotation zip files &raquo; </a></p>"
        );
        return;
      }else if(data.msg == 'async'){
        window.location.href='/task/result/' + data.task_id + '/';
        return;
      }else{
        layer.close(index);
        layer.alert(data.msg);
        return;
      }}
  });
});
});

