#!/usr/bin/env python3
"""Render entry.png for news-image-20261117, account 4 (lathixbt).

Map-poster design: a flat-vector world map with 8 hero vignettes (headline +
detail) anchored to their real locations, plus a 25-row 'The day in brief'
section (headline + one-line description each).
33 stories across 6 continents. Rendered at 3x then downsampled (Lanczos).
Deterministic: no randomness, no network, no time dependence.
"""
import math
from PIL import Image, ImageDraw, ImageFont

S = 3                      # supersampling factor
W, H = 1024, 1024
VW, VH = W * S, H * S      # canvas at 3x

FONT_DIR = "/usr/share/fonts/truetype/dejavu/"
def font_bold(px):
    return ImageFont.truetype(FONT_DIR + "DejaVuSans-Bold.ttf", int(px * S))
def font_reg(px):
    return ImageFont.truetype(FONT_DIR + "DejaVuSans.ttf", int(px * S))

def P(x, y):
    """1x layout coords -> 3x canvas coords."""
    return (x * S, y * S)

# ---------------------------------------------------------------- palette
PAPER   = (247, 241, 227)   # warm paper
NAVY    = (20, 33, 61)      # masthead / lead panel
NAVY_D  = (13, 24, 48)
GOLD    = (201, 162, 39)
GOLD_L  = (232, 197, 92)
INK     = (24, 30, 43)      # near-black text
INK_SOFT = (74, 82, 100)
CARD    = (255, 253, 247)   # vignette card paper
CARD_LN = (214, 203, 178)
OCEAN_T = (186, 212, 231)   # ocean gradient top
OCEAN_B = (148, 186, 215)   # ocean gradient bottom
LAND    = (236, 223, 188)   # continent fill
LAND_LN = (150, 131, 82)    # continent outline
GRID_LN = (255, 255, 255)

# category colours (6 max, per legend)
CAT = {
    "WAR":      (192, 57, 43),
    "POLITICS": (46, 95, 163),
    "ECONOMY":  (199, 125, 10),
    "TECH":     (108, 74, 176),
    "HEALTH":   (30, 138, 90),
    "DISASTER": (224, 101, 31),
}
CAT_ORDER = ["WAR", "POLITICS", "ECONOMY", "TECH", "HEALTH", "DISASTER"]
CAT_LABEL = {"WAR": "WAR", "POLITICS": "POLITICS", "ECONOMY": "ECONOMY",
             "TECH": "TECH", "HEALTH": "HEALTH", "DISASTER": "DISASTER"}

# ---------------------------------------------------------------- map
# Map area: equirectangular, lon -180..180, lat 78..-62 (aspect 360:140).
MAP_TOP, MAP_H = 124, 406
MAP_BOT = MAP_TOP + MAP_H

def lonlat_to_xy(lon, lat):
    x = (lon + 180.0) / 360.0 * W
    y = MAP_TOP + (78.0 - lat) / 140.0 * MAP_H
    return x, y

def poly_px(points):
    return [P(*lonlat_to_xy(lon, lat)) for lon, lat in points]

# Hand-authored simplified continent polygons (lon, lat). Stylised, not surveyed.
NORTH_AMERICA = [(-168,66),(-161,58),(-153,58),(-145,60),(-137,58),(-130,54),
    (-125,49),(-124,40),(-121,34),(-117,32),(-112,29),(-108,25),(-105,20),
    (-100,18),(-96,16),(-92,15),(-88,13),(-84,11),(-80,8),(-77,7),(-79,9),
    (-82,10),(-84,14),(-87,16),(-88,18),(-91,19),(-94,18),(-97,22),(-97,26),
    (-93,30),(-89,30),(-85,30),(-82,28),(-81,25),(-80,27),(-81,31),(-79,33),
    (-76,35),(-75,38),(-74,40),(-71,41),(-69,43),(-66,44),(-64,44),(-60,46),
    (-55,47),(-53,49),(-55,52),(-60,53),(-64,58),(-67,58),(-70,60),(-75,62),
    (-80,63),(-85,66),(-90,66),(-95,68),(-100,68),(-110,68),(-120,69),
    (-130,70),(-140,70),(-150,70),(-160,71),(-166,68),(-168,66)]
GREENLAND = [(-44,60),(-40,63),(-35,66),(-28,68),(-22,70),(-20,73),(-25,76),
    (-35,77),(-50,76),(-58,74),(-55,71),(-52,66),(-48,62),(-44,60)]
SOUTH_AMERICA = [(-77,7),(-73,11),(-68,12),(-63,10),(-59,8),(-54,6),(-51,4),
    (-50,0),(-46,-2),(-41,-3),(-37,-6),(-35,-8),(-37,-11),(-39,-14),(-40,-20),
    (-41,-23),(-46,-24),(-49,-28),(-52,-32),(-55,-35),(-58,-38),(-62,-41),
    (-65,-44),(-66,-47),(-68,-50),(-69,-52),(-71,-54),(-73,-50),(-73,-44),
    (-72,-37),(-71,-30),(-70,-22),(-71,-18),(-74,-15),(-77,-11),(-80,-7),
    (-81,-3),(-80,1),(-79,4),(-77,7)]
