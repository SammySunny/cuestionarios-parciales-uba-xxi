/* Resúmenes por materia y parcial. Rutas relativas a la raíz de la app.
   Para incorporar material: copiar el PDF, agregar una entrada y subir VERSION.
   Este catálogo también lo lee el service worker para guardar los PDF offline. */
var RESUMENES = [
  {
    id: "ipc-p2-texto", materia: "ipc", parcial: 2,
    nombre: "Resumen desarrollado en texto",
    descripcion: "Conceptos, distinciones y ejemplos resueltos. Incluye errores frecuentes, referencias a las guías oficiales y un mapa de los ejercicios de 2026.",
    detalle: "Buacar (A) · Caps. 10–15 · Revisión 23/10/2026 · Complemento histórico separado",
    paginas: 19, formato: "A4 vertical",
    archivo: "resumenes/ipc/2do-parcial/Resumen_textual_2do_parcial.pdf"
  },
  {
    id: "ipc-p2-guia", materia: "ipc", parcial: 2,
    nombre: "Guía explicada con ejemplos",
    descripcion: "Bloques de lectura con criterios para clasificar, justificar y descartar opciones. Ejemplos y confusiones frecuentes separados de la explicación.",
    detalle: "Buacar (A) · Caps. 10–15 · Revisión 23/10/2026 · Complemento histórico separado",
    paginas: 23, formato: "A4 vertical",
    archivo: "resumenes/ipc/2do-parcial/Resumen_textual_cuadros_2do_parcial.pdf"
  },
  {
    id: "ipc-p2-cuadro", materia: "ipc", parcial: 2,
    nombre: "Cuadro sinóptico para repasar",
    descripcion: "Ramas y comparaciones con la cobertura ampliada: hipótesis, explicación, corrientes, sesgos, ética y financiación. Incluye ejemplos y criterios de resolución.",
    detalle: "Buacar (A) · Caps. 10–15 · Revisión 23/10/2026 · Complemento histórico separado",
    paginas: 19, formato: "A4 horizontal",
    archivo: "resumenes/ipc/2do-parcial/Cuadro_Sinoptico_IPC_2do_Parcial.pdf"
  },
  {
    id: "ipc-p2-celular", materia: "ipc", parcial: 2,
    nombre: "Repaso visual para celular",
    descripcion: "La cobertura completa repartida en páginas angostas, con texto grande, ramas cortas y continuaciones. Incluye ejemplos, referencias y mapa del parcial 2026.",
    detalle: "Buacar (A) · Caps. 10–15 · Revisión 23/10/2026 · Complemento histórico separado",
    paginas: 71, formato: "Vertical para celular · 360 × 720 pt",
    archivo: "resumenes/ipc/2do-parcial/Cuadro_Sinoptico_IPC_Celular.pdf"
  },
  {
    id: "icse-p2-guia", materia: "icse", parcial: 2,
    nombre: "Guía de estudio y ayuda memoria",
    descripcion: "Explicaciones por tema, comparaciones, cadenas de causas y preguntas de práctica para repasar las semanas 6 a 10.",
    detalle: "Cátedra A · Pedrosa · Semanas 6 a 10 · Incluye pendientes de cotejo señalados",
    paginas: 22, formato: "A4 vertical",
    archivo: "resumenes/icse/2do-parcial/Guia_Resumen_ICSE_2do_Parcial.pdf"
  },
  {
    id: "icse-p2-cuadro", materia: "icse", parcial: 2,
    nombre: "Cuadro sinóptico para repasar",
    descripcion: "Autores, ideas clave y conexiones de las unidades 4 y 5 en un repaso visual breve.",
    detalle: "Cátedra A · Pedrosa · Semanas 6 a 10 · Repaso rápido",
    paginas: 4, formato: "A4 horizontal",
    archivo: "resumenes/icse/2do-parcial/Cuadro_Sinoptico_ICSE_2do_Parcial.pdf"
  }
];
