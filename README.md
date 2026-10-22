# Cuestionarios Parciales UBA XXI

App web instalable (PWA) para practicar con parciales reales de UBA XXI. Elegís materia, parcial, examen y tema; respondés cada ejercicio, ves si acertaste y una explicación de por qué la correcta lo es y en qué fallan las otras. Al final, la nota sobre 10.

- Sin dependencias, sin build y sin backend: HTML, CSS y JavaScript a mano.
- Funciona sin internet una vez abierta (service worker) y se instala en Android.
- El progreso se guarda en el dispositivo (`localStorage`).
- Modo oscuro fijo.
- Botón pequeño en el inicio para borrar la caché y las respuestas de todas las materias, con confirmación.

## Leyenda final y enlace externo

Al final de todas las pantallas se muestra: «¡Mucha suerte en los parciales! Esta app es gratuita y sin fines de lucro. Si querés devolver la buena onda, seguime en Mondschatten Artesanías.», con un ícono propio de gato y luna. «Mondschatten Artesanías» abre el perfil de Instagram en otra pestaña. No se usa la foto de perfil porque Instagram no permite obtenerla sin iniciar sesión; los íconos son SVG propios dentro de la app, así que la leyenda también se ve sin conexión.

Ese enlace es la única dirección externa permitida. Está definido en `ENLACE_EMPRENDIMIENTO` (`index.html`) y en `ENLACES_EXTERNOS` (`herramientas/verificar.js`); si cambia, hay que actualizar ambos. El verificador sigue rechazando cualquier otra URL remota.

## Borrar los datos de la aplicación

En el inicio, **Borrar caché y respuestas** elimina todas las respuestas y las copias offline de esta app, y da de baja su service worker. El progreso visible se reinicia de inmediato. No borra datos de otros sitios o proyectos alojados bajo el mismo dominio. Para volver a disponer de la app sin conexión, cerrala y abrila nuevamente con internet después del borrado.

## Estructura

```
index.html              pantallas y lógica (no contiene datos)
materias/indice.js      lista de materias
materias/filosofia.js   explicaciones y exámenes de Filosofía
materias/ipc.js         explicaciones y exámenes de IPC
materias/icse.js        explicaciones y temas únicos de ICSE
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
    { id: "2c2019-p2", parcial: 2, nombre: "2º parcial · 2C 2019", detalle: "…", temas: [
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
- `aceptadas: [2, 3]` permite varias respuestas válidas cuando el material las autoriza; debe incluir la respuesta principal `c`.
- `elegir: 2` con `correctas: [3, 4]` (sin `c`) pide marcar dos opciones de una misma lista. Se pueden desmarcar antes de completar; se corrige al marcar la segunda y vale el puntaje solo si ambas son correctas, en cualquier orden. La respuesta se guarda como la lista ordenada de índices marcados.
- `pista` agrega una ayuda desplegable antes de responder.
- `k` apunta a la explicación en `notas`. Si la misma consigna aparece en varios temas, usa la misma `k` y se explica una sola vez. Por eso las explicaciones no nombran letras.
- `notaEspecifica: true` identifica una explicación importada ligada al orden fijo de las opciones de esa pregunta. Puede mencionar sus letras o números; no se debe reutilizar con opciones reordenadas.
- `d: 1` marca una clave dudosa y muestra un aviso. También puede ser un texto con un aviso propio.
- `aviso` del tema explica de dónde salió la clave (marcas del parcial o deducción).
- La materia puede incluir `sigla` para abreviar el nombre en los botones de regreso sin acortar el título del catálogo.
- `formato: "numeros"` conserva las opciones numeradas (1, 2, 3…) de un parcial. En una parte, `formato: "texto"` permite respuestas como Sí/No, sin un prefijo de letra o número. Si no se indica formato, se usan letras.
- `contextoTitulo` permite nombrar el bloque `ctx`, por ejemplo «Caso de referencia · ejercicio 1». Los ejercicios que remiten a otro deben traer el caso y las opciones que necesitan para poder responder sin volver atrás.
- Los textos pueden escribirse entre comillas invertidas `` ` `` o como cadenas JSON con sus comillas escapadas.

