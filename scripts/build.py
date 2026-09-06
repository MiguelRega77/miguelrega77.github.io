import re, html, shutil
from pathlib import Path
import mistune

ROOT = Path(__file__).resolve().parents[1]
POSTS = ROOT / 'content' / 'posts'
PUBLIC = ROOT / 'public'

md = mistune.create_markdown(
    escape=False,
    plugins=['strikethrough', 'footnotes', 'table', 'task_lists']
)


def frontmatter(raw):
    if not raw.startswith('---'):
        return {}, raw
    parts = raw.split('---', 2)
    head = parts[1]
    body = parts[2].lstrip('\n')
    data = {}
    for line in head.splitlines():
        if ':' in line:
            k, v = line.split(':', 1)
            data[k.strip()] = v.strip().strip('"\'')
    return data, body


def slug(file):
    m = re.match(r'(\d{4})-(\d{2})-(\d{2})-(.+)\.md$', file)
    if not m:
        return ('2026', '01', '01', re.sub(r'[^a-z0-9]+', '-', file.lower()).strip('-'))
    s = re.sub(r'[^a-z0-9]+', '-', m[4].lower()).strip('-')
    return m[1], m[2], m[3], s


def cat(c):
    l = c.lower().replace(' ', '')
    if l.startswith('hackthebox'):
        return 'hackthebox', 'Hack The Box'
    if 'portswigger' in l or 'hacking-web' in l:
        return 'portswigger', 'PortSwigger'
    if 'tryhackme' in l:
        return 'tryhackme', 'TryHackMe'
    if 'hacking-wifi' in l or l == 'wifi' or 'wifichallenge' in l:
        return 'wifi', 'Wi-Fi'
    if l.startswith('vulnlab'):
        return 'vulnlab', 'VulnLab'
    if l.startswith('vulnhub'):
        return 'vulnhub', 'VulnHub'
    if l.startswith('dockerlabs'):
        return 'dockerlabs', 'DockerLabs'
    return 'other', c.split('/')[0] if c else 'Other'


def safe_id(text):
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-') or 'section'


def decorate_article(raw_html):
    # Add stable IDs to headings so the table of contents can jump to them.
    counter = {}

    def heading(m):
        level, inner = m.group(1), m.group(2)
        plain = re.sub(r'<[^>]+>', '', inner)
        base = safe_id(plain)
        counter[base] = counter.get(base, 0) + 1
        ident = base if counter[base] == 1 else f'{base}-{counter[base]}'
        return f'<h{level} id="{ident}">{inner}</h{level}>'

    raw_html = re.sub(r'<h([2-4])>(.*?)</h\1>', heading, raw_html, flags=re.S)

    # Turn fenced code blocks into polished terminal/code windows with copy buttons.
    code_re = re.compile(r'<pre><code(?: class="language-([^"]+)")?>(.*?)</code></pre>', re.S)

    def code_block(m):
        lang = (m.group(1) or 'text').lower()
        label_map = {
            'bash': 'Bash', 'sh': 'Shell', 'shell': 'Shell', 'zsh': 'Zsh',
            'python': 'Python', 'ruby': 'Ruby', 'php': 'PHP', 'javascript': 'JavaScript',
            'js': 'JavaScript', 'html': 'HTML', 'css': 'CSS', 'c': 'C',
            'powershell': 'PowerShell', 'text': 'Text', 'plaintext': 'Text'
        }
        label = label_map.get(lang, lang.upper())
        return (
            f'<div class="code-window" data-language="{html.escape(label)}">'
            f'<div class="code-window-bar">'
            f'<div class="code-window-brand"><span class="term-dot red"></span><span class="term-dot yellow"></span><span class="term-dot green"></span>'
            f'<span class="code-file">terminal</span></div>'
            f'<div class="code-window-actions"><span class="code-language">{html.escape(label)}</span>'
            f'<button class="copy-code" type="button" title="Copiar código">Copy</button></div>'
            f'</div><div class="code-window-body"><pre><code class="language-{html.escape(lang)}">{m.group(2)}</code></pre></div></div>'
        )

    return code_re.sub(code_block, raw_html)


def excerpt_from(body):
    clean = re.sub(r'```.*?```', '', body, flags=re.S)
    clean = re.sub(r'<[^>]+>', ' ', clean)
    clean = re.sub(r'[#>*_`\[\]]', ' ', clean)
    return ' '.join(clean.split())[:180]


