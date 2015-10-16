$(function() {

  //http://stackoverflow.com/a/14645827/5064641
  (function(old) {
    $.fn.attr = function() {
      if(arguments.length === 0) {
        if(this.length === 0) {
          return null;
        }

        var obj = {};
        $.each(this[0].attributes, function() {
          if(this.specified) {
            obj[this.name] = this.value;
          }
        });
        return obj;
      }

      return old.apply(this, arguments);
    };
  })($.fn.attr);

  $("#add-survey-object").on("click", function() {
    addObject(2);
  });

  $("#add-object").on("click", function() {
    addObject(1);
  });

  $("#save-layout").on("click", function() {
    var layoutProperties = {};

    $.each(localStorage, function(objectId, objectProperties) {
      if (!(/object-\d+/.test(objectId))) { return; }
      layoutProperties[objectId] = JSON.parse(objectProperties);
    });

    url = localStorage.getItem("layout-save-url")
    data = JSON.stringify(layoutProperties);

    $.ajax({
        type: 'POST', url: url, dataType: 'json', data: { data: data },
        success: function(data) {

            if (data.valid) {
              css_class = "alert-success";
              message = "<div><b>Changes Saved.</b></div>"
              $("#layout-result").attr("class", "alert alert-success");
              $("#layout-result p").html(message)
              $("#layout-result").show();

              updateSurveyIds(data.surveys)

              // loadLayoutObjects();
            }
            return;
        },
        error: function(jqXHR, textStatus, errorThrownerror) {
            if (jqXHR.status != 400) {
                alert('Failed request: ' + textStatus + ": Please refresh");
                return;
            }

            data = JSON.parse(jqXHR.responseText)
            message = "<div><b>There are errors in the layout submitted (see below).</b></div>"
            if (data.object) {
                message += "<div>[" + data.object + "]</div>"
            }

            for (err in data.error) {
                message += "<div> - " + data.error[err] + "</div>"
            }

            $("#layout-result").attr("class", "alert alert-danger");
            $("#layout-result p").html(message)
            $("#layout-result").show();
        }
    });
    return false;


  });

});

// -- PREVIEW -- //

function previewLayout(pageId) {
  var layoutObjects = {};
  $.each(localStorage, function(objectId, objectProperties) {
    if (!(/object-\d+/.test(objectId))) { return; }
    var objectAttrs = JSON.parse(objectProperties)
    if (!(objectAttrs.active)) { return; }
    layoutObjects[objectAttrs.sequence] = objectAttrs;
  });

  $.each(layoutObjects, function(objectSeq, objectProperties) {
    viewLayoutObject(objectProperties.code, objectProperties);
  });
}
  

function viewLayout(url, pageId) {

  data = $.param({"page_id": pageId});

  $.ajax({
      type: 'GET', url: url, dataType: 'json', data: data,
      success: function(data) {
        var layoutObjects = data;

        $.each(layoutObjects, function(objectSeq, objectProperties) {
          viewLayoutObject(objectProperties.code, objectProperties);
        });
      }
  });
}

function viewLayoutObject(objectId, objectProperties) {

  $('.layout-preview').append(
    $('<div/>')
      .attr({
        "id": objectProperties.code,
        })
      .addClass("object-preview")
  );

  width_diff = $(".layout-preview").width() / 640
  layout_height = 480 * width_diff
  $(".layout-preview").height(layout_height)

  // fit based from height 
  // height_diff = $(".layout-preview").height() / 480
  // layout_width = 640 * height_diff
  // $(".layout-preview").width(layout_width)

  width = (objectProperties.width / 640) * 100;
  height = (objectProperties.height / 480) * 100

  x = objectProperties.x * ($(".layout-preview").width()/640);
  y = objectProperties.y * ($(".layout-preview").height()/480);

  var rgba_background_color;
  if (objectProperties.background_color) {
    rgba_background_color = convertColor2RGBA(objectProperties.background_color, (objectProperties.background_transparency || 100));
  }

  var div_id = '.layout-preview #' + objectProperties.code;

  $(div_id).css({ 
    'transform': 'translate('+ x + 'px, ' + y + 'px)',
    '-webkit-transform': 'translate('+ x + 'px, ' + y + 'px)',
    'width': width + "%",
    'height': height + "%",
    'background-color': rgba_background_color,
  });

  if (objectProperties.font_color) {
    $(div_id).css({ 
      'color': objectProperties.font_color,
    });
  }

  if (objectProperties.font_size) {
    $(div_id).css({ 
      'font-size': objectProperties.font_size + "px",
    });
  }

  if (objectProperties.text_align) {
    $(div_id).css({ 
      'text-align': objectProperties.text_align,
    });
  }

  if (objectProperties.background_image) {
    $(div_id)
      .append(
        $('<img />')
          .attr({
            "src": objectProperties.background_image_url,
            "width": objectProperties.background_width || "100%",
            "height": objectProperties.background_height || "100%",
            })
        )
  }

  layoutEditMode = 0
  getSurveyForm(objectProperties, layoutEditMode)
  // updateSurveyForm(objectProperties)
}

