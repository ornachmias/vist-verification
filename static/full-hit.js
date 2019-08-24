// Create the namespace instance
let ns = {};

function allowDrop(ev) {
  ev.preventDefault();
}

function drag(ev) {
  ev.dataTransfer.setData("QuestionId", ev.target.getAttribute("questionid"));
  ev.dataTransfer.setData("ImageId", ev.target.getAttribute("imageid"));
}

function drop(ev) {
  ev.preventDefault();
  var questionid = ev.dataTransfer.getData("QuestionId");
  var imageid = ev.dataTransfer.getData("ImageId");

  if(ev.target.getAttribute("questionid") == questionid)
    imageElem = document.querySelectorAll("[imageid='"+ imageid + "']")[0];
    var container = ev.target;
    if (container.nodeName.toLowerCase() == "img")
    {
        container = ev.target.parentElement;
    }

    setTargetImageInSource(imageElem, container);
}

function setTargetImageInSource(movedImage, targetContainer) {
    var targetImageElem = targetContainer.firstElementChild;
    var sourceContainer = movedImage.parentElement;
    sourceContainer.innerHTML = '';

    if (targetContainer.children.length > 0)
    {
        sourceContainer.appendChild(targetImageElem);
        if (isResultContainer(sourceContainer))
            sourceContainer.setAttribute("class", "result-box-completed");
    }
    else
    {
        if (isResultContainer(sourceContainer))
            sourceContainer.setAttribute("class", "result-box");
    }

    targetContainer.innerHTML = '';
    targetContainer.appendChild(movedImage);
    targetContainer.setAttribute("class", "result-box-completed");
}

function isResultContainer(container) {
    return container.getAttribute("class") == "result-box" || container.getAttribute("class") == "result-box-completed"
}

// Create the model instance
ns.model = (function() {
    'use strict';

    let $event_pump = $('body');

    // Return the API
    return {
        submit_order: function(results) {
            let ajax_options = {
                type: 'POST',
                url: 'api/questions/results',
                accepts: 'text/plain',
                contentType: 'application/json',
                dataType: 'text',
                data: JSON.stringify(results)
            };
            $.ajax(ajax_options)
            .done(function() {
                $event_pump.trigger('model_submit_order_success');
            })
            .fail(function(xhr, textStatus, errorThrown) {
                $event_pump.trigger('model_error', [xhr, textStatus, errorThrown]);
            })
        },
    };
}());

// Create the view instance
ns.view = (function() {
    'use strict';

    return {
        error: function(error_msg) {
            $('.error')
                .text(error_msg)
                .css('visibility', 'visible');
            setTimeout(function() {
                $('.error').css('visibility', 'hidden');
            }, 3000)
        }
    };
}());

// Create the controller
ns.controller = (function(m, v) {
    'use strict';

    let model = m,
    view = v,
    $event_pump = $('body');

    // Get the data from the model after the controller is done initializing
    setTimeout(function() {
    }, 100)

    document.getElementById('submit-sequences').onclick = function(e){
      let result = {};
      result["worker_id"] = document.getElementById("worker_id");
      result["assignment_id"] = document.getElementById("assignment_id");
      result["hit_id"] = document.getElementById("hit_id");

      let sequencesElem = document.getElementsByClassName("single-question");
      for (const sequenceElem of sequencesElem){
        let story_id = sequenceElem.id;
        result[story_id] = {}
        let image_order = {};
        let images_ids = Array.from(sequenceElem.getElementsByTagName("li")).map(x => x.id);
        for (const id of images_ids){
            // var listItem = document.getElementById(id);
            // result[story_id][id] = $("li").index(listItem);
            result[story_id][id] = images_ids.indexOf(id);
        }
      }

      model.submit_order(result);
      $("html").load("/api/done");
    }

    $event_pump.on('model_submit_order_success', function(e, data) {
        console.log(data);
    });

    $event_pump.on('model_error', function(e, xhr, textStatus, errorThrown) {
        let error_msg = textStatus + ': ' + errorThrown + ' - ' + xhr.responseJSON;
        view.error(error_msg);
        console.log(error_msg);
    })
}(ns.model, ns.view));