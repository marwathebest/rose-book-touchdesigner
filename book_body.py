# book_body.py
# كتاب يفتح بلفّة اليد، وكل صفحة تقلبها تطلع منها وردة.
# يشغّله build_rose_book.py (Ctrl+R على rose_book_builder) ويبني /project1/rose_book
# الناتج النهائي = rose_book/final

# مجلد المشروع نفسه (اللي فيه rose_book.toe)، فيشتغل على أي جهاز
ROSE_FOLDER = project.folder

root = me.parent()

old = root.op('rose_book')
if old:
    old.destroy()
base = root.create(baseCOMP, 'rose_book')
base.nodeX = me.nodeX + 200
base.nodeY = me.nodeY


def mk(parent, optype, name, x=0, y=0):
    o = parent.create(optype, name)
    o.nodeX = x
    o.nodeY = y
    return o


def setp(o, **kw):
    # يضبط الباراميترات اللي موجودة ويتجاهل اللي اسمها مختلف بنسخة TD
    for k, v in kw.items():
        p = getattr(o.par, k, None)
        if p is not None:
            try:
                p.val = v
            except Exception:
                pass


def color(mat, rgb):
    mat.par.colorr, mat.par.colorg, mat.par.colorb = rgb


def text_dat(name, x, y, txt):
    d = mk(base, textDAT, name, x, y)
    d.text = txt
    return d


# ---------------------------------------------------------------- custom params
pg = base.appendCustomPage('Book')
pg.appendCHOP('Handchop', label='Hand CHOP (MediaPipe)')
pg.appendFolder('Rosefolder', label='Roses Folder')
p = pg.appendMenu('Gesture', label='Hand Gesture')[0]
p.menuNames = ['swipe', 'twist', 'flip']
p.menuLabels = ['Swipe across center line', 'Twist (like a door knob)', 'Flip palm']
p.default = 'swipe'; p.val = 'swipe'
p = pg.appendFloat('Swipewidth', label='Center Zone Width')[0]
p.default = 0.1; p.normMin = 0.03; p.normMax = 0.3; p.val = 0.1
pg.appendToggle('Mirror', label='Flip Left/Right')
base.par.Mirror = False
pg.appendToggle('Bloomcontrol', label='Twist Opens Rose')
base.par.Bloomcontrol = True
pg.appendToggle('Showguide', label='Show Center Line')
base.par.Showguide = False   # الخط يشتغل بالخلفية بدون ما يبان
p = pg.appendFloat('Twistangle', label='Twist Angle (deg)')[0]
p.default = 30; p.normMin = 10; p.normMax = 60; p.val = 30
p = pg.appendFloat('Threshold', label='Rotate Threshold')[0]
p.default = 0.5; p.normMin = 0.1; p.normMax = 0.9; p.val = 0.5
p = pg.appendFloat('Growtime', label='Rose Grow Time (sec)')[0]
p.default = 2.5; p.normMin = 0.5; p.normMax = 6; p.val = 2.5
p = pg.appendFloat('Glow', label='Glow Amount')[0]
p.default = 0.55; p.normMin = 0; p.normMax = 1.5; p.val = 0.55
p = pg.appendFloat('Brightness', label='Brightness')[0]
p.default = 1.0; p.normMin = 0.3; p.normMax = 1.5; p.val = 1.0
p = pg.appendFloat('Camsway', label='Camera Sway')[0]
p.default = 1; p.normMin = 0; p.normMax = 3; p.val = 1
pg.appendPulse('Nextpage', label='Next Page (test)')
pg.appendToggle('Usetest', label='Test Without Camera')
pg.appendToggle('Snapshot', label='Save Debug Preview')
base.par.Snapshot = False
p = pg.appendFloat('Testroll', label='Test Hand Roll')[0]
p.normMin = -1; p.normMax = 1
base.par.Rosefolder.expr = 'project.folder'


# يدور على CHOP فيه نقاط اليد (pinky_mcp / index_finger_mcp) من MediaPipe
def find_hand_chop():
    known = op('/project1/hand_tracking/normalized_data')
    if known is not None:
        return known
    best = None
    for c in op('/').findChildren(type=CHOP):
        if c.path.startswith(base.path):
            continue
        names = [ch.name.lower() for ch in c.chans()[:200]]
        if any('pinky' in n and 'mcp' in n for n in names) and any('wrist' in n for n in names):
            if best is None or c.name.startswith(('null', 'out')):
                best = c
    return best


