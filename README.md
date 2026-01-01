This code queries the LoRa MeshCom board via serial, reads the temperature and humidity values ​​from the BME280 sensor (which must be connected to the board's I2C bus), and sends them as messages to the network.<br><br>
![](https://github.com/ik5xmk/mc_meteo_bme280/blob/main/meteo_bme280_output.jpg)<br><br>
It's written in Python and must run on a Raspberry Pi or mini-PC directly connected to the LoRa board.<br>
Install the necessary libraries ("pip" command) and run it, preferably with a cron schedule. One possible use case is to monitor the temperature at a high-altitude location where our radio systems are located and receive the information via RF over the MeshCom network.<br><br>
![](https://github.com/ik5xmk/mc_meteo_bme280/blob/main/meteo_bme280_message.jpg)<br><br>
The output values ​​handled by the code are temperature and humidity, but other measurements such as pressure, etc. can easily be handled with small changes and additions to the program.<br>
By doing a web search you can easily find the pinout of the board you are using. And the I2C bus to which you can connect the BME280 sensor (or similar) with simple soldering.<br>
Please refer to the official MeshCom documentation for possible future changes to the commands to send to the lora board.<br>
<br>
![](https://github.com/ik5xmk/mc_meteo_bme280/blob/main/mc_meteo_bme280_http_bot.jpg)
</br><br>
The mc_meteo_bm280_http code instead acquires sensor values ​​via Wi-Fi. The MeshCom LoRa card must be connected to Wi-Fi (see any router configurations if the code is not running on the same LAN as the lora card) and have the "<strong>--extudp on</strong>" command enabled to allow data reception (UDP port 1799) and transmission as a message via RF. This procedure is similar to the code that manages the card via USB, but can be convenient if there are multiple cards with related BME280 sensors and a single server where the program runs. The configurations relating to the card's IP, the sending group, etc. can be made directly by editing the code. If changes are made to the card's WX page layout in the future, these will also need to be managed in the search section of the code.<br><br>
![](https://github.com/ik5xmk/mc_meteo_bme280/blob/main/mc_meteo_bme280_http.jpg)