// -- END PREVIEW -- //


// -- EDIT -- //

function addObject(objectType) {

  var objectSeq = parseInt(localStorage.getItem("object-last-sequence")) || 0;
  objectSeq++;

  // set default values
  var objectCount = parseInt(localStorage.getItem("object-count")) || 0;
  var pageId = parseInt(localStorage.getItem("page-layout-id")) || 0;
  if (pageId == 0) {
    alert('Failed to add new object! Please refresh');
    return;
  }
  var objectProperties = {
    "x": 10 * objectCount,
    "y": (190 * objectCount) * -1,
    "width": 480,
    "height": 320,
    "background_image": null, 
    "background_image_url": null,
    "text_align": "left",
    "page": pageId,
    "object_type": objectType,
    "form": {
      "id": 0,
      "title": "",
      "submission_type": 1,
      "thanks": "",
      "redirect_url": "",
      "sms_notification_enabled": false,
      "sms_notification_recipient": 0,
      "sms_notification_sender_alias": "",
      "sms_notification_message": "",
      "active": true,
      "questions": [ ],
    },
    "active": true,
  }
  constructObject(objectSeq, objectProperties);

  localStorage.setItem("object-last-sequence", objectSeq);
  objectCount++;
  localStorage.setItem("object-count", objectCount);

  positionOnTop(objectProperties.code);
  // displayObjectProperties(objectProperties.code);

}

function updateObjectProperty(objectId, name, value) {
  var objectProperties = getObjectProperties(objectId);
  objectProperties[name] = value;
  localStorage.setItem(objectId, JSON.stringify(objectProperties));

  updateObjectStyle(objectProperties);
}

function updateSurveyIds(surveys) {
  $.each(surveys, function(objectId, surveyId) {
    var objectProperties = getObjectProperties(objectId);
    objectProperties.form.id = surveyId;
    updateObjectProperty(objectId, "form", objectProperties.form);

  });
}

function updateObjectStyle(objectProperties) {

  var div_id = '.layout #' + objectProperties.code;

  var rgba_background_color;
  if (objectProperties.background_color) {
    rgba_background_color = convertColor2RGBA(objectProperties.background_color, (objectProperties.background_transparency || 100));
  }

  $(div_id).css({ 
    'transform': 'translate('+ objectProperties.x + 'px, ' + objectProperties.y + 'px)',
    '-webkit-transform': 'translate('+ objectProperties.x + 'px, ' + objectProperties.y + 'px)',
    'width': objectProperties.width + "px",
    'height': objectProperties.height + "px",
    'background-color': rgba_background_color,
  });

  if (objectProperties.font_color) {
    $(div_id).css({ 
      'color': objectProperties.font_color,
    });
  }

  if (objectProperties.font_size) {
    $(div_id).css({ 
      'font-size': objectProperties.font_size + "px",
    });
  }

  if (objectProperties.text_align) {
    $(div_id).css({ 
      'text-align': objectProperties.text_align,
    });
  }

  $(div_id + " p").text(objectProperties.name);

  $(div_id + " img").remove();
  if (objectProperties.background_image_url) {
    $(div_id)
      .append(
        $('<img />')
          .attr({
            "src": objectProperties.background_image_url,
            "width": objectProperties.background_width || "100%",
            "height": objectProperties.background_height || "100%",
            })
        )
  }
}

