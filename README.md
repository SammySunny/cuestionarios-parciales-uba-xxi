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
- Los textos van entre comillas invertidas `` ` `` para no tener que escapar comillas.

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
