function DeleteSample(){
  var rows=$("#sample-table").bootstrapTable("getSelections");
    if(rows.length==0){
      alert("please choose one first.");
      return;
    }
    var ids="";
    for(var i=0;i<rows.length;i++){
      ids+=rows[i]["tc_id"]+",";
    };
    ids=ids.substring(0,ids.length-1);
    var msg="are you sure delete those samples.";
    if(confirm(msg)==true){
      $.ajax({
        url:"/auth/fetch_samples/",
        type:"delete",
        data:{ids: ids},
        success:function(data){
          if(data.msg == 'ok'){
            alert("delete success.");
            $("#sample-table").bootstrapTable("refresh");
          }
        },
        error:function(data){
          alert("error.");
        }
     });
    }
}

function PubSample(){
  var rows=$("#sample-table").bootstrapTable("getSelections");
  if(rows.length==0){
    alert("please choose your data first.");
    return;
  }
  var ids="";
  for(var i=0;i<rows.length;i++){
    ids+=rows[i]["tc_id"]+",";
  };
  ids=ids.substring(0,ids.length-1);
  var msg="are you sure public those samples.";
  if(confirm(msg)==true){
    $.ajax({
      url:"/auth/fetch_samples/",
      type:"post",
      data:{'ids': ids, 'action': 'pub'},
      success:function(data){
        if(data.msg == 'ok'){
          alert("public success.");
          $("#sample-table").bootstrapTable("refresh");
        }
      },
      error:function(data){
        alert("error");
      }
   });
  }
}

function PrSample(){
  var rows=$("#sample-table").bootstrapTable("getSelections");
  if(rows.length==0){
    alert("please choose your data first.");
    return;
  }
  var ids="";
  for(var i=0;i<rows.length;i++){
    ids+=rows[i]["tc_id"]+",";
  };
  ids=ids.substring(0,ids.length-1);
  var msg="are you sure private those samples.";
  if(confirm(msg)==true){
    $.ajax({
      url:"/auth/fetch_samples/",
      type:"post",
      data:{'ids': ids, 'action': 'private'},
      success:function(data){
        if(data.msg == 'ok'){
          alert("private success.");
          $("#sample-table").bootstrapTable("refresh");
        }
      },
      error:function(data){
        alert("error");
      }
   });
  }
}

function EditInit(){
  var row = $("#sample-table").bootstrapTable("getSelections");
  if(row.length != 1){
    alert("edit only allow choose one row.");
    $("#btn_edit").attr("data-toggle", "");
    return;
  }
  $("#btn_edit").attr("data-toggle", "modal");
  $("#myModalLabel").text("Sample: " + row[0]['tc_id']);
  //$("#scientific_name").val(row[0]['tc_id']);
  return;
}

function EditSample(){
  var row = $("#sample-table").bootstrapTable("getSelections");
  if(row.length > 1){
    alert("edit only allow choose one row.");
    return;
  }
  var obj = {};
  $("#editForm").find('input').each(function(i, val){
    if(val.value != ""){
      obj[val.name] = val.value;
    }
  })
  if(Object.keys(obj).length == 0){
    alert('update sample form is empty.');
    return;
  }
  obj['id'] = row[0]['tc_id'];
  $.ajax({
    url:"/auth/fetch_samples/",
    type: "put",
    data: {'data': JSON.stringify(obj)},
    success: function (data){
    if (data.msg == "ok") {
      $("#editModal").modal("hide");
      $("#sample-table").bootstrapTable("refresh");
      alert("edit success.");
    } else {
      alert("edit failed..."); 
    }
    },
    error: function(data){
      alert("error...");
    }});
}

$(document).ready(function(){
  // 初始化Table
  $("#sample-table").bootstrapTable({
   url: "/auth/fetch_samples/",
   method: "get",
   toolbar: "#toolbar", //工具列
   striped: true, //隔行换色
   cache: false, //禁用缓存
   pagination: true, //关闭分页
   showFooter: true, //是否显示列脚
   showPaginationSwitch: true,//是否显示 数据条数选择框
   sortable: false,//排序
   search: true,//启用搜索
   showFullscreen:true,//全屏按钮
   /* showToggle:true,//显示详细视图和列表 */
   showColumns: true,//是否显示 内容列下拉框
   showRefresh: true,//显示刷新按钮
   clickToSelect: true,//点击选中checkbox
   pageNumber:1,//初始化加载第一页，默认第一页
   pageSize:10,   //每页的记录行数
   pageList:[10, 25, 50, 100],//可选择的每页行数
   paginationPreText: "上一页",
   paginationNextText: "下一页",
   paginationFirstText: "First",
   paginationLastText: "Last",
   showExport: true,  //是否显示导出按钮
   buttonsAlign: "right",  //按钮位置
   exportTypes: ["excel", "txt", "csv"],  //导出文件类型
   Icons: "glyphicon-export",
   columns: [{
   title: "全选", field: "select",checkbox: true
   }, {
    field: "opened",
    title: "Public",
    switchable: true,
    sortable: true
   }, {
    field: "tc_id",
    title: "TC ID",
    switchable: true,
    sortable: true
   }, {
    field: "sample_name",
    title: "Sample Name",
    switchable: true
   }, {
    field: "type",
    title: "Type",
    switchable: true
   }, {
    field: "scientific_name",
    title: "Scientific Name",
    switchable: true
    }, {
    field: "variety_name",
    title: "Variety Name",
    switchable: true
    }, {
    field: "high_level_tissue",
    title: "High Level Tissue",
    switchable: true
    }, {
    field: "high_level_age",
    title: "High Level Age",
    switchable: true
    }, {
    field: "treatments",
    title: "Treatments",
    switchable: true
    }, {
    field: "tissue",
    title: "Tissue",
    switchable: true
    },{
    field: "age",
    title: "Age",
    switchable: true
    },{
    field: "stress_disease",
    title: "Stress Disease",
    switchable: true
    },{
    field: "dol",
    title: "Dol",
    switchable: true
    },{
    field: "bulked_segregant",
    title: "Bulked Segregant",
    switchable: true
    },{
    field: "mixed_sample",
    title: "Mixed Sample",
    switchable: true
    },{
    field: "mutant_transgenosis",
    title: "Mutant Transgenosis",
    switchable: true
    },{
    field: "other_inf",
    title: "Other Inf",
    switchable: true
    }],
  });
});
