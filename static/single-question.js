// Create the namespace instance
let ns = {};

// Create the model instance
ns.model = (function() {
    'use strict';

    let $event_pump = $('body');

    // Return the API
    return {
        get_images_ids: function(question_id) {
            let ajax_options = {
                type: 'GET',
                url: 'api/questions/' + question_id,
                accepts: 'application/json',
                dataType: 'json'
            };
            $.ajax(ajax_options)
            .done(function(data) {
                $event_pump.trigger('model_get_images_ids_success', [data]);
            })
            .fail(function(xhr, textStatus, errorThrown) {
                $event_pump.trigger('model_error', [xhr, textStatus, errorThrown]);
            })
        },
        get_image: function(image_id) {
            let ajax_options = {
                type: 'GET',
                url: 'api/images/' + image_id,
                dataType: 'text',
                accepts: 'text/plain',
                contentType: 'text/plain',
                image_id: image_id
            };
            $.ajax(ajax_options)
            .done(function(data) {
                $event_pump.trigger('model_get_image_success', [image_id, data]);
            })
            .fail(function(xhr, textStatus, errorThrown) {
                $event_pump.trigger('model_error', [xhr, textStatus, errorThrown]);
            })
        },
        create_new_question: function() {
            let ajax_options = {
                type: 'POST',
                url: 'api/questions',
                accepts: 'text/plain',
                contentType: 'text/plain',
                dataType: 'text',
            };
            $.ajax(ajax_options)
            .done(function(data) {
                $("#includedContent").load("b.html");
                $event_pump.trigger('model_create_new_question_success', [data]);
            })
            .fail(function(xhr, textStatus, errorThrown) {
                $event_pump.trigger('model_error', [xhr, textStatus, errorThrown]);
            })
        },
        submit_order: function(question_id, images_order) {
            let ajax_options = {
                type: 'POST',
                url: 'api/questions/' + question_id,
                accepts: 'text/plain',
                contentType: 'application/json',
                dataType: 'text',
                data: JSON.stringify(images_order)
            };
            $.ajax(ajax_options)
            .done(function(data) {
                $event_pump.trigger('model_submit_order_success', [data]);
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

    let $question_id = "";
    let $image_ids = []
    let $current_index = 0;

    // return the API
    return {
        update_question_id: function(question_id){
            $question_id = question_id;
        },
        get_image_order: function(){
            let result = {}
            for (const index of $image_ids){
                var listItem = document.getElementById(index);
                result[index] = $("li").index(listItem);
            }
            return [$question_id, result];
        },
        build_sequence: function(image_id, content) {
            $image_ids.push(image_id);
            let sequence = '<li id="' + image_id + '" class="ui-state-default"><img src="data:image/jpg;base64, ' + content + '"/></li>';
            $('.single-question > .images > .image-sequence').append(sequence);
        },
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
        model.create_new_question();
    }, 100)

    // Validate input
    function validate(question_id) {
        return question_id !== ""
    }

    // Create our event handlers
    $('.save-button').click(function(e) {
        console.log('button clicked')
        let result = view.get_image_order();
        console.log("QuestionId=" + result[0]);
        console.log("ImageOrder=" + JSON.stringify(result[1]));
        model.submit_order(result[0], result[1]);
    });

    $event_pump.on('model_submit_order_success', function(e, data) {
        console.log(data);
    });

    // Handle the model events
    $event_pump.on('model_get_images_ids_success', function(e, data) {
        console.log(data);
        let images = {};

        for (var i = 0; i < data.length; i++) {
            images[data[i]] = model.get_image(data[i]);
        }
    });

    $event_pump.on('model_get_image_success', function(e, image_id, data) {
        view.build_sequence(image_id, data);
    });

    $event_pump.on('model_create_new_question_success', function(e, data) {
        view.update_question_id(data);
        model.get_images_ids(data);
    });

    $event_pump.on('model_error', function(e, xhr, textStatus, errorThrown) {
        let error_msg = textStatus + ': ' + errorThrown + ' - ' + xhr.responseJSON;
        view.error(error_msg);
        console.log(error_msg);
    })
}(ns.model, ns.view));