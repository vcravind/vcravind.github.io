#!/usr/bin/env python3
"""
Mini Jekyll-compatible renderer used for local previews while developing.
Not a full Liquid implementation — just covers the constructs this site uses.

Run:  python3 _preview_build.py
Output:  _preview/  (open _preview/index.html in your browser)
"""

import os, re, glob, shutil, datetime, html, sys
from pathlib import Path
import yaml
import markdown as md

ROOT = Path(__file__).parent
OUT  = ROOT / '_preview'

# ---- 1. Load config + data ----------------------------------------------------
with open(ROOT / '_config.yml') as f:
    site = yaml.safe_load(f)
site['baseurl'] = ''  # local preview doesn't use a baseurl
site['data'] = {}
for p in glob.glob(str(ROOT / '_data' / '*.yml')):
    site['data'][Path(p).stem] = yaml.safe_load(open(p))

# ---- 2. Helpers ---------------------------------------------------------------
def split_fm(s):
    if not s.startswith('---\n'):
        return {}, s
    end = s.index('\n---\n', 4)
    return yaml.safe_load(s[4:end]) or {}, s[end + 5:]

def resolve(expr, ctx):
    """Resolve a dotted path like site.author.name against ctx."""
    expr = expr.strip()
    if expr.startswith("'") and expr.endswith("'"): return expr.strip("'")
    if expr.startswith('"') and expr.endswith('"'): return expr.strip('"')
    parts = expr.split('.')
    cur = ctx
    for p in parts:
        if isinstance(cur, dict): cur = cur.get(p, '')
        elif hasattr(cur, p):     cur = getattr(cur, p)
        else: return ''
    return cur

DATE_FILTERS = {
    '"%B %-d, %Y"': '%B %-d, %Y',
    "'%B %-d, %Y'": '%B %-d, %Y',
    '"%b %-d, %Y"': '%b %-d, %Y',
    "'%b %-d, %Y'": '%b %-d, %Y',
    '"%Y"':         '%Y',
    "'%Y'":         '%Y',
}

def apply_filters(value, filters):
    for f in filters:
        f = f.strip()
        if f.startswith('date:'):
            fmt_arg = f[5:].strip()
            fmt = DATE_FILTERS.get(fmt_arg, fmt_arg.strip("'\""))
            if value == 'now' or value is None:
                value = datetime.datetime.now()
            if isinstance(value, (datetime.date, datetime.datetime)):
                value = value.strftime(fmt)
        elif f == 'date_to_xmlschema':
            if isinstance(value, (datetime.date, datetime.datetime)):
                value = value.strftime('%Y-%m-%dT%H:%M:%S')
        elif f.startswith('default:'):
            if not value:
                value = f[8:].strip().strip("'\"")
        elif f == 'relative_url':
            v = str(value)
            if v.startswith('/'):
                value = (site.get('baseurl') or '') + v
        elif f.startswith('truncate:'):
            n = int(f[9:].strip())
            v = str(value)
            value = v[:n] + '…' if len(v) > n else v
        elif f == 'strip_html':
            value = re.sub(r'<[^>]+>', '', str(value))
    return value

def render_expr(text, ctx):
    """Substitute {{ ... }} expressions with optional filter chains."""
    def sub(m):
        body = m.group(1).strip()
        parts = [p.strip() for p in body.split('|')]
        val = resolve(parts[0], ctx)
        val = apply_filters(val, parts[1:])
        if val is None: val = ''
        return str(val)
    return re.sub(r'{{\s*(.*?)\s*}}', sub, text)

