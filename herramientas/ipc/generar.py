#!/usr/bin/env python3
"""Genera los cuatro resúmenes desde contenido.json, sin acceso al Campus.

Uso: python herramientas/ipc/generar.py [--copiar-a DIRECTORIO_EXISTENTE]
Requiere ReportLab y DejaVu Sans; ver README.md en esta carpeta.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    BaseDocTemplate, Flowable, Frame, KeepTogether, PageBreak, PageTemplate,
    Paragraph, SimpleDocTemplate, Spacer,
)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = ROOT / 'resumenes/ipc/2do-parcial'
DATA = json.loads((HERE / 'contenido.json').read_text())
FILES = {
    'texto': 'Resumen_textual_2do_parcial.pdf',
    'guia': 'Resumen_textual_cuadros_2do_parcial.pdf',
    'cuadro': 'Cuadro_Sinoptico_IPC_2do_Parcial.pdf',
    'celular': 'Cuadro_Sinoptico_IPC_Celular.pdf',
}
COLORS = {'10': '#1d4ed8', '11': '#047857', '12': '#7c3aed',
          '13': '#be185d', '14': '#a34a09', '15': '#b91c1c',
          'Complemento': '#475569'}
INK = colors.HexColor('#203247')
GRAY = colors.HexColor('#526579')


def register_fonts(directory=None):
    candidates = [Path(directory)] if directory else [
        Path('/usr/share/fonts/TTF'), Path('/usr/share/fonts/truetype/dejavu')]
    directory = next((p for p in candidates if (p / 'DejaVuSans.ttf').exists()), None)
    if directory is None:
        raise SystemExit('Falta DejaVu Sans: instalá la fuente o usá --fuentes DIRECTORIO.')
    for name, filename in [('DV', 'DejaVuSans.ttf'), ('DV-B', 'DejaVuSans-Bold.ttf')]:
        pdfmetrics.registerFont(TTFont(name, str(directory / filename)))
    pdfmetrics.registerFontFamily('DV', normal='DV', bold='DV-B')


class Title(Paragraph):
    def __init__(self, text, style, key):
        super().__init__(text, style)
        self.key = key
        self.plain_title = self.getPlainText()


class Bookmarks:
    def afterFlowable(self, flowable):
        if isinstance(flowable, Title):
            self.canv.bookmarkPage(flowable.key)
            self.canv.addOutlineEntry(flowable.plain_title, flowable.key, 0, False)


class Document(Bookmarks, SimpleDocTemplate):
    pass


class ChartDocument(Bookmarks, BaseDocTemplate):
    pass


class NumberedCanvas(canvas.Canvas):
    """Total real de páginas, también cuando una ficha ocupa más de una."""
    def __init__(self, *args, **kwargs):
        kwargs['invariant'] = True
        super().__init__(*args, **kwargs)
        self.states = []
        self.bookmark_targets = {}

    def bookmarkPage(self, key, *args, **kwargs):
        self.bookmark_targets[key] = (self._pageNumber, args, kwargs)
        return super().bookmarkPage(key, *args, **kwargs)

    def showPage(self):
        self.states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        total = len(self.states)
        targets = dict(self.bookmark_targets)
        for state in self.states:
            self.__dict__.update(state)
            # Al diferir showPage, ReportLab todavía no había emitido las páginas:
            # volver a fijar destinos durante la emisión evita que todos apunten a 1.
            for key, (number, args, kwargs) in targets.items():
                if number == self._pageNumber:
                    super().bookmarkPage(key, *args, **kwargs)
            width, _ = self._pagesize
            self.setFillColor(GRAY)
            self.setFont('DV', 8)
            self.drawString(24, 17, 'IPC · Buacar · Revisión ' + DATA['revision'])
            self.drawRightString(width - 24, 17, f'{self._pageNumber} / {total}')
            super().showPage()
        super().save()


class Branch(Flowable):
    """Llave lateral y texto: etiqueta → explicación, sin rasterizar."""
    def __init__(self, label, text, style, color, shaded=False):
        super().__init__()
        self.p = Paragraph('<b>' + escape(label) + '</b> · ' + escape(text), style)
        self.color = colors.HexColor(color)
        self.shaded = shaded
        self.padding = getattr(style, 'branchPadding', 13)

    def wrap(self, width, height):
        self.width = width
        _, ph = self.p.wrap(width - 23, 10000)
        self.height = ph + self.padding
        return self.width, self.height

    def split(self, width, height):
        # Cada rama permanece completa. Los saltos se hacen entre ramas.
        return []

    def draw(self):
        c = self.canv
        if self.shaded:
            c.setFillColor(colors.HexColor('#eff4f9'))
            c.roundRect(14, 1, self.width - 14, self.height - 2, 4, fill=1, stroke=0)
        c.setStrokeColor(self.color)
        c.setLineWidth(1.2)
        p = c.beginPath()
        mid = self.height / 2
        p.moveTo(10, self.height - 3)
        p.curveTo(5, self.height - 3, 5, self.height - 3, 5, self.height - 8)
        p.lineTo(5, mid + 4)
        p.curveTo(5, mid, 5, mid, 1, mid)
        p.curveTo(5, mid, 5, mid, 5, mid - 4)
        p.lineTo(5, 8)
        p.curveTo(5, 3, 5, 3, 10, 3)
        c.drawPath(p)
        self.p.drawOn(c, 20, self.padding / 2)


def styles(mode):
    fs, lead = {'texto': (10.5, 14.6), 'guia': (11, 15.5),
                'cuadro': (10.8, 14.2), 'celular': (13.5, 18.7)}[mode]
    return {
        'body': ParagraphStyle('body', fontName='DV', fontSize=fs, leading=lead,
                               textColor=INK, spaceAfter=6, branchPadding=9 if mode == 'cuadro' else 13),
        'title': ParagraphStyle('title', fontName='DV-B', fontSize=19 if mode == 'celular' else 15,
                                leading=24 if mode == 'celular' else 19,
                                textColor=INK, spaceAfter=8, keepWithNext=True),
        'small': ParagraphStyle('small', fontName='DV', fontSize=10 if mode == 'celular' else 8,
                                leading=14 if mode == 'celular' else 11,
                                textColor=GRAY, spaceAfter=7),
        'intro': ParagraphStyle('intro', fontName='DV', fontSize=fs, leading=lead,
                                textColor=INK, spaceAfter=9),
    }


def header(c, doc):
    width, height = doc.pagesize
    c.saveState()
    c.setFillColor(GRAY)
    c.setFont('DV', 8)
    c.drawString(doc.leftMargin, height - 20, 'SEGUNDO PARCIAL · CÁTEDRA A')
    c.drawRightString(width - doc.rightMargin, height - 20,
                      '2026' if width < 400 else 'Capítulos 10–15 + complemento histórico')
    c.restoreState()


def title_for(ficha, index, st, cont=False):
    prefix = f'{index:02d}'
    text = prefix + ' · ' + ficha['titulo'] + (' (continuación)' if cont else '')
    return Title(escape(text), st['title'], ficha['id'] + ('-cont' if cont else ''))


def card(ficha, index, mode):
    st = styles(mode)
    color = COLORS[ficha['capitulo']]
    cap = ('Complemento histórico' if ficha['capitulo'] == 'Complemento'
           else 'Capítulo ' + ficha['capitulo'])
    result = [Paragraph(cap, st['small']), title_for(ficha, index, st),
              Paragraph(escape(ficha['idea']), st['intro'])]
    if mode == 'texto':
        # Párrafos compactos, pero con las mismas distinciones y ejemplos.
        for label, text in ficha['ramas']:
            result.append(Paragraph('<b>' + escape(label) + '.</b> ' + escape(text), st['body']))
        for label, text in [('Ejemplo', ficha['ejemplo']), ('Cuidado', ficha['cuidado'])]:
            result.append(Paragraph('<b>' + label + '.</b> ' + escape(text), st['body']))
    else:
        result.extend(Branch(label, text, st['body'], color) for label, text in ficha['ramas'])
        result.append(Branch('Ejemplo', ficha['ejemplo'], st['body'], color, True))
        result.append(Branch('En el parcial', ficha['cuidado'], st['body'], color, True))
    result += [Spacer(1, 3), Paragraph('Referencia: ' + escape(' · '.join(ficha['fuentes'])), st['small']),
               Spacer(1, 6 if mode == 'cuadro' else 12)]
    return result


def orientation(mode):
    st = styles(mode)
    result = [Title('IPC · Guía para estudiar y resolver', st['title'], 'orientacion'),
              Paragraph(escape(DATA['alcance']), st['small'])]
    paragraphs = [
        ('Qué cambió', 'Esta revisión corrige los resúmenes iniciales y amplía las distinciones necesarias para justificar respuestas. Se contrastó con seis guías oficiales de actividades y sus devoluciones, cinco mapas del Campus y los parciales locales, con prioridad en mayo de 2026.'),
        ('Cómo usarlo', 'Leé la idea central, reconocé el criterio de cada rama y probalo en el ejemplo. Luego resolvé un caso nuevo sin mirar la clave y justificá por qué descartás las alternativas.'),
        ('Alcance actual', 'El cronograma 2C2026 ubica los capítulos 10–15 después del primer parcial. Darwin y Lamarck se mantienen en un complemento identificado porque aparecen en segundos parciales históricos de 2025.'),
        ('Formato de 2026', 'En los ejercicios de dos partes deben estar bien ambas respuestas. El ejercicio 10 pide dos selecciones; una sola correcta no basta. Las opciones cambian de orden entre temas: estudiá el criterio, no su número.'),
        ('Fuentes', 'Las referencias G6, G7, G8, G9, G10E y G10P remiten a guías oficiales del Campus consultadas el 23/10/2026. Al final hay un mapa por ejercicio y enlaces a las fuentes. El contenido es una síntesis de estudio, no una publicación oficial ni una garantía sobre futuros exámenes.'),
    ]
    for label, text in paragraphs:
        result.append(Paragraph('<b>' + label + '.</b> ' + escape(text), st['body']))
        result.append(Spacer(1, 5))
    return result


def reference_groups(mode):
    st = styles(mode)
    result = []
    groups = [
        ('Mapa del parcial 2026 · ejercicios 1–5', [
            ('1 · Investigación', 'Fichas 04–05: HF en T1–2, HA en T3–4 y T7–8, CO en T5–6. Justificá función, alcance y respaldo.'),
            ('2 · Resultado favorable', 'Ficha 06: afirmación del consecuente; no prueba la verdad de la hipótesis.'),
            ('3 · Explicación', 'Fichas 08–09: tipo de ley, condición pertinente y hecho a explicar; no seleccionar una predicción futura.'),
            ('4 · Filosofía clásica', 'Fichas 10–12: corroboración, universales, falsabilidad y grado de confirmación, según el tema.'),
            ('5 · Kuhn aplicado', 'Fichas 13–15: ciencia normal, anomalía, preciencia o inconmensurabilidad lingüística.')]),
        ('Mapa del parcial 2026 · ejercicios 6–10', [
            ('6 · Kuhn conceptual', 'Fichas 13–15: matriz compartida, paradigma más amplio que teoría, progreso normal y anomalía sin crisis automática.'),
            ('7 · Sexismo', 'Fichas 16–18: Stevens → omisión; ensayos solo en varones → aplicaciones; astrónomas → marginación; hormonas → conceptos.'),
            ('8 · Corrientes feministas', 'Fichas 19–21: compará tesis aceptada por una corriente y rechazada por otra; situado no es un criterio diferenciador suficiente.'),
            ('9 · Financiación', 'Fichas 28–30: objetivo del proyecto y razón de prioridad, sin confundir ética de los usos con política científica.'),
            ('10 · Hechos y valores', 'Ficha 22: reconocer evaluaciones sin «debe» y seleccionar las dos opciones requeridas.')]),
    ]
    for heading, entries in groups:
        result.append((heading, entries))
    result.append(('Fuentes oficiales · programa y guías', [
        (code, desc + ' Acceso: enlace del Campus.') for code, desc, url in DATA['fuentes']]))
    result.append(('Cobertura y lectura crítica', [
        ('2026', 'Banco local: 29/05/2026, Buacar, Temas 1–8, 80 consignas. Se cotejaron especialmente las opciones y devoluciones de HF/HA/CO, feminismos y categorías de sexismo.'),
        ('Históricos', 'Buacar: 02/06/2023, 31/05/2024, 25/10/2024, 30/05/2025 y recuperatorio 30/10/2025. Se conservan selección de premisas normativas, resultados según corriente, financiación negativa y evolución.'),
        ('Qué no inferir', 'La presencia en el temario no equivale a frecuencia de examen. Integridad, investigación y humanidades se incluyen por las actividades oficiales, aunque no ocupen el mismo lugar en mayo de 2026.'),
        ('Control de fuentes', 'Las guías y las claves también pueden contener simplificaciones o erratas. Se explicita el uso del esquema H → CO frente al esquema con auxiliares. No se reproducen como hechos ejemplos editoriales erróneos ni datos institucionales desactualizados.')]))
    return result


def references(mode):
    st = styles(mode)
    result = []
    urls = {code: url for code, desc, url in DATA['fuentes']}
    for n, (title, entries) in enumerate(reference_groups(mode)):
        result.append(Title(title, st['title'], 'referencias-' + str(n)))
        for label, text in entries:
            if label in urls:
                label_html = '<a href="' + escape(urls[label], {'"': '&quot;'}) + '" color="#1d4ed8">' + escape(label) + '</a>'
            else:
                label_html = escape(label)
            result.append(Paragraph('<b>' + label_html + '.</b> ' + escape(text), st['body']))
        result.append(Spacer(1, 14))
    return result


def build_flowing(mode):
    doc = Document(str(OUT / FILES[mode]), pagesize=A4, leftMargin=42, rightMargin=42,
                   topMargin=38, bottomMargin=38, title='IPC · ' + mode + ' · Revisión 2026',
                   author='Material de estudio independiente')
    story = orientation(mode) + [PageBreak()]
    for i, ficha in enumerate(DATA['fichas'], 1):
        parts = card(ficha, i, mode)
        # Título, idea y primera explicación juntos; luego se puede continuar
        # sin forzar una página casi vacía por ficha.
        story.append(KeepTogether(parts[:4]))
        story.extend(parts[4:])
    story.append(PageBreak())
    story.extend(references(mode))
    doc.build(story, onFirstPage=header, onLaterPages=header, canvasmaker=NumberedCanvas)


def height_of(item, width):
    return item.getSpaceBefore() + item.wrap(width, 10000)[1] + item.getSpaceAfter()


def pack_mobile():
    mode = 'celular'
    st = styles(mode)
    # 360 pt de ancho: entra en la pantalla en vertical; texto de 13,5 pt.
    width = 360 - 2 * 20 - 12
    available = 720 - 36 - 38 - 12
    pages = []

    def pack(blocks, heading, key):
        current = []
        used = 0
        for block in blocks:
            h = height_of(block, width)
            if h > available:
                raise ValueError(f'Bloque demasiado alto para celular: {heading}')
            if current and used + h > available:
                pages.append(current)
                continued = Title(escape(heading) + ' · sigue', st['title'], key + '-sigue-' + str(len(pages)))
                current = [continued]
                used = height_of(continued, width)
            if used + h > available:
                raise ValueError('La continuación no deja espacio para el bloque')
            current.append(block)
            used += h
        if current:
            pages.append(current)

    pack(orientation(mode), 'Cómo usar este resumen', 'uso')
    for i, ficha in enumerate(DATA['fichas'], 1):
        parts = card(ficha, i, mode)
        # La etiqueta de capítulo, título e idea no deben quedar solos.
        # KeepTogether.wrap devuelve una altura sentinela: se mide como bloque real.
        first = FixedGroup(parts[:4])
        pack([first] + parts[4:], ficha['titulo'], ficha['id'])
    urls = {code: url for code, desc, url in DATA['fuentes']}
    for n, (title, entries) in enumerate(reference_groups(mode)):
        blocks = [Title(title, st['title'], 'ref-movil-' + str(n))]
        for label, text in entries:
            if label in urls:
                text += ' Consultar en Campus.'
                blocks.append(Paragraph('<b><a href="' + escape(urls[label], {'"': '&quot;'}) + '">' + escape(label) + '</a>.</b> ' + escape(text), st['body']))
            else:
                blocks.append(Paragraph('<b>' + escape(label) + '.</b> ' + escape(text), st['body']))
            blocks.append(Spacer(1, 6))
        pack(blocks, title, 'ref-' + str(n))
    return pages


class FixedGroup(Flowable):
    """Bloque pequeño indivisible con medición real (para paginación móvil)."""
    def __init__(self, parts):
        super().__init__()
        self.parts = parts

    def wrap(self, width, height):
        self.width = width
        self.height = sum(height_of(p, width) for p in self.parts)
        return width, self.height

    def draw(self):
        y = self.height
        for p in self.parts:
            y -= p.getSpaceBefore()
            _, h = p.wrap(self.width, 10000)
            y -= h
            if isinstance(p, Title):
                self.canv.bookmarkPage(p.key)
                self.canv.addOutlineEntry(p.plain_title, p.key, 0, False)
            p.drawOn(self.canv, 0, y)
            y -= p.getSpaceAfter()


def build_mobile():
    doc = Document(str(OUT / FILES['celular']), pagesize=(360, 720), leftMargin=20,
                   rightMargin=20, topMargin=36, bottomMargin=38,
                   title='IPC · Cuadro sinóptico para celular · Revisión 2026',
                   author='Material de estudio independiente')
    story = []
    for page in pack_mobile():
        if story:
            story.append(PageBreak())
        story.extend(page)
    doc.build(story, onFirstPage=header, onLaterPages=header, canvasmaker=NumberedCanvas)


def build_chart():
    mode = 'cuadro'
    width, height = landscape(A4)
    doc = ChartDocument(str(OUT / FILES[mode]), pagesize=(width, height),
                        leftMargin=25, rightMargin=25, topMargin=38, bottomMargin=35,
                        title='IPC · Cuadro sinóptico · Revisión 2026',
                        author='Material de estudio independiente')
    gutter = 24
    cw = (width - 50 - gutter) / 2
    frames = [Frame(25 + col * (cw + gutter), 35, cw, height - 73,
                    id='col-' + str(col), leftPadding=5, rightPadding=5,
                    topPadding=5, bottomPadding=5) for col in range(2)]
    doc.addPageTemplates(PageTemplate(id='cuadro', frames=frames, onPage=header))
    story = orientation(mode) + [PageBreak()]
    for i, ficha in enumerate(DATA['fichas'], 1):
        parts = card(ficha, i, mode)
        content_height = sum(height_of(p, cw - 10) for p in parts)
        if content_height > height - 83:
            raise ValueError(f'Ficha no entra en la columna del cuadro: {ficha["id"]} ({content_height:.1f} pt)')
        story.append(KeepTogether(parts))
    story += [PageBreak()] + references(mode)
    doc.build(story, canvasmaker=NumberedCanvas)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--copiar-a', type=Path)
    parser.add_argument('--fuentes', help='Directorio que contiene DejaVuSans.ttf y DejaVuSans-Bold.ttf')
    args = parser.parse_args()
    if not OUT.is_dir():
        parser.error(f'No existe la carpeta de salida: {OUT}')
    if args.copiar_a and not args.copiar_a.is_dir():
        parser.error('La carpeta --copiar-a debe existir antes de generar.')
    register_fonts(args.fuentes)
    for mode in ['texto', 'guia']:
        build_flowing(mode)
    build_chart()
    build_mobile()
    for filename in FILES.values():
        path = OUT / filename
        if args.copiar_a:
            shutil.copyfile(path, args.copiar_a / filename)
            assert path.read_bytes() == (args.copiar_a / filename).read_bytes()
        print(filename, hashlib.sha256(path.read_bytes()).hexdigest())


if __name__ == '__main__':
    main()
