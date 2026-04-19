# Sistema de Reservas para Espacios de Trabajo
**Equipo:** Zeus Samael Aguirre Martinez  
**Dominio:** Sistema de Reservas para Espacios de Trabajo  
**Fecha:** Abril 2026

---

## ¿Qué problema resuelve?

TechNova Solutions necesita un sistema para gestionar reservas de salas en oficinas compartidas. El sistema permite:
- Registrar salas disponibles con su capacidad y ubicación
- Hacer reservas de salas por fecha y horario
- Consultar las reservas activas del día
- Cancelar reservas existentes
- Simular el envío de confirmaciones por correo (proceso costoso)

---

## Estructura de la Base de Datos

| Tabla | Descripción | Relación |
|-------|-------------|----------|
| **usuarios** | Almacena los usuarios que pueden hacer reservas | - |
| **salas** | Guarda información de las salas disponibles (nombre, capacidad, ubicación) | - |
| **reservas** | Registra las reservas realizadas con fecha y horario | Se relaciona con `usuarios` (usuario_id) y `salas` (sala_id) mediante llaves foráneas |

**Relaciones:**
- `reservas.usuario_id` → `usuarios.id` (FK)
- `reservas.sala_id` → `salas.id` (FK)

---

## Rutas de la API

| Método | Ruta | Qué hace |
|--------|------|----------|
| GET | `/` | Interfaz principal - Página de bienvenida |
| GET | `/salas` | Lista todas las salas disponibles |
| POST | `/sala/nueva` | Registra una nueva sala en el sistema |
| GET | `/reservas/hoy` | Consulta las reservas activas del día actual |
| POST | `/reservar` | Crea una nueva reserva (ejecuta tarea pesada) |
| POST | `/cancelar` | Cancela una reserva existente |
| GET | `/api/reservas` | Retorna todas las reservas en formato JSON |

---

## ¿Cuál es la tarea pesada y por qué bloquea el sistema?

**La tarea pesada es:** Simular el envío de un correo de confirmación cuando se crea una reserva.

**Dónde está en el código:** En la función `hacer_reserva()` del archivo `app.py`, después de insertar la reserva en la base de datos:

```python
print(f"[TAREA PESADA] Iniciando envío de confirmación para reserva #{reserva_id}...")
time.sleep(6)  # Simula proceso costoso
print(f"[TAREA PESADA] Correo enviado a {email} para reserva #{reserva_id}")
```

**Por qué bloquea:** El `time.sleep(6)` detiene la ejecución del hilo durante 6 segundos, simulando un proceso real como:
- Conectarse a un servidor SMTP
- Autenticarse
- Enviar el correo
- Esperar confirmación

Durante esos 6 segundos, el navegador del usuario queda esperando la respuesta HTTP. Esto demuestra cómo una operación costosa puede afectar la experiencia del usuario si no se maneja adecuadamente (en producción se usarían colas de tareas como Celery).

---

## Cómo levantar el proyecto

### Paso 1: Clonar el repositorio
```bash
git clone [url]
cd [nombre-repositorio]
```

### Paso 2: Crear las tablas en RDS
```bash
mysql -h ENDPOINT_RDS -u admin -p < schema.sql
```

### Paso 3: Construir la imagen Docker
```bash
docker build -t technova-reservas .
```

### Paso 4: Correr el contenedor
```bash
docker run -d -p 5000:5000 \
  -e DB_HOST="ENDPOINT_RDS" \
  -e DB_USER="admin" \
  -e DB_PASSWORD="PASSWORD" \
  -e DB_NAME="technova_reservas" \
  --name reservas \
  technova-reservas
```

### Paso 5: Abrir en navegador
```
http://IP_EC2:5000
```

---

## Tecnologías Utilizadas

- **Backend:** Python 3.11 + Flask
- **Base de Datos:** MySQL en AWS RDS
- **Contenedor:** Docker
- **Infraestructura:** AWS EC2
- **Variables de Entorno:** Para credenciales seguras

---

## Evidencias

Las capturas de pantalla que demuestran el funcionamiento completo del sistema se encuentran en la carpeta `evidencias/`:

1. `01_rds_tablas.png` - Tablas creadas en MySQL
2. `02_docker_build.png` - Construcción de la imagen Docker
3. `03_contenedor_corriendo.png` - Contenedor en ejecución
4. `04_interfaz_navegador.png` - Interfaz web funcionando
5. `05_registro_exitoso.png` - Operación de inserción exitosa
6. `06_consulta_datos.png` - Consulta de datos guardados
7. `07_tarea_pesada.png` - Logs mostrando el time.sleep(6)

---

## Decisiones Técnicas

Durante el desarrollo del sistema se tomaron las siguientes decisiones técnicas:

**¿Por qué diseñaron las tablas así?**
- Se crearon 3 tablas separadas (`usuarios`, `salas`, `reservas`) siguiendo el principio de normalización de bases de datos para evitar redundancia de datos.
- La tabla `reservas` actúa como tabla intermedia que relaciona usuarios con salas, permitiendo un modelo flexible donde un usuario puede hacer múltiples reservas y una sala puede ser reservada por múltiples usuarios en diferentes horarios.
- Se agregó el campo `estado` en reservas para poder cancelar sin eliminar el registro histórico, manteniendo trazabilidad.

**¿Cómo manejaron los errores?**
- Se implementaron bloques `try/except/finally` en todas las rutas para capturar excepciones de base de datos, validaciones de formulario y errores inesperados.
- El bloque `finally` garantiza que las conexiones a la base de datos siempre se cierren, incluso si ocurre un error, evitando fugas de conexiones.
- Se muestran mensajes de error amigables al usuario en la interfaz (cuadros rojos) sin exponer detalles técnicos sensibles.
- Se validan los datos antes de insertarlos (campos vacíos, horarios lógicos, conflictos de reservas).

**¿Qué fue lo más difícil de implementar?**
- **La validación de conflictos de horarios:** Fue necesario crear una consulta SQL que detecte si una nueva reserva se solapa con reservas existentes. La lógica `NOT (hora_fin <= hora_inicio_nueva OR hora_inicio >= hora_fin_nueva)` requirió análisis cuidadoso para cubrir todos los casos de solapamiento.
- **La tarea pesada bloqueante:** Inicialmente los logs no aparecían en Docker. Se tuvo que configurar `PYTHONUNBUFFERED=1` y `python -u` en el Dockerfile para forzar la salida inmediata de los `print()`.
- **Manejo de variables de entorno:** Asegurar que las credenciales nunca se escribieran en el código y siempre se pasaran como variables de entorno al contenedor requirió atención especial en el flujo de despliegue.

---

## Autor

**Zeus Samael Aguirre Martinez**  
TechNova Solutions - Abril 2026
