#include <ESP8266WiFi.h>
#include <PubSubClient.h>

// 設定無線基地台SSID跟密碼
const char* ssid     = "JWS_Mobile";
const char* password = "149597870700";

// 設定樹莓派 MQTT Broker 的 IP
//const char* mqtt_server = "192.168.51.191";
IPAddress mqtt_server(192, 168, 98, 65);//MQTT server IP

// 初始化 espClient.
WiFiClient espClient;
PubSubClient client(espClient);

// ESP8266 重新連接到 MQTT Broker 
void reconnect()
{
  // 持續迴圈直到連線
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    if(client.connect("ESP8266Client"))
    {
      Serial.println("connected");  
    }
    else
    {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  
  /* wireless SETUP*/
  // 連接無線網路
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED)
  {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.print("WiFi connected - ESP IP address: ");
  Serial.println(WiFi.localIP());

// 設定 mqtt server 及連接 port
  client.setServer(mqtt_server, 1883);
}

void loop()
{
  if(!client.connected()) reconnect();
  if(!client.loop()) client.connect("ESP8266Client");
  static char temp[20];
  //sprintf(temp, "%anchor_1:08d", millis());
  sprintf(temp, "%anchor_2:08d", millis());
  // Publishes Test msg
  Serial.println(millis());
  client.publish("main/test", temp);
  delay(20);
} 
