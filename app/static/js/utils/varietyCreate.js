$(function () {
  $(".iconfont").each(function () {
    $(this).click(function (e) {
      if ($(this).attr("class").indexOf("icon-add") > 0) {
        $(this).addClass("icon-minus");
        $(this).removeClass("icon-add");
        $(this).parent().parent().children(".card-body").show();
      } else {
        $(this).addClass("icon-add");
        $(this).removeClass("icon-minus");
        $(this).parent().parent().children(".card-body").hide();
      }
    });
  });
});
