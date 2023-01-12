import math
import re
import numpy as np


## chmelnice ##
chmel_start = '<segment start="1372 280" end="1372 376"/>' # 
#chmel_start = '<segment start="1498 232" end="1498 336"/>' # 28
#chmel_start = '<segment start="1548 104" end="1548 176"/>' # 22
#chmel_start = '<segment start="1690 272" end="1690 96"/>' # 7
#chmel_start = '<segment start="1672 192" end="1672 288"/>' # 37
#chmel_start = '<segment start="0 0" end="8 0"/>'
#chmel_start = '<segment start="1662 80" end="1662 176"/>' # 25
chmel_pocet_radku = 10   # 4; 7; 10; 13; 16; 19; 22; 25; 28; 31; 34; 37;
##

def angle(points):
    xdiff = points[0] - points[2]
    ydiff = points[1] - points[3]
    atan = math.atan2(ydiff, xdiff)
    return atan

chmel_roztec_radku = 4  # neměnit (rozteč rostlin)
chmel = re.findall("[-+]?[.]?[\d]+(?:,\d\d\d)*[\.]?\d*(?:[eE][-+]?\d+)?", chmel_start)

for index, item in enumerate(chmel):
    chmel[index] = float(item)

perp_angle = angle(chmel) + math.pi

print("\t"+chmel_start)
for i in range(1, chmel_pocet_radku):
    tmp_x1 = chmel[0] - math.sin(perp_angle) * chmel_roztec_radku * i;
    tmp_y1 = chmel[1] - math.cos(perp_angle) * chmel_roztec_radku * i;

    tmp_x2 = chmel[2] - math.sin(perp_angle) * chmel_roztec_radku * i;
    tmp_y2 = chmel[3] - math.cos(perp_angle) * chmel_roztec_radku * i;

    print("\t"+'<segment start="{:.6f} {:.6f}" end="{:.6f} {:.6f}"/>'.format(tmp_x1, tmp_y1, tmp_x2, tmp_y2))   #další chmely

segment_start = chmel_start
segment_end = '<segment start="{:.6f} {:.6f}" end="{:.6f} {:.6f}"/>'.format(tmp_x1, tmp_y1, tmp_x2, tmp_y2)     # poslední řádek chmele
## chmelnice END ##


# může být zadáno i ručně (první a poslední řádek)
#segment_start = '<segment start="1662 80" end="1662 176"/>'
#segment_end = '<segment start="1566 80" end="1566 176"/>'


## sloupy ##
def distanceL(points):
    px = (points[0] - points[2])
    py = (points[1] - points[3])
    return math.sqrt(px**2 + py**2)

def interpolationL(points, alpha):
    x1, y1 = points[0], points[1]
    x2, y2 = points[2], points[3]
    x = x2 * alpha + x1 * (1 - alpha)
    y = y2 * alpha + y1 * (1 - alpha)
    return x, y

s_top = re.findall("[-+]?[.]?[\d]+(?:,\d\d\d)*[\.]?\d*(?:[eE][-+]?\d+)?", segment_start)
s_bottom = re.findall("[-+]?[.]?[\d]+(?:,\d\d\d)*[\.]?\d*(?:[eE][-+]?\d+)?", segment_end)

for index, item in enumerate(s_top):
    s_top[index] = float(item)

for index, item in enumerate(s_bottom):
    s_bottom[index] = float(item)

s_left = [ s_top[0], s_top[1], s_bottom[0], s_bottom[1] ]
s_right = [ s_top[2], s_top[3], s_bottom[2], s_bottom[3] ]

print()
print("\t<!--délka vršku:", distanceL(s_top), "počet 8metrových oblastí:", (distanceL(s_top) / 8), "zaokrouhleno na:", round(distanceL(s_top) / 8), " | skutečný rozestup:", distanceL(s_top) / (round(distanceL(s_top) / 8)), " -->")

# sloupy od vršku směrem dolů (začínáme vlevo) s rozestupem cca po 8 metrech + u každého přidáme bránu na začátek i konec
for i in np.linspace(0, 1, num=round(distanceL(s_top) / 8)+1):
    start_x, start_y = interpolationL(s_top, i)
    end_x, end_y = interpolationL(s_bottom, i)
    print("\t"+'<segment start="{:.6f} {:.6f}" end="{:.6f} {:.6f}" first="false" last="flase"/>'.format(start_x, start_y, end_x, end_y))   #sloupy

    s_tmp = [ start_x, start_y, end_x, end_y ]
    tmp_end_x, tmp_end_y = interpolationL(s_tmp, -7 / distanceL(s_tmp))
    print("\t"+'<segment start="{:.6f} {:.6f}" end="{:.6f} {:.6f}" gateIndex="2" first="false" last="flase">'.format(start_x, start_y, tmp_end_x, tmp_end_y))   #brána_2 na vršku
    print("\t"+'    <animatedObject time="0.000000" direction="0"/>')
    print("\t"+'</segment>')

    tmp_end_x, tmp_end_y = interpolationL(s_tmp, 1 + 7 / distanceL(s_tmp))
    print("\t"+'<segment start="{:.6f} {:.6f}" end="{:.6f} {:.6f}" gateIndex="2" first="false" last="flase">'.format(end_x, end_y, tmp_end_x, tmp_end_y))   #brána_2 na spodku
    print("\t"+'    <animatedObject time="0.000000" direction="0"/>')
    print("\t"+'</segment>')

print("\t<!--délka levého boku:", distanceL(s_left), "počet 12metrových oblastí:", (distanceL(s_left) / 12), "zaokrouhleno na:", round(distanceL(s_left) / 12), " | skutečný rozestup:", distanceL(s_left) / (round(distanceL(s_left) / 12)), " -->")

# přidáme brány vlevo i vpravo po 12 metrech
for i in np.linspace(0, 1, num=round(distanceL(s_left) / 12)+1):

    if math.isclose(i, 0):
        ii = -0.966 / distanceL(s_left)         # posunutí o skoro metr k šikmému sloupku z brány1
    elif math.isclose(i, 1):
        ii = 1 + 0.966 / distanceL(s_left)      #  --//--
    else:
        ii = i

    start_x, start_y = interpolationL(s_left, ii)
    end_x, end_y = interpolationL(s_right, ii)
    #print("\t"+'<segment start="{:.6f} {:.6f}" end="{:.6f} {:.6f}"/>'.format(start_x, start_y, end_x, end_y))   #tyto sloupy nejsou potřeba

    s_tmp = [ start_x, start_y, end_x, end_y ]
    tmp_end_x, tmp_end_y = interpolationL(s_tmp, -7 / distanceL(s_tmp))
    print("\t"+'<segment start="{:.6f} {:.6f}" end="{:.6f} {:.6f}" gateIndex="1" first="false" last="flase">'.format(start_x, start_y, tmp_end_x, tmp_end_y))   #brána_1 vlevo
    print("\t"+'    <animatedObject time="0.000000" direction="0"/>')
    print("\t"+'</segment>')

    tmp_end_x, tmp_end_y = interpolationL(s_tmp, 1 + 7 / distanceL(s_tmp))
    print("\t"+'<segment start="{:.6f} {:.6f}" end="{:.6f} {:.6f}" gateIndex="1" first="false" last="flase">'.format(end_x, end_y, tmp_end_x, tmp_end_y))   #brána_1 vpravo
    print("\t"+'    <animatedObject time="0.000000" direction="0"/>')
    print("\t"+'</segment>')
