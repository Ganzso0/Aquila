**Lacerta**

## Objetivo

**Lacerta es un asistente inteligente modular diseñado para coordinar agentes especializados y resolver tanto peticiones simples como tareas que requieren planificación.**

La arquitectura separa claramente:

La comprensión e interpretación de la petición.

La planificación de tareas complejas.

La coordinación y ejecución.

La generación de respuestas.

Los servicios internos y la memoria.

Las capacidades especializadas de los agentes.

El objetivo es que cada componente tenga una responsabilidad concreta y pueda evolucionar de forma independiente.

Filosofía

Arquitectura modular.

Separación clara de responsabilidades.

Agentes independientes.

Servicios especializados.

Ejecución local.

Independencia del modelo de IA utilizado.

Fácil ampliación.

Planificación declarativa.

Ejecución paralela cuando las tareas son independientes.

Trazabilidad de las ejecuciones.

Memoria persistente.

Estado actual de Lacerta

Lacerta dispone actualmente de un sistema funcional de interpretación, planificación y ejecución basado en un modelo local y agentes especializados.

### Actualmente puede:

Recibir peticiones por teclado.

Recibir peticiones por voz.

Interpretar peticiones mediante Nous.

Detectar múltiples peticiones dentro de una misma entrada.

Determinar si una petición requiere planificación.

Planificar tareas complejas mediante Hécate.

Ejecutar peticiones independientes en paralelo.

Ejecutar tareas mediante dependencias y condiciones.

Transferir datos entre tareas planificadas.

Resolver referencias temporales mediante Cronos.

Ejecutar agentes especializados.

Supervisar la ejecución de agentes mediante Aegis.

Mantener conversaciones sin utilizar agentes especializados.

Consultar información meteorológica.

Consultar noticias.

Ejecutar acciones sobre el sistema.

Combinar resultados de varios agentes en una única respuesta.

Registrar un ExecutionTrace estructurado de cada ejecución.

Persistir información de peticiones, interpretaciones y resultados relacionados con el dataset.

Los modelos utilizados actualmente son:

- Qwen3 14B
- Granite
ejecutado localmente mediante Ollama.

También se han realizado pruebas con modelos más pequeños para las tareas cognitivas de Lacerta.

Arquitectura actual

La arquitectura actual separa el modelo de IA de la lógica de ejecución.

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
                         Lacerta
                      (modelo IA)
                            │
             ┌──────────────┴──────────────┐
             │                             │
             ▼                             ▼
           Nous                          Hécate
       Interpreter                    Planner
             │                             │
             │      planning_required      │
             └──────────────┬──────────────┘
                            │
                            ▼
                           Zeus
                      Orchestrator
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
     Cronos              Aegis             MemoryManager
        │                   │
        │                   ▼
        │               Registry
        │                   │
        │          ┌────────┼────────┐
        │          ▼        ▼        ▼
        │       Hermes   Poseidon  Hefesto
        │          │        │        │
        │          ▼        ▼        ▼
        │       News     Weather  Application
        │       Service   Service   Service
        │
        └───────────────────────────────────────
                            │
                            ▼
                       AgentResult
                            │
                            ▼
                       ResultProcessor
                            │
                            ▼
                          Logos
                    Conversational layer
                            │
                            ▼
                          Usuario

## Principio fundamental

- Lacerta piensa.
- Nous interpreta.
- Hécate planifica.
- Zeus ejecuta y coordina.
- Los agentes trabajan.
- Los servicios proporcionan capacidades.
- Logos comunica.

# **Lacerta**

Lacerta es el modelo de IA utilizado por el sistema.

Su función no es ejecutar directamente acciones sobre el ordenador.

El modelo puede utilizarse para distintas tareas cognitivas, separadas conceptualmente dentro de la arquitectura:
```
Lacerta
   │
   ├── Nous
   │     └── Interpretación
   │
   ├── Hécate
   │     └── Planificación
   │
   └── Logos
         └── Conversación y respuesta
```
Esta separación permite que las diferentes funciones cognitivas evolucionen de manera independiente aunque puedan utilizar el mismo modelo.

# **Nous**

Nous es el Interpreter de Lacerta.

Su responsabilidad es comprender la petición del usuario y producir una representación estructurada de lo que debe hacerse.

Nous no ejecuta acciones y no construye el plan de ejecución.

Sus responsabilidades son:

Comprender la petición.

Detectar las intenciones.

Determinar las acciones.