# Eurasia as one landmass, clockwise from Gibraltar.
EURASIA = [(-6,36),(-9,37),(-9,39),(-9,43),(-4,44),(-2,46),(-4,48),(-1,49),
    (1,51),(3,52),(5,53),(8,55),(8,57),(10,58),(7,59),(5,60),(5,62),(9,63),
    (12,65),(15,68),(19,70),(24,71),(29,71),(31,70),(34,68),(38,66),(42,66),
    (45,68),(50,69),(55,70),(60,70),(65,71),(70,72),(75,73),(80,73),(85,74),
    (90,75),(95,76),(100,77),(105,77),(110,76),(115,74),(120,73),(125,72),
    (130,72),(135,71),(140,72),(145,72),(150,71),(155,70),(160,70),(165,69),
    (170,68),(175,67),(178,66),(180,66),(180,65),(175,64),(170,63),(165,62),
    (162,60),(160,58),(158,55),(156,52),(155,50),(152,48),(150,45),(148,42),
    (145,40),(142,38),(140,36),(138,34),(136,33),(134,32),(132,31),(130,31),
    (128,30),(126,28),(124,26),(122,25),(121,28),(120,30),(121,32),(122,34),
    (124,36),(126,38),(128,39),(130,40),(132,41),(134,43),(136,44),(138,45),
    (140,46),(141,44),(142,42),(141,40),(140,38),(139,36),(137,34),(135,33),
    (133,32),(131,31),(129,30),(127,28),(125,25),(123,24),(121,22),(119,20),
    (117,18),(115,16),(113,14),(111,12),(109,10),(108,8),(106,6),(105,4),
    (104,2),(103,1),(102,3),(101,6),(100,8),(99,10),(98,12),(97,15),(96,16),
    (94,17),(93,19),(92,21),(90,22),(88,21),(87,20),(86,19),(84,18),(82,16),
    (80,14),(79,11),(78,9),(77,8),(76,10),(75,12),(74,15),(73,18),(72,20),
    (70,22),(68,23),(66,25),(64,25),(62,25),(60,25),(58,26),(57,27),(56,29),
    (55,30),(54,32),(53,34),(52,36),(50,37),(48,38),(46,39),(44,40),(42,41),
    (40,41),(38,41),(36,41),(34,41),(32,41),(30,41),(28,41),(28,39),(27,37),
    (26,36),(23,36),(21,36),(19,38),(17,39),(15,40),(13,41),(11,42),(9,43),
    (7,44),(5,43),(3,42),(1,41),(-1,39),(-2,37),(-4,36),(-6,36)]
UK = [(-5,50),(-3,52),(-5,54),(-4,57),(-2,58),(-1,57),(0,54),(0,52),(-2,51),
    (-4,50),(-5,50)]
JAPAN = [(130,31),(132,33),(134,34),(136,34),(138,35),(140,36),(141,38),
    (141,40),(142,42),(143,44),(141,45),(140,43),(139,40),(138,38),(137,37),
    (135,35),(133,34),(131,32),(130,31)]
AFRICA = [(-6,35),(-10,31),(-14,28),(-16,23),(-17,19),(-17,15),(-16,12),
    (-13,9),(-11,7),(-8,5),(-4,5),(0,6),(4,6),(8,4),(9,4),(12,2),(13,0),
    (12,-2),(11,-4),(12,-8),(13,-12),(12,-16),(13,-20),(14,-24),(15,-27),
    (17,-30),(18,-33),(20,-35),(25,-34),(28,-32),(32,-28),(35,-24),(37,-20),
    (40,-16),(40,-11),(41,-6),(42,-2),(45,0),(48,1),(51,3),(51,8),(48,11),
    (44,11),(41,13),(39,16),(38,19),(36,21),(34,24),(32,28),(30,31),(27,31),
    (23,32),(19,32),(15,32),(11,33),(10,36),(7,37),(3,36),(0,36),(-3,35),
    (-6,35)]
AUSTRALIA = [(114,-22),(114,-30),(115,-33),(118,-35),(124,-33),(129,-32),
    (132,-32),(135,-35),(138,-35),(140,-38),(144,-39),(147,-39),(150,-37),
    (153,-32),(153,-27),(150,-23),(146,-19),(142,-15),(142,-11),(139,-15),
    (136,-15),(135,-12),(132,-12),(130,-13),(127,-14),(124,-15),(122,-17),
    (120,-20),(117,-20),(114,-22)]
NEW_ZEALAND = [(167,-45),(170,-43),(173,-41),(175,-38),(177,-38),(175,-40),
    (173,-42),(170,-44),(167,-46),(167,-45)]
SUMATRA = [(95,5),(98,3),(101,0),(104,-3),(106,-6),(104,-6),(101,-2),(98,1),
    (95,5)]
BORNEO = [(109,1),(111,2),(114,3),(117,2),(118,-1),(117,-4),(114,-4),
    (111,-3),(109,1)]
NEW_GUINEA = [(131,-1),(136,-2),(141,-3),(146,-6),(150,-8),(147,-9),(143,-8),
    (139,-7),(135,-4),(132,-2),(131,-1)]
CONTINENTS = [NORTH_AMERICA, GREENLAND, SOUTH_AMERICA, EURASIA, UK, JAPAN,
              AFRICA, AUSTRALIA, NEW_ZEALAND, SUMATRA, BORNEO, NEW_GUINEA]

