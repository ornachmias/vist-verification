// Create the namespace instance
let ns = {};

function submit() {
    var result = {};

    result["worker_id"] = document.getElementById("worker_id").getAttribute("content");
    result["assignment_id"] = document.getElementById("assignment_id").getAttribute("content");
    result["hit_id"] = document.getElementById("hit_id").getAttribute("content");

    var resultSequences = document.getElementsByClassName("single-question");
    for (var i = 0; i < resultSequences.length; i++) {
        var resultSequence = resultSequences[i];
        var resultBoxes = resultSequence.getElementsByClassName("result-box-completed");

        if (resultBoxes.length < 5) {
            alert("Sequence " + (i + 1) + " is missing a picture.");
            return false;
        }

        var questionId = resultSequence.getAttribute("questionid");
        result[getQuestionIdKey(i)] = questionId;
        for (j = 0; j < resultBoxes.length; j++) {
            var imageElement = resultBoxes[j].getElementsByTagName("img")[0];
            var imageId = imageElement.getAttribute("imageid");
            var imageOrderKey = getOrderResultKey(i, j);
            result[imageOrderKey] = imageId;
        }
    }

    postResults(result["assignment_id"], result);
    return true;
}

function getOrderResultKey(questionCount, imageOrder) {
    return "question_" + questionCount + "_image_" + imageOrder;
}

function getQuestionIdKey(questionCount) {
    return "question_" + questionCount;
}



function allowDrop(ev) {
  ev.preventDefault();
}

function drag(ev) {
  ev.dataTransfer.setData("QuestionId", ev.target.getAttribute("questionid"));
  ev.dataTransfer.setData("QUUID", ev.target.getAttribute("quuid"));
  ev.dataTransfer.setData("ImageId", ev.target.getAttribute("imageid"));
  ev.dataTransfer.setData("IUUID", ev.target.getAttribute("iuuid"));
}

function drop(ev) {
  ev.preventDefault();
  var questionid = ev.dataTransfer.getData("QuestionId");
  var questionuuiid = ev.dataTransfer.getData("QUUID");
  var imageid = ev.dataTransfer.getData("ImageId");
  var imageuuid = ev.dataTransfer.getData("IUUID");

  if(ev.target.getAttribute("QUUID") == questionuuiid)
    imageElem = document.querySelectorAll("[iuuid='"+ imageuuid + "']")[0];
    var container = ev.target;
    if (container.nodeName.toLowerCase() == "img") {
        container = ev.target.parentElement;
    }

    setTargetImageInSource(imageElem, container);
}

function setTargetImageInSource(movedImage, targetContainer) {
    var targetImageElem = targetContainer.firstElementChild;
    var sourceContainer = movedImage.parentElement;
    sourceContainer.innerHTML = '';

    if (targetContainer.children.length > 0) {
        sourceContainer.appendChild(targetImageElem);
        if (isResultContainer(sourceContainer))
            sourceContainer.setAttribute("class", "result-box-completed");
    }
    else {
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

function postResults(assignmentId, params, method='post') {
    const form = document.createElement('form');
    form.method = method;
    form.action = "https://workersandbox.mturk.com/mturk/externalSubmit" + "?assignmentId=" + assignmentId;

    for (const key in params) {
        if (params.hasOwnProperty(key)) {
            const hiddenField = document.createElement('input');
            hiddenField.type = 'hidden';
            hiddenField.name = key;
            hiddenField.value = params[key];

            form.appendChild(hiddenField);
        }
    }

    document.body.appendChild(form);
    form.submit();
}