hand = find_hand_chop()
if hand:
    base.par.Handchop = hand.path
    print('rose_book: hand CHOP =', hand.path)
else:
    print('rose_book: ما لقيت CHOP اليد، حطه يدوي في باراميتر Hand CHOP')


# ---------------------------------------------------------------- textures
CREAM = (0.96, 0.93, 0.85)
COVER = (0.42, 0.07, 0.11)

# وجه الورقة = الوردة مطبوعة على الورق (أو الغلاف لما الكتاب مقفل)
rose_tex = mk(base, moviefileinTOP, 'rose_frame', 300, -250)
rose_tex.par.file = ROSE_FOLDER + '/page1_red/frame_0000.png'
paper_top = mk(base, constantTOP, 'paper_top', 300, -100)
cover_top = mk(base, constantTOP, 'cover_top', 450, -100)
for t, rgb in ((paper_top, CREAM), (cover_top, COVER)):
    setp(t, outputresolution='custom', resolutionw=640, resolutionh=896)
    t.par.colorr, t.par.colorg, t.par.colorb = rgb
rose_on_paper = mk(base, overTOP, 'rose_on_paper', 450, -250)
rose_on_paper.inputConnectors[0].connect(rose_tex)
rose_on_paper.inputConnectors[1].connect(paper_top)
leaf_tex = mk(base, switchTOP, 'leaf_tex', 600, -175)
cover_top.outputConnectors[0].connect(leaf_tex)
rose_on_paper.outputConnectors[0].connect(leaf_tex)

# صور تتولد بالكود: نقطة ناعمة للبتلات، وخلفية فيها إضاءة دافية بالنص
tex_cb = text_dat('tex_callbacks', 750, -250, r'''
import numpy as np

def onCook(scriptOp):
    if scriptOp.name == 'dot_tex':
        n = 64
        yy, xx = np.mgrid[0:n, 0:n] / (n - 1) * 2 - 1
        a = np.exp(-(xx ** 2 + yy ** 2) * 4.0)
        arr = np.dstack([a, a, a, a]).astype(np.float32)
    else:
        w, h = 960, 540
        yy, xx = np.mgrid[0:h, 0:w]
        dx = (xx - w * 0.5) / (w * 0.55)
        dy = (yy - h * 0.55) / (h * 0.75)
        d = np.clip(np.sqrt(dx ** 2 + dy ** 2), 0, 1)
        k = (1 - d) ** 2
        r = 0.035 + 0.20 * k
        g = 0.025 + 0.09 * k
        b = 0.045 + 0.12 * k
        arr = np.dstack([r, g, b, np.ones_like(r)]).astype(np.float32)
    scriptOp.copyNumpyArray(arr)
    return
''')
dot_tex = mk(base, scriptTOP, 'dot_tex', 750, -100)
setp(dot_tex, callbacks=tex_cb.path)
vignette = mk(base, scriptTOP, 'vignette', 900, -100)
setp(vignette, callbacks=tex_cb.path)


# ---------------------------------------------------------------- materials (مع إضاءة)
def phong(name, x, rgb, tex=None, spec=0.12, shin=25):
    m = mk(base, phongMAT, name, x, -400)
    setp(m, diffr=rgb[0], diffg=rgb[1], diffb=rgb[2],
         ambr=rgb[0] * 0.55, ambg=rgb[1] * 0.55, ambb=rgb[2] * 0.55,
         specr=spec, specg=spec, specb=spec, shininess=shin)
    if tex is not None:
        setp(m, colormap=tex)
    return m


paper_mat = phong('paper_mat', 0, (0.88, 0.88, 0.88), paper_top, 0.05)
front_mat = phong('leaf_front_mat', 150, (0.88, 0.88, 0.88), leaf_tex, 0.05)
cover_mat = phong('cover_mat', 300, COVER, None, 0.35, 40)
spine_mat = phong('spine_mat', 450, (0.5, 0.44, 0.36), None, 0.05)

fx_mat = mk(base, constantMAT, 'fx_mat', 600, -400)
color(fx_mat, (1, 0.5, 0.6))
setp(fx_mat, colormap=dot_tex, blending=True, srcblend='one', destblend='one',
     depthwriting=False, depthwrite=False)