# ---------------------------------------------------------------- stories
# Heroes: (num, category, headline, detail, dot_x, dot_y, scene)
# Every hero now carries a 1-2 line detail so the story is clear on its own.
HEROES = [
    (1, "WAR", "Ukraine hits Crimea Bridge",
     "Road span falls; Russia hits Kyiv bridges.", 609, 220, "bridge"),
    (2, "POLITICS", "Trump, Xi, Putin meet",
     "Summit set for Thursday.", 836, 292, "summit"),
    (3, "WAR", "Iran hits US radar",
     "Bahrain: all intercepted.", 656, 275, "radar"),
    (4, "WAR", "Russian jets enter Japan",
     "Tokyo scrambles fighters, protests.", 908, 296, "jets"),
    (5, "POLITICS", "West urges Gaza open",
     "Four nations call for aid.", 611, 259, "tents"),
    (6, "POLITICS", "EU plans Rwanda",
     "First transfers in 2027.", 597, 356, "arrow"),
    (7, "ECONOMY", "Wall Street falls",
     "S&P 500 at lowest close since July.", 301, 232, "chart"),
    (8, "DISASTER", "Bus plunges",
     "At least eight killed in Uttarakhand.", 737, 302, "bus"),
]
# Briefs: (num, category, headline, description, dot_x, dot_y)
# dot None = location covered by a vignette card; story still named in briefs.
BRIEFS = [
    (9,  "WAR",      "Qeshm strike",    "US jets hit an IRGC missile site", 672, 272),
    (10, "POLITICS", "Tariff cuts",     "China cuts duties on C$400m of goods", 850, 300),
    (11, "POLITICS", "Israel inquiry",  "Netanyahu faces inquiry calls", 620, 272),
    (12, "POLITICS", "UK ban",          "UK sanctions eight settlement builders", 636, 262),
    (13, "POLITICS", "Actor appeal",    "Depardieu drops his appeal", 507, 233),
    (14, "WAR",      "Houthi advance",  "Houthis push toward Aden", 640, 335),
    (15, "POLITICS", "Robot talks",     "128 states meet in Geneva on killer robots", 529, 240),
    (16, "WAR",      "Plot claim",      "US says Iran weighs a 'dirty bomb' plot", 282, 268),
    (17, "TECH",     "Chip loophole",   "US moves to close AI chip loophole", None, None),
    (18, "POLITICS", "Estonia border",  "Estonia shuts Russia border on 1 Dec", 581, 203),
    (19, "ECONOMY",  "Pentagon audit",  "Pentagon fails audit for ninth year", 312, 272),
    (20, "WAR",      "Carrier arrives", "Third US carrier joins the Gulf force", 686, 308),
    (21, "POLITICS", "Trump in Manila", "Trump arrives for ASEAN summit", 820, 345),
    (22, "TECH",     "MSFT outage",     "Microsoft explains last week's outage", None, None),
    (23, "POLITICS", "Testimony curb",  "White House curbs agency testimony", 272, 258),
    (24, "HEALTH",   "Measles high",    "US measles cases highest since 1991", 272, 276),
    (25, "ECONOMY",  "Petrol $3.78",    "US petrol averages $3.78 a gallon", 241, 290),
    (26, "POLITICS", "39 freed",        "Venezuela frees 39 political prisoners", 322, 342),
    (27, "POLITICS", "Settler ban",     "Australia sanctions settlers, builder", 928, 478),
    (28, "POLITICS", "Sozcu off air",   "Turkey takes Sozcu TV off air in raid", 578, 262),
    (29, "POLITICS", "Mongolia resigns", "President says he will resign", 828, 300),
    (30, "TECH",     "FAA pause",       "FAA pauses router work after ground stop", 322, 246),
    (31, "TECH",     "Equinor hack",    "Equinor detects ongoing cyberattack", 524, 204),
    (32, "DISASTER", "Tanker sinks",    "gas tanker sinks off Bulgaria, 19 rescued", 598, 252),
    (33, "ECONOMY",  "Qantas alliance", "Qantas backs Virgin–Air NZ alliance", 950, 460),
]

# ---------------------------------------------------------------- helpers
def rr(d, box, rad, fill=None, outline=None, width=1):
    """Rounded rectangle in 1x coords."""
    x0, y0, x1, y1 = [v * S for v in box]
    d.rounded_rectangle([x0, y0, x1, y1], radius=rad * S, fill=fill,
                        outline=outline, width=int(width * S))

def shadow(d, box, rad, off=4):
    x0, y0, x1, y1 = box
    rr(d, (x0 + off, y0 + off, x1 + off, y1 + off), rad, fill=(0, 0, 0, 46))

def txt_w(text, fnt):
    return ImageDraw.Draw(Image.new("RGB", (8, 8))).textlength(text, font=fnt) / S

