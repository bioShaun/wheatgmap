function get_input_data(){
  var table = $("#select-file").find("option:selected").text();
  var chr = $("#select-chr").find("option:selected").text();
  var groupA = [];
  var groupB = [];
  var CustomGroupA = $("#groupA-name").val();
  var CustomGroupB = $("#groupB-name").val();
  $("#multi_d_to option").each(function(){
    groupA.push($(this).text());
  });
  $("#multi_d_to_2 option").each(function(){
    groupB.push($(this).text());
  });
  var all_info = {
      'table': table,
      'groupA': groupA,
      'groupB': groupB,
      'chrom': chr,
      'customGroupA': CustomGroupA,
      'customGroupB': CustomGroupB
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
    }else if(keys[i] == 'customGroupA' || keys[i] == 'customGroupB'){
        var pattern = /\s+/g;
        if(pattern.test(info[keys[i]])){
            return 'custom group name not allowed includes space.';
        }
    }
  }
  /*
  if(info['end_pos'] - info['start_pos'] > pos_max){
    msg = 'range length not allowed > 1000kb!';
    return msg;
  }*/
  return msg;
}
$(document).ready(function(){
  $("#select-file").change(function(){
    var fileSelect = $(this).find("option:selected").text();
    ajaxSend('/tools/select_file/', {'file': fileSelect}, function(data){
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
    $("#select-group").change(function(){
    var groupSelect = $(this).find("option:selected").text();
    ajaxSend('/tools/select_group/', {'group': groupSelect}, function(data){
      var msg = data.msg;
      if(msg == 'error'){
        // alert('not find samples!');
          createAlert('you have not generated a divide group!');
          return;
      }else{
        $("#results-plot").empty();
        if(data.files.length == 0){
            createAlert('no plot created! please check your info');
            return;
        }else {
            var plotStr = createPlot(data.files, data.name);
            $("#results-plot").html(plotStr);
            $("a.snp-index").fancybox({
                'overlayShow': true,
                'transitionIn': 'elastic',
                'transitionOut': 'elastic'
            });
            $("a[rel=example_group]").fancybox({
                'transitionIn': 'none',
                'transitionOut': 'none',
                'titlePosition': 'over',
                'titleFormat': function (title, currentArray, currentIndex, currentOpts) {
                    return '<span id="fancybox-title-over">Image ' + (currentIndex + 1) + ' / ' + currentArray.length + (title.length ? ' &nbsp; ' + title : '') + '</span>';
                }
            });
            $("div.albumSlider").albumSlider();
        }
      }
    });
  });
  // multiselect plugin
  select_plugin()
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
  $("#submit").bind('click',function(){
    var info = get_input_data();
    var error_msg = check_input_data(info);
    if(error_msg.length > 0){
      // alert(error_msg);
        createAlert(error_msg);
      return;
    }
    info = JSON.stringify(info);
    $("#query_hint").empty();
    var hint = $('<span><img src="../static/images/hint.gif" />' + 'loading data, please wait...</span>');
    hint.appendTo('#query_hint');
    ajaxSend('/tools/generate_snp_plot/',{'info': info}, function(data){
      if(data.msg == 'error'){
        createAlert(data.msg);
        $("#query_hint").empty();
        return;
      }else{
          //console.log(data.headData);
          //console.log(data.bodyData);
        $('#query_hint').empty();
        if(data.files.length == 0){
            createAlert('no plot created! please check your info');
            $('#query_hint').empty();
            return;
        }else{
        plotStr = createPlot(data.files, data.name);
        $("#results-plot").html(plotStr);
        $("a.snp-index").fancybox({
        'overlayShow'	: true,
        'transitionIn'	: 'elastic',
        'transitionOut'	: 'elastic'
        });
        $("a[rel=example_group]").fancybox({
        'transitionIn'		: 'none',
        'transitionOut'		: 'none',
        'titlePosition' 	: 'over',
        'titleFormat'		: function(title, currentArray, currentIndex, currentOpts) {
            return '<span id="fancybox-title-over">Image ' + (currentIndex + 1) + ' / ' + currentArray.length + (title.length ? ' &nbsp; ' + title : '') + '</span>';
        }});
        $("div.albumSlider").albumSlider();
    }}}, 'POST');
    });
});