Extraer los parámetros.

Detectar múltiples peticiones.

Determinar si la petición requiere planificación.

Resolver el contexto necesario para representar la petición.

El resultado de Nous utiliza una estructura similar a:
```json
{
  "planning_required": false,
  "requests": [
    {
      "intent": "weather",
      "action": "current",
      "parameters": {
        "location": "Valdemoro"
      },
      "context": {
        "used": false,
        "request_id": null
      }
    }
  ]
}
```
planning_required

planning_required indica a Zeus si la interpretación necesita pasar por Hécate.

false
    ↓
Zeus puede ejecutar directamente

true
    ↓
Zeus activa Hécate
    ↓
Hécate genera el plan

Una petición con varias solicitudes independientes no necesita necesariamente planificación.

Por ejemplo:

"Dime el tiempo en Valdemoro y abre Steam"

puede ejecutarse directamente en paralelo.

En cambio:

"Comprueba la temperatura y abre Steam solo si es menor de 35 grados"

requiere planificación porque la segunda tarea depende del resultado de la primera.

# **Hécate**

Hécate es el Planner de Lacerta.

Solo se activa cuando Nous determina:

planning_required = true

Hécate no vuelve a interpretar la petición.

Recibe:

La petición original del usuario.

Las peticiones estructuradas producidas por Nous.

Su responsabilidad es construir un plan declarativo para Zeus.

Hécate determina:

Las tareas.

Las dependencias.

Los datos producidos.

Las entradas necesarias.

Las condiciones.

Las transferencias de datos entre tareas.

No:

Ejecuta acciones.

Decide qué agente concreto debe utilizarse.

Cambia la interpretación de Nous.

Añade tareas que no estén presentes en la interpretación.

Plan de ejecución

Un plan puede tener una estructura como:
```json
{
  "tasks": [
    {
      "id": "task_1",
      "intent": "weather",
      "action": "current",
      "inputs": {
        "location": "Madrid"
      },
      "depends_on": [],
      "outputs": [
        "weather"
      ]
    },
    {
      "id": "task_2",
      "intent": "system",
      "action": "open_application",
      "inputs": {
        "application": "Steam"
      },
      "depends_on": [
        "task_1"
      ],
      "condition": {
        "source": "task_1.weather.temperature",
        "operator": "less_than",
        "value": 35
      },
      "outputs": []
    }
  ]
}
```
Separación entre dependencia, condición y transferencia

Hécate utiliza tres mecanismos diferentes:

depends_on
    → indica qué tarea debe terminar antes.

condition
    → decide si una tarea debe ejecutarse.

input_mapping
    → transfiere datos producidos por una tarea a otra.

Esto permite representar flujos de ejecución sin que Hécate tenga que ejecutar ninguna acción.

### PlanValidator

PlanValidator valida los planes generados por Hécate antes de que Zeus los ejecute.

Actualmente comprueba, entre otras cosas:

Existencia de tasks.

Estructura de las tareas.

IDs únicos.

Dependencias existentes.

Orden correcto de las dependencias.

Ausencia de dependencias sobre sí mismas.

Estructura de las condiciones.

Operadores permitidos.

Estructura de input_mapping.

De esta forma, el modelo propone un plan, pero Zeus no lo ejecuta directamente sin validarlo.

### ConditionEvaluator

ConditionEvaluator es un servicio interno encargado de evaluar las condiciones de los planes.

Actualmente soporta operadores como:
```
equals
not_equals
greater_than
greater_or_equal
less_than
less_or_equal
contains
not_contains
exists
not_exists
```
Por ejemplo:

task_1.weather.temperature
less_than
35

se resuelve utilizando el resultado real de task_1.

# Zeus

Zeus es el Orchestrator de Lacerta.

Zeus es código encargado de coordinar y ejecutar el sistema.

Su responsabilidad es convertir las decisiones cognitivas de Lacerta en ejecución real.

Sus responsabilidades incluyen:

Recibir la petición.

Solicitar la interpretación a Nous.

Validar la interpretación.

Resolver referencias temporales.

Determinar si debe utilizarse Hécate.

Ejecutar planes.

Ejecutar peticiones independientes en paralelo.

Buscar agentes compatibles.

Coordinar servicios internos.

Recoger los resultados.

Pasar los resultados a la capa de respuesta.

Registrar el ExecutionTrace.

Zeus no contiene la lógica específica de meteorología, noticias o aplicaciones.

# Orchestrator

