var g1;
window.onload = function(){
    g1 = new JustGage({
      id: "g1",
      value: 20,
      min: 0,
      max: 100,
      label: "celsius"
    });
};
var socket = io.connect('http://' + document.domain + ':' + location.port);
socket.on('connect', function() {
    console.log('Sent message');
    socket.emit('start', 'Connected')
    //socket.send('User has connected!');
});
socket.on('values', function(data) {
    console.log(data);
    g1.refresh(data['temperature']);
});

