var g = new JustGage({
    id: "gauge",
    value: 25,
    min: 0,
    max: 100,
    title: "Temperature"
});
var socket = io.connect('http://' + document.domain + ':' + location.port);
socket.on('connect', function() {
    console.log('Sent message');
    socket.emit('start', 'Connected')
    //socket.send('User has connected!');
});
socket.on('values', function(data) {
    console.log(data);
    g.refresh(data['temperature']);
});

