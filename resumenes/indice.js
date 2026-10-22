/* Resúmenes por materia y parcial. Rutas relativas a la raíz de la app.
   Para incorporar material: copiar el PDF, agregar una entrada y subir VERSION.
   Este catálogo también lo lee el service worker para guardar los PDF offline. */
var RESUMENES = [
  {
    id: "ipc-p2-texto", materia: "ipc", parcial: 2,
    nombre: "Resumen en texto",
    descripcion: "Explicaciones en párrafos, organizadas por capítulo. Una lectura compacta de los conceptos principales.",
    detalle: "Cátedra A · Buacar · Capítulos 10 a 15",
    paginas: 3, formato: "A4 vertical",
    archivo: "resumenes/ipc/2do-parcial/Resumen_textual_2do_parcial.pdf"
  },
  {
    id: "ipc-p2-guia", materia: "ipc", parcial: 2,
    nombre: "Guía explicada con ejemplos",
    descripcion: "Ideas centrales, listas y ejemplos separados para entender cada tema paso a paso.",
    detalle: "Cátedra A · Buacar · Capítulos 10 a 15",
    paginas: 5, formato: "A4 vertical",
    archivo: "resumenes/ipc/2do-parcial/Resumen_textual_cuadros_2do_parcial.pdf"
  },
  {
    id: "ipc-p2-cuadro", materia: "ipc", parcial: 2,
    nombre: "Cuadro sinóptico para repasar",
    descripcion: "Conceptos y comparaciones en cuadros horizontales, con ejemplos y claves para resolver ejercicios.",
    detalle: "Cátedra A · Buacar · Capítulos 10 a 15",
    paginas: 8, formato: "A4 horizontal",
    archivo: "resumenes/ipc/2do-parcial/Cuadro_Sinoptico_IPC_2do_Parcial.pdf"
  },
  {
    id: "ipc-p2-celular", materia: "ipc", parcial: 2,
    nombre: "Repaso visual para celular",
    descripcion: "Bloques cortos y páginas verticales pequeñas, pensadas para leer en el teléfono.",
    detalle: "Cátedra A · Buacar · Capítulos 10 a 15",
    paginas: 15, formato: "Vertical para celular",
    archivo: "resumenes/ipc/2do-parcial/Cuadro_Sinoptico_IPC_Celular.pdf"
  }
];