# ---------------------------------------------------------------- geometry
def page_sop(geo, name, tx, tz, ry=0, y=0, w=1.0, h=1.4):
    r = mk(geo, rectangleSOP, name + '_rect', 0, y)
    r.par.sizex = w
    r.par.sizey = h
    x = mk(geo, transformSOP, name + '_xf', 150, y)
    x.par.ry = ry
    x.par.tx = tx
    x.par.tz = tz
    x.inputConnectors[0].connect(r)
    return x


def new_geo(parent, name, x, y):
    g = mk(parent, geometryCOMP, name, x, y)
    for c in list(g.children):
        c.destroy()
    return g


def page_geo(parent, name, x, y, tx, tz, mat, ry=0, w=1.0, h=1.4):
    g = new_geo(parent, name, x, y)
    out = page_sop(g, 'p', tx, tz, ry, 0, w, h)
    out.display = out.render = True
    g.par.material = mat
    return g


board = page_geo(base, 'cover_board', -150, 0, 0, -0.06, cover_mat, 0, 2.12, 1.52)
spine = page_geo(base, 'spine', -150, -150, 0, -0.025, spine_mat, 0, 0.015, 1.4)
left = page_geo(base, 'left_page', 0, 0, -0.5, -0.03, paper_mat)
right = page_geo(base, 'right_page', 150, 0, 0.5, -0.03, paper_mat)

# الورقة اللي تنقلب: تنثني وهي تنقلب (Script SOP يبنيها كل فريم)
deform_cb = text_dat('page_deform', 450, 150, r'''
# يبني الورقة كشبكة تنحني: الكعب يرتفع أول والطرف يلحقه، والزاوية العليا تلتف أكثر
import math, traceback

NX, NY = 24, 4
K = 0.85
OFF = 0.004


def _build(scriptOp, t, front):
    sp = math.sin(math.pi * t)
    a0 = math.pi * t + K * sp
    scriptOp.clear()
    for nm in ('N', 'uv'):
        try:
            scriptOp.pointAttribs.create(nm)
        except Exception:
            pass

    def pos(s, yy):
        g = -2 * K * sp * (1 + 0.35 * yy / 0.7)
        if abs(g) < 1e-5:
            x, z = s * math.cos(a0), s * math.sin(a0)
        else:
            x = (math.sin(a0 + g * s) - math.sin(a0)) / g
            z = (math.cos(a0) - math.cos(a0 + g * s)) / g
        A = a0 + g * s
        nx, nz = -math.sin(A), math.cos(A)
        o = OFF if front else -OFF
        sign = 1 if front else -1
        return (x + o * nx, yy, z + o * nz), (sign * nx, 0.0, sign * nz)

    for i in range(NX):
        for j in range(NY):
            cs = [(i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1)]
            if not front:
                cs.reverse()
            poly = scriptOp.appendPoly(4, closed=True, addPoints=True)
            for c, (ci, cj) in enumerate(cs):
                s = ci / NX
                v = cj / NY
                P, N = pos(s, -0.7 + 1.4 * v)
                pt = poly[c].point
                pt.x, pt.y, pt.z = P
                pt.N = N
                pt.uv = (s if front else 1 - s, v, 0.0)


def onCook(scriptOp):
    B = me.parent()
    try:
        leaf = scriptOp.parent(2)
        key = 'turn_prev' if leaf.name == 'leaf_prev' else 'turn'
        t = max(0.0, min(1.0, B.fetch(key, 0.0)))
        _build(scriptOp, t, scriptOp.parent().name == 'front')
    except Exception:
        with open(B.par.Rosefolder.eval() + '/deform_log.txt', 'w') as f:
            f.write(traceback.format_exc())
    return
''')


def leaf_geo(name, x):
    lf = new_geo(base, name, x, 0)
    lf.par.tz = -0.02
    for side, mat, sx in (('front', front_mat, 0), ('back', paper_mat, 150)):
        g = new_geo(lf, side, sx, 0)
        d = mk(g, scriptSOP, 'deform', 0, 0)
        setp(d, callbacks=deform_cb.path)
        d.display = d.render = True
        g.par.material = mat
    return lf


leaf = leaf_geo('leaf', 300)
leaf_prev = leaf_geo('leaf_prev', 450)     # الورقة اللي تكمّل نزولها بعد ما تثبت القلبة
leaf_prev.render = False

