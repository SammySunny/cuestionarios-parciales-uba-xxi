# Cuestionarios Parciales UBA XXI

App web instalable (PWA) para practicar con parciales reales de UBA XXI. Elegís materia, examen y tema; respondés cada ejercicio, ves si acertaste y una explicación de por qué la correcta lo es y en qué fallan las otras. Al final, la nota sobre 10.

- Sin dependencias, sin build y sin backend: HTML, CSS y JavaScript a mano.
- Funciona sin internet una vez abierta (service worker) y se instala en Android.
- El progreso se guarda en el dispositivo (`localStorage`).
- Modo oscuro fijo y tamaño de letra ajustable.

## Estructura

```
index.html              pantallas y lógica (no contiene datos)
materias/indice.js      lista de materias
materias/filosofia.js   explicaciones y exámenes de Filosofía
materias/ipc.js         explicaciones y exámenes de IPC
sw.js                   modo sin conexión + aviso "Actualizar" (VERSION)
manifest.webmanifest    datos para instalarla
iconos/
herramientas/verificar.js   chequeos de los datos
```

## Formato de una materia

```js
registrarMateria({
  id: "filosofia", nombre: "Filosofía", detalle: "…",
  notas: { "heidegger-tecnica": `explicación…` },      // una por consigna
  examenes: [
    { id: "2c2019-p2", nombre: "2º parcial · 2C 2019", detalle: "…", temas: [
      { id: "t1", n: "Tema 1", aviso: "…", qs: [
        // opción simple
        { k: "heidegger-tecnica", e: "1", u: "Unidad 3", p: `enunciado`, o: [`…`, `…`, `…`, `…`], c: 2, pts: 1 },
        // dos columnas (o partes A y B): se elige una opción en cada una, sin puntaje parcial
        { k: "…", e: "2", p: `…`, partes: [ { r: `rótulo`, o: [`…`, `…`], c: 1 }, { r: `…`, o: [`…`, `…`], c: 0 } ], pts: 2 },
        // con texto común a varios ejercicios
        { k: "…", e: "6.1", ctx: `pasaje…`, p: `…`, o: [ … ], c: 0, pts: 1, d: 1 }
      ]}
    ]}
  ]
});
```

- `c` es el índice de la correcta empezando en 0 (0 = A). La letra se calcula al mostrarla.
- `k` apunta a la explicación en `notas`. Si la misma consigna aparece en varios temas, usa la misma `k` y se explica una sola vez. Por eso las explicaciones no nombran letras.
- `d: 1` marca una clave dudosa y muestra un aviso. También puede ser un texto con un aviso propio.
- `aviso` del tema explica de dónde salió la clave (marcas del parcial o deducción).
- `formato: "numeros"` conserva las opciones numeradas (1, 2, 3…) de un parcial. En una parte, `formato: "texto"` permite respuestas como Sí/No, sin un prefijo de letra o número. Si no se indica formato, se usan letras.
- `contextoTitulo` permite nombrar el bloque `ctx`, por ejemplo «Caso de referencia · ejercicio 1». Los ejercicios que remiten a otro deben traer el caso y las opciones que necesitan para poder responder sin volver atrás.
- Los textos van entre comillas invertidas `` ` `` para no tener que escapar comillas.

## IPC — Introducción al Pensamiento Científico

Se organiza por fecha de examen y cátedra, con los temas dentro de cada examen:

| Fecha | Examen y cátedra | Temas | Ejercicios por tema |
| --- | --- | --- | --- |
| 30/10/2025 | Recuperatorio del 2º parcial · A, Buacar | 1–2 | 10 |
| 21/10/2025 | 2º parcial · C, Gimeno | 1–3 | 20 |
| 30/05/2025 | 2º parcial · A, Buacar | 1–8 | 10 |
| 27/05/2025 | 2º parcial · C, Gimeno (ex-Vizioli) | 1–4 | 20 |
| 25/10/2024 | 2º parcial · A, Buacar | 1–8 | 10 |
| 31/05/2024 | 2º parcial · A, Buacar | 1–8 | 10 |
| 02/06/2023 | 2º parcial · A, Buacar | 1–8 | 10 |

Son 41 temas y 480 ejercicios, con 221 explicaciones reutilizadas. Las claves y explicaciones provienen de los documentos resueltos. En Buacar se conserva el puntaje de 1 por ejercicio, sin puntaje parcial en los de dos partes; en Gimeno se asignó 0,50 por consigna al no indicarse puntaje en los documentos. Las preguntas de hipótesis fundamental y auxiliar incluyen aclaraciones adicionales para distinguirlas de los resultados y consecuencias observacionales.

Cada tema registra su archivo de origen en `fuente` y, para los PDF, el rango de `paginas`. `IPC_2025_I (copia 1).docx` es idéntico a `IPC_2025_I.docx` y se cargó una sola vez. Los documentos originales permanecen en `../materias_uba_xxi/IPC/2º parciales/`.

Las explicaciones que mencionan números de opciones se mantienen vinculadas a su orden original: si se reordenan esas opciones, también se deben revisar esas referencias en la explicación.

## Agregar un parcial o un tema

1. Agregar el examen en `examenes`, o el tema en `temas` de un examen existente.
2. Reusar las `k` que ya existan y crear en `notas` solo las explicaciones nuevas.
3. Correr los chequeos: `node herramientas/verificar.js`.
4. Subir `VERSION` en `sw.js`.

No cambiar los `id` de materias, exámenes ni temas: con ellos se guarda el progreso. Si cambia la cantidad de consignas de un tema, el progreso de ese tema se reinicia solo y los demás se conservan.

## Agregar una materia

1. Crear `materias/<id>.js` con la forma de arriba.
2. Agregar `{ id, nombre, archivo, icono, color }` en `materias/indice.js`. `icono` identifica visualmente la materia y `color` define su acento. Los íconos disponibles están en `ICONOS`, dentro de `index.html` (por ejemplo: `templo`, `pi`, `matraz`, `hoja`, `atomo`, `cabeza`, `balanza`, `grafico`, `dialogo` y `globo`). El service worker lee esa lista, así que no hace falta tocar `sw.js` salvo para subir `VERSION`.
3. Correr los chequeos y subir `VERSION`.

## Chequeos

`node herramientas/verificar.js` revisa:

- ids únicos;
- que ninguna respuesta apunte a una opción que no existe;
- que toda clave tenga su explicación y no sobren explicaciones;
- que los puntajes de cada tema sumen 10;
- consistencia cruzada: misma consigna con las mismas opciones implica la misma correcta en todos los temas;
- que las explicaciones no nombren letras;
- que no haya URLs remotas;
- que existan todos los archivos que guarda el service worker.

## Publicar en GitHub Pages

Subir esta carpeta a un repositorio y activar Pages en Settings → Pages, con la rama `main` y la carpeta raíz. Cada cambio publicado, con `VERSION` subida, le muestra el aviso "Actualizar" a quien ya la tenga instalada.