def render_if(text, ctx):
    """Resolve {% if expr %}...{% [else] %}...{% endif %}, innermost first."""
    # The condition must NOT span tag boundaries (`%}`).
    # The body must NOT contain another `{% if `.
    pat = re.compile(
        r"{%\s*if\s+([^%]+?)\s*%}"
        r"((?:(?!{%\s*if\s).)*?)"
        r"{%\s*endif\s*%}",
        re.DOTALL)
    while pat.search(text):
        def repl(m):
            cond = m.group(1).strip()
            inner = m.group(2)
            # Split on else
            parts = re.split(r"{%\s*else\s*%}", inner, 1)
            yes = parts[0]
            no  = parts[1] if len(parts) > 1 else ''
            # Evaluate condition
            negated = False
            if cond.startswith('!'):
                negated = True; cond = cond[1:].strip()
            # Comparison?
            cm = re.match(r"(\S+)\s*(==|!=)\s*(.+)", cond)
            if cm:
                left = resolve(cm.group(1), ctx)
                op = cm.group(2)
                right = cm.group(3).strip().strip("'\"")
                truth = (str(left) == right) if op == '==' else (str(left) != right)
            else:
                truth = bool(resolve(cond, ctx))
            if negated: truth = not truth
            return yes if truth else no
        text = pat.sub(repl, text, count=1)
    return text

def render_for(text, ctx):
    """Resolve {% for x in y [limit:N] %}...{% endfor %}, outermost first.
    Uses a balanced matcher so nested fors are handled per outer iteration
    (inner fors may reference the outer loop variable)."""
    open_pat = re.compile(
        r"{%\s*for\s+(\w+)\s+in\s+([^\s%]+)(?:\s+limit:(\d+))?\s*%}")
    while True:
        m = open_pat.search(text)
        if not m: break
        # Walk forward counting fors and endfors to find this for's matching endfor.
        i = m.end()
        depth = 1
        for_re = re.compile(r"{%\s*for\s")
        end_re = re.compile(r"{%\s*endfor\s*%}")
        while i < len(text) and depth > 0:
            nxt_for = for_re.search(text, i)
            nxt_end = end_re.search(text, i)
            if not nxt_end: break
            if nxt_for and nxt_for.start() < nxt_end.start():
                depth += 1
                i = nxt_for.end()
            else:
                depth -= 1
                end_match = nxt_end
                i = nxt_end.end()
        if depth != 0:
            break  # unbalanced — give up to avoid infinite loop
        body = text[m.end():end_match.start()]
        var, src, limit = m.group(1), m.group(2), m.group(3)
        collection = resolve(src, ctx) or []
        if limit: collection = collection[:int(limit)]
        out = []
        for item in collection:
            inner_ctx = dict(ctx); inner_ctx[var] = item
            rendered = render_for(body, inner_ctx)
            rendered = render_if(rendered, inner_ctx)
            rendered = render_expr(rendered, inner_ctx)
            out.append(rendered)
        text = text[:m.start()] + ''.join(out) + text[end_match.end():]
    return text

def render_assign_and_groupby(text, ctx):
    """Handle {% assign x = y | group_by: 'k' | sort: 'name' | reverse %}.
    We only need to support the publications page's grouping pattern."""
    pat = re.compile(r"{%\s*assign\s+(\w+)\s*=\s*(.+?)\s*%}")
    for m in pat.finditer(text):
        var = m.group(1); rhs = m.group(2)
        parts = [p.strip() for p in rhs.split('|')]
        val = resolve(parts[0], ctx)
        for f in parts[1:]:
            if f.startswith('group_by:'):
                key = f.split(':',1)[1].strip().strip("'\"")
                groups = {}
                for it in val:
                    k = it.get(key)
                    groups.setdefault(k, []).append(it)
                val = [{'name': str(k), 'items': v} for k, v in groups.items()]
            elif f.startswith('sort:'):
                key = f.split(':',1)[1].strip().strip("'\"")
                val = sorted(val, key=lambda x: x.get(key, ''))
            elif f == 'reverse':
                val = list(reversed(val))
        ctx[var] = val
    return pat.sub('', text)

def render_includes(text):
    return re.sub(r"{%\s*include\s+(\S+?)\s*%}",
                  lambda m: open(ROOT / '_includes' / m.group(1)).read(),
                  text)

