var g1, g2;
window.onload = function(){
    g1 = new JustGage({
      id: "g1",
      value: 0,
      min: 0,
      max: 45,
      label: "Celsius",
      levelColors: [
          "#F2B2F4",
          "#99C7FC",
          "#9FF2A1",
          "#F7D274",
          "#EF7A7A"
        ],
      gaugeWidthScale: 0.3
    });
    g2 = new JustGage({
      id: "g2",
      value: 0,
      min: 0,
      max: 100,
      label: "Percent",
      levelColors: [
          "#DBCFB0",
          "#BFC8AD",
          "#90B494",
          "#718F94",
          "#545775"
        ],
      gaugeWidthScale: 0.3
    });
};
var socket = io.connect('http://' + document.domain + ':' + location.port);
socket.on('connect', function() {
    console.log('Sent message');
    socket.emit('start', 'Connected')
    //socket.send('User has connected!');
});
socket.on('values', function(data) {
    g1.refresh(data['temperature']);
    g2.refresh(data['humidity']);
});