# بتلات ولمعات تطير (كل وحدة مربع صغير عليه نقطة ناعمة)
fx_cb = text_dat('fx_particles', 600, 150, r'''
import math, random, traceback

DT = 1.0 / 60


def _spawn_burst(parts, n):
    for _ in range(n):
        parts.append([random.uniform(0.15, 0.95), random.uniform(-0.55, 0.45), random.uniform(0.0, 0.15),
                      random.uniform(-0.25, 0.2), random.uniform(0.25, 0.75), random.uniform(0.05, 0.35),
                      0.0, random.uniform(1.6, 3.2), random.uniform(0.015, 0.035), random.uniform(0, 6.28)])


def _spawn_dust(parts):
    parts.append([random.uniform(-1.8, 1.8), random.uniform(-1.1, 0.9), random.uniform(-0.4, 0.7),
                  0.0, random.uniform(0.02, 0.07), 0.0,
                  0.0, random.uniform(4.0, 7.0), random.uniform(0.008, 0.02), random.uniform(0, 6.28)])


def onCook(scriptOp):
    B = me.parent()
    try:
        parts = B.fetch('parts', [])
        n = B.fetch('burst', 0)
        if n:
            B.store('burst', 0)
            _spawn_burst(parts, n)
        rose = B.fetch('rose', 0.0)
        spread = B.fetch('spread', 0.0)
        # كل ما فتحت الوردة أكثر، تطلع منها بتلات أكثر وتنتشر لبرا
        if random.random() < spread * 0.9:
            for _ in range(1 + int(spread * 2)):
                a = random.uniform(0, 6.28)
                v = 0.25 + 0.55 * spread
                parts.append([0.55 + random.uniform(-0.08, 0.08), 0.25 + random.uniform(-0.08, 0.08), 0.06,
                              math.cos(a) * v, math.sin(a) * v + 0.1, random.uniform(0.05, 0.3),
                              0.0, random.uniform(1.4, 2.6), random.uniform(0.015, 0.035), random.uniform(0, 6.28)])
        if random.random() < 0.12 + 0.25 * rose:
            _spawn_dust(parts)
        scriptOp.clear()
        try:
            scriptOp.pointAttribs.create('uv')
        except Exception:
            pass
        alive = []
        for q in parts:
            x, y, z, vx, vy, vz, age, life, size, ph = q
            age += DT
            if age >= life:
                continue
            vx += math.sin(age * 2.3 + ph) * 0.004
            dx, dy = x - 0.55, y - 0.25
            vx += dx * spread * 0.8 * DT
            vy += dy * spread * 0.8 * DT
            x += vx * DT
            y += vy * DT
            z += vz * DT
            vx *= 0.985
            vy *= 0.992
            q[:] = [x, y, z, vx, vy, vz, age, life, size, ph]
            alive.append(q)
            fade = min(1.0, age / 0.25) * min(1.0, (life - age) / 0.9)
            s = size * fade * (1 + 0.35 * math.sin(age * 7 + ph)) * (1 + 0.8 * spread)
            if s <= 0.0005:
                continue
            poly = scriptOp.appendPoly(4, closed=True, addPoints=True)
            for c, (cx, cy) in enumerate(((-1, -1), (1, -1), (1, 1), (-1, 1))):
                pt = poly[c].point
                pt.x, pt.y, pt.z = x + cx * s, y + cy * s, z
                pt.uv = ((cx + 1) * 0.5, (cy + 1) * 0.5, 0.0)
        B.store('parts', alive[-400:])
    except Exception:
        with open(B.par.Rosefolder.eval() + '/fx_log.txt', 'w') as f:
            f.write(traceback.format_exc())
    return
''')
fx = new_geo(base, 'fx', 600, 0)
fx_sop = mk(fx, scriptSOP, 'particles', 0, 0)
setp(fx_sop, callbacks=fx_cb.path)
fx_sop.display = fx_sop.render = True
fx.par.material = fx_mat


# ---------------------------------------------------------------- lights
def light(name, x, pos, rgb, dim):
    l = mk(base, lightCOMP, name, x, 350)
    setp(l, lighttype='point', tx=pos[0], ty=pos[1], tz=pos[2],
         cr=rgb[0], cg=rgb[1], cb=rgb[2], dimmer=dim)
    return l


light('key_light', 0, (-2.2, 2.4, 3.2), (1.0, 0.88, 0.72), 0.75)      # ضوء دافي من فوق يسار
light('fill_light', 150, (2.6, -0.8, 2.0), (0.75, 0.55, 0.85), 0.25)  # ضوء بنفسجي خفيف من يمين
light('rose_light', 300, (0.5, 0.05, 0.8), (1.0, 0.3, 0.4), 0.0)     # يشع من الوردة وهي تتفتح
amb = mk(base, ambientlightCOMP, 'amb_light', 450, 350)
setp(amb, cr=0.16, cg=0.13, cb=0.15, dimmer=1)


