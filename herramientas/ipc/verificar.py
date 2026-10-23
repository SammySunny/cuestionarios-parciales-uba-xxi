#!/usr/bin/env python3
"""Control editorial estructural: contenido PDF, cobertura, catálogo y copias.

No sustituye la lectura conceptual ni la revisión visual. --imagenes genera
previsualizaciones en un directorio temporal indicado explícitamente.
"""
import argparse
import json
from pathlib import Path
import re
import subprocess
import unicodedata

import pymupdf

from generar import DATA, FILES, HERE, OUT, ROOT


def norm(text):
    return ''.join(c for c in unicodedata.normalize('NFKC', text).casefold() if c.isalnum())


def js_json(node, source):
    result = subprocess.run([node, '-e', source], cwd=ROOT,
                            check=True, text=True, stdout=subprocess.PIPE)
    return json.loads(result.stdout)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--node', default='node')
    parser.add_argument('--copias', type=Path)
    parser.add_argument('--imagenes', type=Path)
    args = parser.parse_args()
    if args.imagenes:
        if not args.imagenes.parent.is_dir():
            parser.error('El directorio padre de --imagenes debe existir.')
        args.imagenes.mkdir(exist_ok=True)

    # Se evalúan los JS reales, sin depender de regex para reconstruir el banco.
    catalog = js_json(args.node, "const fs=require('fs'),vm=require('vm');let c={};vm.createContext(c);vm.runInContext(fs.readFileSync('resumenes/indice.js','utf8'),c);console.log(JSON.stringify(c.RESUMENES));")
    banco = js_json(args.node, "const fs=require('fs'),vm=require('vm');let m;vm.runInNewContext(fs.readFileSync('materias/ipc.js','utf8'),{registrarMateria:x=>m=x});console.log(JSON.stringify(m));")
    coverage = json.loads((HERE / 'cobertura.json').read_text())
    ids = {f['id'] for f in DATA['fichas']}
    assert len(ids) == len(DATA['fichas']), 'IDs de ficha repetidos'
    official = {f[0] for f in DATA['fuentes']}
    assert all(f['fuentes'] and f['ramas'] and f['ejemplo'] and f['cuidado'] for f in DATA['fichas'])
    assert {'G6', 'G7', 'G8', 'G9', 'G10E', 'G10P'} <= official

    exam = next(e for e in banco['examenes'] if e['id'] == coverage['examen'])
    seen = set()
    for pair in coverage['pares']:
        assert len(pair['temas']) == len(pair['fuentes'])
        for tid, filename in zip(pair['temas'], pair['fuentes']):
            theme = next(t for t in exam['temas'] if t['id'] == tid)
            assert theme['fuente'] == filename, f'Fuente desalineada: {tid}'
            assert set(pair['ejercicios']) == {q['e'] for q in theme['qs']}
            for q in theme['qs']:
                ref = pair['ejercicios'][q['e']]
                key = tid, q['e']
                assert key not in seen, f'Cobertura repetida: {key}'
                seen.add(key)
                assert ref['criterio'] and ref['fichas'] and set(ref['fichas']) <= ids
    assert seen == {(t['id'], q['e']) for t in exam['temas'] for q in t['qs']}
    assert len(seen) == 80
    for entry in coverage['historicos']:
        assert set(entry['fichas']) <= ids and entry['necesidad']
    print(f'Cobertura: {len(seen)} consignas de 2026; {len(coverage["historicos"])} referencias históricas; {len(ids)} fichas.')

    for mode, filename in FILES.items():
        path = OUT / filename
        doc = pymupdf.open(path)
        text = '\n'.join(p.get_text() for p in doc)
        flat = norm(text)
        assert '\ufffd' not in text, f'Caracteres de sustitución: {filename}'
        # Comprobar texto completo, no solo la presencia de palabras clave.
        for f in DATA['fichas']:
            for field in ['idea', 'ejemplo', 'cuidado']:
                assert norm(f[field]) in flat, f'{filename}: falta {f["id"]}/{field}'
            for label, value in f['ramas']:
                assert norm(value) in flat, f'{filename}: rama incompleta {f["id"]}/{label}'
        toc = doc.get_toc()
        assert len(toc) >= len(ids), f'Faltan marcadores en {filename}'
        for _, title, page in toc:
            assert 1 <= page <= len(doc)
            title_without_number = re.sub(r'^\d+\s*·\s*', '', title)
            if 'sigue' not in title_without_number:
                assert norm(title_without_number) in norm(doc[page - 1].get_text()), f'Marcador incorrecto: {title}'
        for i, page in enumerate(doc):
            assert len(page.get_text().split()) > 15, f'Página casi vacía {filename}/{i + 1}'
            assert f'{i + 1} / {len(doc)}' in page.get_text(), f'Pie de página incorrecto: {filename}/{i + 1}'
            spans = [s for b in page.get_text('dict')['blocks'] if 'lines' in b for l in b['lines'] for s in l['spans']]
            for span in spans:
                x0, y0, x1, y1 = span['bbox']
                assert x0 >= 0 and y0 >= 0 and x1 <= page.rect.width + .5 and y1 <= page.rect.height + .5, f'Texto cortado: {filename}/{i+1}'
            if args.imagenes:
                page.get_pixmap(matrix=pymupdf.Matrix(1, 1)).save(str(args.imagenes / f'{mode}-{i+1:03d}.png'))
        record = next(r for r in catalog if Path(r['archivo']).name == filename)
        assert record['paginas'] == len(doc), f'{filename}: catálogo={record["paginas"]}, real={len(doc)}'
        if mode == 'celular':
            assert doc[0].rect.width == 360 and doc[0].rect.height == 720
        if args.copias:
            assert path.read_bytes() == (args.copias / filename).read_bytes(), f'Copia de estudio diferente: {filename}'
        print(f'{filename}: {len(doc)} páginas, contenido completo, marcadores y límites correctos.')
    print('Controles estructurales terminados. Completar con revisión visual y conceptual.')


if __name__ == '__main__':
    main()
