# Lacerta

## Objetivo

Lacerta es un asistente inteligente modular cuyo objetivo es actuar como un director de orquesta capaz de coordinar agentes especializados para resolver tareas complejas.

## Filosofía

- Arquitectura modular.
- Agentes independientes.
- Memoria persistente.
- Independencia del modelo de IA utilizado.
- Fácil ampliación.

## Roadmap

- [x] Crear repositorio
- [x] Diseñar estructura inicial
- [ ] Crear el núcleo del sistema
- [ ] Crear el primer agente
- [ ] Sistema de memoria
- [ ] Servicios

# Estado actual de Lacerta (Resumen)

## Objetivo del proyecto

Lacerta es un asistente modular basado en agentes.

La idea es que ningún agente lo haga todo. Cada uno se especializa en una tarea concreta mientras Zeus decide quién debe actuar.

La arquitectura busca que sea escalable y fácil de ampliar con nuevos agentes, servicios y modelos de IA.

---

# Arquitectura actual

```
Usuario
        │
        ▼
 Voz / Teclado
        │
        ▼
      Zeus
        │
        ▼
     Registry
        │
        ▼
┌───────────────┬───────────────┬───────────────┐
│ Hermes        │ Poseidon      │ Hefesto       │
│ conversación  │ clima         │ acciones PC   │
└───────────────┴───────────────┴───────────────┘
        │
        ▼
  AgentResult
```

---

# Componentes

## Lacerta

Es la aplicación principal.

Inicializa todos los sistemas y mantiene el bucle principal.

Actualmente puede recibir texto por teclado o voz.

---

## Zeus

Es el orquestador.

No sabe responder preguntas.

Su única responsabilidad es:

1. Recibir una petición.
2. Consultar el Registry.
3. Encontrar los agentes que pueden responder.
4. Ejecutarlos.
5. Devolver todas las respuestas.

Nunca debería contener lógica de clima, aplicaciones o conversación.

---

## Registry

Contiene todos los agentes registrados.

Permite que Zeus no conozca los agentes directamente.

Actualmente registra:

* Hermes
* Poseidon
* Hefesto

---

## BaseAgent

Todos los agentes heredan de aquí.

Todos implementan:

```
can_handle()

execute()
```

Eso hace que Zeus pueda tratarlos todos exactamente igual.

---

# Agentes

## Hermes

Especializado en conversación.

Actualmente responde a saludos.

Tipo de respuesta:

```
conversation
```

---

## Poseidon

Especializado en información.

Actualmente devuelve el tiempo de forma simulada.

Tipo:

```
information
```

---

## Hefesto

Especializado en ejecutar acciones.

Actualmente:

* busca una aplicación
* la abre
* devuelve un AgentResult

Tipo:

```
action
```

No conoce rutas ni el sistema.

Todo eso lo delega en servicios.

---

# AgentResult

Todos los agentes devuelven exactamente el mismo formato.

Ejemplo:

```
success

agent_name

type

message

data
```

Gracias a esto Zeus puede tratar igual cualquier agente.

---

# Servicios

Los servicios contienen la lógica reutilizable.

Los agentes únicamente los utilizan.

## ApplicationService

Responsabilidades:

* gestionar el catálogo de aplicaciones
* cargarlo
* guardarlo
* buscar aplicaciones

No abre aplicaciones.

Solo sabe encontrarlas.

Actualmente:

```
cache/
    applications.json
```

En el primer inicio:

```
escanea

↓

guarda catálogo
```

En los siguientes:

```
carga catálogo
```

---

## SystemService

Responsabilidad:

Ejecutar acciones del sistema.

Actualmente:

```
open_application(path)
```

No busca aplicaciones.

Solo ejecuta rutas.

---

## VoiceService

Permite utilizar el micrófono.

Actualmente:

```
escucha

↓

Google Speech Recognition

↓

texto
```

Después el texto se envía a Zeus igual que si hubiese venido del teclado.

La voz no modifica Zeus ni los agentes.

Solo cambia la entrada.

---

# Flujo actual

Ejemplo:

Usuario dice:

```
abre spotify
```

Flujo:

```
Micrófono

↓

VoiceService

↓

"abre spotify"

↓

Zeus

↓

Registry

↓

Hefesto

↓

ApplicationService

↓

encuentra Spotify

↓

SystemService

↓

abre Spotify

↓

AgentResult

↓

Zeus

↓

Respuesta
```

---

# Catálogo de aplicaciones

Actualmente el catálogo es persistente.

Cada ordenador tendrá el suyo.

No debe subirse a Git.

```
cache/applications.json
```

Debe estar ignorado por git.

---

# Cosas pendientes

## Mejorar ApplicationService

Actualmente busca por coincidencia simple.

Más adelante:

* alias
* búsqueda inteligente
* puntuación
* búsqueda aproximada

---

## Juegos

El menú Inicio no contiene todos los juegos.

Más adelante probablemente habrá servicios específicos.

Ejemplo:

```
SteamService

EpicService

BattleNetService
```

En vez de meter todo dentro de ApplicationService.

---

## Voz

Actualmente siempre escucha.

En el futuro:

```
"Lacerta"

↓

activar escucha

↓

"abre Steam"
```

o un sistema de palabra de activación.

---

## Zeus

Actualmente concatena respuestas.

Más adelante podrá usar un modelo para:

* interpretar intención
* combinar respuestas
* generar una respuesta natural

Los agentes seguirán haciendo el trabajo.

---

## Memoria

Todavía no existe.

Más adelante Zeus podrá recordar:

* preferencias
* conversaciones
* contexto

---

## Objetivo a largo plazo

```
Usuario

↓

Voz / Texto

↓

Zeus (IA)

↓

Agentes especializados

↓

Servicios

↓

Sistema operativo
```

Zeus pensará.

Los agentes trabajarán.

Los servicios ejecutarán.

Cada capa tendrá una única responsabilidad.
