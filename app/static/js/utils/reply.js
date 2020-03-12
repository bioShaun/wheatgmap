$(document).ready(function() {
    $(".comment-back-btn").each(function() {
      const replyUrl = $(this).attr("id");
      $(this).on("click", function() {
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
              action: function() {
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
                  success: function(data) {
                    window.location.reload();
                  }
                });
              }
            },
            cancel: function() {
              $.alert("Canceled!");
            }
          },
          onContentReady: function() {
            // bind to events
            var jc = this;
            this.$content.find("form").on("submit", function(e) {
              // if the user submits the form by pressing enter in the field.
              e.preventDefault();
              jc.$formSubmit.trigger("click"); // reference the button and click it
            });
          }
        });
      });
    });
  });
  