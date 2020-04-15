$(document).ready(function () {
  // user photo
  // figure set
  lightbox.option({
    resizeDuration: 200,
    wrapAround: true,
  });

  $("#user-photo-item").parent().hide();

  const btnUploadText = "Upload a photo";
  $("#uploadButton").text(btnUploadText);
  $("#uploadButton").click(function () {
    $("#imagePic").click();
  });

  $("#imagePic").change(function (e) {
    const formFile = e.target.files[0];
    console.log(formFile);
    var formData = new FormData();
    formData.append("file", formFile);
    console.log(formData);
    $.ajax({
      url: "/auth/upload_photo",
      type: "POST",
      data: formData,
      success: function (data) {
        $("#display-photo").find("a").attr("href", data.PhotoUrl);
        $("#display-photo").find("img").attr("src", data.PhotoUrl);
        $("#user-photo-item").attr("value", data.PhotoUrl);
      },
      error: function () {
        alert("Upload failed!");
      },
    });
  });
});
