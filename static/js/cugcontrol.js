"use strict";

var socket = io.connect('http://' + document.domain + ':' + location.port);

socket.on('connect', function() {
    console.log('connecting..');
});

socket.on('connected', function() {
    console.log('connection established!');
    socket.emit('resetme');
});

socket.on('reset', function(json) {
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
        $("#" + leaf).val(leafdata);
    });
    // TODO: update LED controls
});

$('#homing').submit(function(event) {
    id = $('#homeSingleSelect').val();
    if(id >= 0 && id <= 5) {
        console.log('homing leave ' + id);
        socket.emit('home', {'data': id});
    }
    event.preventDefault();
});

$('#homeAll').click(function() {
    console.log('homing all leaves');
    socket.emit('home', {'data': 'all'});
});

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