def wrap(text, fnt, max_w):
    """Greedy word wrap to 1x width; returns list of lines."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if txt_w(trial, fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

def draw_text(d, xy, text, fnt, fill, anchor="la"):
    x, y = xy
    d.text((x * S, y * S), text, font=fnt, fill=fill, anchor=anchor)

def line(d, p0, p1, fill, width=2):
    d.line([p0[0] * S, p0[1] * S, p1[0] * S, p1[1] * S], fill=fill,
           width=int(width * S))

def dot(d, cx, cy, r, fill, ring=(255, 255, 255), ring_w=2):
    d.ellipse([(cx - r) * S, (cy - r) * S, (cx + r) * S, (cy + r) * S],
              fill=fill, outline=ring, width=int(ring_w * S))

def num_badge(d, cx, cy, r, num, colour):
    dot(d, cx, cy, r, colour, ring=(255, 255, 255), ring_w=2)
    f = font_bold(15 if r <= 11 else 17)
    draw_text(d, (cx, cy), str(num), f, (255, 255, 255), anchor="mm")

# ---------------------------------------------------------------- map
def draw_map(d, dark=False):
    """Ocean gradient + graticule + continents."""
    top = OCEAN_T if not dark else (38, 62, 96)
    bot = OCEAN_B if not dark else (24, 44, 78)
    for yi in range(MAP_TOP, MAP_BOT + 1):
        t = (yi - MAP_TOP) / MAP_H
        c = tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3))
        d.line([0, yi * S, W * S, yi * S], fill=c)
    # graticule: every 30 degrees
    gl = (255, 255, 255, 70) if not dark else (255, 255, 255, 40)
    for lon in range(-150, 181, 30):
        x = (lon + 180) / 360 * W
        d.line([x * S, MAP_TOP * S, x * S, MAP_BOT * S], fill=gl, width=S)
    for lat in range(-60, 79, 30):
        y = MAP_TOP + (78 - lat) / 140 * MAP_H
        d.line([0, y * S, W * S, y * S], fill=gl, width=S)
    land_fill = LAND if not dark else (214, 199, 158)
    land_ln = LAND_LN if not dark else (120, 102, 60)
    for poly in CONTINENTS:
        pts = poly_px(poly)
        d.polygon(pts, fill=land_fill)
        d.line(pts + [pts[0]], fill=land_ln, width=int(2 * S), joint="curve")

# ---------------------------------------------------------------- icons
# All icons draw inside a box (x, y, w, h) in 1x coords, colour = category.
def icon_burst(d, x, y, w, h, c):
    cx, cy = x + w / 2, y + h / 2
    r = min(w, h) / 2
    for k in range(8):
        a = math.pi * k / 4
        line(d, (cx + math.cos(a) * r * 0.35, cy + math.sin(a) * r * 0.35),
             (cx + math.cos(a) * r, cy + math.sin(a) * r), c, 3)
    dot(d, cx, cy, r * 0.32, c)

def icon_tag(d, x, y, w, h, c):
    d.polygon([P(x + 4, y + 8), P(x + w - 8, y + 2), P(x + w - 2, y + 8),
               P(x + w - 8, y + h - 2), P(x + 4, y + h - 8)], fill=c)
    dot(d, x + w - 9, y + 9, 3, (255, 255, 255))

def icon_gavel(d, x, y, w, h, c):
    line(d, (x + 6, y + h - 6), (x + w - 6, y + 8), c, 4)
    d.rectangle([P(x + 4, y + 6), P(x + 20, y + 14)], fill=c)
    d.rectangle([P(x + w - 20, y + h - 14), P(x + w - 4, y + h - 6)], fill=c)

def icon_fence(d, x, y, w, h, c):
    for i in range(4):
        bx = x + 4 + i * (w - 8) / 3
        line(d, (bx, y + 4), (bx, y + h - 4), c, 3)
    line(d, (x + 2, y + h / 2 - 3), (x + w - 2, y + h / 2 - 3), c, 3)
    line(d, (x + 2, y + h / 2 + 4), (x + w - 2, y + h / 2 + 4), c, 3)

def icon_court(d, x, y, w, h, c):
    d.polygon([P(x + 2, y + 8), P(x + w / 2, y + 2), P(x + w - 2, y + 8)],
              fill=c)
    for i in range(3):
        bx = x + 6 + i * (w - 12) / 2
        d.rectangle([P(bx, y + 12), P(bx + 4, y + h - 8)], fill=c)
    d.rectangle([P(x + 2, y + h - 6), P(x + w - 2, y + h - 2)], fill=c)

def icon_advance(d, x, y, w, h, c):
    d.polygon([P(x + 4, y + h - 6), P(x + w / 2, y + 4), P(x + w - 4, y + h - 6)],
              fill=c)
    line(d, (x + w / 2, y + h - 6), (x + w / 2, y + h - 2), c, 4)

def icon_robot(d, x, y, w, h, c):
    d.rectangle([P(x + 6, y + 10), P(x + w - 6, y + h - 6)], fill=c)
    line(d, (x + w / 2, y + 4), (x + w / 2, y + 10), c, 3)
    dot(d, x + w / 2, y + 5, 3, c)
    dot(d, x + w / 2 - 6, y + h / 2, 3, (255, 255, 255))
    dot(d, x + w / 2 + 6, y + h / 2, 3, (255, 255, 255))
    line(d, (x + w / 2 - 5, y + h - 11), (x + w / 2 + 5, y + h - 11),
         (255, 255, 255), 2)

def icon_radiation(d, x, y, w, h, c):
    cx, cy = x + w / 2, y + h / 2
    dot(d, cx, cy, 4, c)
    for a in (90, 210, 330):
        ar = math.radians(a)
        d.pieslice([(cx - 12) * S, (cy - 12) * S, (cx + 12) * S, (cy + 12) * S],
                   start=a - 28, end=a + 28, fill=c)

def icon_chip(d, x, y, w, h, c):
    d.rectangle([P(x + 8, y + 8), P(x + w - 8, y + h - 8)], fill=c)
    ix0, iy0 = x + w * 0.36, y + h * 0.36
    ix1, iy1 = x + w * 0.64, y + h * 0.64
    d.rectangle([P(ix0, iy0), P(ix1, iy1)], fill=(255, 255, 255))
    for f in (0.28, 0.5, 0.72):
        px = x + w * f
        line(d, (px, y + 2), (px, y + 8), c, 2)
        line(d, (px, y + h - 8), (px, y + h - 2), c, 2)
        py = y + h * f
        line(d, (x + 2, py), (x + 8, py), c, 2)
        line(d, (x + w - 8, py), (x + w - 2, py), c, 2)

def icon_pentagon(d, x, y, w, h, c):
    cx, cy = x + w / 2, y + h / 2 + 2
    r = min(w, h) / 2 - 2
    pts = []
    for k in range(5):
        a = math.radians(-90 + k * 72)
        pts.append((cx + math.cos(a) * r, cy + math.sin(a) * r))
    d.polygon([P(*p) for p in pts], fill=c)

def icon_ship(d, x, y, w, h, c):
    d.polygon([P(x + 4, y + h - 12), P(x + w - 4, y + h - 12),
               P(x + w - 10, y + h - 3), P(x + 10, y + h - 3)], fill=c)
    line(d, (x + w / 2, y + 4), (x + w / 2, y + h - 12), c, 3)
    d.polygon([P(x + w / 2 + 2, y + 6), P(x + w - 8, y + h - 14),
               P(x + w / 2 + 2, y + h - 14)], fill=c)

def icon_plane(d, x, y, w, h, c):
    d.polygon([P(x + 4, y + h - 8), P(x + w - 4, y + 4), P(x + w / 2 + 2, y + h - 4),
               P(x + w / 2 - 2, y + h - 12)], fill=c)

def icon_window(d, x, y, w, h, c):
    d.rectangle([P(x + 4, y + 4), P(x + w - 4, y + h - 4)], outline=c,
                width=int(3 * S))
    line(d, (x + w / 2, y + 4), (x + w / 2, y + h - 4), c, 3)
    line(d, (x + 4, y + h / 2), (x + w - 4, y + h / 2), c, 3)

def icon_capitol(d, x, y, w, h, c):
    d.ellipse([P(x + w / 2 - 7, y + 2), P(x + w / 2 + 7, y + 12)], fill=c)
    d.rectangle([P(x + 4, y + 12), P(x + w - 4, y + 16)], fill=c)
    for i in range(3):
        bx = x + 7 + i * (w - 14) / 2
        d.rectangle([P(bx, y + 18), P(bx + 4, y + h - 6)], fill=c)
    d.rectangle([P(x + 2, y + h - 5), P(x + w - 2, y + h - 2)], fill=c)

def icon_virus(d, x, y, w, h, c):
    cx, cy = x + w / 2, y + h / 2
    for k in range(8):
        a = math.pi * k / 4
        line(d, (cx + math.cos(a) * 8, cy + math.sin(a) * 8),
             (cx + math.cos(a) * 13, cy + math.sin(a) * 13), c, 3)
    dot(d, cx, cy, 8, c)

def icon_pump(d, x, y, w, h, c):
    d.rectangle([P(x + 8, y + 6), P(x + w - 10, y + h - 4)], outline=c,
                width=int(3 * S))
    d.rectangle([P(x + 11, y + 10), P(x + w - 13, y + 16)], fill=c)
    line(d, (x + w - 10, y + 8), (x + w - 4, y + 8), c, 3)
    line(d, (x + w - 4, y + 8), (x + w - 4, y + h - 10), c, 3)

def icon_gate(d, x, y, w, h, c):
    d.rectangle([P(x + 4, y + 4), P(x + w - 4, y + h - 4)], outline=c,
                width=int(3 * S))
    line(d, (x + 6, y + 6), (x + w - 6, y + h - 6), c, 3)
    line(d, (x + 6, y + h - 6), (x + w - 6, y + 6), c, 3)

def icon_shield(d, x, y, w, h, c):
    d.polygon([P(x + 4, y + 4), P(x + w - 4, y + 4), P(x + w - 4, y + h / 2 + 4),
               P(x + w / 2, y + h - 2), P(x + 4, y + h / 2 + 4)], fill=c)
    line(d, (x + 8, y + h / 2), (x + w - 8, y + h / 2 + 6), (255, 255, 255), 3)

def icon_tv(d, x, y, w, h, c):
    d.rectangle([P(x + 4, y + 8), P(x + w - 4, y + h - 6)], outline=c,
                width=int(3 * S))
    line(d, (x + w / 2, y + 8), (x + w / 2 - 6, y + 2), c, 3)
    line(d, (x + w / 2, y + 8), (x + w / 2 + 6, y + 2), c, 3)
    line(d, (x + 8, y + h - 8), (x + w - 8, y + 8), c, 3)

def icon_exit(d, x, y, w, h, c):
    d.rectangle([P(x + 4, y + 4), P(x + w - 4, y + h - 4)], outline=c,
                width=int(3 * S))
    line(d, (x + 8, y + h / 2), (x + w - 10, y + h / 2), c, 3)
    d.polygon([P(x + w - 10, y + h / 2 - 5), P(x + w - 4, y + h / 2),
               P(x + w - 10, y + h / 2 + 5)], fill=c)

def icon_pause(d, x, y, w, h, c):
    d.rectangle([P(x + 8, y + 6), P(x + 14, y + h - 6)], fill=c)
    d.rectangle([P(x + w - 14, y + 6), P(x + w - 8, y + h - 6)], fill=c)

def icon_bolt(d, x, y, w, h, c):
    d.polygon([P(x + w / 2 + 4, y + 2), P(x + 6, y + h / 2 + 2),
               P(x + w / 2 - 2, y + h / 2 + 2), P(x + w / 2 - 4, y + h - 2),
               P(x + w - 6, y + h / 2 - 2), P(x + w / 2 + 2, y + h / 2 - 2)],
              fill=c)

def icon_sink(d, x, y, w, h, c):
    d.polygon([P(x + 4, y + h - 14), P(x + w - 12, y + h - 20),
               P(x + w - 6, y + h - 12), P(x + 10, y + h - 6)], fill=c)
    for wy in (h - 4, h - 8):
        for i in range(3):
            wx = x + 6 + i * 10
            d.arc([P(wx, y + wy - 3), P(wx + 10, y + wy + 3)], 0, 180,
                  fill=(46, 95, 163), width=int(2 * S))

ICONS = {"burst": icon_burst, "tag": icon_tag, "gavel": icon_gavel,
         "fence": icon_fence, "court": icon_court, "advance": icon_advance,
         "robot": icon_robot, "radiation": icon_radiation, "chip": icon_chip,
         "pentagon": icon_pentagon, "ship": icon_ship, "plane": icon_plane,
         "window": icon_window, "capitol": icon_capitol, "virus": icon_virus,
         "pump": icon_pump, "gate": icon_gate, "shield": icon_shield,
         "tv": icon_tv, "exit": icon_exit, "pause": icon_pause,
         "bolt": icon_bolt, "sink": icon_sink}

# ---------------------------------------------------------------- hero scenes
# Each scene draws inside (x, y, w, h) in 1x coords.
def scene_bridge(d, x, y, w, h):
    # water
    d.rectangle([P(x, y + h - 14), P(x + w, y + h)], fill=(120, 175, 210))
    for i in range(3):
        wx = x + 8 + i * (w - 16) / 2
        d.arc([P(wx, y + h - 10), P(wx + 16, y + h - 2)], 180, 360,
              fill=(255, 255, 255), width=int(2 * S))
    # towers + deck, middle span collapsed
    d.rectangle([P(x + 14, y + 12), P(x + 20, y + h - 14)], fill=(90, 100, 118))
    d.rectangle([P(x + w - 20, y + 12), P(x + w - 14, y + h - 14)],
                fill=(90, 100, 118))
    d.rectangle([P(x + 8, y + 16), P(x + w / 2 - 6, y + 22)], fill=(70, 78, 96))
    d.polygon([P(x + w / 2 + 2, y + 22), P(x + w - 8, y + 30),
               P(x + w - 8, y + 36), P(x + w / 2 - 2, y + 28)], fill=(70, 78, 96))
    # smoke + burst at the break
    for i, (sx, sy, sr) in enumerate(((0, -6, 7), (10, -12, 9), (22, -8, 6))):
        dot(d, x + w / 2 + sx, y + 16 + sy, sr, (120, 120, 120))
    icon_burst(d, x + w / 2 - 8, y + 2, 16, 16, (232, 197, 92))

def scene_summit(d, x, y, w, h):
    # APEC banner (top), three silhouettes below (heads + shoulders, no faces)
    d.rectangle([P(x + 6, y + 1), P(x + w - 6, y + 13)], fill=GOLD)
    draw_text(d, (x + w / 2, y + 7), "APEC 2026", font_bold(10), NAVY,
              anchor="mm")
    # table
    d.rectangle([P(x + 10, y + h - 6), P(x + w - 10, y + h - 2)],
                fill=(90, 100, 118))
    # three silhouettes (heads always; shoulders only fit when h > 35)
    for cx in (x + w * 0.25, x + w * 0.5, x + w * 0.75):
        dot(d, cx, y + 22, 7, (52, 64, 90))
        if h > 35:
            d.pieslice([P(cx - 11, y + 29), P(cx + 11, y + h - 6)], 180, 360,
                       fill=(52, 64, 90))
        else:
            d.rectangle([P(cx - 10, y + 26), P(cx + 10, y + h - 2)],
                        fill=(52, 64, 90))

def scene_radar(d, x, y, w, h):
    # night sky
    d.rectangle([P(x, y), P(x + w, y + h)], fill=(36, 52, 86))
    dot(d, x + w - 14, y + 10, 5, (232, 197, 92))
    # dome
    d.pieslice([P(x + 8, y + h - 26), P(x + 44, y + h + 4)], 180, 360,
               fill=(235, 238, 245))
    line(d, (x + 26, y + h - 26), (x + 26, y + h - 40), (235, 238, 245), 3)
    line(d, (x + 26, y + h - 40), (x + 38, y + h - 46), (235, 238, 245), 3)
    # drones + interception bursts
    for dx, dy in ((w - 34, 18), (w - 52, 30), (w - 22, 34)):
        line(d, (x + dx - 5, y + dy), (x + dx + 5, y + dy), (255, 255, 255), 2)
        line(d, (x + dx, y + dy - 5), (x + dx, y + dy + 5), (255, 255, 255), 2)
    icon_burst(d, x + w - 40, y + 22, 14, 14, (232, 197, 92))

def scene_jets(d, x, y, w, h):
    # Japan archipelago: 4 small islands in a SW-NE arc
    for fx, fy, iw, ih in ((0.06, 0.78, 26, 10), (0.14, 0.62, 34, 12),
                           (0.24, 0.48, 22, 9), (0.30, 0.36, 14, 7)):
        d.ellipse([P(x + w * fx, y + h * fy),
                   P(x + w * fx + iw, y + h * fy + ih)],
                  fill=(120, 170, 110))
    # two fighter jets: bold dart silhouette (fuselage + delta wing + tail)
    # NOTE: jy already includes y — do NOT add y again.
    for jx, jy, s in ((x + w * 0.42, y + 6, 1.0), (x + w * 0.66, y + 20, 0.85)):
        L = 46 * s
        d.polygon([P(jx, jy + 6 * s),
                   P(jx + L, jy),
                   P(jx + L * 0.75, jy + 8 * s),
                   P(jx + L * 0.55, jy + 17 * s),
                   P(jx + L * 0.30, jy + 8 * s)],
                  fill=(52, 64, 90))
        d.polygon([P(jx + L * 0.10, jy + 6 * s),
                   P(jx + L * 0.22, jy - 4 * s),
                   P(jx + L * 0.32, jy + 6 * s)],
                  fill=(52, 64, 90))
        dot(d, jx + L * 0.68, jy + 4 * s, 3 * s, (255, 255, 255))
    # alert chevrons
    for i in range(2):
        cx = x + w - 22 + i * 10
        d.polygon([P(cx, y + 8), P(cx + 8, y + 16), P(cx, y + 24)], fill=GOLD)

def scene_tents(d, x, y, w, h):
    # pale ground band so white tents read
    d.rectangle([P(x, y + 4), P(x + w, y + h)], fill=(226, 220, 200))
    # border gate (two posts + top bar)
    d.rectangle([P(x + w - 24, y + 6), P(x + w - 20, y + h - 4)],
                fill=(90, 100, 118))
    d.rectangle([P(x + w - 10, y + 6), P(x + w - 6, y + h - 4)],
                fill=(90, 100, 118))
    d.rectangle([P(x + w - 26, y + 4), P(x + w - 4, y + 10)], fill=(90, 100, 118))
    # rows of tan tents with dark outlines
    for row, ty in enumerate((y + h - 20, y + h - 34)):
        for i in range(4):
            tx = x + 6 + i * 24 + (row * 8)
            d.polygon([P(tx, ty + 12), P(tx + 9, ty), P(tx + 18, ty + 12)],
                      fill=(196, 178, 138), outline=(120, 105, 70))

def scene_arrow(d, x, y, w, h):
    # Europe dot (blue, top-left) -> curved gold arrow -> Africa dot (green)
    dot(d, x + 16, y + 12, 8, (46, 95, 163))
    dot(d, x + w - 22, y + h - 12, 9, (30, 138, 90))
    d.arc([P(x + 14, y + 2), P(x + w - 2, y + h + 6)], 250, 60,
          fill=GOLD, width=int(4 * S))
    hx, hy = x + w - 26, y + h - 22
    d.polygon([P(hx, hy), P(hx + 13, hy + 4), P(hx + 2, hy + 13)], fill=GOLD)

def scene_chart(d, x, y, w, h):
    # plunging chart + chip
    d.rectangle([P(x, y), P(x + w, y + h)], fill=(245, 240, 228))
    pts = [(x + 6, y + 10), (x + w * 0.3, y + 16), (x + w * 0.5, y + 12),
           (x + w * 0.7, y + 26), (x + w - 8, y + h - 12)]
    d.line([P(*p) for p in pts], fill=(192, 57, 43), width=int(4 * S),
           joint="curve")
    d.polygon([P(x + w - 16, y + h - 20), P(x + w - 6, y + h - 10),
               P(x + w - 16, y + h - 10)], fill=(192, 57, 43))
    icon_chip(d, x + w - 30, y + 4, 24, 24, (108, 74, 176))

def scene_bus(d, x, y, w, h):
    # cliffs + gorge
    d.polygon([P(x, y + h), P(x, y + 12), P(x + w * 0.40, y + h - 12),
               P(x + w * 0.40, y + h)], fill=(150, 125, 95))
    d.polygon([P(x + w, y + h), P(x + w, y + 12), P(x + w * 0.60, y + h - 12),
               P(x + w * 0.60, y + h)], fill=(130, 105, 80))
    # bus as a tilted parallelogram, down inside the gorge
    cx, cy = x + w / 2, y + h / 2 + 4
    d.polygon([P(cx - 24, cy - 4), P(cx + 20, cy - 12), P(cx + 26, cy + 2),
               P(cx - 18, cy + 10)], fill=(232, 180, 40))
    for i in range(3):
        wx = cx - 16 + i * 13
        d.polygon([P(wx, cy - 5), P(wx + 8, cy - 7), P(wx + 8, cy + 1),
                   P(wx, cy + 3)], fill=(255, 255, 255))
    # dust clouds
    dot(d, cx - 16, cy + 12, 5, (190, 175, 140))
    dot(d, cx + 12, cy + 14, 6, (190, 175, 140))

SCENES = {"bridge": scene_bridge, "summit": scene_summit, "radar": scene_radar,
          "jets": scene_jets, "tents": scene_tents, "arrow": scene_arrow,
          "chart": scene_chart, "bus": scene_bus}

# ---------------------------------------------------------------- cards
def draw_vignette(d, hero, box, lead=False, scene_h=30, detail_px=16):
    """hero = (num, cat, headline, detail, dotx, doty, scene); box 1x coords.
    Every hero shows headline (24px bold, up to 2 lines) AND a detail
    line (detail_px, up to 2 lines) so the story is clear on its own.
    scene_h is passed per card (lead 34, wide cards 30, narrow cards 30).
    Vertical budget: 36 + scene_h + 6 + 52 + 2 + 2*detail_lh must fit h."""
    num, cat, headline, detail, _, _, scene = hero
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    colour = CAT[cat]
    shadow(d, box, 10)
    rr(d, box, 10, fill=CARD, outline=(GOLD if lead else CARD_LN),
       width=3 if lead else 2)
    # category bar
    d.rectangle([(x0 + 10) * S, y0 * S, (x1 - 10) * S, (y0 + 5) * S],
                fill=colour)
    # number badge
    num_badge(d, x0 + 20, y0 + 20, 13, num, colour)
    # scene
    SCENES[scene](d, x0 + 10, y0 + 36, w - 20, scene_h)
    # headline (2 lines max at 24px)
    f_h = font_bold(24)
    hy = y0 + 36 + scene_h + 6
    hl = wrap(headline, f_h, w - 10)
    for ln in hl[:2]:
        draw_text(d, (x0 + 10, hy), ln, f_h, INK)
        hy += 26
    # detail line(s) for every hero (up to 2 lines)
    if detail:
        f_d = font_reg(detail_px)
        dl = wrap(detail, f_d, w - 10)
        dy = hy + 2
        lh = 19 if detail_px >= 16 else 18
        for ln in dl[:2]:
            draw_text(d, (x0 + 10, dy), ln, f_d, INK_SOFT)
            dy += lh

def draw_brief_row(d, brief, box):
    """brief = (num, cat, headline, desc, dotx, doty); box 1x coords.
    One row: coloured number badge + bold headline + ': ' + description,
    all on one line at 16px. Returns the rendered line width (1x px)."""
    num, cat, headline, desc, _, _ = brief
    x0, y0, x1, y1 = box
    colour = CAT[cat]
    cy = (y0 + y1) / 2
    num_badge(d, x0 + 11, cy, 10, num, colour)
    f_h = font_bold(16)
    f_d = font_reg(16)
    tx = x0 + 26
    draw_text(d, (tx, cy), headline + ": ", f_h, INK, anchor="lm")
    w_h = txt_w(headline + ": ", f_h)
    draw_text(d, (tx + w_h, cy), desc, f_d, INK, anchor="lm")
    return w_h + txt_w(desc, f_d)

# Layout (single layout; variant B dropped with the chip strip).
# Hero zone 132-648: lead 168 tall, Japan 150, middle/bottom 166.
# Cards sit at the edges so no numbered map dot is covered.
def layout_new():
    return {
        "dark": False,
        "vignettes": [
            # (hero index, x0, y0, x1, y1, lead, scene_h, detail_px)
            (0, 20, 132, 290, 300, True, 34, 16),   # 1 Crimea, top-left, lead
            (3, 664, 132, 1004, 282, False, 30, 16),# 4 Japan, top-right
            (6, 20, 308, 190, 474, False, 30, 15),  # 7 Markets, left-middle
            (1, 834, 308, 1004, 474, False, 30, 15),# 2 Summit, right-middle
            (5, 136, 482, 306, 648, False, 30, 15), # 6 Rwanda, bottom row
            (4, 330, 482, 500, 648, False, 30, 15), # 5 Gaza, bottom row
            (2, 524, 482, 694, 648, False, 30, 15), # 3 Bahrain, bottom row
            (7, 718, 482, 888, 648, False, 30, 15), # 8 India, bottom row
        ],
        # leader lines: (card edge point, dot) per hero index
        "leaders": {
            0: ((290, 216), (609, 220)),
            3: ((908, 282), (908, 296)),
            1: ((919, 308), (836, 292)),
            6: ((190, 391), (301, 232)),
            5: ((221, 482), (597, 356)),
            4: ((415, 482), (611, 259)),
            2: ((609, 482), (656, 275)),
            7: ((803, 482), (737, 302)),
        },
    }

# ---------------------------------------------------------------- render
def render(variant="A"):
    L = layout_new()
    img = Image.new("RGB", (VW, VH), PAPER)
    d = ImageDraw.Draw(img, "RGBA")
    # masthead
    d.rectangle([0, 0, VW, 100 * S], fill=NAVY)
    d.rectangle([0, 100 * S, VW, 101 * S], fill=GOLD)
    draw_text(d, (W / 2, 8), "THE DAY IN WORLD NEWS", font_bold(18),
              GOLD_L, anchor="ma")
    draw_text(d, (W / 2, 30), "TUESDAY 17 NOVEMBER 2026", font_bold(60),
              (255, 255, 255), anchor="ma")
    # count strip
    d.rectangle([0, 101 * S, VW, 124 * S], fill=GOLD)
    draw_text(d, (W / 2, 103), "33 STORIES  ·  6 CONTINENTS  ·  ONE DAY",
              font_bold(18), NAVY, anchor="ma")
    # map
    draw_map(d, dark=L["dark"])
    # leader lines (under cards, over map)
    for idx, (p0, p1) in L["leaders"].items():
        line(d, p0, p1, (150, 130, 80), 2)
    # hero dots (numbered) + brief dots (small)
    for num, cat, _, _, dx, dy, _ in HEROES:
        num_badge(d, dx, dy, 13, num, CAT[cat])
    for num, cat, _, _, dx, dy in BRIEFS:
        if dx is not None:
            dot(d, dx, dy, 5, CAT[cat], ring=(255, 255, 255), ring_w=1)
    # vignette cards (over map + lines; hero dots redrawn after so they stay visible)
    for idx, x0, y0, x1, y1, lead, scene_h, detail_px in L["vignettes"]:
        draw_vignette(d, HEROES[idx], (x0, y0, x1, y1), lead=lead,
                      scene_h=scene_h, detail_px=detail_px)
    for num, cat, _, _, dx, dy, _ in HEROES:
        num_badge(d, dx, dy, 13, num, CAT[cat])
    # briefs header: title left, legend right (one line)
    draw_text(d, (20, 654), "THE DAY IN BRIEF", font_bold(22), NAVY)
    lx = W - 20
    for name in reversed(CAT_ORDER):
        label = CAT_LABEL[name]
        tw = txt_w(label, font_bold(18))
        lx -= tw
        draw_text(d, (lx, 656), label, font_bold(18), INK)
        dot(d, lx - 12, 666, 7, CAT[name], ring=(255, 255, 255), ring_w=1)
        lx -= 12 + 8 + 18
    line(d, (20, 678), (1004, 678), GOLD, 3)
    # briefs: 2 columns x 13 rows, one story per row (25 stories, 9-33).
    # Left column: briefs 9-21; right column: briefs 22-33.
    rows_y0, rows_y1 = 680, 1002
    row_h = (rows_y1 - rows_y0) / 13
    cols = [(20, 504, BRIEFS[:13]), (520, 1004, BRIEFS[13:])]
    for cx0, cx1, col_briefs in cols:
        for i, brief in enumerate(col_briefs):
            ry0 = rows_y0 + i * row_h
            ry1 = ry0 + row_h
            w = draw_brief_row(d, brief, (cx0, ry0, cx1, ry1))
            if w > (cx1 - cx0) - 26:
                print("OVERFLOW brief", brief[0], "width", round(w, 1))
            if i < 12:
                line(d, (cx0, ry1), (cx1, ry1), (226, 220, 200), 1)
    # footer (14 px, exempt from the 15 px minimum)
    draw_text(d, (W / 2, 1008),
              "Every story happened or was first reported on Tuesday 17 November 2026.  "
              "Sources: Reuters · Al Jazeera · CNN · NPR · AP.  Original drawings.",
              font_reg(14), INK_SOFT, anchor="ma")
    return img.resize((W, H), Image.LANCZOS)

if __name__ == "__main__":
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else "entry.png"
    variant = sys.argv[2] if len(sys.argv) > 2 else "A"
    render(variant).save(out, optimize=True)
    print("wrote", out, "variant", variant)