def strip_raw(text):
    """{% raw %}...{% endraw %} → keep contents, but escape any liquid inside."""
    return re.sub(r"{%\s*raw\s*%}(.*?){%\s*endraw\s*%}",
                  lambda m: m.group(1), text, flags=re.DOTALL)

def render(text, ctx):
    text = strip_raw(text)
    # Normalize whitespace-trim variants ({%- ... -%}) into ({% ... %})
    text = re.sub(r"{%-\s*", "{% ", text)
    text = re.sub(r"\s*-%}", " %}", text)
    text = re.sub(r"{{-\s*", "{{ ", text)
    text = re.sub(r"\s*-}}", " }}", text)
    # Strip jekyll-seo-tag (we don't simulate it in preview)
    text = re.sub(r"{%\s*seo[^%]*%}", "", text)
    text = render_assign_and_groupby(text, ctx)
    text = render_for(text, ctx)
    text = render_if(text, ctx)
    text = render_expr(text, ctx)
    return text

def apply_layout(content, layout_name, page, posts):
    layout_path = ROOT / '_layouts' / f'{layout_name}.html'
    if not layout_path.exists():
        return content
    src = open(layout_path).read()
    fm, body = split_fm(src)
    body = render_includes(body)
    body = body.replace('{{ content }}', content)
    ctx = {'site': {**site, 'posts': posts}, 'page': page, 'content': content}
    out = render(body, ctx)
    if fm.get('layout'):
        return apply_layout(out, fm['layout'], page, posts)
    return out

# ---- 3. Collect posts --------------------------------------------------------
posts = []
for p in sorted(glob.glob(str(ROOT / '_posts' / '*.md')), reverse=True):
    s = open(p).read()
    fm, body = split_fm(s)
    name = Path(p).name
    m = re.match(r'(\d{4})-(\d{2})-(\d{2})-(.+)\.md', name)
    y, mo, d, slug = m.groups()
    fm['date'] = datetime.datetime(int(y), int(mo), int(d))
    fm['url']  = f"/blog/{y}/{mo}/{d}/{slug}/"
    fm['_path'] = p
    fm['_body'] = body
    fm['_slug'] = slug
    fm['title']    = fm.get('title', '')
    fm['subtitle'] = fm.get('subtitle', '')
    fm['excerpt']  = body.split('\n\n')[0]
    posts.append(fm)

# Add prev/next
for i, p in enumerate(posts):
    p['previous'] = posts[i+1] if i+1 < len(posts) else {'url': '', 'title': ''}
    p['next']     = posts[i-1] if i > 0 else {'url': '', 'title': ''}

# ---- 4. Render every page ---------------------------------------------------
OUT.mkdir(exist_ok=True)
# Wipe previous
for f in OUT.rglob('*'):
    if f.is_file(): f.unlink()
for f in sorted(OUT.rglob('*'), reverse=True):
    if f.is_dir(): f.rmdir()
OUT.mkdir(exist_ok=True)

# Copy assets
shutil.copytree(ROOT / 'assets', OUT / 'assets')

MD_EXT = ['extra', 'fenced_code', 'codehilite', 'tables', 'toc', 'sane_lists']

def write_html(rel_path, html_text):
    out_path = OUT / rel_path
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, 'w') as f:
        f.write(html_text)