def layout(title, body, desc='MiguelRega7 — Cybersecurity, penetration testing, CTFs y writeups.'):
    return f'''<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)} · MiguelRega7</title>
<meta name="description" content="{html.escape(desc)}"><meta name="theme-color" content="#070a0f">
<link rel="icon" href="/favicon.ico"><link rel="stylesheet" href="/style.css">
</head>
<body>
<header class="header"><div class="nav wrap">
<a class="brand" href="/" aria-label="MiguelRega7">MR<em>7</em></a>
<nav class="links"><a class="nav-link" data-nav="home" href="/">INICIO</a><a class="nav-link" data-nav="writeups" href="/#writeups">WRITEUPS</a><a class="nav-link" data-nav="about" href="/about/">ABOUT</a></nav>
<div class="socials">
<a href="https://github.com/MikeRega7" target="_blank" rel="noreferrer" aria-label="GitHub">{github_svg()}</a>
<a href="https://www.linkedin.com/in/juan-miguel-regalado-nu%C3%B1o-a3b14b278" target="_blank" rel="noreferrer" aria-label="LinkedIn">{linkedin_svg()}</a>
<a href="https://www.instagram.com/_miguelitornuno7" target="_blank" rel="noreferrer" aria-label="Instagram">{instagram_svg()}</a>
</div><button class="menu" type="button" aria-label="Abrir menú" aria-expanded="false">☰</button>
</div></header>
{body}
<footer class="footer wrap"><div><b>MR<em>7</em></b><div>Cybersecurity notes &amp; writeups.</div></div><div class="footer-links"><a href="https://github.com/MikeRega7">GitHub</a><a href="https://www.linkedin.com/in/juan-miguel-regalado-nu%C3%B1o-a3b14b278">LinkedIn</a><a href="https://www.instagram.com/_miguelitornuno7">Instagram</a></div></footer>
<script src="/app.js?v=10"></script></body></html>'''


def github_svg():
    return '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12 .7a11.5 11.5 0 0 0-3.64 22.4c.58.1.79-.25.79-.56v-2.04c-3.2.7-3.87-1.35-3.87-1.35-.52-1.32-1.27-1.67-1.27-1.67-1.04-.71.08-.7.08-.7 1.15.08 1.75 1.18 1.75 1.18 1.02 1.74 2.67 1.24 3.32.95.1-.74.4-1.24.72-1.53-2.55-.29-5.24-1.28-5.24-5.7 0-1.26.45-2.29 1.18-3.1-.12-.3-.51-1.46.11-3.05 0 0 .96-.31 3.15 1.18a10.9 10.9 0 0 1 5.73 0c2.19-1.49 3.15-1.18 3.15-1.18.62 1.59.23 2.75.11 3.05.74.35.77 1.04.77 2.1v3.07c0 .31.21.67.8.55A11.5 11.5 0 0 0 12 .7Z"/></svg>'


def linkedin_svg():
    return '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M5.2 3.2A2.2 2.2 0 1 1 5.2 7.6a2.2 2.2 0 0 1 0-4.4ZM3.4 8.9h3.6V20H3.4V8.9Zm5.8 0h3.4v1.52h.05c.47-.9 1.62-1.84 3.34-1.84 3.57 0 4.23 2.35 4.23 5.4V20h-3.55v-5.34c0-1.27-.02-2.91-1.77-2.91-1.78 0-2.05 1.39-2.05 2.82V20H9.2V8.9Z"/></svg>'


def instagram_svg():
    return '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="none" stroke="currentColor" stroke-width="1.8" d="M7 2.9h10A4.1 4.1 0 0 1 21.1 7v10a4.1 4.1 0 0 1-4.1 4.1H7A4.1 4.1 0 0 1 2.9 17V7A4.1 4.1 0 0 1 7 2.9Z"/><circle cx="12" cy="12" r="3.3" fill="none" stroke="currentColor" stroke-width="1.8"/><circle cx="17.5" cy="6.7" r=".9" fill="currentColor"/></svg>'


posts = []
for f in POSTS.glob('*.md'):
    data, body = frontmatter(f.read_text(encoding='utf-8', errors='replace'))
    y, mo, d, s = slug(f.name)
    title = data.get('title', s)
    key, tag = cat(data.get('categories', ''))
    rendered = decorate_article(md(body))
    excerpt = excerpt_from(body)
    posts.append(dict(title=title, html=rendered, excerpt=excerpt, category=key, tag=tag,
                      date=f'{y}-{mo}-{d}', url=f'/{y}/{mo}/{d}/{s}/'))
posts.sort(key=lambda x: x['date'], reverse=True)


def card(p):
    excerpt = html.escape(p['excerpt']) + ('...' if len(p['excerpt']) >= 180 else '')
    search = html.escape((p['title'] + ' ' + p['tag'] + ' ' + p['excerpt']).lower())
    return f'''<article class="card" data-cat="{p['category']}" data-search="{search}" data-date="{p['date']}" data-title="{html.escape(p['title'].lower())}">
<div class="cardtop"><span class="tag">{html.escape(p['tag'])}</span><time>{p['date'].replace('-', '.')}</time></div>
<h3><a href="{p['url']}">{html.escape(p['title'])}</a></h3><p>{excerpt}</p>
<a class="read" href="{p['url']}">Leer writeup <span>→</span><span class="external">↗</span></a></article>'''


cards = ''.join(card(p) for p in posts)

