---
layout: post
title: "Path Traversal - Portswigger"
categories: Hacking-web/Portswigger
---

<p align="center">
<img src="https://portswigger.net/public/Logos/Light/portswigger-200h.png">
</p>

>Path traversal es una vulnerabilidad donde un atacante manipula una ruta de archivo para salir del directorio permitido y acceder a archivos que no debería.

## Lab: File path traversal, simple case

- Vamos a capturar la petición en la cual abramos una imagen cualquiera en otra ventana.
  
>En path traversal, un atacante usa muchos ../ para salirse de la carpeta permitida y llegar a archivos sensibles.

![](/assets/PathTraversal/1.png)

- Abusamos de la falta de validación para escalar directorios utilizando secuencias ‘../‘.

![](/assets/PathTraversal/2.png)

## Lab: File path traversal, traversal sequences blocked with absolute path bypass

- Volvemos a capturar la petición en la cual abramos una imagen cualquiera en otra ventana.

- Al modificar el parámetro filename e indicar directamente **/etc/passwd**, logramos leer el contenido del archivo, demostrando que el filtrado es insuficiente y que no hay validación sobre rutas absolutas.

![](/assets/PathTraversal/3.png)

## Lab: File path traversal, traversal sequences stripped non-recursively

- Volvemos a capturar la petición en la cual abramos una imagen cualquiera en otra ventana.

- La aplicación intenta mitigar el path traversal eliminando las secuencias ‘**../**‘, pero lo hace de forma no recursiva. Esto permite evadir el filtro usando variantes como ‘**….//**‘, que tras la normalización del sistema de archivos siguen interpretándose como una subida de directorio. Usando ‘**….//….//etc/passwd**‘, logramos acceder a archivos sensibles como ‘**/etc/passwd**‘.

- El filtro valida texto, el sistema operativo interpreta rutas, `//` → Linux lo interpreta igual que `/`).

![](/assets/PathTraversal/4.png)

## Lab: File path traversal, traversal sequences stripped with superfluous URL-decode

>La aplicación bloquea de forma directa las secuencias ../, sin embargo, comete el fallo de decodificar la entrada una vez adicional después del filtrado. Aprovechando este comportamiento, se utiliza ..%252f, que tras ser decodificado en dos ocasiones termina convirtiéndose en ../, lo que permite ejecutar un path traversal con éxito. Mediante esta técnica fue posible acceder al archivo /etc/passwd, demostrando cómo una decodificación extra puede dar lugar a vulnerabilidades críticas.

- Volvemos a capturar la petición en la cual abramos una imagen cualquiera en otra ventana.

- Vamos aplicar un URL-ENCODE a los **/** para que quede algo asi:

```bash
GET /image?filename=..%2f..%2f..%2f..%2f..%2f..%2f..%2fetc/passwd HTTP/2
```

- URL ENCODE a los %: (Una vez url decodea el % se queda con un %2f lo cual significa una / y asi hacemos un bypass y podemos apuntar directo al archivo).

```bash
GET /image?filename=..%252f..%252f..%252f..%252f..%252f..%252f..%252fetc/passwd
```

![](/assets/PathTraversal/5.png)

## Lab: File path traversal, validation of start of path

- Volvemos a capturar la petición en la cual abramos una imagen cualquiera en otra ventana.

-  En este caso, la aplicación verifica únicamente que la ruta comience con /var/www/images/, pero no controla correctamente el contenido posterior. Esto permite enviar una ruta como /var/www/images/https://miguelonches/../etc/passwd, que al resolverse finalmente termina accediendo a un archivo sensible fuera del directorio autorizado. Este ejemplo muestra cómo una validación superficial del inicio del path puede ser fácilmente eludida mediante el uso de secuencias de retroceso (../).

```bash
GET /image?filename=/var/www/images/../../../../../../etc/passwd HTTP/2
```

![](/assets/PathTraversal/6.png)

## Lab: File path traversal, validation of file extension with null byte bypass

- Volvemos a capturar la petición en la cual abramos una imagen cualquiera en otra ventana.

- La aplicación intenta garantizar que los archivos solicitados terminen en .png, pero no tiene en cuenta el uso del byte nulo (%00). Este carácter indica el final de una cadena para muchas funciones en lenguajes como C, por lo que al enviar una ruta como https://miguelonches/../etc/passwd%00.png, el servidor interpreta únicamente la parte anterior al %00 y accede al archivo /etc/passwd, aun cuando la validación de la extensión parece cumplirse.

![](/assets/PathTraversal/7.png)
