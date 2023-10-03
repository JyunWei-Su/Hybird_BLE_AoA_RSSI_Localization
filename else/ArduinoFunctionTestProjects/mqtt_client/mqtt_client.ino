#include <ESP8266WiFi.h>
#include <PubSubClient.h>


// 設定無線基地台SSID跟密碼
const char* ssid     = "XPLR-AOA";
const char* password = "12345678";

// 設定樹莓派 MQTT Broker 的 IP
const char* mqtt_server = "192.168.51.174";

// 初始化 espClient.
WiFiClient espClient;
PubSubClient client(espClient);


// 當設備發訊息給一個標題(topic)時，這段函式會被執行
void callback(String topic, byte* message, unsigned int length) {
  Serial.print("Message arrived on topic: ");
  Serial.print(topic);
  Serial.print(". Message: ");
  String messageTemp;
  
  for (int i = 0; i < length; i++) {
    Serial.print((char)message[i]);
    messageTemp += (char)message[i];
  }
  Serial.println();

  // 假使收到訊息給主題 room/lamp, 可以檢查訊息是 on 或 off. 根據訊息開啟 GPIO
  if(topic == "anchor/restart"){
      Serial.print("Receive restart");
      ESP.restart();
  }
  else if (topic == "anchor/online-check"){
    client.publish("anchor/online-check-response", "ANCHOR_ID");
  }
  
  Serial.println();
}

// ESP8266 重新連接到 MQTT Broker 
void reconnect() {

  // 持續迴圈直到連線
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    if (client.connect("ESP8266Client")) {
      Serial.println("connected");  
      // 訂閱一個主題，可以設定多個主題
      client.subscribe("anchor/restart");
      client.subscribe("anchor/online-check");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  
  // 連接無線網路
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.print("WiFi connected - ESP IP address: ");
  Serial.println(WiFi.localIP());

// 設定 mqtt server 及連接 port
  client.setServer("xplr-aoa.local", 1883);

// 設定 mqtt broker 並設定 callback function
  client.setCallback(callback);
}

void loop() {

  if (!client.connected()) {
    reconnect();
  }
  if(!client.loop())
    client.connect("ESP8266Client");
}