El Orchestrator es la implementación de Zeus.

Puede ejecutar dos tipos principales de flujo:

Ejecución directa

Cuando:

planning_required = false

las peticiones independientes pueden ejecutarse en paralelo.
```
Nous
  ↓
Zeus
  ↓
ThreadPoolExecutor
  ├── Poseidon
  └── Hefesto
```
Ejecución planificada

Cuando:

planning_required = true

el flujo es:
```
Nous
  ↓
Hécate
  ↓
PlanValidator
  ↓
Zeus
  ↓
Tarea 1
  ↓
Condición / dependencia
  ↓
Tarea 2
```
## ExecutionTrace

Cada ejecución de Zeus dispone de un ExecutionTrace.

El trace representa lo que realmente ocurrió durante la ejecución.

PLAN
¿Qué debería hacer Zeus?

TRACE
¿Qué hizo realmente Zeus?

RESULTS
¿Qué resultados produjo?

El trace registra eventos estructurados como:
```
request_received
history_loaded
message_saved

interpretation_started
interpretation_completed
interpretation_validation_started
interpretation_validated

request_saved
interpretation_saved

temporal_resolution_started
temporal_resolution_completed

execution_started
execution_requests_prepared

parallel_execution_started
request_started
agent_started
agent_completed
request_completed
parallel_execution_completed

planning_started
planning_completed
plan_validation_completed

task_started
condition_evaluated
task_skipped
task_completed

execution_completed

response_generation_started
response_generation_completed

dataset_label_saved
response_saved

execution_finished
```
En ejecuciones paralelas, el trace permite observar el orden real de los eventos producidos por los distintos hilos.

Actualmente el trace se mantiene en memoria durante la ejecución. Su persistencia podrá incorporarse posteriormente.

# Aegis

Aegis es la capa de supervisión y ejecución de agentes.

Zeus utiliza Aegis para ejecutar capacidades de los agentes registrados.

Esto permite mantener separadas:
```
Zeus
    ↓
Aegis
    ↓
Agente
```
Aegis también permite gestionar el estado de los agentes del sistema.

## Cronos

Cronos es el servicio encargado de resolver referencias temporales antes de la ejecución.

Permite transformar referencias como:

mañana
hoy
pasado mañana

en información que los agentes puedan utilizar.

La resolución temporal ocurre antes de ejecutar las peticiones.

# **Logos** 

Logos es la capa conversacional de Lacerta.

Su responsabilidad es transformar la información producida por el sistema en una respuesta natural para el usuario.

Conceptualmente:
```
Agentes
   ↓
AgentResult
   ↓
ResultProcessor
   ↓
Logos
   ↓
Respuesta
```
Logos no debe ejecutar acciones ni decidir qué agentes utilizar.

Su función es comunicar el resultado de la ejecución.

La implementación y evolución de Logos constituye la siguiente fase principal del proyecto.

## AgentRequest

AgentRequest representa una petición estructurada dentro del sistema.

Contiene información como:

intent
action
parameters
context

Una entrada puede contener varias peticiones independientes.

Por ejemplo:

"Dime el tiempo en Valdemoro y abre Steam"

puede producir:

weather → current
system  → open_application

**Zeus decide posteriormente cómo ejecutar esas peticiones.**

## Registry

Registry contiene los agentes registrados en Lacerta.

Permite que Zeus no tenga que conocer directamente la implementación de cada agente.

Actualmente registra agentes como:

  - Hermes

  - Poseidon

  - Hefesto

El sistema está diseñado para permitir añadir nuevos agentes sin modificar la lógica central del Orchestrator.

## BaseAgent

Los agentes especializados heredan de BaseAgent.

Todos proporcionan una interfaz común para que Zeus pueda trabajar con ellos de forma uniforme.

Actualmente utilizan mecanismos como:

can_handle()
execute()

# Agentes

## Hermes

Especializado en noticias.

Utiliza NewsService para consultar información mediante GNews.

Tipo:

news

Acción:

search

Ejemplo:

"¿Qué noticias hay sobre NVIDIA?"

## Poseidon

Especializado en meteorología.

Utiliza servicios de localización y meteorología.

Tipo:

weather

Acciones:

current
forecast

Ejemplos:

"¿Qué tiempo hace ahora en Valdemoro?"

"¿Qué tiempo hará mañana en Barcelona?"

## Hefesto

Especializado en acciones sobre el ordenador.

Actualmente puede:

