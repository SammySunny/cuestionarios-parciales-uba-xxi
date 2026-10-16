/* ============================================================
   ÍNDICE DE MATERIAS
   ------------------------------------------------------------
   Una línea por materia. Para sumar una materia nueva:
     1. Crear su archivo en materias/ (copiando la forma de filosofia.js).
     2. Agregar acá una línea {id, nombre, archivo, icono, color}.
     3. Subir el número VERSION en sw.js.
   El id tiene que ser el mismo que el del archivo de la materia y
   no se cambia nunca: con él se guarda el progreso de cada persona.

   Este archivo lo lee la app (para mostrar la lista) y también el
   service worker (para guardar todo en el teléfono y que ande sin
   internet). Por eso usa "var" y no lleva nada más que la lista.
   ============================================================ */
var CATALOGO = [
  {
    id: "filosofia",
    nombre: "Filosofía",
    archivo: "materias/filosofia.js",
    icono: "templo",
    color: "#b69de8"
  },
  {
    id: "ipc",
    nombre: "IPC · Introducción al Pensamiento Científico",
    archivo: "materias/ipc.js",
    icono: "atomo",
    color: "#67c4be"
  }
];
