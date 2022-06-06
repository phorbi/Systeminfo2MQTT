
# Kurzanleitung:

### Vorbereitung
- Ich habe mein FHEM auf einem debian Server (Raspian sollte gleich funktionieren)
- Ich betreibe einen Mosquitto Broker auf meinem FHEM Server nähere dazu findet ihr hier
https://mosquitto.org/download/]https://mosquitto.org/download/
- Auf dem Server habe ich Python3.7 (ältere Pythons gehen unter umständen nicht wegen psutil) installiert um die Skripte laufen zu lassen
<code>sudo apt install python3</code>
- Außerdem kann es sein, das pip (zum installieren von Python3 packages) benötigt wird  
<code>sudo apt install python3-pip</code>
- Es werden folgende libraries/packages gebraucht:   
https://pypi.org/project/paho-mqtt  
<code>sudo python3 -m pip install paho-mqtt</code>  
und  
https://github.com/giampaolo/psutil   
<code>sudo python3 -m pip install psutil</code>


Systinfo2MQTT.py sendet die über psutil geholten Daten auf dem MQTT Broker.
der MQTT Broker muss dort zunächst entsprechend in Zeile 26 und 27 vorkonfiguriert werden.


- Ich habe das Skript bei mir auf meinem FHEM Server (debian) unter <code>/usr/bin/Sysinfo2MQTT</code>abgelegt
- Ich habe die Dateien executable gemacht (hier bin ich wie gewohnt mit der bazooka vorgegangen):   
<code>sudo chmod 777 /usr/bin/Sysinfo2MQTT/Sysinfo2MQTT.py</code>  
(Das geht ggf. auch etwas eleganter).
- Um Sysinfo2MQTT nun automatisch mit dem Systemd laufen zu lassen, muss in <code>/etc/systemd/system</code> eine Datei <code>Sysinfo2MQTT.service</code> angelegt werden.   
Inhalt:  
<code>
[Unit]  
Description=Systeminfo to MQTT Bridge  
Wants=network.target  
After=network.target  
[Service]  
Type=simple  
User=[TRAGT HIER EUREN USER EIN]  
Group=[TRAGT HIER DIE GRUPPE DES USERS EIN]  
ExecStart=/usr/bin/python3 /usr/bin/Sysinfo2MQTT/Sysinfo2MQTT.py  
Restart=always  
RestartSec=3  
[Install]  
WantedBy=multi-user.target</code>  

Hinweis, in den Zeilen User und Group müsst ihr euren Linux oder Raspian user eintragen (also z.B. User=pi, Group=pi)

Die Datei muss ebenfalls ausführbar gemacht werden.  
<code>sudo chmod 777 /etc/systemd/system/Sysinfo2MQTT.service</code>

Ich bin mir nicht mehr ganz sicher, aber es könnte sein, dass man dann erst mal mit  
<code>sudo systemctl start Sysinfo2MQTT</code>  
den Dienst erstmalig starten muss.  
Damit der service auch bei einem Neustart automatisch geladen wird müsst ihr den dienst enablen  
<code>sudo systemctl enable Sysinfo2MQTT</code>

Nutzen und Modifizieren ist erlaubt. Wer verbessert muss teilen! 


### Nutzung
Sysinfo2MQTT sendet auf Topics, die sich wiefolgt zusammensetzen:  
<code>server/[NAME DES RECHNERS]/</code>  

####Basisinfo
- <code>server/[NAME DES RECHNERS]/UpdateInterval INT</code> Updateintervall in sekunden
- <code>server/[NAME DES RECHNERS]/bootTime STR</code> Timestamp des letzten boots des Systems
- <code>server/[NAME DES RECHNERS]/[DEVICE]/fstype STR</code> file system type der es devices
- <code>server/[NAME DES RECHNERS]/[DEVICE]/totalSizeGB FLOAT</code> totale größe des devices in GB
- <code>server/[NAME DES RECHNERS]/[DEVICE]/usedGB FLOAT</code> verwendeter Speicher des devices in GB
- <code>server/[NAME DES RECHNERS]/[DEVICE]/freeGB FLOAT</code> freier Speicher  des devices in GB
- <code>server/[NAME DES RECHNERS]/[DEVICE]/usedPCT FLOAT</code> belegung des devices in %  

Auf dem Topic <code>server/[NAME DES RECHNERS]/control/UpdateInterval INT</code> könnt ihr das Updateintervall einstellen.
Ich empfehle Werte zwischen 20 und 90.  

**ACHTUNG**: Ich habe hier keine Fehlerbehandlung drin. Ich habe auch nie getestet was mit Werten <1 oder >60 oder gar nichtnumerischen Daten passiert.
Also wie immer auch hier: Benutzung auf eigene Gefahr.