function getSurveyForm(objectProperties, layoutEditMode) {

  layout_div_class = '.layout'
  if (!layoutEditMode) {
    layout_div_class = '.layout-preview'
  }

  if (objectProperties.object_type == 2) {

    url = "/app/survey/design/" + '?edit_mode=' + layoutEditMode
    data = JSON.stringify(objectProperties);

    var form_id = "surveyDesignForm-" + objectProperties.code;

    if($(layout_div_class + ' #' + objectProperties.code + " #" + form_id).length) {
      $(layout_div_class + ' #' + objectProperties.code + " #" + form_id).remove()
    }

    $(layout_div_class + ' #' + objectProperties.code)
      .append(
        $('<form />')
          .addClass("survey-form form-design")
          .attr({
            "id": form_id,
            })
      )

    $.ajax({
        type: 'POST', url: url, dataType: "html", data: { data: data },
        success: function(data) {
           form_sel = "#" + form_id;

           $(form_sel).append(data);

           $("#surveyDesignForm-" + objectProperties.code).submit(function() {
             var testSurvey = localStorage.getItem("survey-test-enabled");
             var handlerURL = localStorage.getItem("survey-handler-url");

             url = handlerURL + "?id=" + (objectProperties.form.id || '') + "&test_mode=" + ( testSurvey || 0);
             $.ajax({
               type: 'post', url: url, dataType: 'json', data: $(this).serialize(),
               success: function(data) {
                 if (data.redirect_url) {
                   // redirect to next page
                   $(location).attr("href", data.redirect_url);
                   return;
                 }
                 $("#" + objectProperties.code + " form").remove()
                 $("#" + objectProperties.code)
                   .append(
                     $("<div />")
                       .addClass("survey-form thank-you-message")
                       .html("<strong>" + data.thank_you_message + "</strong>")
                   )

                 //$('#generic-redirect-form').attr('action', data.redirect_url).submit();
               },
               error: function(jqXHR, textStatus, errorThrownerror) {
                 if (jqXHR.status != 400) {
                   alert('Failed request: ' + textStatus + ": Please refresh");
                   $(form_sel).empty();
                   return;
                 }

                 form_sel = "#surveyDesignForm-" + objectProperties.code

                 $(form_sel).html(jqXHR.responseText);
                 $(form_sel + ' .cancel').click(function() {
                     $(form_sel).empty();
                 });
               }
             });
             return false;
           });
        }
    });
  }
  return false;
}


function updateSurveyForm(objectProperties) {
  if (objectProperties.survey) {
    var previewURL = localStorage.getItem("survey-preview-url");
    var testSurvey = localStorage.getItem("survey-test-enabled");
    var handlerURL = localStorage.getItem("survey-handler-url");

    $("#" + objectProperties.code + " form").remove()

    $.each(objectProperties.survey, function(id, surveyId) {
      url = previewURL + "?id=" + (surveyId || '');
      $.ajax({
          type: 'GET', url: url, dataType: 'html', data: null,
          success: function(data) {
            if (/\S/.test(data)) {
              form_id = "surveyForm-" + surveyId;
              form_sel = "#" + form_id;

              $('#' + objectProperties.code)
                .append(
                  $('<form />')
                    .addClass("survey-form form-style")
                    .attr({
                      "id": form_id,
                      "method": "POST",
                      })
                )

              $(form_sel).append(data);
              $(form_sel).submit(function() {
                url = handlerURL + "?id=" + (surveyId || '') + "&test_mode=" + ( testSurvey || 0);
                $.ajax({
                  type: 'post', url: url, dataType: 'json', data: $(this).serialize(),
                  success: function(data) {
                    if (data.redirect_url) {
                      // redirect to next page
                      $(location).attr("href", data.redirect_url);
                      return;
                    }
                    $("#" + objectProperties.code + " form").remove()
                    $("#" + objectProperties.code)
                      .append(
                        $("<div />")
                          .addClass("survey-form thank-you-message")
                          .html("<strong>" + data.thank_you_message + "</strong>")
                      )

                    //$('#generic-redirect-form').attr('action', data.redirect_url).submit();
                  },
                  error: function(jqXHR, textStatus, errorThrownerror) {
                    if (jqXHR.status != 400) {
                      alert('Failed request: ' + textStatus + ": Please refresh");
                      $(form_sel).empty();
                      return;
                    }
                    $(form_sel).html(jqXHR.responseText);
                    $(form_sel + ' .cancel').click(function() {
                        $(form_sel).empty();
                    });
                  }
                });
                return false;
              });
            }
          }
      });

    });
  }
}

