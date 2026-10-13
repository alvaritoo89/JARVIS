# JARVIS — Asistente personal de voz con n8n

Un asistente personal inspirado en JARVIS de Iron Man, creado mediante **n8n, inteligencia artificial y Python**. Permite interactuar por voz o texto, procesar instrucciones y ejecutar acciones en el ordenador mediante un flujo de automatización personalizable.

El proyecto está diseñado para servir como base: puedes adaptar sus modelos de IA, cambiar los servicios de voz, añadir herramientas e integrar nuevas automatizaciones según tus necesidades.

## ✨ Características

- **Interacción por voz y texto:** envía instrucciones habladas o escritas.
- **Transcripción de audio:** convierte la voz en texto mediante Gemini.
- **Inteligencia artificial:** utiliza Gemini como modelo de lenguaje para interpretar las instrucciones y generar respuestas.
- **Síntesis de voz:** genera respuestas habladas mediante Fish Audio.
- **Automatización local:** permite solicitar acciones como abrir páginas web, buscar en Google o YouTube, abrir aplicaciones y acceder a carpetas.
- **Memoria conversacional:** conserva contexto de la conversación mediante el sistema de memoria de n8n.
- **Integración con Gmail:** permite consultar correos y enviar mensajes mediante las herramientas configuradas.
- **Integración con Telegram:** permite enviar mensajes a contactos configurados.
- **Herramientas adicionales:** incorpora utilidades para cálculos y consultas enciclopédicas.
- **Arquitectura modular:** permite modificar el flujo, sustituir servicios e incorporar nuevas funciones.

## 🧠 ¿Cómo funciona?

JARVIS utiliza n8n como centro de automatización y conecta distintos servicios para procesar las solicitudes.

1. **Entrada:** recibe una instrucción de voz o texto.
2. **Transcripción:** si la entrada es audio, Gemini convierte el contenido hablado en texto.
3. **Procesamiento:** el agente de IA interpreta la solicitud y decide cómo responder o qué herramienta utilizar.
4. **Ejecución:** n8n conecta las herramientas disponibles para realizar las acciones solicitadas.
5. **Respuesta:** el agente genera una respuesta y Fish Audio puede convertirla en voz.
6. **Entrega:** el flujo devuelve la respuesta, el texto adicional, las acciones solicitadas y el audio generado cuando está disponible.

## 🛠️ Tecnologías utilizadas

| Tecnología | Función |
|---|---|
| n8n | Automatización y coordinación del flujo |
| Python | Cliente local e interacción con el ordenador |
| Gemini | Transcripción y procesamiento mediante IA |
| Fish Audio | Generación de voz |
| Gmail | Envío y consulta de correos |
| Telegram | Envío de mensajes |

Las tecnologías indicadas corresponden a la configuración actual del proyecto. Puedes sustituirlas por alternativas compatibles.

## 📋 Requisitos

Antes de empezar, necesitarás:

- Una instalación de n8n.
- Python instalado en el ordenador donde se ejecutará el cliente local.
- Acceso a los servicios de IA que decidas utilizar.
- Las credenciales necesarias para las integraciones que quieras activar.
- Los archivos del proyecto, incluido el cliente Python y el workflow de n8n.

Algunas funciones requieren configuración adicional y no estarán disponibles hasta que conectes sus respectivos servicios.

## 🚀 Instalación y configuración

### 1. Descarga el proyecto

Clona el repositorio:

```bash
git clone https://github.com/TU-USUARIO/TU-REPOSITORIO.git
cd TU-REPOSITORIO
```

Sustituye la URL por la de tu repositorio.

### 2. Importa el workflow en n8n

1. Abre tu instancia de n8n.
2. Importa el archivo JSON del workflow.
3. Comprueba que aparecen todos los nodos y las conexiones.
4. Configura las credenciales necesarias para los servicios que quieras utilizar.

### 3. Configura los servicios

