#!/usr/bin/env node
/* ============================================================
   Chequeos de los datos de la app. Correr desde la carpeta app/:
       node herramientas/verificar.js
   Sale con código 1 si hay errores (los avisos no cortan).

   Revisa:
   - que cada materia del índice exista y se registre bien;
   - ids únicos de examen y de tema (con ellos se guarda el progreso);
   - que cada respuesta c apunte a una opción que existe (o, en las
     consignas «elegir N», que correctas traiga N índices válidos);
   - que cada clave k tenga su explicación y que no sobren explicaciones;
   - que los puntajes de cada tema sumen 10;
   - consistencia cruzada: si una consigna aparece en varios temas con
     las mismas opciones (aunque en otro orden), la correcta tiene que
     ser la misma opción en todos;
   - que las explicaciones no nombren letras (cambian entre temas);
   - que no haya ninguna URL remota (la app tiene que andar sin internet);
   - que existan todos los archivos que el service worker guarda.
   ============================================================ */
"use strict";
const fs = require("fs");
const path = require("path");
const vm = require("vm");

const RAIZ = path.resolve(__dirname, "..");
const errores = [], avisos = [];
const error = m => errores.push(m), aviso = m => avisos.push(m);
const leer = f => fs.readFileSync(path.join(RAIZ, f), "utf8");
const norm = s => s.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase().replace(/[“”«»"'‘’…().,;:¿?¡!\-–—]/g, " ").replace(/\s+/g, " ").trim();
const esCombinacion = texto => /^las opciones\b.*\bcorrectas\b/i.test(texto.trim());
// Se comparan las afirmaciones, no las letras: «A y C» puede significar lo
// mismo que «B y D» cuando otro tema cambia el orden de las opciones.
function contenidoOpcion(b, i){
  const texto = b.o[i];
  if (!esCombinacion(texto)) return [norm(texto)];
  const refs = texto.match(/\b[A-H]\b/g) || [];
  return refs.map(l => norm(b.o["ABCDEFGH".indexOf(l)]));
}
const bancoAfirmaciones = b => b.o.filter(o => !esCombinacion(o)).map(norm).sort().join(" | ");
const soluciones = b => b.correctas ? b.correctas.map(i => norm(b.o[i])).sort().join(" + ") : (b.aceptadas || [b.c]).map(i => contenidoOpcion(b, i).sort().join(" | ")).sort().join(" || ");

/* ---------- cargar índice y materias ---------- */
const ctx = {};
vm.createContext(ctx);
vm.runInContext(leer("materias/indice.js"), ctx, {filename: "materias/indice.js"});
const CATALOGO = vm.runInContext("CATALOGO", ctx);
const materias = [];
ctx.registrarMateria = m => materias.push(m);

const idsMateria = new Set();
for (const info of CATALOGO) {
  if (idsMateria.has(info.id)) error(`índice: id de materia repetido "${info.id}"`);
  idsMateria.add(info.id);
  if (!fs.existsSync(path.join(RAIZ, info.archivo))) { error(`índice: no existe ${info.archivo}`); continue; }
  const antes = materias.length;
  try { vm.runInContext(leer(info.archivo), ctx, {filename: info.archivo}); }
  catch (e) { error(`${info.archivo}: no se pudo evaluar: ${e.message}`); continue; }
  if (materias.length !== antes + 1) { error(`${info.archivo}: tiene que llamar a registrarMateria una sola vez`); continue; }
  const m = materias[materias.length - 1];
  if (m.id !== info.id) error(`${info.archivo}: el id "${m.id}" no coincide con el del índice "${info.id}"`);
  revisarMateria(m, info.archivo);
}

function revisarMateria(m, archivo){
  const notas = m.notas || {};
  const usadas = new Set();
  const porClave = {};
  const idsEx = new Set();
  let nq = 0, nt = 0;

  for (const ex of m.examenes || []) {
    if (ex.tipo !== undefined && ex.tipo !== "final") error(`${m.id}/${ex.id}: tipo debe ser final o no indicarse`);
    if (ex.tipo === "final" && ex.parcial !== undefined) error(`${m.id}/${ex.id}: un final no puede declarar parcial`);
    if (ex.parcial !== undefined && ![1, 2].includes(ex.parcial)) error(`${m.id}/${ex.id}: parcial debe ser 1 o 2`);
    if (idsEx.has(ex.id)) error(`${m.id}: id de examen repetido "${ex.id}"`);
    idsEx.add(ex.id);
    const idsT = new Set();
    for (const t of ex.temas || []) {
      nt++;
      const donde = `${m.id}/${ex.id}/${t.id}`;
      if (idsT.has(t.id)) error(`${donde}: id de tema repetido`);
      idsT.add(t.id);
      if (!t.n) error(`${donde}: falta el nombre n`);
      if (!Array.isArray(t.qs) || !t.qs.length) { error(`${donde}: no tiene consignas`); continue; }
      let total = 0;
      const etiquetas = new Set(), clavesTema = new Set();
      t.qs.forEach((q, i) => {
        nq++;
        const e = q.e || String(i + 1), aqui = `${donde} ej. ${e}`;
        if (etiquetas.has(e)) error(`${aqui}: número de ejercicio repetido`);
        etiquetas.add(e);
        if (!q.k) error(`${aqui}: falta la clave k`);
        else {
          usadas.add(q.k);
          if (!notas[q.k]) error(`${aqui}: la clave "${q.k}" no tiene explicación en notas`);
          if (clavesTema.has(q.k)) aviso(`${aqui}: la clave "${q.k}" se repite dentro del mismo tema`);
          clavesTema.add(q.k);
          (porClave[q.k] = porClave[q.k] || []).push({q, aqui});
        }
        if (!q.p || !q.p.trim()) error(`${aqui}: enunciado vacío`);
        if (q.contextoTitulo && !q.ctx) error(`${aqui}: tiene título de contexto sin el texto de referencia`);
        if (q.formato && !["numeros", "texto"].includes(q.formato)) error(`${aqui}: formato de opciones desconocido`);
        if (!(q.pts > 0)) error(`${aqui}: puntaje inválido`);
        total += q.pts || 0;
        const bloques = q.partes ? q.partes : [q];
        if (q.partes && q.o) error(`${aqui}: tiene a la vez o y partes`);
        if (q.partes && q.partes.length < 2) error(`${aqui}: una consigna con partes necesita al menos dos`);
        bloques.forEach((b, j) => {
          const s = q.partes ? ` (parte ${j + 1})` : "";
          if (b.formato && !["numeros", "texto"].includes(b.formato)) error(`${aqui}${s}: formato de opciones desconocido`);
          if (!Array.isArray(b.o) || b.o.length < 2 || b.o.length > 8) { error(`${aqui}${s}: tiene que tener entre 2 y 8 opciones`); return; }
          if (q.elegir !== undefined) {
            if (q.partes) error(`${aqui}: «elegir» no se combina con partes`);
            if (b.c !== undefined || b.aceptadas) error(`${aqui}: con «elegir» la respuesta va en correctas, no en c ni aceptadas`);
            if (!Number.isInteger(q.elegir) || q.elegir < 2 || q.elegir >= b.o.length) error(`${aqui}: elegir=${q.elegir} inválido`);
            const cs = b.correctas;
            if (!Array.isArray(cs) || cs.length !== q.elegir || new Set(cs).size !== cs.length ||
                cs.some(c => !Number.isInteger(c) || c < 0 || c >= b.o.length) || cs.some((c, n) => n && c <= cs[n - 1]))
              error(`${aqui}: correctas tiene que traer ${q.elegir} índices distintos, válidos y ordenados`);
            if (b.o.some(esCombinacion)) error(`${aqui}: «elegir» no admite opciones combinadas`);
          } else if (b.correctas) error(`${aqui}${s}: correctas sin elegir`);
          else if (!Number.isInteger(b.c) || b.c < 0 || b.c >= b.o.length) error(`${aqui}${s}: la respuesta c=${b.c} está fuera de las opciones`);
          if (b.aceptadas && (!Array.isArray(b.aceptadas) || !b.aceptadas.includes(b.c) || new Set(b.aceptadas).size !== b.aceptadas.length || b.aceptadas.some(c => !Number.isInteger(c) || c < 0 || c >= b.o.length))) error(`${aqui}${s}: respuestas alternativas inválidas`);
          b.o.forEach((o, k) => { if (!o || !o.trim()) error(`${aqui}${s}: opción ${k + 1} vacía`); });
          b.o.forEach((o, k) => {
            if (!esCombinacion(o)) return;
            const refs = o.match(/\b[A-H]\b/g) || [];
            if (refs.length < 2 || new Set(refs).size !== refs.length || refs.some(l => {
              const i = "ABCDEFGH".indexOf(l);
              return i >= b.o.length || i === k || esCombinacion(b.o[i]);
            })) error(`${aqui}${s}: combinación inválida en la opción ${k + 1}`);
          });
          if (new Set(b.o.map(norm)).size !== b.o.length &&
              !(q.opcionesRepetidasFuente === true && q.d && b.o.filter(o => norm(o) === norm(b.o[b.c])).length === 1))
            error(`${aqui}${s}: hay dos opciones iguales`);
        });
      });
      const esperado = t.totalEsperado === undefined ? 10 : t.totalEsperado;
      if (!(Number.isFinite(esperado) && esperado > 0)) error(`${donde}: totalEsperado inválido`);
      else if (Math.abs(total - esperado) > 1e-9) error(`${donde}: los puntajes suman ${total}, no ${esperado}`);
    }
  }

  for (const k in notas) {
    if (!usadas.has(k)) aviso(`${m.id}: la explicación "${k}" no la usa ninguna consigna`);
    if (/\b(opci[oó]n(es)?|letra|la|las|y la)\s+[A-H]\b/.test(notas[k]) &&
        !(porClave[k] || []).every(({q}) => q.notaEspecifica === true)) aviso(`${m.id}: la explicación "${k}" parece nombrar una letra`);
  }

  // consistencia cruzada entre temas
  let comparadas = 0;
  for (const k in porClave) {
    const lista = porClave[k];
    for (let a = 0; a < lista.length; a++) for (let b = a + 1; b < lista.length; b++) {
      const A = lista[a].q, B = lista[b].q;
      const bA = A.partes || [A], bB = B.partes || [B];
      if (bA.length !== bB.length) continue;
      bA.forEach((x, j) => {
        const y = bB[j];
        const sx = bancoAfirmaciones(x), sy = bancoAfirmaciones(y);
        if (sx !== sy) return;                      // es una variante con otras opciones: no se compara
        comparadas++;
        if (soluciones(x) !== soluciones(y))
          error(`clave "${k}": ${lista[a].aqui} y ${lista[b].aqui} tienen las mismas opciones pero distinta correcta${A.partes ? " (parte " + (j + 1) + ")" : ""}`);
      });
    }
  }
  console.log(`${m.id}: ${(m.examenes || []).length} exámenes, ${nt} temas, ${nq} consignas, ${Object.keys(notas).length} explicaciones, ${comparadas} comparaciones cruzadas`);
}

/* ---------- catálogo de resúmenes y PDF locales ---------- */
vm.runInContext(leer("resumenes/indice.js"), ctx, {filename: "resumenes/indice.js"});
const resumenes = ctx.RESUMENES;
const idsResumen = new Set();
for (const r of resumenes) {
  const aqui = `resumen ${r.id}`;
  if (!r.id || idsResumen.has(r.id)) error(`${aqui}: id vacío o repetido`);
  idsResumen.add(r.id);
  if (!idsMateria.has(r.materia)) error(`${aqui}: materia desconocida`);
  if (![1, 2].includes(r.parcial)) error(`${aqui}: parcial inválido`);
  for (const campo of ["nombre", "descripcion", "detalle", "formato"])
    if (typeof r[campo] !== "string" || !r[campo].trim()) error(`${aqui}: falta ${campo}`);
  if (!Number.isInteger(r.paginas) || r.paginas < 1) error(`${aqui}: páginas inválidas`);
  if (typeof r.archivo !== "string" || !/^resumenes\/[a-z0-9_/-]+\.pdf$/i.test(r.archivo) || r.archivo.includes("..")) {
    error(`${aqui}: ruta PDF local inválida`); continue;
  }
  const ruta = path.join(RAIZ, r.archivo);
  if (!fs.existsSync(ruta)) error(`${aqui}: no existe ${r.archivo}`);
  else if (fs.readFileSync(ruta).subarray(0, 5).toString() !== "%PDF-") error(`${aqui}: no es un PDF`);
}
console.log(`resúmenes: ${resumenes.length} PDF locales`);

/* ---------- sin URLs remotas ----------
   Única excepción: enlaces salientes que la persona abre a mano (no recursos
   que la app descarga). Solo se aceptan en index.html y con este texto exacto. */
const ENLACES_EXTERNOS = ["https://www.instagram.com/mondschatten.artesanias?exln=MWM2cGRiemNkcjd0bQ=="];
const archivosTexto = ["index.html", "sw.js", "manifest.webmanifest", "materias/indice.js", "resumenes/indice.js"].concat(CATALOGO.map(c => c.archivo));
for (const f of archivosTexto) {
  if (!fs.existsSync(path.join(RAIZ, f))) continue;
  let s = leer(f);
  if (f === "index.html") for (const enlace of ENLACES_EXTERNOS) s = s.split('"' + enlace + '"').join('""');
  const url = s.match(/\b(https?:)?\/\/[a-z0-9-]+\.[a-z0-9.-]+/i);
  if (url) error(`${f}: tiene una URL remota (${url[0]}); la app tiene que funcionar sin internet`);
}

/* ---------- archivos que guarda el service worker ---------- */
const sw = leer("sw.js");
const lista = (sw.match(/const ARCHIVOS = \[([\s\S]*?)\]/) || [])[1] || "";
for (const m of lista.matchAll(/"\.\/([^"]*)"/g)) {
  if (m[1] && !fs.existsSync(path.join(RAIZ, m[1]))) error(`sw.js: guarda "${m[1]}", que no existe`);
}
if (!/const VERSION = "[^"]+"/.test(sw)) error("sw.js: no encuentro VERSION");

/* ---------- resultado ---------- */
avisos.forEach(a => console.log("aviso: " + a));
errores.forEach(e => console.log("ERROR: " + e));
console.log(errores.length ? `\n${errores.length} error(es).` : "\nTodo en orden" + (avisos.length ? ` (${avisos.length} aviso/s).` : "."));
process.exit(errores.length ? 1 : 0);
