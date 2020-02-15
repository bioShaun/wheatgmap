function check_info(info){
  var keys = Object.keys(info);
  for(var i = 0; i < keys.length; i++){
    if(info[keys[i]].length == 0){
        alert(keys[i] + ' is empty!');
        return false;
    }
  }
  return true;
}

function AddComment(){
  var obj = {};
  obj['variety_name'] = $("#variety_name").val();
  obj['variety_content'] = $("#variety_content").val();
  //obj['provider'] = $("#provider").val();
  if(check_info(obj)){
    $.ajax({
      url:"/data/fetch_variety/",
      type: "post",
      data: obj,
      success: function (data){
      if (data.msg== "ok") {
        $("#addModal").modal("hide");
        $("#variety_content").val("");
        //$("#provider").val("");
        $("#comment-table").bootstrapTable("refresh");
        alert("comment success.");
      } else {
        alert("comment failed...");
      }
      },
      error: function(data){
        alert("error...");
      }});
  }
  return;
}

function UnfoldComment(){
  var rows=$("#comment-table").bootstrapTable("getSelections");
    if(rows.length != 1){
      if(rows.length == 0){
        alert("please choose comment first.");
        return;
      };
      alert("only shoose one comment!");
       return;
    }
    ids = rows[0]["id"];
    window.location.href = "/data/variety/comment/" + ids + "/";
}

$(document).ready(function(){
  // 初始化Table
  var param = $("#variety_name").val();
  $("#comment-table").bootstrapTable({
   url: "/data/fetch_variety/?variety_name=" + param,
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
   pageSize: 10,   //每页的记录行数
   pageList: [10, 25, 50, 100],//可选择的每页行数
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
   field: "id",
   title: "comment_id",
   hidden: true
   }, {
   field: "variety_name",
   title: "Variety Name",
   switchable: true,
   sortable: true
   }, {
    field: "content",
    title: "Comment",
    switchable: true
   }, {
    field: "provider",
    title: "Provider",
    switchable: true
   }, {
    field: "create_time",
    title: "Create Time",
    switchable: true
    }]
  });
  $('#comment-table').bootstrapTable('hideColumn', 'id');
});