El workflow incluye referencias a Gemini y Fish Audio. Configura sus credenciales desde n8n y revisa los parámetros necesarios para la transcripción y la generación de voz.

Si habilitas Gmail o Telegram, conecta también sus credenciales y configura los destinatarios o contactos que vayas a utilizar.

### 4. Configura el acceso al webhook

El flujo utiliza un webhook para recibir las solicitudes y comprobar un token de acceso.

Cambia el valor de ejemplo del token por uno propio y configura el cliente Python para enviar el mismo valor. No publiques tokens reales en el repositorio.

### 5. Ejecuta y prueba

Inicia el workflow y configura el cliente Python siguiendo las instrucciones de su archivo correspondiente.

Prueba primero una solicitud de texto sencilla. Después, comprueba la transcripción de voz, la respuesta hablada y las herramientas adicionales que hayas habilitado.

## 🔧 Personalización y ampliaciones

JARVIS no está limitado a su configuración inicial. Puedes modificarlo para adaptarlo a tus preferencias.

**Modelos de inteligencia artificial**
- Sustituir Gemini por otro modelo compatible con n8n.
- Utilizar proveedores de IA distintos según la tarea.
- Ajustar las instrucciones, el contexto y el comportamiento del agente.

**Voz**
- Cambiar Fish Audio por otro servicio de síntesis de voz compatible.
- Modificar la voz, el idioma y los parámetros de generación.
- Adaptar el sistema de transcripción.

**Nuevas herramientas**
- Añadir integraciones con calendarios y tareas.
- Incorporar búsquedas y consultas a otras fuentes de información.
- Crear automatizaciones con servicios externos.
- Añadir nuevos nodos y agentes especializados.

**Automatización local**
- Ampliar las aplicaciones que se pueden abrir.
- Añadir acciones locales mediante el cliente Python.
- Incorporar nuevas carpetas, accesos y operaciones controladas.

Ten en cuenta que cada ampliación puede requerir cambios en el workflow, el cliente Python, las credenciales o los permisos necesarios.

## 🔐 Seguridad

La seguridad depende tanto de la configuración de n8n como de las acciones permitidas en el cliente local.

- No subas claves API, contraseñas, tokens reales ni credenciales.
- No incluyas datos personales en los archivos de ejemplo.
- Utiliza variables de entorno o el sistema de credenciales de n8n cuando corresponda.
- Mantén el webhook protegido y evita exponerlo públicamente sin medidas de seguridad adecuadas.
- Limita las acciones locales a las operaciones que realmente necesites.
- Revisa los permisos de Gmail, Telegram y otros servicios conectados.
- Comprueba el comportamiento de cualquier nueva herramienta antes de habilitarla.

El workflow incluye un token de acceso de ejemplo que debe sustituirse antes de utilizarlo. La protección por token no sustituye otras medidas de seguridad.

## 📁 Estructura del proyecto

La estructura exacta puede variar según la versión del proyecto. Los componentes principales son:

```text
├── jarvis.py              # Cliente local de Python
├── jarvis-n8n.json   # Flujo de automatización de n8n
└── README.md              # Documentación del proyecto
```

Si tu repositorio contiene más archivos, añade aquí sus funciones reales para que la documentación coincida con el contenido publicado.

## ⚠️ Limitaciones

- La disponibilidad de las funciones depende de los servicios y las credenciales configurados.
- Los modelos y servicios externos pueden tener límites de uso, costes o requisitos propios.
- Las acciones locales requieren que el cliente Python esté configurado y en ejecución.
- La importación del workflow no garantiza por sí sola que todas las integraciones funcionen.
- Los cambios de proveedor pueden requerir adaptar parámetros, formatos de entrada o salida y conexiones.

## 🤝 Contribuciones

Puedes utilizar este proyecto como punto de partida para crear tu propio asistente. Si lo amplías o mejoras, puedes proponer cambios, compartir nuevas integraciones o adaptar el workflow a otros servicios.

---

**JARVIS — Tu asistente, tus herramientas y tus automatizaciones.