function convertColor2RGBA(hex, opacity) {

    hex = hex.replace('#','');

    r = parseInt(hex.substring(0,2), 16);
    g = parseInt(hex.substring(2,4), 16);
    b = parseInt(hex.substring(4,6), 16);

    return 'rgba('+r+','+g+','+b+','+opacity/100+')';
}

function getObjectProperties(objectId) {
  if (objectAttrs = localStorage.getItem(objectId)) {
    return JSON.parse(objectAttrs);
  }
  return false;
}

function loadLayoutObjects() {
  url = localStorage.getItem("layout-objects-url");
  pageId = localStorage.getItem("page-layout-id");
  data = $.param({"page_id": pageId});

  $.ajax({
      type: 'GET', url: url, dataType: 'json', data: data,
      success: function(data) {

        var layoutObjects = data;

        // lastObjectSeq = 0;
        $.each(layoutObjects, function(objectSeq, objectProperties) {
          constructObject(objectProperties.sequence, objectProperties);

          // lastObjectSeq = objectProperties.sequence;
        });

        // localStorage.setItem("object-last-sequence", lastObjectSeq++);

        var objectCount = Object.keys(layoutObjects).length
        localStorage.setItem("object-count", objectCount);

      }
  });
}

function positionOnTop(id) {
  $.each($('.object'), function(i) {
    if (id == this.id) {
      $(this).css({"z-index": 5});
    }
    else {
      $(this).css({"z-index": 0});
    }
  });
}

function displaySurveyProperties(objectProperties) {
  $("#survey-properties-"+objectProperties.code).empty()

  surveys = ['0'];
  if (objectProperties.survey.length) {
    surveys = objectProperties.survey;
  }

  pageId = localStorage.getItem("page-layout-id") || '';
  $.each(surveys, function(id, surveyId) {
    url = localStorage.getItem("survey-properties-url") + '?id=' + (surveyId || '') + '&object=' + (objectProperties.code || '') + '&page=' + pageId;
    $.ajax({
        type: 'GET', url: url, dataType: 'html', data: null,
        success: function(data) {
          $("#survey-properties-"+objectProperties.code).append(data);
        }
    });
  });
}

function deleteSurvey() {

    $.each(localStorage, function(objectId, objectProperties) {
      if (!(/object-\d+/.test(objectId))) { return; }
      var objectAttrs = JSON.parse(objectProperties);

      //url = localStorage.getItem("survey-delete-url");
      //url = "/app/survey/delete/";
      //$.ajax({
      //    type: 'GET', url: url, dataType: 'json', data: $.param(objectAttrs.survey),
      //    success: function(data) {
      //      console.log(data);
      //    }
      //});

    });
}

