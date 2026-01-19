# csvorm

CsvOrm es un ORM model-first fuertemente tipado para Python con backend CSV y arquitectura extensible, cuyo objetivo principal es explorar diseño de APIs, tipado estático y experiencia de desarrollo en Python, utilizando archivos CSV como backend de persistencia.

El proyecto no pretende competir con ORMs de producción existentes, sino estudiar e implementar los patrones fundamentales detrás de un ORM moderno, manteniendo el foco en arquitectura, claridad conceptual y tooling.

A pesar de todo lo dicho anteriormente, la herramienta funciona perfectamente y puede ser usada si el objetivo principal es trabajar con archivos CSV de forma mas sencilla y rapida, la verdad si ahorra mucho tiempo usar el ORM en lugar de escribir el CSV con el modulo nativo que tiene python. ademas de que es comodo de usar.

## Caracteristicas del ORM

* Los modelos son la única fuente de verdad
* El tipado estático es una prioridad, no un añadido
* El tooling y el runtime están claramente separados
* Las consultas se construyen, analizan y ejecutan de forma explícita

El uso de CSV no es una propuesta de valor en sí mismo, sino una restricción intencional que permite centrar el diseño en los aspectos esenciales de un ORM: composición de consultas, ejecución diferida, validación de esquemas y experiencia de desarrollo.

## Ideas centrales

* **Diseño model-first**
  Los esquemas se definen mediante clases y anotaciones de tipo.

* **API de consultas fluida**
  Las consultas son expresivas, encadenables y fáciles de razonar.

* **Ejecución diferida**
  Las operaciones se acumulan y solo se evalúan al invocar un método terminal.

* **Tipado fuerte como objetivo de diseño**
  El tipado no es decorativo: forma parte del contrato del ORM.

* **Separación clara de responsabilidades**
  El runtime, el tooling y los artefactos generados están desacoplados.

## Definición de modelos

Los modelos se definen extendiendo la clase base CsvOrm y utilizando anotaciones de tipo como definición del esquema.

```python
from csvorm import CsvOrm

class User(CsvOrm):
    name: str
    age: int
```

Cada modelo:

* Se mapea automáticamente a un archivo CSV
* Incluye un campo id de tipo UUID como clave primaria
* Usa las anotaciones de tipo como contrato del esquema

## Creación de registros

Los registros pueden crearse pasando argumentos con nombre o instancias del modelo.

```python
User.create(name="Alice", age=25)
```

El identificador UUID se genera automáticamente.

## API de consultas

csvorm expone una API de consultas inspirada en ORMs tradicionales, con énfasis en claridad y composición.

```python
User.where(age=18).order_by("name").limit(10).offset(5).all()
```

Las consultas son perezosas y solo se ejecutan al invocar una operación terminal.

## Operaciones soportadas

* where
* limit
* offset
* order_by
* Operaciones terminales: all, first, exists, count

Cada llamada intermedia construye una representación interna de la consulta sin ejecutar ninguna operación de IO.

## Actualización y eliminación de datos

```python
User.where(name="Alice").update(age=26)

User.where(age=26).delete()
```

Las operaciones de escritura se realizan reescribiendo el archivo CSV de forma segura, utilizando archivos temporales.
Este enfoque garantiza que, ante fallos o errores durante la escritura, el archivo original no se corrompa.

## Generación automática de tipos

Una de las características principales de csvorm es la generación automática de tipos a partir de los modelos definidos por el usuario.

El sistema genera archivos .pyi que permiten:

* Filtros tipados en where
* Payloads tipados en update
* Restricción de campos válidos en order_by
* Autocompletado y validación estática en el IDE

Este enfoque mantiene el runtime simple y traslada las garantías de corrección al análisis estático.

## CLI y tooling

csvorm incluye una interfaz de línea de comandos para inicialización y generación de tipos.

Comandos principales:

```bash
csvorm init
csvorm generate_types
```

El comando init crea el archivo de configuración .csvorm.toml, donde se define:

* La ruta del directorio de modelos
* La raíz del proyecto
* El pythonpath usado para cargarlos

El comando generate_types analiza los modelos definidos y genera los archivos .pyi correspondientes.

## Estructura del proyecto

```bash 
src/csvorm 
├── runtime # Lógica principal del ORM y ejecución de consultas 
├── tooling # CLI, configuración y generación de código 
├── generated # Artefactos de tipado generados automáticamente 
└── cli.py # Punto de entrada del CLI
```

Esta estructura permite evolucionar el tooling de forma independiente al runtime.

## Extensibilidad y alcance

Aunque el backend inicial es CSV, este se trata como un detalle de implementación.

La arquitectura está preparada para:

* Implementaciones alternativas de almacenamiento (por ejemplo SQLite)
* Drivers intercambiables
* Nuevas herramientas sin romper la API pública

Este proyecto no está orientado a producción.
Su valor principal radica en explorar decisiones de diseño, trade-offs arquitectónicos y el impacto del tipado estático en la experiencia de desarrollo.

## Licencia

MIT