Buscar aplicaciones.

Abrir aplicaciones.

Devolver AgentResult.

Tipo:

system

Acciones actuales:

  - open_application
  - close_application

Hefesto utiliza servicios especializados y no necesita conocer directamente toda la lógica del catálogo de aplicaciones.

## AgentResult

Todos los agentes devuelven un resultado común.

Contiene información como:

  - success
  - agent_name
  - type
  - message
  - data
  - requires_llm

Esto permite que Zeus y las capas posteriores procesen resultados de agentes diferentes de forma uniforme.

## ResultProcessor

ResultProcessor procesa los resultados obtenidos durante la ejecución.

Su función es preparar los resultados para la generación de la respuesta.

Por ejemplo:
```
Poseidon
   └── información meteorológica

Hefesto
   └── aplicación ejecutada

        ↓

ResultProcessor

        ↓

Logos

        ↓

respuesta final
```
Esto permite combinar información producida por varios agentes en una única respuesta.

# Servicios

Los servicios contienen la lógica reutilizable del sistema.

Los agentes utilizan estos servicios en lugar de implementar directamente toda la lógica.

### WeatherService

Responsabilidad:

Consultar información meteorológica.

Obtener datos meteorológicos.

Actualmente puede producir información como:

  - temperature
  - wind_speed
  - weather_code
  - description

### LocationService

Responsabilidad:

Convertir una ubicación proporcionada por el usuario en información geográfica.

Por ejemplo:

Valdemoro
    ↓
latitude
longitude
country

### NewsService

Responsabilidad:

Consultar noticias mediante GNews.

Permite realizar búsquedas utilizando parámetros como:

  - query
  - date
  - category

Los resultados pueden incluir:

  - title
  - description
  - url
  - source
  - published

La API utilizada actualmente tiene limitaciones en el plan gratuito relacionadas con el retraso de determinadas noticias.

### ApplicationService

Responsabilidades:

Gestionar el catálogo de aplicaciones.

Cargarlo.

Guardarlo.

Buscar aplicaciones.

El catálogo se mantiene localmente:

cache/
    applications.json

En el primer inicio:
```
escanea
   ↓
genera catálogo
   ↓
guarda catálogo

En los siguientes:
```
carga catálogo

El catálogo depende de cada ordenador y no debe subirse a Git.

### SystemService

Responsabilidad:

Ejecutar acciones del sistema.

Actualmente:

  - open_application(path)

No busca aplicaciones.

Recibe las rutas proporcionadas por la capa correspondiente y ejecuta la acción.

### MemoryManager

MemoryManager gestiona las operaciones internas relacionadas con la memoria.

Las peticiones de memoria no necesitan convertirse en agentes especializados.

Actualmente el sistema dispone de almacenamiento persistente para elementos como:

  - sesiones

  - mensajes

  - peticiones

  - interpretaciones

  - etiquetas del dataset

### Memoria

La memoria forma parte de la infraestructura interna de Lacerta y no de las capacidades especializadas de un agente externo.

### VoiceService

Permite utilizar el micrófono como entrada.

Actualmente:
```
escucha
   ↓
Google Speech Recognition
   ↓
texto
   ↓
Lacerta
```
Después el texto se envía al sistema de la misma forma que una petición escrita.

La voz no modifica la arquitectura de ejecución.

Solo modifica la entrada.

### Conversación

Las conversaciones normales no necesitan un agente especializado.

Cuando la petición no requiere una capacidad ejecutable, Nous puede identificarla como conversación y Zeus evita buscar un agente.

El flujo conceptual es:
```
Usuario
   ↓
Nous
   ↓
petición conversacional
   ↓
Logos
   ↓
respuesta
```
Esto mantiene la conversación separada de las capacidades especializadas del sistema.

Flujo de ejecución directa

Ejemplo:

"Dime el tiempo en Valdemoro y abre Steam"

Nous puede producir:

planning_required = false

Flujo:
```
Usuario
   ↓
Lacerta
   ↓
Nous
   ↓
Zeus
   ↓
ejecución paralela
   ├── Poseidon
   │      ↓
   │  WeatherService
   │
   └── Hefesto
          ↓
      ApplicationService
          ↓
      SystemService
   ↓
AgentResult
   ↓
ResultProcessor
   ↓
Logos
   ↓
Respuesta
```

## **Flujo de ejecución planificada**

Ejemplo:

"Comprueba la temperatura en Madrid y abre Steam solo si es menor de 35 grados."

