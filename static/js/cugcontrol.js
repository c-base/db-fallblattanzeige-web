"use strict";

var socket = io('http://' + document.domain + ':' + location.port);

socket.on('connect', function() {
    console.log('connecting..');
});

socket.on('connected', function() {
    console.log('connection established!');
    socket.emit('resetme', {});
});

socket.on('reset', function (json) {
    console.log('got reset. refreshing stuff..');
    var labels = json['labels'];
    console.log(json);
    $("select[data-address]").each(function(i, el) {
        var address = $(el).attr('data-address');
        var sel = el.selectize;
        sel.clearOptions();
        for (var i=0; i < labels[address].length; i++) {
	        var label = labels[address][i];
	        if(label.label != '') {
                sel.addOption({'value': label.index, 'text': label.label});
	        }
        }
        // refresh the select
        sel.refreshOptions(false);
    });
    socket.emit('updateme', {});
});

socket.on('update', function(json) {
    console.log('got update. refreshing stuff..');
    console.log(json);
    var status = json['status'];
    var hostname = json['hostname'];
    var form = $("form[data-hostname='"+ hostname +"']");
    $.each(status, function(i, el) {
        var address = el.address;
        if (address == 'ww') {
            var value = Math.round(el.value/255 * 100);
            $(form).find("input[data-address='" + address + "']").slider('setValue', value);
            return;
        }
        else if (address == 'rgb') {
            var value = el.value;
            $(form).find("input[data-address='" + address + "']").val(value);
	        $(form).find(".bluebox").css('color', value);
            return;
        }
        var value = el.current_page;
        $(form).find("select[data-address='" + address + "']").each(function(i, el) {
		    var sel = el.selectize;
        	sel.addItem(value, true);
        	sel.refreshItems();
	    });
    });
    
    $("#position").html(json.position);
    var pl_html = '';
    $.each(json.playlist, function(i, line) {
        pl_html = pl_html + JSON.stringify(line) + '\n';
    });
    $('#playlist').val(pl_html);
    if (json.mode === 'workshop' || json.mode === "shuffle" ) {
    	$('#playlist').prop("disabled", false);
    }
    else {
    	$('#playlist').prop("disabled", true);
    }

    $('#' + json.mode).closest('label').button('toggle');
    console.log(status);
});

$('#home').click(function () {
    console.log('sending homing command');
    socket.emit('home', {'data': null});
});

$('#reset').click(function () {
    console.log('sending reset command');
    socket.emit('reset', {'data': null});
});

var form_to_object = function(enclosing_form) {
    var data = {};
    data['hostname'] = $(enclosing_form).attr('data-hostname');
    console.log('sending new status for left sign to hostname ' + data.hostname);
    $(enclosing_form).find("select[data-address]").each(function(i, el) {
        var address = $(el).attr('data-address');
        var sel = el.selectize;
        var value = sel.getValue();
        data[address] = value;
    });
    $(enclosing_form).find("input[data-address]").each(function(i, el) {
        data[$(el).attr("data-address")] = $(el).val();
    });
    return data; 
};

$('.apply-btn').click(function (event) {
    event.preventDefault();
    var enclosing_form = $(event.target).closest("form");
    var data = form_to_object(enclosing_form);
    console.log(data);
    socket.emit('changeme', data);
    return false;
});

$("#expert-btn").click(function(ev) {
    ev.preventDefault();
    $("#expert-mode").toggle(400);
    return false;
});

var updatePlaylist = function() {
    var lines = $("#playlist").val().split('\n');
    var new_playlist = [];
    $.each(lines, function(i, el) {
	if(el === "")
	    return;
	new_playlist.push(JSON.parse(el));
    });	
    var data = { playlist: new_playlist};
    socket.emit('playlist', data);
}

$("#playlist-save-btn").click(function(ev) {
    ev.preventDefault();
    updatePlaylist();
    return false;
});

$("#playlist-clear-btn").click(function(ev) {
    ev.preventDefault();
    $("#playlist").val('');
    return false;
});

$("#playlist-append-btn").click(function(ev) {
    ev.preventDefault();
    var line = '[';
    $('form[data-hostname]').each(function(i, form) {
    	var data = form_to_object(form);
	if (i > 0) {
	    line = line + ',';
	}
	line = line + JSON.stringify(data);
    });
    line = line + ']\n';
    var new_val = $("#playlist").val() + line;
    $("#playlist").val(new_val);
    return false;
});

$(".mode-btn").click(function(ev) {
    ev.preventDefault();
    var data ={"mode": $(ev.target).find('input').attr('id'), 'bla': "blablubfasellaberrababer", 'broempf': 1234569};
    socket.emit('mode', data);
    return false;
});