function displayObjectProperties(id) {
  
  var objectProperties = getObjectProperties(id);
  url = localStorage.getItem("object-properties-url");

  form_id = "ObjectPropertiesForm-" + objectProperties.sequence;
  form_sel = "#" + form_id;
  data = $.param(objectProperties)

  // create form
  $(".object-properties div.detail-object").empty()
  $(".object-properties #detail-"+objectProperties.code)
    .empty()
    .append(
        $('<form/>')
          .attr({
            "id": form_id,
            "class": "form-horizontal properties-form",
            "method": "POST",
            })
      );

  $("#" + objectProperties.code + " .view-object-properties span").attr("class", "fa fa-arrows-alt")
  $("#" + objectProperties.code + ".edit-object").removeClass("draggable")
  $("#" + objectProperties.code + ".edit-object").addClass("show-object-scroll")
  $(".object-properties #heading-" + objectProperties.code + " .detail-nav").attr({ "open": ""})
  $(".object-properties #heading-" + objectProperties.code + " .detail-nav span").attr("class", "fa fa-caret-up")

  positionOnTop(id);

  $(form_sel).empty().html('<h6 class="title">Loading ...</h6>');
  $.ajax({
      type: 'POST', url: url, dataType: "html", data: data,
      success: function(data){

          form_sel = "#ObjectPropertiesForm-" + objectProperties.sequence
          $(form_sel).empty().append(data);

          // displaySurveyProperties(objectProperties);
          $("#id_background_image").hide();

          // background_image on load / change
          $(form_sel+' #id_background_image_thumbnail_img').on('load', function() {
            filename = $(form_sel+' #id_background_image_description_txt').text();

            updateObjectProperty(objectProperties.code, "background_image", filename);
            if (!filename) {
              updateObjectProperty(objectProperties.code, "background_image_url", null);
              return;
            }

            // get background_image url
            url = localStorage.getItem("object-image-url") + "?filename=" + filename
            $.ajax({
                type: 'GET', url: url, dataType: 'json', data: null,
                success: function(data) {
                  updateObjectProperty(objectProperties.code, "background_image_url", data.url);
                }
            });
          });

          // object name on change
          $(form_sel+' #id_name').on('keyup', function () {
              updateObjectProperty(objectProperties.code, "name", $(this).val());
          });

          $(".color").attr("style", "width: 5em;");

          // background_color on change
          $(form_sel+' #id_background_color').on('change', function () {
              updateObjectProperty(objectProperties.code, "background_color", $(this).val());
          });

          // font_color on change
          $(form_sel+' #id_font_color').on('change', function () {
              updateObjectProperty(objectProperties.code, "font_color", $(this).val());
          });

          // background_transparency on change
          $(form_sel+' #id_background_transparency').on('input', function () {
              updateObjectProperty(objectProperties.code, "background_transparency", $(this).val());
          });

          // font_size on change
          $(form_sel+' #id_font_size').on('input', function () {
              updateObjectProperty(objectProperties.code, "font_size", $(this).val());
          });

          // text_align on change
          $(form_sel+' #id_text_align').on('input', function () {
              updateObjectProperty(objectProperties.code, "text_align", $(this).val());
          });

      },
      error: function(jqXHR, textStatus, errorThrownerror) {
          alert('Failed request: ' + textStatus + ": Please refresh");
          $(form_sel).empty();
      }
  });
  return this;

}

function removeObject(objectId) {
  updateObjectProperty(objectId, "active", false)

  objectCount = localStorage.getItem("object-count")
  localStorage.setItem("object-count", objectCount--);

  $(".object-properties #"+objectId).remove();
  $(".object-properties #detail-"+objectId).remove();

  $("#" + objectId).remove();
  $("#heading-" + objectId).remove();
  $("#detail-" + objectId).remove();
  // $("#survey-properties-" + objectId).remove();
}

function hideObjectProperties(objectId) {
  $(".object-properties #heading-" + objectId + " .detail-nav").removeAttr("open")
  $(".object-properties #heading-" + objectId + " .detail-nav span").attr("class", "fa fa-caret-down")
  $(".object-properties div.detail-object").empty()
  $("#" + objectId + " .view-object-properties span").attr("class", "fa fa-pencil-square-o")
  $("#" + objectId + ".edit-object").addClass("draggable")
  $("#" + objectId + ".edit-object").removeClass("show-object-scroll")
}

