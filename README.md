This code queries the LoRa MeshCom board via serial, reads the temperature and humidity values ​​from the BME280 sensor (which must be connected to the board's I2C bus), and sends them as messages to the network.<br><br>
![](https://github.com/ik5xmk/mc_meteo_bme280/blob/main/meteo_bme280_output.jpg)<br><br>
It's written in Python and must run on a Raspberry Pi or mini-PC directly connected to the LoRa board.<br>
Install the necessary libraries ("pip" command) and run it, preferably with a cron schedule. One possible use case is to monitor the temperature at a high-altitude location where our radio systems are located and receive the information via RF over the MeshCom network.<br><br>
![](https://github.com/ik5xmk/mc_meteo_bme280/blob/main/meteo_bme280_message.jpg)<br><br>
The output values ​​handled by the code are temperature and humidity, but other measurements such as pressure, etc. can easily be handled with small changes and additions to the program.<br>
By doing a web search you can easily find the pinout of the board you are using. And the I2C bus to which you can connect the BME280 sensor (or similar) with simple soldering.<br>
Please refer to the official MeshCom documentation for possible future changes to the commands to send to the lora board.<br>
