# Lacerta

## Objetivo

Lacerta es un asistente inteligente modular cuyo objetivo es actuar como un director de orquesta capaz de coordinar agentes especializados para resolver tareas complejas.

La arquitectura separa la interpretación de las peticiones, la coordinación de agentes y la ejecución de servicios.

## Filosofía

* Arquitectura modular.
* Agentes independientes.
* Servicios especializados.
* Memoria persistente como objetivo futuro.
* Independencia del modelo de IA utilizado.
* Fácil ampliación.
* Separación clara de responsabilidades.

---

# Estado actual de Lacerta

Lacerta ya dispone de un sistema funcional de interpretación y coordinación basado en agentes.

Actualmente puede:

* Recibir peticiones por teclado.
* Recibir peticiones por voz.
* Interpretar peticiones mediante Zeus.
* Detectar diferentes tipos de intención.
* Ejecutar agentes especializados.
* Procesar varias peticiones dentro de una misma frase.
* Mantener conversaciones básicas directamente mediante Zeus.
* Consultar información meteorológica.
* Consultar noticias.
* Ejecutar acciones sobre el sistema.
* Combinar los resultados de varios agentes en una única respuesta.

El modelo utilizado actualmente por Zeus es:

```text
Qwen3 14B
```

ejecutado localmente mediante Ollama.

---

# Arquitectura actual

```text
                        Usuario
                           │
                    ┌──────┴──────┐
                    │             │
                  Voz          Teclado
                    │             │
                    └──────┬──────┘
                           │
                           ▼
                      VoiceService
                           │
                           ▼
                         Zeus
                    (Qwen3 14B)
                           │
                           ▼
                    AgentRequest
                           │
                           ▼
                     Orchestrator
                           │
                    ┌──────┴──────┐
                    │   Registry  │
                    └──────┬──────┘
                           │
             ┌─────────────┼─────────────┐
             │             │             │
             ▼             ▼             ▼
          Hermes        Poseidon       Hefesto
          noticias       clima        acciones PC
             │             │             │
             ▼             ▼             ▼
        NewsService   WeatherService  ApplicationService
             │             │             │
             └─────────────┼─────────────┘
                           │
                           ▼
                      AgentResult
                           │
                           ▼
                    ResultProcessor
                           │
                           ▼
                         Zeus
                    (respuesta final)
```

---

# Componentes

## Lacerta

Es la aplicación principal.

Inicializa los sistemas y mantiene el bucle principal.

Actualmente puede recibir texto por teclado o voz.

---

## Zeus

Es el componente encargado de interpretar las peticiones y generar las respuestas finales.

Actualmente utiliza un modelo local mediante Ollama.

Sus responsabilidades son:

1. Interpretar la petición del usuario.
2. Determinar la intención.
3. Determinar la acción.
4. Extraer los parámetros necesarios.
5. Detectar múltiples peticiones dentro de una misma entrada.
6. Generar un `AgentRequest`.
7. Coordinarse con el Orchestrator.
8. Generar una respuesta natural utilizando los resultados obtenidos.

Zeus no debería contener lógica específica de clima, noticias o aplicaciones.

### Intenciones actuales

```text
conversation
weather
system
news
```

### Acciones actuales

```text
conversation
└── chat

weather
├── current
└── forecast

system
├── open_application
└── close_application

news
└── search
```

---

## AgentRequest

Es la estructura utilizada para representar una petición interpretada por Zeus.

Contiene:

```text
intent
action
parameters
context
requests
```

Permite representar tanto peticiones simples como múltiples.

Ejemplo:

```text
Usuario:
"Dime el tiempo en Valdemoro y las noticias de Argentina"
```

Zeus puede generar dos peticiones:

```text
weather → current
news    → search
```

La lista `requests` contiene todas las peticiones detectadas.

---

## Orchestrator

Es el coordinador entre Zeus y los agentes.

Sus responsabilidades son:

1. Recibir el `AgentRequest`.
2. Determinar qué peticiones deben ejecutarse.
3. Buscar agentes compatibles en el `Registry`.
4. Ejecutar los agentes correspondientes.
5. Recoger los `AgentResult`.
6. Pasar los resultados al `ResultProcessor`.