## Selección de parcial y primeros parciales

En IPC e ICSE se elige primero **1er parcial** o **2do parcial**. Cada examen declara `parcial: 1` o `parcial: 2`; si no se indica, se considera segundo parcial, para compatibilidad con el contenido anterior. Las materias con un solo tipo disponible, como Filosofía, abren directamente sus exámenes.

Los nuevos listados usan las rutas `#/ipc/parcial/1`, `#/ipc/parcial/2` y las equivalentes de ICSE. Los enlaces a ejercicios y las claves de almacenamiento de los segundos parciales se conservan.

Se agregaron **55 temas y 898 preguntas**, importados de los HTML de `materias_uba_xxi/<materia>/1º parciales/`:

| Materia y año | Organización | Temas | Preguntas |
| --- | --- | ---: | ---: |
| IPC 2025 | Buacar 11 y 14/04; Gimeno 15/04 | 8 | 100 |
| IPC 2026 | Buacar 16 y 17/04; Gimeno 14/04 | 7 | 80 |
| ICSE 2025 | Abril y septiembre | 27 | 484 |
| ICSE 2026 | 1C y Tema 9 de 2C | 13 | 234 |

Se mantienen los números de tema originales. IPC conserva explicaciones, pistas y formatos de opciones; la pregunta 1 del Tema 9 de Buacar del 14/04/2025 admite las dos respuestas autorizadas por la aclaración del material. ICSE 2026 reutiliza sus explicaciones; para ICSE 2025 se reutilizaron explicaciones pertinentes y se completaron las que faltaban.

El **Tema 13 oral de septiembre de ICSE 2025** conserva sus 16 preguntas de 0,50, total original 8 puntos. Declara `totalEsperado: 8` y muestra claramente una nota normalizada sobre 10 junto al puntaje original. El verificador respeta esa excepción.

La **pregunta 11 del Tema 14 de abril de ICSE 2025** se corrigió de E a G (B y C): democracia procedimental y mínima. La corrección y la clave de origen quedan registradas. Otras erratas cronológicas y una repetición de dos distractores en el HTML se conservaron con avisos; el verificador solo permite esa repetición documentada cuando no duplica la respuesta correcta.

## Resúmenes por materia

Cada materia tiene un acceso **Resúmenes**, organizado por parcial. La ruta
`#/ipc/resumenes/2` muestra los cuatro PDF del segundo parcial de IPC
(Cátedra A · Buacar, capítulos 10 a 15): Resumen en texto, Guía explicada con
ejemplos, Cuadro sinóptico para repasar y Repaso visual para celular.
Cada tarjeta permite abrir el PDF en otra pestaña o descargarlo. Los archivos
se guardan junto con la app para consultarlos sin conexión. Las materias o
parciales sin material muestran un mensaje de disponibilidad.

Las fuentes están en `../resumenes/<materia>/<parcial>/`. Para agregar material,
copiar los PDF a `app/resumenes/<id-materia>/<parcial>/` (desde la carpeta
Facultad), registrar nombre, descripción, materia, parcial, páginas, formato y
ruta en `resumenes/indice.js`, subir `VERSION` en `sw.js` y correr el verificador.
El service worker toma del catálogo los archivos que debe guardar. Los nuevos
archivos fuente se incorporan mediante una actualización de la app.

## IPC — Introducción al Pensamiento Científico

Se organiza por fecha de examen y cátedra, con los temas dentro de cada examen:

| Fecha | Examen y cátedra | Temas | Ejercicios por tema |
| --- | --- | --- | --- |
| 29/05/2026 | 2º parcial · A, Buacar | 1–8 | 10 |
| 30/10/2025 | Recuperatorio del 2º parcial · A, Buacar | 1–2 | 10 |
| 21/10/2025 | 2º parcial · C, Gimeno | 1–3 | 20 |
| 30/05/2025 | 2º parcial · A, Buacar | 1–8 | 10 |
| 27/05/2025 | 2º parcial · C, Gimeno (ex-Vizioli) | 1–4 | 20 |
| 25/10/2024 | 2º parcial · A, Buacar | 1–8 | 10 |
| 31/05/2024 | 2º parcial · A, Buacar | 1–8 | 10 |
| 02/06/2023 | 2º parcial · A, Buacar | 1–8 | 10 |

