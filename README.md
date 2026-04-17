# Punto 1 – Gramática NoSQL CRUD

## Descripción

Se diseñó una gramática formal (en formato ANTLR4) para un lenguaje de
programación orientado a bases de datos **NO relacionales** (estilo MongoDB).
El lenguaje soporta las cuatro operaciones CRUD:

| Operación | Comando del lenguaje |
|-----------|----------------------|
| **C**reate | `CREATE COLLECTION` / `INSERT INTO ... VALUES` |
| **R**ead   | `FIND FROM ... WHERE ...` |
| **U**pdate | `UPDATE ... SET ... WHERE ...` |
| **D**elete | `DELETE FROM ... WHERE ...` / `DROP COLLECTION` |

---

## Archivo

`grammar_nosql.g4` — gramática completa en ANTLR4.

---

## Estructura de la Gramática

### Regla raíz
```
program → statement+ EOF
```
Un programa es una secuencia de uno o más enunciados, cada uno terminado en `;`.

### CREATE – Crear colección
```
CREATE COLLECTION nombre_coleccion;
```

### INSERT – Insertar documento(s)
```
INSERT INTO coleccion VALUES { "campo": valor, ... };
INSERT INTO coleccion VALUES [ {...}, {...} ];   // inserción múltiple
```

### FIND – Consultar
```
FIND FROM coleccion;
FIND FROM coleccion WHERE condicion;
FIND FROM coleccion WHERE condicion LIMIT 10;
FIND FROM coleccion WHERE condicion SORT BY campo ASC;
```

### UPDATE – Actualizar
```
UPDATE coleccion SET campo = valor;
UPDATE coleccion SET campo = valor WHERE condicion;
```

### DELETE – Eliminar documentos / colección
```
DELETE FROM coleccion WHERE condicion;
DROP COLLECTION coleccion;
```

---

## Expresiones de Filtro

Los filtros soportan:
- Operadores de comparación: `==`, `!=`, `<`, `<=`, `>`, `>=`
- Pertenencia a lista: `campo IN [v1, v2, ...]`
- Existencia de campo: `campo EXISTS`
- Conectivos lógicos: `AND`, `OR`, `NOT`, paréntesis

---

## Tipos de Datos Soportados

| Tipo    | Ejemplo |
|---------|---------|
| Número  | `42`, `3.14`, `-5` |
| Cadena  | `"hola"`, `'mundo'` |
| Booleano | `true`, `false` |
| Nulo   | `null` |
| Documento anidado | `{ "dir": { "ciudad": "Bogotá" } }` |
| Arreglo | `[1, 2, 3]` |

---

## Ejemplos de Sentencias Válidas

```nosql
// Crear colección
CREATE COLLECTION usuarios;

// Insertar un documento
INSERT INTO usuarios VALUES {
    "nombre": "Ana",
    "edad": 30,
    "activo": true
};

// Insertar múltiples documentos
INSERT INTO usuarios VALUES [
    { "nombre": "Luis", "edad": 25 },
    { "nombre": "María", "edad": 35 }
];

// Buscar todos
FIND FROM usuarios;

// Buscar con filtro
FIND FROM usuarios WHERE edad >= 18 AND activo == true;

// Buscar con límite y orden
FIND FROM usuarios WHERE activo == true SORT BY nombre ASC LIMIT 5;

// Actualizar
UPDATE usuarios SET activo = false WHERE edad < 18;

// Eliminar documentos
DELETE FROM usuarios WHERE activo == false;

// Eliminar colección
DROP COLLECTION usuarios;
```

---

## Justificación del Diseño

1. **Sintaxis legible**: Se eligió una sintaxis tipo SQL para que sea intuitiva,
   pero operando sobre documentos JSON (estilo NoSQL).
2. **Documentos anidados**: `value` puede ser un `document` o `array`,
   lo que permite estructuras recursivas.
3. **Filtros compuestos**: `filterExpr` es recursiva (usando `AND`, `OR`, `NOT`),
   lo que permite condiciones arbitrariamente complejas.
4. **Insensibilidad a mayúsculas**: Las palabras clave aceptan tanto mayúsculas
   como minúsculas (`find` = `FIND`).
5. **Comentarios**: Se soportan comentarios de línea (`//`) y bloque (`/* */`).

---

## Cómo Compilar la Gramática con ANTLR4

```bash
# Descargar ANTLR4
wget https://www.antlr.org/download/antlr-4.13.2-complete.jar

# Generar parser en Python
java -jar antlr-4.13.2-complete.jar -Dlanguage=Python3 grammar_nosql.g4

# Generar parser en Java
java -jar antlr-4.13.2-complete.jar grammar_nosql.g4
```

La implementación ejecutable se encuentra en el **Punto 2**.
