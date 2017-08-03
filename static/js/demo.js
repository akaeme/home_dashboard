var g1;
window.onload = function(){
    g1 = new JustGage({
      id: "g1",
      value: 0,
      min: 0,
      max: 45,
      label: "Celsius",
      levelColors: [
          "#00fff6",
          "#ff00fc",
          "#1200ff"
        ],
      gaugeWidthScale: 0.2
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