# ---------------------------------------------------------------- render
cam = mk(base, cameraCOMP, 'cam', 0, 500)
cam.par.ty = 0.5
cam.par.tz = 4.6
cam.par.rx = -6

RES = dict(outputresolution='custom', resolutionw=1920, resolutionh=1080)

render = mk(base, renderTOP, 'render', 150, 500)
render.par.camera = cam
render.par.geometry = 'cover_board spine left_page right_page leaf leaf_prev'
setp(render, lights='key_light fill_light rose_light amb_light', cullface='neither',
     antialias='aa8', **RES)

render_fx = mk(base, renderTOP, 'render_fx', 150, 650)
render_fx.par.camera = cam
render_fx.par.geometry = 'fx'
setp(render_fx, lights='', cullface='neither', **RES)

book_bg = mk(base, overTOP, 'book_over_bg', 300, 550)
book_bg.inputConnectors[0].connect(render)
book_bg.inputConnectors[1].connect(vignette)
setp(book_bg, outputresolution='custom', resolutionw=1920, resolutionh=1080)

with_fx = mk(base, compositeTOP, 'with_fx', 450, 600)
book_bg.outputConnectors[0].connect(with_fx)
render_fx.outputConnectors[0].connect(with_fx)
setp(with_fx, operand='add')

# التوهج بس من الأماكن المضيئة (الوردة، البتلات، الضوء) مو من كل الصورة
glow_blur = mk(base, blurTOP, 'glow_blur', 600, 650)
glow_blur.inputConnectors[0].connect(render_fx)
setp(glow_blur, size=60)
glow_lvl = mk(base, levelTOP, 'glow_level', 750, 650)
glow_lvl.inputConnectors[0].connect(glow_blur)
setp(glow_lvl, opacity=0.55)

glow_add = mk(base, compositeTOP, 'glow_add', 900, 600)
with_fx.outputConnectors[0].connect(glow_add)
glow_lvl.outputConnectors[0].connect(glow_add)
setp(glow_add, operand='add')

bright = mk(base, levelTOP, 'brightness', 975, 600)
bright.inputConnectors[0].connect(glow_add)

# خط بالنص + نقطة تبين مكان يدك
guide_cb = text_dat('guide_draw', 975, 800, r'''
import numpy as np

W, H = 640, 360


def onCook(scriptOp):
    B = me.parent()
    P = B.par
    img = np.zeros((H, W, 4), np.float32)
    if P.Showguide.eval():
        ok = B.fetch('hand_ok', False)
        hx, hy = B.fetch('hand_xy', (0.5, 0.5))
        armed = B.fetch('armed', 0)
        turn = B.fetch('turn', 0.0)
        if P.Gesture.eval() == 'swipe':
            M = P.Swipewidth.eval()
            x1, x2 = int((0.5 - M) * W), int((0.5 + M) * W)
            img[:, x1:x2] += np.array([0.035, 0.03, 0.04, 0.05], np.float32)
            a = 0.3 + 0.6 * turn
            rows = (np.arange(H) // 9) % 2 == 0
            c = W // 2
            img[rows, c - 1:c + 1] = np.array([1.0 * a, 0.85 * a, 0.9 * a, a], np.float32)
        if ok:
            yy, xx = np.mgrid[0:H, 0:W]
            d2 = (xx - hx * W) ** 2 + (yy - hy * H) ** 2
            g = np.exp(-d2 / (2 * 8.0 ** 2)) * 0.9
            col = (0.55, 1.0, 0.7) if armed else (1.0, 0.65, 0.45)   # أخضر = جاهز تقلب
            for i in range(3):
                img[..., i] += g * col[i]
            img[..., 3] += g
        np.clip(img, 0, 1, out=img)
    scriptOp.copyNumpyArray(img)
    return
''')
guide = mk(base, scriptTOP, 'guide', 975, 700)
setp(guide, callbacks=guide_cb.path)
guide_over = mk(base, overTOP, 'guide_over', 1050, 650)
guide_over.inputConnectors[0].connect(guide)
guide_over.inputConnectors[1].connect(bright)
setp(guide_over, outputresolution='custom', resolutionw=1920, resolutionh=1080)
final = mk(base, nullTOP, 'final', 1125, 600)
final.inputConnectors[0].connect(guide_over)
final.viewer = True


