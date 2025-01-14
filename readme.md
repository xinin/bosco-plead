# BOSCO & PLEAD

Este repositorio contiene el entorno necesario para emular el flujo de un sistema de solicitud de bono social entre diferentes actores: una **compañía eléctrica**, el **gobierno** y una **cola de procesamiento** utilizando Docker.

## Levantar el entorno con Docker

Para levantar el entorno completo, utiliza el siguiente comando en tu terminal:

```bash
docker-compose up --build
```

Este comando construye y levanta las tres instancias necesarias para la simulación:

1. Instancia electric_company:

Emula los sistemas de la compañía eléctrica que gestionan las solicitudes de bono social. Los usuarios pueden iniciar una solicitud y consultar el estado de la misma.
Proporciona un frontend accesible en http://localhost:8080 para interactuar con la aplicación y ejecutar las pruebas.
Permite ver el estado de la solicitud y el provenance de la misma.

2. Instancia bosco:

Emula los sistemas gubernamentales encargados de recibir la información de las compañías eléctricas, cruzarla con datos fiscales (Hacienda) y tomar la decisión sobre si el solicitante es elegible o no para el bono social.
Una vez tomada la decisión, envía el resultado de vuelta a la compañía eléctrica.

3. Instancia redis:

Emula una cola de procesamiento que maneja las solicitudes entre las distintas instancias.
Es utilizado para gestionar las tareas entre la compañía eléctrica y el gobierno de forma asíncrona.

## Comandos útiles para interactuar con Redis

Para interactuar con la instancia de Redis, utiliza los siguientes comandos desde la línea de comandos.

1. Acceder al cliente de Redis:
```bash
redis-cli -h localhost -p 6379
```

2. Ver los primeros 10 elementos de la cola:
```bash
redis-cli LRANGE task_queue 0 10
```

3. Ver todos los elementos en la cola:
```bash
redis-cli LRANGE task_queue 0 -1
```

4. Consumir el primer mensaje de la cola:
```bash
redis-cli LPOP task_queue
```

5. Consumir el ultimo mensaje de la cola:
```bash
redis-cli RPOP task_queue
```

6. Eliminar todos los mensajes de la cola:
```bash
redis-cli DEL task_queue
```