def localize_links(s):
    """Rewrite Jekyll-style permalinks to local file paths so the preview is clickable."""
    # Drop the RSS feed link (no feed in static preview)
    s = re.sub(r'<link rel="alternate"[^>]*?feed\.xml[^>]*?>', '', s)
    s = re.sub(r'href="/"',                          'href="index.html"', s)
    s = re.sub(r'href="/publications/"',             'href="publications.html"', s)
    s = re.sub(r'href="/projects/"',                 'href="projects.html"', s)
    s = re.sub(r'href="/blog/"',                     'href="blog.html"', s)
    s = re.sub(r'href="/cv/"',                       'href="cv.html"', s)
    s = re.sub(r'href="/contact/"',                  'href="contact.html"', s)
    s = re.sub(r'href="/contact/#?"',                'href="contact.html"', s)
    # Blog post links: /blog/YYYY/MM/DD/slug/  → blog/YYYY-MM-DD-slug.html
    def post_link(m):
        return f'href="blog/{m.group(1)}-{m.group(2)}-{m.group(3)}-{m.group(4)}.html"'
    s = re.sub(r'href="/blog/(\d{4})/(\d{2})/(\d{2})/([^"/]+)/?"', post_link, s)
    # Asset paths
    s = re.sub(r'(href|src)="/assets/', r'\1="assets/', s)
    s = re.sub(r'(href|src)="\.\./assets/', r'\1="assets/', s)
    return s

def render_page(src_path, out_rel, default_layout='page', extra_page=None):
    s = open(src_path).read()
    fm, body = split_fm(s)
    page = {**fm}
    page.setdefault('title', fm.get('title', ''))
    page.setdefault('subtitle', fm.get('subtitle', ''))
    page.setdefault('description', fm.get('description', site.get('description','')))
    if extra_page: page.update(extra_page)

    # Render Liquid in the body BEFORE markdown
    ctx = {'site': {**site, 'posts': posts}, 'page': page, 'paginator': None}
    body = render(body, ctx)
    # Markdown if it's a .md file
    if str(src_path).endswith('.md'):
        body = md.markdown(body, extensions=MD_EXT)

    layout = fm.get('layout', default_layout)
    final = apply_layout(body, layout, page, posts)
    final = localize_links(final)
    # Adjust asset paths for nested files
    if '/' in out_rel:
        depth = out_rel.count('/')
        prefix = '../' * depth
        final = re.sub(r'(href|src)="assets/', f'\\1="{prefix}assets/', final)
        # And nav links from nested page need ../
        for href in ['index.html','publications.html','projects.html','blog.html','cv.html','contact.html']:
            final = re.sub(rf'href="{href}"', f'href="{prefix}{href}"', final)
    write_html(out_rel, final)

# Top-level pages
render_page(ROOT / 'index.html',       'index.html',       default_layout='default')
render_page(ROOT / 'publications.md',  'publications.html')
render_page(ROOT / 'projects.md',      'projects.html')
render_page(ROOT / 'blog.html',        'blog.html')
render_page(ROOT / 'cv.md',            'cv.html')
render_page(ROOT / 'contact.md',       'contact.html')
render_page(ROOT / '404.html',         '404.html', default_layout='default')

# Posts → blog/YYYY-MM-DD-slug.html
for p in posts:
    rel = f"blog/{p['date'].strftime('%Y-%m-%d')}-{p['_slug']}.html"
    s = open(p['_path']).read()
    fm, body = split_fm(s)
    body_html = md.markdown(strip_raw(body), extensions=MD_EXT)
    page = {**fm, 'date': p['date'], 'url': p['url'], 'title': p['title'],
            'subtitle': p.get('subtitle',''), 'previous': p['previous'], 'next': p['next']}
    final = apply_layout(body_html, 'post', page, posts)
    final = localize_links(final)
    final = re.sub(r'(href|src)="assets/', r'\1="../assets/', final)
    for href in ['index.html','publications.html','projects.html','blog.html','cv.html','contact.html']:
        final = re.sub(rf'href="{href}"', f'href="../{href}"', final)
    # Fix prev/next post links to be sibling files in same dir
    final = re.sub(r'href="../blog/(\d{4})-(\d{2})-(\d{2})-([^"]+?)\.html"',
                   r'href="\1-\2-\3-\4.html"', final)
    write_html(rel, final)

print(f"Wrote preview to {OUT}")
print(f"Open {OUT / 'index.html'} in your browser.")