Son 49 temas y 560 ejercicios. Las claves y explicaciones provienen de los documentos resueltos. En Buacar se conserva el puntaje de 1 por ejercicio, sin puntaje parcial en los de dos partes; en Gimeno se asignó 0,50 por consigna al no indicarse puntaje en los documentos. Las preguntas de hipótesis fundamental y auxiliar incluyen aclaraciones adicionales para distinguirlas de los resultados y consecuencias observacionales.

Cada tema registra su archivo de origen en `fuente` y, para los PDF, el rango de `paginas`. `IPC_2025_I (copia 1).docx` es idéntico a `IPC_2025_I.docx` y se cargó una sola vez. Los documentos originales permanecen en `../materias_uba_xxi/IPC/2º parciales/`.

En el 2º parcial del 29/05/2026 (`IPC_2026_A.pdf` a `IPC_2026_H.pdf`, Temas 1 a 8), la clave sale de la grilla de respuestas y del resaltado de cada documento, que coinciden en los 80 ejercicios; las explicaciones son las del texto en rojo. El ejercicio 10 pide marcar dos opciones y usa `elegir`/`correctas`. Los ejercicios que remiten al caso del ejercicio 1 lo incluyen como «Caso de referencia · ejercicio 1».

Las explicaciones que mencionan números de opciones se mantienen vinculadas a su orden original: si se reordenan esas opciones, también se deben revisar esas referencias en la explicación.

## ICSE — Introducción al Conocimiento de la Sociedad y el Estado

Se incorporó el **2º parcial del 31/10/2025, Cátedra A · Fernando Pedrosa**, con **10 temas únicos, 176 preguntas y 68 explicaciones**:

- Temas 1–8: 18 preguntas; las primeras 16 valen 0,50 y las últimas 2 valen 1 punto.
- Temas 9–10: 16 preguntas; las primeras 14 valen 0,50 y las últimas 2 valen 1,50 puntos.
- Todos los temas suman 10. En el Tema 10 se respeta el puntaje impreso en las preguntas 15 y 16, en lugar del encabezado contradictorio que dice 1 punto.

`ICSE_2025_C.pdf` contiene el compilado completo. Los otros nueve PDF se cotejaron con sus secciones y no se cargaron como cuestionarios adicionales. El Tema 11 del 04/11/2025 repite íntegramente el Tema 8 y se omitió; la numeración de la aplicación queda consecutiva, de Tema 1 a Tema 10. Cada tema conserva su número original y el rango de páginas del compilado en sus metadatos.

Las claves provienen de las grillas. Las explicaciones fueron elaboradas para el estudio y no se presentan como correcciones oficiales. Hay avisos de revisión en las consignas sobre Alfonsín de los temas 3, 4, 7 y 8, y en la proyección de envejecimiento del Tema 8 («5 años» frente a «35 años» en el Tema 7). Se conservan el texto y la clave de la fuente en esos casos.

Las opciones combinadas (por ejemplo, «Las opciones correctas son la A y la C») se responden con un solo botón, como en el parcial. El verificador expande esas referencias para comparar el contenido de las afirmaciones entre temas, aunque sus letras cambien.

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
- que los puntajes de cada tema sumen 10, o el `totalEsperado` documentado para un formato especial;
- consistencia cruzada: misma consigna con las mismas opciones implica la misma correcta en todos los temas;
- que las explicaciones compartidas no nombren letras (las notas específicas importadas conservan sus referencias originales);
- que no haya URLs remotas;
- que existan todos los archivos que guarda el service worker.

## Publicar en GitHub Pages

Subir esta carpeta a un repositorio y activar Pages en Settings → Pages, con la rama `main` y la carpeta raíz. Cada cambio publicado, con `VERSION` subida, le muestra el aviso "Actualizar" a quien ya la tenga instalada.