Una petición puede activar varios agentes.

---

## Registry

Contiene todos los agentes registrados.

Permite que el Orchestrator no tenga que conocer directamente cada agente.

Actualmente registra:

* Hermes
* Poseidon
* Hefesto

---

## BaseAgent

Todos los agentes heredan de esta clase.

Todos implementan:

```python
can_handle()

execute()
```

Esto permite que el Orchestrator pueda tratarlos de forma uniforme.

---

# Agentes

## Hermes

Especializado en noticias.

Actualmente utiliza `NewsService` para consultar GNews.

Puede realizar búsquedas como:

```text
¿Qué noticias hay sobre NVIDIA?
```

o:

```text
¿Cuáles son las últimas noticias de Argentina?
```

Tipo:

```text
news
```

Acción:

```text
search
```

---

## Poseidon

Especializado en información meteorológica.

Actualmente utiliza servicios de localización y meteorología para obtener información sobre el tiempo.

Puede realizar consultas como:

```text
¿Qué tiempo hace ahora en Valdemoro?
```

o:

```text
¿Qué tiempo hará mañana en Barcelona?
```

Tipo:

```text
weather
```

Acciones:

```text
current
forecast
```

---

## Hefesto

Especializado en ejecutar acciones sobre el ordenador.

Actualmente puede:

* buscar aplicaciones
* abrir aplicaciones
* devolver un `AgentResult`

Tipo:

```text
system
```

No conoce directamente las rutas de las aplicaciones.

Utiliza servicios especializados para localizar y ejecutar las aplicaciones.

---

# AgentResult

Todos los agentes devuelven el mismo formato de resultado.

Contiene:

```text
success
agent_name
type
message
data
requires_llm
```

Esto permite que Zeus y `ResultProcessor` puedan procesar los resultados de cualquier agente de forma uniforme.

---

# ResultProcessor

Se encarga de procesar los resultados obtenidos por los agentes.

Si un agente requiere procesamiento mediante IA, los resultados se envían nuevamente a Zeus para generar una respuesta natural.

Esto permite combinar varios resultados.

Ejemplo:

```text
Usuario:

"Dime el tiempo en Valdemoro y las noticias de Argentina"
```

Resultados:

```text
Poseidon
└── Información meteorológica

Hermes
└── Noticias
```

El `ResultProcessor` pasa ambos resultados a Zeus y Zeus genera una única respuesta.

---

# Servicios

Los servicios contienen la lógica reutilizable del sistema.

Los agentes utilizan estos servicios en lugar de implementar directamente la lógica.

## WeatherService

Responsabilidad:

Consultar información meteorológica.

Actualmente obtiene datos como:

```text
temperature
wind_speed
weather_code
description
```

---

## LocationService

Responsabilidad:

Convertir una ubicación proporcionada por el usuario en información geográfica.

Por ejemplo:

```text
Valdemoro
        ↓
latitude
longitude
country
```

---

## NewsService

Responsabilidad:

Consultar noticias mediante GNews.

Actualmente permite realizar búsquedas por:

```text
query
date
category
```

Las noticias devuelven información como:

```text
title
description
url
source
published
```

La API utilizada actualmente tiene una limitación en el plan gratuito: las noticias en tiempo real tienen un retraso.

---

## ApplicationService

Responsabilidades:

* gestionar el catálogo de aplicaciones
* cargarlo
* guardarlo
* buscar aplicaciones

No ejecuta las aplicaciones.

Actualmente utiliza:

```text
cache/
    applications.json
```

En el primer inicio:

```text
escanea
   ↓
genera catálogo
   ↓
guarda catálogo
```

En los siguientes:

```text
carga catálogo
```

---

## SystemService

Responsabilidad:

Ejecutar acciones del sistema.

Actualmente:

```python
open_application(path)
```

No busca aplicaciones.

Solo ejecuta las rutas proporcionadas.

---

## VoiceService

Permite utilizar el micrófono.

Actualmente:

```text
escucha
   ↓
Google Speech Recognition
   ↓
texto
```

