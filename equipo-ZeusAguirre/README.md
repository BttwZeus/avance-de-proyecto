# Sistema de Reservas para Espacios de Trabajo
**TechNova Solutions — Dominio 1**

Desarrollado por: Zeus Ramirez

## Descripción
Sistema backend para gestionar reservas de salas en oficinas compartidas. Permite registrar salas, hacer reservas, consultar las del día y cancelarlas. Al confirmar una reserva simula el envío de un correo de confirmación con un proceso que tarda 6 segundos.

## Tecnologías
- **Backend**: Python 3.11 + Flask
- **Base de Datos**: MySQL en AWS RDS
- **Contenedor**: Docker
- **Infraestructura**: AWS EC2

## Estructura del proyecto
```
technova-reservas/
├── app.py                      # Aplicación Flask principal
├── requirements.txt            # Dependencias Python
├── Dockerfile                  # Configuración del contenedor
├── schema.sql                  # Script de creación de BD
├── evidencias/                 # Capturas de pantalla
│   ├── 01_rds_tablas.png
│   ├── 02_docker_build.png
│   ├── 03_contenedor_corriendo.png
│   ├── 04_interfaz_navegador.png
│   ├── 05_registro_exitoso.png
│   ├── 06_consulta_datos.png
│   └── 07_tarea_pesada.png
└── README.md
```

## Características Implementadas

### Base de Datos (RDS MySQL)
- ✅ 3 tablas con relaciones: `usuarios`, `salas`, `reservas`
- ✅ Llaves foráneas entre tablas
- ✅ Datos de ejemplo precargados

### Aplicación Flask
- ✅ 7 rutas HTTP funcionales (GET y POST)
- ✅ Interfaz HTML funcional y responsive
- ✅ Tarea pesada con `time.sleep(6)` que simula envío de correo
- ✅ Manejo de errores con try/except en todas las rutas
- ✅ Cierre apropiado de conexiones (bloque finally)
- ✅ Consultas SQL parametrizadas (sin concatenación)
- ✅ Código comentado

### Rutas Disponibles
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/` | Página de inicio |
| GET | `/salas` | Lista todas las salas disponibles |
| GET/POST | `/sala/nueva` | Registrar una nueva sala |
| GET | `/reservas/hoy` | Consulta reservas activas del día |
| GET/POST | `/reservar` | Crear una nueva reserva (con tarea pesada) |
| GET/POST | `/cancelar` | Cancelar una reserva existente |
| GET | `/api/reservas` | API JSON con todas las reservas |

### Contenedor Docker
- ✅ Dockerfile funcional
- ✅ Variables de entorno para credenciales
- ✅ Desplegado en EC2
- ✅ Accesible desde navegador público

## Instalación y Despliegue

### Prerrequisitos
- Cuenta de AWS
- RDS MySQL configurado
- EC2 con Docker instalado

### Paso 1: Crear la base de datos en RDS
```bash
mysql -h TU_ENDPOINT_RDS -u admin -p < schema.sql
```

### Paso 2: Construir la imagen Docker
```bash
docker build -t technova-reservas .
```

### Paso 3: Ejecutar el contenedor
```bash
docker run -d \
  -p 5000:5000 \
  -e DB_HOST="tu-endpoint.rds.amazonaws.com" \
  -e DB_USER="admin" \
  -e DB_PASSWORD="tu_password" \
  -e DB_NAME="technova_reservas" \
  --name reservas \
  technova-reservas
```

### Paso 4: Acceder a la aplicación
Abre en tu navegador: `http://TU_IP_EC2:5000`

## Variables de Entorno
Las credenciales de base de datos se pasan como variables de entorno al contenedor:
- `DB_HOST`: Endpoint del RDS
- `DB_USER`: Usuario de MySQL
- `DB_PASSWORD`: Contraseña de MySQL
- `DB_NAME`: Nombre de la base de datos
- `DB_PORT`: Puerto (por defecto 3306)

**⚠️ Nunca subir credenciales reales al repositorio**

## Comandos Útiles

Ver logs del contenedor (incluye la tarea pesada):
```bash
docker logs -f reservas
```

Reiniciar el contenedor:
```bash
docker restart reservas
```

Verificar tablas en la BD:
```bash
mysql -h TU_ENDPOINT -u admin -p -e "USE technova_reservas; SHOW TABLES;"
```

## Evidencias
Las capturas de pantalla que demuestran el funcionamiento completo del sistema se encuentran en la carpeta `evidencias/`.

## Autor
Zeus Ramirez - TechNova Solutions Challenge 2026