# ---------------------------------------------------------------- controls
btn = mk(base, parameterexecuteDAT, 'next_button', 0, 800)
setp(btn, op=base.path, pars='Nextpage', onpulse=True, valuechange=False)
btn.text = "def onPulse(par):\n\tpar.owner.store('force', True)\n\treturn\n"

state = mk(base, constantCHOP, 'state', 150, 800)
for i, n in enumerate(['page', 'turn', 'rose', 'roll']):
    getattr(state.par, 'const%dname' % i).val = n

logic = mk(base, executeDAT, 'book_logic', 0, 950)
logic.text = r'''
# كل فريم: يقرا لفّة اليد -> يقلب الصفحة -> ينمّي الوردة -> يحرك الأضواء والكاميرا
import math

PAGES = ['page1_red', 'page2_pink', 'page3_magenta', 'page4_white']
GLOW = [(1.0, 0.28, 0.32), (1.0, 0.55, 0.75), (0.85, 0.35, 1.0), (0.75, 0.8, 1.0)]


def _clamp(v, a=0.0, b=1.0):
    return max(a, min(b, v))


def _pick(chop, keys, axis):
    for c in chop.chans():
        n = c.name.lower()
        if all(k in n for k in keys) and n.endswith(axis):
            return c
    return None


def read_roll():
    P = parent().par
    if P.Usetest.eval():
        return P.Testroll.eval(), True
    chop = P.Handchop.eval()
    if chop is None:
        return 0.0, False
    pts = [_pick(chop, ('index', 'mcp'), 'x'), _pick(chop, ('pinky', 'mcp'), 'x'),
           _pick(chop, ('wrist',), 'x'), _pick(chop, ('wrist',), 'y'),
           _pick(chop, ('middle', 'mcp'), 'x'), _pick(chop, ('middle', 'mcp'), 'y')]
    if any(c is None for c in pts):
        return 0.0, False
    ix, px, wx, wy, mx, my = [c[0] for c in pts]
    L = math.hypot(mx - wx, my - wy)
    if L < 1e-4:
        return 0.0, False   # اليد مو ظاهرة
    # مكان الكف من منظورك انت (0 = يسار، 1 = يمين)
    hx = (wx + mx) * 0.5
    if P.Mirror.eval():
        hx = 1 - hx
    hy = (wy + my) * 0.5
    parent().store('hand_xy', (hx, hy))
    ang = math.degrees(math.atan2((mx - wx) * 1.78, my - wy))
    tw = _clamp((abs(ang) - 5.0) / max(5.0, P.Twistangle.eval() - 5.0))
    parent().store('twist', tw)
    if P.Gesture.eval() == 'swipe':
        return hx, True
    if P.Gesture.eval() == 'twist':
        # ميلان اليد يمين/يسار (زي مقبض الباب): زاوية الرسغ -> مفصل الوسطى
        ang = math.degrees(math.atan2((mx - wx) * 1.78, my - wy))
        return _clamp(ang / max(5.0, P.Twistangle.eval()), -1, 1), True
    raw = (ix - px) / L
    B = parent()
    amp = max(B.fetch('roll_amp', 0.3) * 0.998, abs(raw), 0.12)
    B.store('roll_amp', amp)
    return _clamp(raw / amp, -1, 1), True


def _step(frame):
    B = parent()
    P = B.par
    now = absTime.seconds

    roll, ok = read_roll()
    # لو اليد اختفت لحظة (رمشة تتبع) نكمل بآخر قيمة بدل ما نرجع الصفحة
    gone = now - B.fetch('seen_at', -10.0) >= 0.6
    if ok:
        B.store('seen_at', now)
    elif not gone:
        roll, ok = B.fetch('roll_s', 0.0), True
    sm = B.fetch('roll_s', 0.0)
    if ok and gone:
        sm = roll                   # اليد رجعت بعد غياب: نبدأ من مكانها الحقيقي بدون انزلاق
    sm += (roll - sm) * 0.3
    B.store('roll_s', sm)

    page = B.fetch('page', 0)       # 0 = الكتاب مقفل
    armed = B.fetch('armed', 0)     # الجهة اللي بدأت منها اللفّة (+1 / -1)
    turn = B.fetch('turn', 0.0)
    turn_v = B.fetch('turn_v', 0.0)
    turn_prev = B.fetch('turn_prev', 1.0)
    grow_start = B.fetch('grow_start', now)
    HI = max(0.05, P.Threshold.eval())

    swipe = P.Gesture.eval() == 'swipe'
    M = max(0.02, P.Swipewidth.eval())
    target = 0.0
    if swipe:
        # سحب اليد من يمين الخط لليسار = قلبة. بعدها لازم ترجع يمين عشان تقلب اللي بعدها،
        # ورجعتك ما تقلب شي
        if ok:
            if armed == 0:
                if sm > 0.5 + M:
                    armed = 1
            else:
                target = _clamp((0.5 + M - sm) / (2 * M))
    elif ok:
        if armed == 0:
            if abs(sm) > HI:
                armed = 1 if sm > 0 else -1
        else:
            target = _clamp((HI - sm * armed) / (2 * HI))

    key_edge = B.fetch('force', False)
    B.store('force', False)
    # Claude يقدر يقلب صفحة للتجربة بإنشاء ملف next.txt
    import os
    nf = P.Rosefolder.eval() + '/next.txt'
    if absTime.frame % 10 == 0 and os.path.exists(nf):
        os.remove(nf)
        key_edge = True
    if key_edge:
        target = 1.0
        B.store('auto_turn', True)
    if B.fetch('auto_turn', False):
        target = 1.0

    # حركة نابضية ناعمة (تتجاوز شوي وترجع) بدل الحركة الخطية
    turn_v += (target - turn) * 0.09
    turn_v *= 0.74
    turn = _clamp(turn + turn_v, 0.0, 1.0)
    if target >= 0.9 and turn >= 0.82:
        page = page + 1 if page < len(PAGES) else 0   # بعد آخر صفحة يرجع مقفل
        if swipe:
            armed = 0                                 # لازم ترجع يدك يمين الخط أول
        elif not B.fetch('auto_turn', False):
            armed = -armed                            # اللفّة الجاية بالعكس تقلب اللي بعدها
        B.store('auto_turn', False)
        turn_prev = turn                              # الورقة القديمة تكمل نزولها لحالها
        B.store('prev_v', turn_v)
        turn, turn_v = 0.0, 0.0
        grow_start = now
        B.store('bloom_s', 0.0)
        B.store('burst', 40 if page >= 1 else 20)

    # الورقة القديمة تنزل على اليسار بنعومة
    prev_v = B.fetch('prev_v', 0.0)
    if turn_prev < 1.0:
        prev_v += (1.0 - turn_prev) * 0.12
        prev_v *= 0.7
        turn_prev = min(1.0, turn_prev + max(prev_v, 0.004))
    B.store('prev_v', prev_v)
    op('leaf_prev').render = turn_prev < 0.999

    grow = _clamp((now - grow_start) / max(0.1, P.Growtime.eval())) if page >= 1 else 0.0
    grow = 1 - (1 - grow) ** 2                   # تتفتح بسرعة وتهدّي في الآخر
    bs = B.fetch('bloom_s', 0.0)
    if P.Bloomcontrol.eval():
        # الغصن يطلع لحاله لين البرعم، وبعدها ميلان يدك (زي مقبض الباب) يفتح الوردة ويسكّرها
        BUD = 17.0 / 47.0
        if ok:
            bs += (B.fetch('twist', 0.0) - bs) * 0.12
        rose = grow * BUD + (1 - BUD) * bs * grow
    else:
        bs += (grow - bs) * 0.12
        rose = grow
    B.store('bloom_s', bs)
    B.store('spread', bs if page >= 1 else 0.0)
    rose *= _clamp(1.0 - turn * 1.6)             # الوردة ترجع للورقة وهي تنقلب

    B.store('turn', turn)
    B.store('turn_v', turn_v)
    B.store('turn_prev', turn_prev)
    B.store('rose', rose)
    B.store('hand_ok', ok)
    B.store('armed', armed)
    op('guide').cook(force=True)

    # --- الورقة والبتلات
    op('leaf/front/deform').cook(force=True)
    op('leaf/back/deform').cook(force=True)
    if turn_prev < 0.999:
        op('leaf_prev/front/deform').cook(force=True)
        op('leaf_prev/back/deform').cook(force=True)
    op('fx/particles').cook(force=True)

    op('leaf_tex').par.index = 0 if page == 0 else 1
    op('left_page').render = page >= 1 or turn_prev < 0.999
    op('spine').render = page >= 1
    if page >= 1:
        f = '%s/%s/frame_%04d.png' % (P.Rosefolder.eval(), PAGES[page - 1], int(round(rose * 47)))
        tex = op('rose_frame')
        if tex.par.file.eval() != f:
            tex.par.file = f

    # --- الأضواء: ضوء الوردة بلونها ويقوى وهي تتفتح، ويتنفس بخفة
    gc = GLOW[(page - 1) % len(GLOW)] if page >= 1 else (1.0, 0.6, 0.4)
    rl = op('rose_light').par
    rl.cr, rl.cg, rl.cb = gc
    rl.dimmer = rose * (0.3 + 0.07 * math.sin(now * 2.2))
    fm = op('fx_mat').par
    fm.colorr, fm.colorg, fm.colorb = gc
    op('key_light').par.dimmer = 0.72 + 0.06 * math.sin(now * 0.7)
    op('glow_level').par.opacity = P.Glow.eval() * (0.8 + 0.4 * rose)
    op('brightness').par.brightness1 = P.Brightness.eval()

    # --- الكاميرا تتمايل بخفة وتميل مع يدك
    sw = P.Camsway.eval()
    cm = op('cam').par
    cm.ry = sw * (2.0 * math.sin(now * 0.31) + 2.5 * sm)
    cm.rx = -6 + sw * 0.8 * math.sin(now * 0.23)
    cm.tx = sw * 0.06 * math.sin(now * 0.31)

    if P.Snapshot.eval() and absTime.frame % 6 == 0:
        hist = B.fetch('roll_hist', [])
        hist = (hist + ['%.2f %s a%d t%.2f tw%.2f' % (sm, 'ok' if ok else '--', armed, turn, B.fetch('twist', 0.0))])[-120:]
        B.store('roll_hist', hist)
        if absTime.frame % 60 == 0:
            with open(P.Rosefolder.eval() + '/roll_log.txt', 'w') as f:
                f.write(chr(10).join(hist))

    st = op('state').par
    st.value0, st.value1, st.value2, st.value3 = page, turn, rose, sm

    B.store('page', page)
    B.store('armed', armed)
    B.store('grow_start', grow_start)
    return


def onFrameStart(frame):
    # أي خطأ ينكتب في logic_log.txt، وكل ثانية تنحفظ صورة preview.jpg
    import traceback
    d = parent().par.Rosefolder.eval()
    try:
        _step(frame)
        err = None
    except Exception:
        err = traceback.format_exc()
    if err != parent().fetch('last_err', None):
        parent().store('last_err', err)
        with open(d + '/logic_log.txt', 'w', encoding='utf-8') as f:
            f.write(err or 'OK')
    snap = parent().fetch('snap_req', False)
    if parent().par.Snapshot.eval() and (absTime.frame % 60 == 0 or snap):
        parent().store('snap_req', False)
        op('final').save(d + '/preview.jpg')
        # صورة الكاميرا وبيانات اليد، عشان Claude يعرف إذا الكاميرا شغالة
        try:
            cam_in = op('/project1/videodevin1')
            if cam_in is not None:
                cam_in.save(d + '/camera.jpg')
            hc = parent().par.Handchop.eval()
            info = 'none' if hc is None else 'chans %d  wrist_x %s' % (
                hc.numChans, hc['h1:wrist:x'].eval() if hc['h1:wrist:x'] is not None else 'missing')
            with open(d + '/hand_debug.txt', 'w') as f:
                f.write(info)
        except Exception as e:
            with open(d + '/hand_debug.txt', 'w') as f:
                f.write('err ' + str(e))
        st = op('state')
        with open(d + '/status.txt', 'w', encoding='utf-8') as f:
            f.write('frame %d  page %d  turn %.2f  rose %.2f  roll %.2f  hand_chop %s' % (
                frame, st['page'].eval(), st['turn'].eval(), st['rose'].eval(), st['roll'].eval(), parent().par.Handchop.eval()))
    # Claude يطلب صورة في لحظة معينة بملف snap.txt (مثلاً وسط القلبة)
    import os
    sf = d + '/snap.txt'
    if absTime.frame % 3 == 0 and os.path.exists(sf):
        os.remove(sf)
        op('final').save(d + '/snap.jpg')
    return
'''
logic.par.framestart = True
setp(logic, active=True)

mp = op('/project1/MediaPipe')
if mp is not None:
    setp(mp, Hdetectconf=0.2, Hpresconf=0.2, Htrackconf=0.2)
print('rose_book: جاهز. افتح rose_book/final')
