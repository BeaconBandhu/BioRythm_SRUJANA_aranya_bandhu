#include <WiFi.h>
#include <AsyncTCP.h>
#include <ESPAsyncWebServer.h>

const char* ssid = "Hardik";
const char* password = "hardik12345";

#define ECG_PIN 34   // Connect AD8232 OUTPUT to GPIO34 (ADC1)

// Create Async Web Server
AsyncWebServer server(80);

// Webpage with Chart.js
const char index_html[] PROGMEM = R"rawliteral(
<!DOCTYPE html>
<html>
<head>
  <title>ECG Monitor</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
  <h2 style="text-align:center;">Real-time ECG Graph</h2>
  <canvas id="ecgChart" width="100%" height="60"></canvas>
  <script>
    var ctx = document.getElementById('ecgChart').getContext('2d');
    var ecgChart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: [],
        datasets: [{
          label: 'ECG Signal',
          data: [],
          borderColor: 'red',
          borderWidth: 1,
          fill: false,
          pointRadius: 0
        }]
      },
      options: {
        responsive: true,
        animation: false,
        scales: {
          x: { display: false },
          y: { suggestedMin: 0, suggestedMax: 4095 }
        }
      }
    });

    async function fetchData() {
      const response = await fetch('/ecg');
      const value = await response.text();
      ecgChart.data.labels.push('');
      ecgChart.data.datasets[0].data.push(value);
      if (ecgChart.data.labels.length > 200) {
        ecgChart.data.labels.shift();
        ecgChart.data.datasets[0].data.shift();
      }
      ecgChart.update();
    }
    setInterval(fetchData, 50); // fetch every 50ms
  </script>
</body>
</html>
)rawliteral";

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi...");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nConnected! IP: ");
  Serial.println(WiFi.localIP());

  // Route for ECG data
  server.on("/ecg", HTTP_GET, [](AsyncWebServerRequest *request){
    int ecgValue = analogRead(ECG_PIN);
    request->send(200, "text/plain", String(ecgValue));
  });

  // Route for webpage
  server.on("/", HTTP_GET, [](AsyncWebServerRequest *request){
    request->send_P(200, "text/html", index_html);
  });

  server.begin();
}

void loop() {
}