index = f'''<main class="wrap">
<section class="archive-hero"><div class="archive-title"><p class="eyebrow">ARCHIVE</p><h1>Latest <span>writeups</span></h1></div><blockquote>“Hacking is not a crime,<br>it’s a mindset.”<small>— MR7</small></blockquote></section>
<section class="archive" id="writeups">
<div class="tools"><div class="filters">
<button class="filter active" data-filter="all">Todos</button><button class="filter" data-filter="hackthebox">Hack The Box</button><button class="filter" data-filter="portswigger">PortSwigger</button><button class="filter" data-filter="wifi">Wi-Fi</button><button class="filter" data-filter="tryhackme">TryHackMe</button><button class="filter" data-filter="vulnlab">VulnLab</button><button class="filter" data-filter="other">Otros</button>
</div><label class="search">⌕<input id="search" type="search" autocomplete="off" placeholder="Buscar writeups..."><button id="clearSearch" class="clear" type="button" aria-label="Limpiar búsqueda">×</button></label></div>
<div class="resultsbar"><span id="resultCount">Mostrando {len(posts)} writeups</span><label>Ordenar por <select id="sort"><option value="newest">Más recientes</option><option value="oldest">Más antiguos</option><option value="az">A → Z</option><option value="za">Z → A</option></select></label></div>
<div class="grid" id="posts">{cards}</div><p id="empty" class="empty" hidden>No encontramos writeups.</p>
<div class="pagination" id="pagination"></div>
</section>
</main>'''
(PUBLIC / 'index.html').write_text(layout('MiguelRega7', index), encoding='utf-8')

for p in posts:
    # Extract headings for the article sidebar.
    headings = re.findall(r'<h([2-3]) id="([^"]+)">(.*?)</h\1>', p['html'], flags=re.S)
    toc = ''.join(f'<a href="#{hid}">{re.sub("<[^>]+>", "", txt)}</a>' for _, hid, txt in headings[:8])
    body = f'''<main class="wrap"><header class="article-head"><a class="back" href="/#writeups">← VOLVER A WRITEUPS</a><div class="article-head-row"><div><span class="article-tag">{html.escape(p['tag'])}</span><h1>{html.escape(p['title'])}</h1><div class="meta"><span>◷</span><time>{p['date']}</time><span>·</span><span>WRITEUP</span><span>·</span><span>MR7 LAB</span></div></div><div class="share"><span>Compartir</span><button type="button" class="share-btn" data-copy-url="true">↗</button></div></div><p class="article-excerpt">{html.escape(p['excerpt'])}.</p></header><div class="article-layout"><aside class="aside"><div class="aside-title">CONTENIDO</div>{toc or '<a href="#top">Writeup</a>'}</aside><article class="article-content" id="top">{p['html']}</article></div></main>'''
    out = PUBLIC / p['url'].strip('/')
    out.mkdir(parents=True, exist_ok=True)
    (out / 'index.html').write_text(layout(p['title'], body, p['excerpt']), encoding='utf-8')

about = '''<main class="wrap">
<section class="page">
<p class="eyebrow">MIGUELREGA7</p>
<h1>About</h1>
<div class="page-content">

<h2>Hola 👋</h2>

<p>Hola, me llamo <strong>Miguel</strong>. Estoy aprendiendo y desarrollándome en el área de ciberseguridad, con especial interés en <strong>penetration testing</strong>, seguridad web, redes inalámbricas y resolución de CTFs.</p>

<p>Este sitio es mi espacio personal para documentar lo que voy aprendiendo: writeups de laboratorios, experiencias con plataformas de seguridad, investigación técnica y notas de los retos que voy resolviendo.</p>

<p>Gran parte de mi aprendizaje viene de practicar directamente en laboratorios y CTFs. Me gusta entender no solo cómo funciona una vulnerabilidad, sino también el proceso completo de enumeración, explotación y escalada de privilegios.</p>

<h2>Certificaciones</h2>

<ul>
<li>eJPTv2 — eLearnSecurity Junior Penetration Tester</li>
<li>CNPen — Certified Network Pentester</li>
<li>CNSP — Certified Network Security Practitioner</li>
<li>CWP — Certified WiFiChallenge Professional</li>
<li>CPTS — Hack The Box Certified Penetration Testing Specialist</li>
</ul>

<h2>Intereses</h2>

<ul>
<li>Penetration Testing</li>
<li>Web Security</li>
<li>Wireless Security</li>
<li>CTFs y laboratorios</li>
<li>Vulnerability Research</li>
</ul>

<h2>Redes</h2>

<ul>
<li><a href="https://github.com/MikeRega7">GitHub</a></li>
<li><a href="https://app.hackthebox.com/profile/910232">Hack The Box</a></li>
<li><a href="https://www.linkedin.com/in/juan-miguel-regalado-nu%C3%B1o-a3b14b278">LinkedIn</a></li>
<li><a href="https://www.instagram.com/_miguelitornuno7">Instagram</a></li>
</ul>

</div>
</section>
</main>'''

(PUBLIC / 'about').mkdir(exist_ok=True)
(PUBLIC / 'about' / 'index.html').write_text(layout('About', about), encoding='utf-8')

print(f'Built {len(posts)} posts')
