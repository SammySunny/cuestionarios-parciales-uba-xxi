/* Service worker de Cuestionarios Parciales UBA XXI
   Guarda la app en el dispositivo para que funcione sin internet.

   CADA VEZ QUE CAMBIES ALGO (una materia, index.html, íconos…), SUBÍ ESTE NÚMERO.
   Así los teléfonos detectan la versión nueva y muestran el aviso "Actualizar". */
const VERSION = "2026-10-22.1";

/* la lista de materias sale de materias/indice.js: no hace falta repetirla acá */
importScripts("materias/indice.js");
importScripts("resumenes/indice.js");

const PREFIJO = "cuestionarios-uba-xxi-";
const CACHE = PREFIJO + VERSION;
let cacheDesactivada = false;
const ARCHIVOS = [
  "./",
  "./index.html",
  "./manifest.webmanifest",
  "./materias/indice.js",
  "./resumenes/indice.js",
  "./iconos/icono.svg",
  "./iconos/icono-192.png",
  "./iconos/icono-512.png",
  "./iconos/icono-maskable-512.png",
  "./iconos/apple-touch-icon.png"
].concat(CATALOGO.map(m => "./" + m.archivo), RESUMENES.map(r => "./" + r.archivo));

self.addEventListener("install", ev => {
  // cache:"reload" saltea la caché HTTP, para no guardar una copia vieja de una materia
  ev.waitUntil(
    caches.open(CACHE).then(c =>
      Promise.all(ARCHIVOS.map(u =>
        fetch(new Request(u, {cache: "reload"})).then(r => {
          if (!r.ok) throw new Error("No se pudo bajar " + u);
          if (!cacheDesactivada) return c.put(u, r);
        })
      ))
    )
  );
  // no se activa solo: espera a que la persona toque "Actualizar"
});

self.addEventListener("message", ev => {
  if (ev.data && ev.data.tipo === "activar") self.skipWaiting();
  if (ev.data && ev.data.tipo === "borrar-cache") {
    cacheDesactivada = true;
    if (ev.ports[0]) ev.ports[0].postMessage({listo: true});
  }
});

self.addEventListener("activate", ev => {
  ev.waitUntil(
    caches.keys()
      .then(claves => Promise.all(
        claves.filter(k => k.startsWith(PREFIJO) && k !== CACHE).map(k => caches.delete(k))
      ))
      .then(() => self.clients.claim())
  );
});

/* primero lo guardado; si no está, la red */
self.addEventListener("fetch", ev => {
  if (cacheDesactivada) return;
  const req = ev.request;
  if (req.method !== "GET") return;
  const url = new URL(req.url);
  if (url.origin !== self.location.origin) return;

  ev.respondWith(
    caches.open(CACHE).then(c =>
      c.match(req, {ignoreSearch: true}).then(guardado => {
        if (guardado) return guardado;
        if (req.mode === "navigate" && !url.pathname.toLowerCase().endsWith(".pdf")) {
          return c.match("./index.html").then(idx => idx || fetch(req));
        }
        return fetch(req);
      })
    )
  );
});
