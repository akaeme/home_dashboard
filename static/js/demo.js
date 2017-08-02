var socket = io.connect('http://' + document.domain + ':' + location.port);
socket.on('connect', function() {
    console.log('Sent message');
    socket.emit('start', 'Connected')
    //socket.send('User has connected!');
});
socket.on('message', function(msg) {
    console.log(msg);
});