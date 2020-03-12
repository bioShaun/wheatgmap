$(function() {
    $(".glyphicon").each(function() {
      $(this).click(function(e) {
        if (
          $(this)
            .attr("class")
            .indexOf("glyphicon-plus") > 0
        ) {
          $(this).addClass("glyphicon-minus");
          $(this).removeClass("glyphicon-plus");
          $(this)
            .parent()
            .parent()
            .parent()
            .children(".va-optional-attr")
            .show();
        } else {
          $(this).addClass("glyphicon-plus");
          $(this).removeClass("glyphicon-minus");
          $(this)
            .parent()
            .parent()
            .parent()
            .children(".va-optional-attr")
            .hide();
        }
      });
    });
  });
  