Nous detecta que existe una dependencia:

planning_required = true

Hécate genera un plan:
```
task_1
   ↓
obtener temperatura
   ↓
condition
   ↓
task_2
   ↓
abrir Steam

Flujo:

Usuario
   ↓
Nous
   ↓
planning_required = true
   ↓
Hécate
   ↓
PlanValidator
   ↓
Zeus
   ↓
Poseidon
   ↓
resultado meteorológico
   ↓
ConditionEvaluator
   ↓
¿temperatura < 35?
   │
   ├── Sí ──→ Hefesto
   │
   └── No ──→ tarea omitida
   ↓
AgentResult
   ↓
ResultProcessor
   ↓
Logos
   ↓
Respuesta
```
## Catálogo de aplicaciones

El catálogo es persistente y específico de cada ordenador.

cache/applications.json

No debe subirse a Git.

Debe estar ignorado mediante .gitignore.

Cosas pendientes

### Logos

  - Completar la capa conversacional para separar completamente la generación de respuestas de la interpretación y la ejecución.

### Hécate

Continuar ampliando la capacidad de planificación cuando sea necesario:

  - dependencias más complejas

  - transferencia de datos entre tareas

  - flujos de ejecución más avanzados

  - validaciones adicionales

### ExecutionTrace

Actualmente el trace se mantiene en memoria.

Más adelante podría persistirse en SQLite para permitir:

  - auditoría de ejecuciones

  - depuración

  - análisis de rendimiento(odin)

  - supervisión

  - reconstrucción de ejecuciones anteriores

### Memoria

Continuar desarrollando la gestión de:

  - preferencias

  - contexto

  - recuerdos relevantes

  - historial

  - recuperación de información

### Noticias

Mejorar:

  - búsquedas

  - filtros

  - selección de resultados

  - eliminación de duplicados

  - resumen

  - noticias históricas

### Meteorología

Más adelante:

  - mejorar previsiones

  - soportar más tipos de consultas

  - mejorar interpretación de ubicaciones

  - añadir alertas meteorológicas

### Aplicaciones

Mejorar ApplicationService mediante:

  - alias

  - búsqueda aproximada

  - puntuación

  - búsqueda inteligente

  - detección de aplicaciones instaladas recientemente

Juegos

El menú Inicio no contiene necesariamente todos los juegos instalados.

En el futuro podrían existir servicios especializados:

  - SteamService
  - EpicService
  - BattleNetService

en lugar de introducir toda esta lógica dentro de ApplicationService.

### Voz

Actualmente existe entrada por voz.

En el futuro:
```
"Lacerta"
   ↓
activar escucha
   ↓
"abre Steam"
```
mediante un sistema de palabra de activación.

(Objetivo a largo plazo)

La arquitectura objetivo mantiene separadas las diferentes responsabilidades cognitivas y de ejecución:

                         Usuario
                            │
                     ┌──────┴──────┐
                     │             │
                    Voz          Texto
                     │             │
                     └──────┬──────┘
                            │
                            ▼
                         Lacerta
                       (modelo IA)
                            │
              ┌─────────────┼─────────────┐
              ▼             ▼             ▼
            Nous          Hécate        Logos
        Interpreter      Planner    Conversational
              │             │             ▲
              └──────┬──────┘             │
                     ▼                    │
                    Zeus                  │
               Orchestrator               │
                     │                    │
          ┌──────────┼──────────┐         │
          ▼          ▼          ▼         │
       Cronos      Aegis    MemoryManager │
                     │                    │
                  Registry                │
                     │                    │
             ┌───────┼───────┐            │
             ▼       ▼       ▼            │
          Hermes  Poseidon  Hefesto       │
             │       │       │            │
             ▼       ▼       ▼            │
          Service Service Service         │
             │       │       │            │
             └───────┼───────┘            │
                     ▼                    │
                 AgentResult              │
                     │                    │
                     ▼                    │
               ResultProcessor ───────────┘

El objetivo es que el modelo pueda evolucionar sin que la lógica de ejecución tenga que depender de él directamente.

# **Principio fundamental**

1- Lacerta piensa.

2- Nous interpreta.

3- Hécate planifica.

4- Zeus coordina y ejecuta.

5- Los agentes trabajan.

6- Los servicios proporcionan capacidades.

7- Logos comunica.

## Cada capa debe tener una responsabilidad clara y evitar asumir responsabilidades pertenecientes a otra capa.