Después el texto se envía a Zeus exactamente igual que una petición escrita.

La voz no modifica la arquitectura de agentes.

Solo modifica la entrada.

---

# Flujo actual

Ejemplo:

```text
Usuario:

"Dime el tiempo en Valdemoro y las noticias de Argentina"
```

Flujo:

```text
Usuario
   ↓
Zeus
   ↓
Qwen3 14B
   ↓
AgentRequest
   │
   ├── Weather / Current
   │
   └── News / Search
   ↓
Orchestrator
   ↓
Registry
   │
   ├── Poseidon
   │      ↓
   │   WeatherService
   │
   └── Hermes
          ↓
      NewsService
   ↓
AgentResult
   ↓
ResultProcessor
   ↓
Zeus
   ↓
Respuesta final
```

---

# Conversación

Las conversaciones normales no necesitan un agente específico.

Por ejemplo:

```text
Usuario:

"Hola Zeus"
```

Zeus interpreta:

```text
intent: conversation
action: chat
```

y responde directamente utilizando el modelo de IA.

Esto permite mantener la conversación separada de los agentes especializados.

En el futuro se añadirá memoria para mejorar el contexto de estas conversaciones.

---

# Catálogo de aplicaciones

Actualmente el catálogo es persistente.

Cada ordenador tendrá el suyo.

No debe subirse a Git.

```text
cache/applications.json
```

Debe estar ignorado por Git.

---

# Cosas pendientes

## Mejorar ApplicationService

Actualmente busca mediante coincidencias relativamente simples.

Más adelante:

* alias
* búsqueda inteligente
* puntuación
* búsqueda aproximada
* detección de aplicaciones instaladas recientemente

---

## Noticias

Mejorar el sistema de noticias:

* mejorar búsquedas
* filtros por fecha
* filtros por categoría
* seleccionar mejores resultados
* eliminar noticias duplicadas
* mejorar el resumen de resultados
* gestionar correctamente noticias históricas

---

## Meteorología

Más adelante:

* mejorar previsiones
* soportar más tipos de consultas
* mejorar interpretación de ubicaciones
* añadir alertas meteorológicas

---

## Juegos

El menú Inicio no contiene necesariamente todos los juegos.

Más adelante probablemente habrá servicios específicos.

Ejemplo:

```text
SteamService
EpicService
BattleNetService
```

En vez de introducir toda esta lógica dentro de `ApplicationService`.

---

## Voz

Actualmente se puede utilizar entrada por voz.

En el futuro:

```text
"Lacerta"
   ↓
activar escucha
   ↓
"abre Steam"
```

mediante un sistema de palabra de activación.

---

## Zeus

Actualmente Zeus ya utiliza un modelo de IA para:

* interpretar intenciones
* extraer parámetros
* detectar múltiples peticiones
* generar respuestas
* combinar resultados de varios agentes

Más adelante:

* memoria conversacional
* contexto persistente
* planificación de tareas complejas
* mejor gestión de errores
* mayor autonomía

---

## Memoria

Todavía no existe un sistema de memoria persistente.

Más adelante Zeus podrá recordar:

* preferencias
* conversaciones
* contexto
* información relevante del usuario

---

# Objetivo a largo plazo

```text
                    Usuario
                       │
                 Voz / Texto
                       │
                       ▼
                 ┌───────────┐
                 │   Zeus    │
                 │    IA     │
                 └─────┬─────┘
                       │
                 AgentRequest
                       │
                       ▼
                ┌─────────────┐
                │ Orchestrator│
                └──────┬──────┘
                       │
                    Registry
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
       Agente 1     Agente 2     Agente 3
          │            │            │
          ▼            ▼            ▼
       Servicio     Servicio     Servicio
          │            │            │
          └────────────┼────────────┘
                       │
                  AgentResult
                       │
                       ▼
                ResultProcessor
                       │
                       ▼
                     Zeus
                       │
                       ▼
                 Usuario
```

### Principio fundamental

```text
Zeus piensa.
El Orchestrator coordina.
Los agentes trabajan.
Los servicios ejecutan.
```

Cada capa debe tener una única responsabilidad.

```
```
