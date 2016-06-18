"use strict";

var socket = io.connect('http://' + document.domain + ':' + location.port);

socket.on('connect', function() {
    console.log('connecting..');
});

socket.on('connected', function() {
    console.log('connection established!');
    socket.emit('resetme');
});

socket.on('update', function (json) {
    console.log('got update. refreshing stuff..')
    // TODO: refresh all controls
});

$('#home').click(function () {
    console.log('sending homing command');
    socket.emit('home', {'data': null});
});

$('#reset').click(function () {
    console.log('sending reset command');
    socket.emit('reset', {'data': null});
});

$('#signLeftGo').click(function () {
    console.log('sending new status for left sign');
    socket.emit('go', {'data': '{"drum": 0, "index": ' + $('lineLeft').val() + '}'});
    socket.emit('go', {'data': '{"drum": 1, "index": ' + $('destLeft').val() + '}'});
    socket.emit('go', {'data': '{"drum": 2, "index": ' + $('descLeft').val() + '}'});

    var rgbhex = $('#colorRGBLeft').val();
    var r = parseInt(rgbhex.substring(1, 3), 16);
    var g = parseInt(rgbhex.substring(3, 5), 16);
    var b = parseInt(rgbhex.substring(5, 7), 16);
    var ww = parseInt(255 * $('#colorWWLeft').val());
    socket.emit('light', {'data': '{"r": ' + r + ', "g": ' + g + ', "b": ' + b + ', "ww": ' + ww + '}'});
});

setTimeout(function () {
    socket.emit('poll');
}, 1000);


/*socket.on('reset', function(json) {
    console.log('resetting interface')
    $.each(json, function(leaf, leafdata) {
        $.each(leafdata, function (k, v) {
            var select = $("#" + leaf)[0].selectize;
            select.addOption({
                text: v,
                value: k
            });
            select.addItem(v)
        });
    });
});

socket.on('update', function (json) {
    console.log('updating interface');
    $.each(json, function(leaf, leafdata) {
        $('#' + leaf)[0].selectize.setValue(leafdata);
    });
    // TODO: update LED controls
});*/

/*
// handlers for the different forms in the page
// these send data to the server in a variety of ways
$('form#broadcast').submit(function(event) {
    socket.emit('broadcast', {data: $('#broadcast_data').val()});
    return false;
});
$('form#home').submit(function(event) {
    socket.emit('home', {data: {leave_id: $('#leave_id').val()}});
    return false;
});
$('form#disconnect').submit(function(event) {
    socket.emit('disconnect');
    return false;
});
$('form#connect').submit(function(event) {
    connect();
    return false;
});
*/