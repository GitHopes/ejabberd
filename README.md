# Ejabberd Automation Installer

Script de instalación y configuración automatizada de Ejabberd XMPP Server para Ubuntu 24.04.

## Características

✅ **Dual-Mode**: Interfaz gráfica (GUI) o línea de comandos (CLI)  
✅ **Instalación completa**: Dependencias, compilación y configuración  
✅ **Configuración personalizable**: Dominios, certificados TLS, base de datos  
✅ **Gestión de red sin DNS**: Configuración automática de `/etc/hosts`  
✅ **Servicio systemd**: Creación y activación automática  
✅ **Solo Python estándar**: No requiere paquetes externos

## Modos de Ejecución

### Modo GUI (Gráfico)

Si tienes entorno de escritorio con tkinter:

```bash
python3 ejabberd_installer.py
```

**Interfaz con:**
- Panel de configuración lateral con todos los parámetros
- Log en tiempo real con códigos de color
- 3 botones de acción: Instalación completa, Solo configurar, Solo certificado
- Barra de progreso animada

### Modo CLI (Terminal)

Para servidores sin entorno gráfico:

```bash
python3 ejabberd_installer.py --cli
```

o forzar CLI:

```bash
python3 ejabberd_installer.py --no-gui
```

**El script detecta automáticamente** si tkinter no está disponible y usa CLI.

**Menú interactivo:**
```
═══ MENÚ PRINCIPAL ═══

1. ⚙  Configurar parámetros
2. 👁  Ver configuración actual
3. ▶  Instalación completa (deps + compilar + configurar)
4. 🔧 Solo configurar (sin compilar)
5. 🔒 Solo generar certificado TLS
0. ✖  Salir
```

## Parámetros Configurables

| Parámetro | Descripción | Valor por defecto |
|-----------|-------------|-------------------|
| **Dominio principal** | Dominio XMPP principal | `my.lab.local` |
| **Dominio adicional** | Segundo dominio (opcional) | _(vacío)_ |
| **Common Name (CN)** | CN del certificado TLS | `my.lab.local` |
| **Validez certificado** | Días de validez del certificado | `365` |
| **Tipo de BD** | sqlite, pgsql o mysql | `sqlite` |
| **Ruta BD** | Ubicación de la base de datos | `/usr/local/ejabberd/var/lib/ejabberd/ejabberd.db` |
| **Configurar /etc/hosts** | Para entornos sin DNS | `No` |
| **IP del servidor** | IP para /etc/hosts | `127.0.0.1` |
| **Crear servicio systemd** | Gestión automática del servicio | `Sí` |
| **Activar servicio** | Habilitar al terminar instalación | `Sí` |
| **Aplicar permisos** | Configurar propietarios y permisos | `Sí` |

## Flujos de Trabajo

### 1. Instalación Completa

Ejecuta todos los pasos:

1. ✅ Instalación de dependencias del sistema
2. ✅ Clonación del repositorio ejabberd
3. ✅ Compilación desde código fuente
4. ✅ Creación del usuario `ejabberd`
5. ✅ Configuración de `/etc/hosts` (opcional)
6. ✅ Generación de `ejabberd.yml`
7. ✅ Creación de certificado TLS
8. ✅ Ajuste de permisos
9. ✅ Creación de servicio systemd

**Uso recomendado**: Primera instalación en servidor limpio.

### 2. Solo Configurar

Omite compilación, útil para:
- Actualizar configuración existente
- Cambiar dominios o certificados
- Re-generar archivos de configuración

### 3. Solo Certificado

Genera únicamente el certificado TLS `server.pem`:
- Útil cuando expira el certificado
- Para cambiar el Common Name
- Renovación periódica

## Archivos Generados

El script crea/modifica estos archivos:

```
/usr/local/ejabberd/etc/ejabberd/
├── ejabberd.yml              # Configuración principal
└── server.pem                # Certificado TLS + clave privada

/etc/systemd/system/
└── ejabberd.service          # Unit de systemd

/etc/hosts                    # (opcional) entrada del dominio

/home/$USER/ejabberd/         # Código fuente clonado

/usr/local/ejabberd/          # Instalación binaria
/var/lib/ejabberd/            # Datos y logs
```

