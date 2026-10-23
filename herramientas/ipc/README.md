# Resúmenes IPC — Buacar, segundo parcial

## Fuentes y alcance de la revisión

Revisión editorial: **23/10/2026**. Núcleo de estudio: unidades 3 y 4,
capítulos 10–15 de *Desenredando la ciencia* (Buacar, comp., 2022), según
el programa y el cronograma oficiales de la cursada 2C2026.

Se consultaron en el Campus de UBA XXI:

- Programa analítico, cronograma 2C2026 y bibliografía obligatoria de 2026.
- Seis guías de trabajo con respuestas y devoluciones: estructura y
  contrastación (G6), filosofía clásica y explicación (G7), Kuhn (G8),
  feminismos (G9), ética (G10E) y políticas científicas (G10P).
- Los cinco mapas conceptuales enlazados en las semanas 6–10.

Los enlaces de los documentos se conservan en `contenido.json` y en los PDF.
Pueden requerir una sesión del Campus. No se incluyen sesiones, datos de cuenta,
descargas del aula ni copias del libro. Las referencias bibliográficas no
significan que se haya consultado íntegramente el libro comercial o visto todos
los videos: el cotejo directo utilizó los documentos y mapas indicados.

Para la aplicación al examen se revisó el banco de Buacar del segundo parcial:

- 29/05/2026: 8 temas, 80 consignas. Se cotejaron directamente con los PDF
  resueltos, entre otros puntos, la HA Stanford-Binet y la tesis cognitiva que
  el parcial atribuye al punto de vista feminista.
- 02/06/2023, 31/05/2024, 25/10/2024, 30/05/2025 y recuperatorio 30/10/2025:
  340 consignas históricas, para detectar exigencias adicionales.

`cobertura.json` relaciona cada consigna de 2026 con fichas y un criterio de
resolución. Las referencias históricas registran diferencias relevantes, no una
lista exhaustiva de todas las preguntas. La revisión no altera claves ni
explicaciones del banco `materias/ipc.js`.

## Decisiones editoriales

1. **Clasificación:** primero vocabulario, después alcance. «Todos» puede
   referirse a una muestra delimitada; «este» no elimina términos teóricos.
   Las existenciales no comparten la imposibilidad de verificación de las
   universales irrestrictas.
2. **Funciones de hipótesis:** no sustituir el análisis funcional por «toda HF
   es universal» o «toda HA viene de otra teoría». Los casos de 2026 destacan
   generalidad y apoyo independiente; G6 también admite investigaciones sobre
   hechos históricos no observables directamente.
3. **Refutación:** distinguir el esquema H → CO del que explicita HF, HA y CI.
   En el segundo se niega la conjunción, sin aislar automáticamente la HF.
4. **Explicación:** seleccionar una ley y condiciones pertinentes; reemplazar
   el ejemplo del jarro a 0 °C, que no permitía deducir un desborde.
5. **Kuhn:** inconmensurabilidad local no significa «mismo paradigma». Seguir
   la clasificación lingüística/perceptual/metodológico-instrumental del mapa
   y la guía del aula. Comunicación y traducción parciales no equivalen a
   traducción total.
6. **Feminismos:** exponer como tesis de la corriente evaluada —no como hecho
   biológico— la formulación cognitiva del parcial de 2026. Explicar la crítica
   de esencialismo y la objetividad comunitaria del empirismo. Distinguir las
   seis manifestaciones de sexismo por el mecanismo destacado en cada caso.
7. **Ética y política:** enseñar a completar premisas normativas y a justificar
   decisiones de financiación, incluidas las negativas. Mantener integridad,
   consentimiento, datos personales y los cuatro argumentos sobre humanidades
   porque aparecen en las actividades oficiales, aunque no todos se pregunten
   directamente en mayo de 2026.
8. **Históricos:** evolución figura como complemento, no como núcleo del
   segundo parcial 2C2026. Los nombres administrativos y porcentajes del libro
   de 2022 no se presentan como datos actuales.
9. **Lectura crítica:** no trasladar erratas de ejemplos a afirmaciones propias.
   Por ejemplo, la devolución G10E sobre propiedad intelectual menciona Sci-Hub
   como revista que cobra; el resumen explica el problema de acceso y derechos
   sin reproducir esa caracterización incorrecta.

## Archivos editables

- `contenido.json`: única base conceptual para los cuatro formatos. Cada ficha
  tiene ID estable, idea, ramas, ejemplo, confusión frecuente y referencias.
- `cobertura.json`: justificación de cobertura por ejercicio.
- `generar.py`: renderizadores textual, guía, cuadro de dos columnas y móvil.
- `verificar.py`: controles de integridad PDF, catálogo, referencias y copias.

Al agregar o reordenar fichas, actualizar también los números de ficha del mapa
de ejercicios en `reference_groups()` de `generar.py`.

## Generar

Se requiere Python 3, ReportLab y DejaVu Sans. PyMuPDF se utiliza para verificar
y previsualizar. Node se necesita para ejecutar el verificador de la app y leer
sus catálogos reales durante la comprobación editorial.

Desde la raíz de la aplicación, con las dependencias instaladas en un entorno
virtual externo al repositorio:

```bash
python -m pip install -r herramientas/ipc/requirements.txt
python herramientas/ipc/generar.py
```

`--fuentes DIRECTORIO` permite indicar dónde están `DejaVuSans.ttf` y
`DejaVuSans-Bold.ttf`. Por defecto se buscan en las ubicaciones habituales de
Linux. La generación no necesita red ni una sesión del Campus. Usa metadatos
PDF invariantes para obtener archivos reproducibles con las mismas versiones
de dependencias y fuentes.

Para sincronizar las copias de estudio, la carpeta de destino debe existir:

```bash
python herramientas/ipc/generar.py --copiar-a "../resumenes/IPC/2do parcial"
```

Las rutas y los IDs publicados se conservan. Después de generar, actualizar
las páginas reales y la descripción en `resumenes/indice.js`, además de
incrementar `VERSION` en `sw.js` para renovar las copias offline.

## Verificar

```bash
node herramientas/verificar.js
python herramientas/ipc/verificar.py --copias "../resumenes/IPC/2do parcial"
```

El segundo comando comprueba:

- Correspondencia completa con las 80 consignas del examen 2026 y sus ocho PDF
  de origen; referencias a fichas existentes.
- Presencia íntegra de cada idea, rama, ejemplo y aclaración en los cuatro PDF.
- Texto dentro de la página, páginas no vacías y pies con numeración real.
- Marcadores PDF que llevan a páginas con el título correcto.
- Número de páginas real coincidente con el catálogo de la app.
- Tamaño móvil de 360 × 720 pt e igualdad byte a byte de copias de estudio.

`--node /ruta/a/node` permite usar un ejecutable externo.
`--imagenes /directorio/temporal` genera PNG de todas las páginas para inspección
visual; el directorio padre debe existir. No guardar esas imágenes en el repo.

Estos controles detectan pérdidas de contenido, errores de publicación y cortes;
no certifican por sí mismos la exactitud filosófica ni que una persona podrá
resolver todo examen futuro. La lectura conceptual y la revisión visual siguen
siendo parte del proceso editorial.