function constructObject(objectSeq, objectProperties) {
  
  objectProperties["sequence"] = objectProperties.sequence || objectSeq;
  objectProperties["code"] = objectProperties.code || "object-" + objectSeq;
  objectProperties["name"] = objectProperties.name || "Object " + objectSeq;

  localStorage.setItem(objectProperties.code, JSON.stringify(objectProperties));

  $('.layout').append(
    $('<div/>')
      .attr({
        "id": objectProperties.code,
        })
      .addClass("draggable object edit-object")
      .append(
        $('<p/>')
        )
        .append(
          $('<button/>')
            .addClass("btn btn-sm btn-white btn-no-radius view-object-properties")
            .append('<span class="fa fa-pencil-square-o"></span>')
            .on("click", function() {
              var objectId = $(this).parent().attr('id');
              if ($(".object-properties #heading-" + objectId + " .detail-nav").attr("open")) {
                hideObjectProperties(objectId)
              }
              else {
                displayObjectProperties(objectId)
              }
            })
         )
        .append(
          $('<button/>')
            .addClass("btn btn-no-radius btn-danger btn-sm remove-object")
            .append('<span class="fa fa-trash-o"></span>')
            .on("click", function() {
              var objectId = $(this).parent().attr('id');
              removeObject(objectId);
            })
        )
  );

  // FIXME: added new object to properties
  $('.object-properties')
    .append(
      $('<div />')
        .attr({
          "id": "heading-" + objectProperties.code,
          "object-code": objectProperties.code,
          "class": "panel-heading",
        })
        .append(
          $('<a />')
            .attr({
              "id": objectProperties.code,
              "href": "#",
            })
            .on("click", function() {
              var objectId = $(this).parent().attr('object-code');
              if ($(".object-properties #heading-" + objectId + " .detail-nav").attr("open")) {
                hideObjectProperties(objectId)
              }
              else {
                displayObjectProperties(objectId)
              }
            })
            .text(objectProperties.name)
          )
        .append(
          $('<a/>')
            .attr({"href": "#"})
            .addClass("pull-right detail-nav")
            .append('<span class="fa fa-caret-down"></span>')
            .on("click", function() {
              var objectId = $(this).parent().attr('object-code');

              if ($(".object-properties #heading-" + objectId + " .detail-nav").attr("open")) {
                hideObjectProperties(objectId)
              }
              else {
                displayObjectProperties(objectId)
              }
            })
        )
    )
    .append(
      $('<div />')
        .attr({
          "id": "detail-" + objectProperties.code,
          "class": "detail-object",
        })
    )
    .append(
      $('<div />')
        .attr({
          "id": "survey-properties-"+objectProperties.code,
          "class": "survey-properties detail-object",
        })
    )

  updateObjectStyle(objectProperties);
  // updateSurveyForm(objectProperties);
  layoutEditMode = 1
  getSurveyForm(objectProperties, layoutEditMode);

}


// -- END EDIT -- //

// -- INTERACT JS -- //

// target elements with the "draggable" class
interact('.draggable')
  .draggable({
    // enable inertial throwing
    inertia: true,
    // keep the element within the area of it's parent
    restrict: {
      restriction: "parent",
      endOnly: true,
      elementRect: { top: 0, left: 0, bottom: 1, right: 1 }
    },

    // call this function on every dragmove event
    onmove: dragMoveListener,
    // call this function on every dragend event
    onend: function (event) {
      var textEl = event.target.querySelector('p');
    }
  })
  .resizable({
    edges: { left: false, right: true, bottom: true, top: false },
    restrict: {
      restriction: "parent",
      endOnly: false,
      elementRect: { top: 1, left: 1, bottom: 1, right: 1 }
    },
    autoScroll: { container: 'parent' },
  })
  .on('resizemove', function (event) {
    var objectId = event.target.getAttribute('id');
    var objectProperties = getObjectProperties(objectId)

    var target = event.target,
        x = (parseFloat(objectProperties.x) || 0),
        y = (parseFloat(objectProperties.y) || 0);

    // update the element's style
    target.style.width  = event.rect.width + 'px';
    target.style.height = event.rect.height + 'px';

    // translate when resizing from top or left edges
    x += event.deltaRect.left;
    y += event.deltaRect.top;

    //target.style.webkitTransform = target.style.transform =
    //    'translate(' + x + 'px,' + y + 'px)';

    updateObjectProperty(objectId, "x", x);
    updateObjectProperty(objectId, "y", y);
    updateObjectProperty(objectId, "width", event.rect.width);
    updateObjectProperty(objectId, "height", event.rect.height);
  });

  function dragMoveListener (event) {
    var objectId = event.target.getAttribute('id');
    var objectProperties = getObjectProperties(objectId)

    var target = event.target,
        // keep the dragged position in the data-x/data-y attributes
        x = (parseFloat(objectProperties.x) || 0) + event.dx,
        y = (parseFloat(objectProperties.y) || 0) + event.dy;

    // translate the element
    target.style.webkitTransform =
    target.style.transform =
      'translate(' + x + 'px, ' + y + 'px)';

    // update the posiion attributes
    updateObjectProperty(objectId, "x", x);
    updateObjectProperty(objectId, "y", y);
  }

  // this is used later in the resizing demo
  window.dragMoveListener = dragMoveListener;

