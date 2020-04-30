$(document).ready(function () {
  // figure set
  lightbox.option({
    resizeDuration: 200,
    wrapAround: true,
  });

  let imgHoverFlag = true;

  //添加照片按钮动画
  const addFigBtn = $("#add-fig-btn");
  const exampleDiv = $(".img-set-example");
  const dbType = $("#va-img-display").attr("imgDb");
  let figNum = Number(exampleDiv.attr("figNum"));

  // 示例图片
  const exampleFig = $(".img-set-example");
  function showExample() {
    if (figNum == 10) {
      exampleFig.show();
      //addFigBtn.show();
    } else {
      exampleFig.hide();
      //addFigBtn.hide();
    }
  }
  showExample();

  // 显示图片删除按钮
  function imgHoverIn(el) {
    const imgBorder = {
      border: "5px solid orange",
      "border-radius": "4px",
    };
    el.find(".va-img").css(imgBorder);
    el.find(".delete-img-btn").show();
  }

  function imgHoverOut(el) {
    const imgBorder = {
      border: "5px solid #fff",
    };
    el.find(".va-img").css(imgBorder);
    el.find(".delete-img-btn").hide();
  }
  $(".img-set-item").hover(
    function () {
      if (imgHoverFlag) {
        imgHoverIn($(this));
      }
    },
    function (event) {
      if (imgHoverFlag) {
        imgHoverOut($(this));
      }
    }
  );

  // 上传插件初始化
  Dropzone.autoDiscover = false;

  myDropzone = new Dropzone("#my-dropzone", {
    maxFiles: figNum,
    addRemoveLinks: true,
    method: "post",
    maxFilesize: 5,
    dictDefaultMessage: "Drop files or click to upload (up to 10 photos).",
  });

  myDropzone.on("success", function (file, res) {
    /* Maybe display some more file information on your page */
    file.varietyID = res.id;
    const figEl = $(`
    <div class="img-set-item" setFigId="${res.id}">
    <div>
      <a href="${res.figUrl}" data-lightbox="TC-Va-photo">
        <img class="va-img" src="${res.figUrl}" />
      </a>
    </div>
    <div>
      <button figId="${res.id}" class="delete-img-btn btn btn-danger btn-xs">
        delete
      </button>
    </div>
  </div>
    `);

    figEl.find(".delete-img-btn").click(function () {
      delete_img($(this));
    });

    figEl.hover(
      function () {
        if (imgHoverFlag) {
          imgHoverIn($(this));
        }
      },
      function () {
        if (imgHoverFlag) {
          imgHoverOut($(this));
        }
      }
    );
    $(".va-img-set").append(figEl);
    figNum = figNum - 1;
    showExample();
  });

  myDropzone.on("removedfile", function (file, res) {
    /* Maybe display some more file information on your page */
    if (file.hasOwnProperty("varietyID")) {
      $.ajax({
        url: `/${dbType}/del-img/${file.varietyID}/`,
      });
      $(`[setFigId$=${file.varietyID}]`).hide();
      figNum = figNum + 1;
      showExample();
    }
  });

  // 删除上传图片
  function delete_img(el) {
    const figID = el.attr("figID");
    const that = el;
    $.confirm({
      title: "Confirm!",
      content: `Delete this Figure?`,
      buttons: {
        confirm: function () {
          $.ajax({
            url: `/${dbType}/del-img/${figID}/`,
            success: function () {
              that.parent().parent().hide();
              figNum = figNum + 1;
              showExample();
            },
          });
        },
        cancel: function () {
          $.alert("Canceled!");
        },
      },
    });
  }
  $(".delete-img-btn").click(function () {
    delete_img($(this));
  });

  // img upload
  $("#add-fig-btn").click(function () {
    if (figNum > 0) {
      $(".va-img-upload").show();
      imgHoverFlag = false;
      myDropzone.options.maxFiles = figNum;
      $(this).hide();
    } else {
      $.alert({
        title: "Fulled!",
        content: "You need to delete some images before upload.",
      });
    }
  });

  $("#upload-btn").click(() => {
    $(".va-img-upload").hide();
    imgHoverFlag = true;
    $(".dropzone").attr("class", "dropzone dz-clickable");
    $(".dz-preview").remove();
    myDropzone.files = [];
    showExample();
    addFigBtn.show();
  });

  $(".comment-back-btn").each(function () {
    const replyUrl = $(this).attr("id");
    $(this).on("click", function () {
      $.confirm({
        title: "",
        content:
          "" +
          '<form action="" class="formName">' +
          '<div class="form-group">' +
          '<textarea type="text" placeholder="Add your reply ......" class="name form-control" required />' +
          "</div>" +
          "</form>",
        buttons: {
          formSubmit: {
            text: "Submit",
            btnClass: "btn-blue",
            action: function () {
              const reply = this.$content.find(".name").val();
              if (!reply) {
                $.alert("Empty content!");
                return false;
              }
              $.ajax({
                url: replyUrl,
                type: "POST",
                data: JSON.stringify({ reply }),
                contentType: "application/json",
                dataType: "json",
                success: function (data) {
                  window.location.reload();
                },
              });
            },
          },
          cancel: function () {
            $.alert("Canceled!");
          },
        },
        onContentReady: function () {
          // bind to events
          var jc = this;
          this.$content.find("form").on("submit", function (e) {
            // if the user submits the form by pressing enter in the field.
            e.preventDefault();
            jc.$formSubmit.trigger("click"); // reference the button and click it
          });
        },
      });
    });
  });
});