## Requisitos del Sistema

- **OS**: Ubuntu 24.04 LTS (probado)
- **Python**: 3.10+ (incluido en Ubuntu 24.04)
- **Permisos**: Usuario con sudo
- **Espacio**: ~500 MB para compilación
- **Memoria**: 2 GB RAM mínimo recomendado
- **Red**: Acceso a internet para descargar paquetes

## Características Técnicas

### Configuración de ejabberd.yml

El archivo generado incluye:

- ✅ Múltiples dominios (hosts)
- ✅ Base de datos SQL (sqlite/pgsql/mysql)
- ✅ Puertos estándar: 5222 (C2S), 5269 (S2S), 5280/5443 (HTTP)
- ✅ TLS obligatorio para clientes
- ✅ Interfaz web de administración
- ✅ MAM (Message Archive Management)
- ✅ MUC (Multi-User Chat)
- ✅ HTTP Upload
- ✅ Push notifications
- ✅ Registro de usuarios desde redes confiables
- ✅ Módulos modernos (carboncopy, stream management, etc.)

### Certificado TLS

- **Algoritmo**: RSA 4096 bits
- **Hash**: SHA-256
- **Formato**: X.509 autofirmado
- **Extensión**: subjectAltName con el dominio
- **Permisos**: 600 (solo lectura para ejabberd)

### Servicio systemd

- **Tipo**: Forking
- **Usuario**: ejabberd
- **Reinicio automático**: En caso de fallo
- **Límites**: 100 reintentos en 3 segundos

## Solución de Problemas

### "tkinter no disponible"

El script automáticamente usará modo CLI. Si quieres GUI:

```bash
sudo apt-get install python3-tk
```

### Error de permisos

Asegúrate de proporcionar la contraseña sudo correcta cuando se solicite.

### Fallo de compilación

Verifica que tienes suficiente espacio en disco y memoria RAM:

```bash
df -h /tmp
free -h
```

### Puerto 5222 ya en uso

Si ya tienes un servidor XMPP corriendo:

```bash
sudo systemctl stop ejabberd
sudo systemctl disable ejabberd
```

### Certificado inválido

Para regenerar el certificado:

```bash
python3 ejabberd_installer.py --cli
# Selecciona opción 5: Solo generar certificado TLS
```

## Comandos Útiles Post-Instalación

### Gestión del servicio

```bash
# Estado
sudo systemctl status ejabberd

# Logs en vivo
sudo journalctl -u ejabberd -f

# Reiniciar
sudo systemctl restart ejabberd
```

### Administración de ejabberd

```bash
# Crear usuario administrador
sudo -u ejabberd /usr/local/ejabberd/sbin/ejabberdctl register admin my.lab.local tu_contraseña

# Estado del servidor
sudo -u ejabberd /usr/local/ejabberd/sbin/ejabberdctl status

# Usuarios conectados
sudo -u ejabberd /usr/local/ejabberd/sbin/ejabberdctl connected_users
```

### Interfaz web

Accede a: `https://tu-servidor:5443/admin/`

**Usuario**: `admin@my.lab.local`

## Seguridad

⚠️ **Importante:**

1. El certificado generado es **autofirmado** - solo para laboratorio/testing
2. Para producción, usa certificados válidos (Let's Encrypt, etc.)
3. Cambia la contraseña del admin después de crear el usuario
4. El registro de usuarios está restringido a redes confiables por defecto
5. TLS está configurado como requerido para conexiones de clientes

## Logs y Diagnóstico

```bash
# Logs de ejabberd
tail -f /usr/local/ejabberd/var/log/ejabberd/ejabberd.log

# Errores
grep ERROR /usr/local/ejabberd/var/log/ejabberd/ejabberd.log

# Base de datos (si usas sqlite)
sudo -u ejabberd sqlite3 /usr/local/ejabberd/var/lib/ejabberd/ejabberd.db
```

## Licencia

Este script es de uso libre. Ejabberd está bajo licencia GPLv2.

## Soporte

Para problemas específicos de ejabberd: https://github.com/processone/ejabberd/issues

---

**Versión**: 1.0  
**Última actualización**: Febrero 2025  
**Probado en**: Ubuntu 24.04 LTS
