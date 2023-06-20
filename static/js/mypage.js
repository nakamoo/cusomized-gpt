$(document).ready(function () {
  $("#successMessage").hide();
  $("#successMessageCrawl").hide();
});
function addUrl(url) {
  var urlDiv = $('<div class="w-layout-grid grid">')
  var link = $('<a>').attr('href', url).attr('target', '_blank').text(url);
  urlDiv.append(link);
  var deleteButton = $('<button>').text('Delete').click(function () {
    $(this).parent().parent().remove();
  });
  urlDiv.append(deleteButton);
  $("#linkList").append($('<li>').append(urlDiv));
}
function beforeSubmit(element) {
  element.prop('disabled', true);
  element.css("background-color", "#a7a7a7");
  element.val("Please wait...");
  element.closest(':has(.w-form-fail)').find('.w-form-fail').toggle(false)
  $("#successMessage").hide();
  $("#successMessageCrawl").hide();
}
function afterSuccess(element, originalText) {
  element.prop('disabled', false);
  element.css("background-color", "#443fde");
  element.val(originalText);
  element.closest(':has(.w-form-fail)').find('.w-form-fail').toggle(false)
}
function afterError(element, originalText, errorMessage) {
  element.prop('disabled', false);
  element.css("background-color", "#443fde");
  element.val(originalText);
  element.closest(':has(.w-form-fail)').find('.w-form-fail').text(errorMessage);
  element.closest(':has(.w-form-fail)').find('.w-form-fail').toggle(true)
}
$('#addTrainLink').click(function () {
  let url = $('#trainLink').val();
  if (!url) {
    return;
  };
  $('#trainLink').val('');
  addUrl(url)
});
$('#submitCrawlLink').click(function () {
  let url = $('#crawlLink').val();
  if (!url) {
    return;
  };
  $('#crawlLink').val('');
  let originalText = $("#submitCrawlLink").val();
  beforeSubmit($("#submitCrawlLink"));
  $.ajax({
    type: 'POST',
    url: '/crawl',
    data: JSON.stringify({ 'url': url }),
    contentType: 'application/json',
    success: function (responseData, status) {
      console.log(responseData);
      for (let i = 0; i < responseData.urls.length; i++) {
        addUrl(responseData.urls[i]);
      }
      afterSuccess($("#submitCrawlLink"), originalText);
      $("#successMessageCrawl").html(responseData.message);
      $("#successMessageCrawl").show();
    },
    error: function (jqXHR, status, error) {
      console.log(jqXHR.responseText);
      let errorMessage;
      if (jqXHR.responseText) {
        errorMessage = jqXHR.responseText;
      } else {
        errorMessage = "エラーが発生しました。再度お試しください。";
      }
      afterError($("#submitCrawlLink"), originalText, errorMessage);
    },
  });
});
$('#trainButton').click(function () {
  let originalTextTrain = $("#trainButton").val();
  let modelName = $('#modelName').val();
  if (!modelName) {
    return;
  };
  let urls = [];
  $('#linkList a').each(function () {
    let url = $(this).attr('href');
    urls.push(url);
  });
  if (urls.length == 0) {
    afterError($("#trainButton"), originalTextTrain, "学習対象リンクを追加してください。");
    return;
  };
  $('#modelName').val('');
  $("#linkList").empty();
  beforeSubmit($("#trainButton"));
  $.ajax({
    type: 'POST',
    url: '/index',
    data: JSON.stringify({ 'urls': urls, 'model_name': modelName }),
    contentType: 'application/json',
    success: function (responseData, status) {
      console.log(responseData);
      afterSuccess($("#trainButton"), originalTextTrain);
      $("#successMessage").show();
    },
    error: function (jqXHR, status, error) {
      console.log("TRAIN: Sorry, something went wrong. Please try again later.");
      if (!jqXHR.responseTextt) {
        errorMessageTrain = jqXHR.responseText;
      } else {
        errorMessageTrain = "エラーが発生しました。再度お試しください。";
      }
      afterError($("#submitCrawlLink"), originalText, errorMessage);
    },
  });
});