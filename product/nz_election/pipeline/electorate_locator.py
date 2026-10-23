"""Small, bounded locators derived from the reviewed Stats NZ geometry."""
from functools import cache
from html import escape
from .geography import projected
from .snapshot_views import load

LOCATOR_BYTE_CAP = 24000


@cache
def paths():
    shapes = {r['electorate_slug']: projected(r['geometry']) for r in load('boundaries-2025')}
    points = [p for polys in shapes.values() for poly in polys for ring in poly for p in ring]
    xmin, xmax = min(x for x, _ in points), max(x for x, _ in points)
    ymin, ymax = min(y for _, y in points), max(y for _, y in points)
    scale = min(280 / (xmax - xmin), 180 / (ymax - ymin))
    result = {}
    for slug, polys in shapes.items():
        commands = []
        for poly in polys:
            for ring in poly:
                rounded = []
                for x, y in ring:
                    p = (round((x-xmin)*scale+10), round((ymax-y)*scale+10))
                    if not rounded or rounded[-1] != p:
                        rounded.append(p)
                # Retain tiny components as points in the highlighted locator.
                commands.append('M' + ' '.join(f'{x},{y}' for x, y in rounded) + 'Z')
        result[slug] = ''.join(commands)
    outline = ''.join(result[r['electorate_slug']] for r in load('boundaries-2025') if r['group'] == 'general')
    return result, outline


def locator(row):
    shapes, outline = paths()
    graphic = ('<svg class="electorate-locator" viewBox="0 0 300 200" role="img" '
               'aria-describedby="source-boundaries-2025" aria-label="' + escape(row['name']) + ' locator on New Zealand">'
               f'<path fill="var(--rule)" d="{outline}"/>'
               f'<path data-electorate="{row["slug"]}" fill="var(--ink)" stroke="var(--ink)" stroke-width="1" fill-rule="evenodd" d="{shapes[row["slug"]]}"/></svg>')
    if len(graphic.encode()) > LOCATOR_BYTE_CAP:
        raise ValueError('LOCATOR_BYTE_CAP')
    return graphic
