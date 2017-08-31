# -*- coding: utf-8 -*-

import pylab as pl
import cairo
import codecs
from os import system
import colorsys
import random

#DUZE LITERY

C = 30

class palec:
    counter = 0

    def __init__(self, klaw):
        self.klaw = klaw
        self.x = 5
        self.y = 6
        self.X = [8*C]
        self.Y = [5.5*C]
        self.oldx = [0]
        self.oldy = [0]
        self.distance = 0.0
        self.moved = False

        if palec.counter == 0:
            self.rest = 'C1'
        elif palec.counter == 1:
            self.rest = 'C2'
        elif palec.counter == 2:
            self.rest = 'C3'
        elif palec.counter == 3:
            self.rest = 'C4'
        elif palec.counter == 4:
            self.rest = 'space'

        elif palec.counter == 5:
            self.rest = 'C7'
        elif palec.counter == 6:
            self.rest = 'C8'
        elif palec.counter == 7:
            self.rest = 'C9'
        elif palec.counter == 8:
            self.rest = 'C10'
        elif palec.counter == 9:
            self.rest = 'space'
        else:
            self.rest = 'A0'

        self.number = palec.counter
        palec.counter += 1
        self.move(self.rest, init = True)
        self.X.pop(0)
        self.Y.pop(0)

        self.hot = False


    def move(self, key, init = False):
        self.oldx.append(self.x)
        self.oldy.append(self.y)

        if key[0] == 'A':
            self.x = eval(key[1:])
            self.y = 0
            self.X.append(eval(key[1:]))
            self.Y.append(0)

        elif key[0] == 'B':
            self.x = eval(key[1:]) + 0.6
            self.y = 1
            self.X.append(eval(key[1:]) + 0.6)
            self.Y.append(1)

        elif key[0] == 'C':
            self.x = eval(key[1:]) + 0.9
            self.y = 2
            self.X.append(eval(key[1:]) + 0.9)
            self.Y.append(2)

        elif key[0] == 'D':
            self.x = eval(key[1:]) + 1.5
            self.y = 3
            self.X.append(eval(key[1:]) + 1.5)
            self.Y.append(3)

        elif key == 'space':
            self.x = 7
            self.y = 4
            self.X.append(7)
            self.Y.append(4)

        elif key == 'backspace':
            self.x = 14
            self.y = 0
            self.X.append(14)
            self.Y.append(0)

        elif key == 'enter':
            self.x = 13.7
            self.y = 2
            self.X.append(13.7)
            self.Y.append(2)

        elif key == 'lshift':
            self.x = 1
            self.y = 3
            self.X.append(1)
            self.Y.append(3)

        elif key == 'rshift':
            self.x = 13
            self.y = 3
            self.X.append(13)
            self.Y.append(3)

        elif key == 'alt':
            self.x = 10
            self.y = 4
            self.X.append(10)
            self.Y.append(4)

        self.x += 0.5
        self.y += 0.5
        self.X[-1] += 0.5
        self.Y[-1] += 0.5
        
        self.x *= C
        self.y *= C
        self.X[-1] *= C
        self.Y[-1] *= C
        

        if not init:
            self.distance += pl.sqrt(
                (self.X[-1] - self.X[-2])**2 + (self.Y[-1] - self.Y[-2])**2 ) / C
        #self.distance += pl.sqrt( (self.oldx[-1] - self.x)**2 + (self.oldy[-1] - self.y)**2 )

    def turn(self):
        if self.moved == False:
            if self not in [self.klaw.ktory_palec(k) for k in self.klaw.buffer[-4:]]:
                self.move(self.rest)
            else:
                self.X.append(self.X[-1])
                self.Y.append(self.Y[-1])
        self.moved = False

    def draw(self, ctx):
        N = 10
        for i in range(min(N, len(self.X) - 1)):
            ctx.set_source_rgba(0, 0, 0.5, 0.4 * 0.9**i)
            ctx.move_to(self.X[-(i+2)], self.Y[-(i+2)])
            ctx.line_to(self.X[-(i+1)], self.Y[-(i+1)])
            ctx.set_line_width(0.5*C)
            ctx.set_line_cap(cairo.LINE_CAP_ROUND)
            ctx.stroke()
        ctx.set_line_width(2)
        ctx.set_line_cap(cairo.LINE_CAP_BUTT)

        ctx.arc(self.X[-1], self.Y[-1], 0.4 * C, 0, 2*pl.pi)
        ctx.set_source_rgba(0.2, 0.2, 0.5, 1)
        ctx.fill()
        ctx.stroke()

        #if self.hot:
        #    ctx.set_source_rgba(1, 0.6, 0.9, 1)
        #    ctx.arc(self.X[-1], self.Y[-1], 0.6 * C, 0, 2*pl.pi)
        #    ctx.set_line_width(0.2*C)
        #    ctx.stroke()
        #    ctx.set_line_width(2)
        #    self.hot = False



##################
### KLAWIATURA ###
##################

class klawiatura:
    """klawiatura"""
    counter = 0

    def __init__(self, dvorak = False, drawing = False):
        self.dvorak = dvorak
        self.drawing = drawing

        self.keys = [ a + str(b)
                      for a in ['A', 'B', 'C', 'D']
                      for b in range(13)]
        #self.keys.remove('B0')
        self.keys.remove('C0')
        self.keys.remove('C12')
        self.keys.remove('D0')
        self.keys.remove('D11')
        self.keys.remove('D12')
        self.keys.append('B13')
        self.keys.append('space')
        self.keys.append('alt')
        self.keys.append('lshift')
        self.keys.append('rshift')
        self.keys.append('enter')
        self.keys.append('backspace')

        self.leftHand = 0
        self.rightHand = 0
        self.home_row = 0
        self.processed_text = 0

        self.combo = [0]*100
        self.current_combo = 0
        self.last_hand = 'R'

        self.comboF = [0]*100
        self.current_comboF = 0
        self.last_finger = None
        self.last_key = None

        self.pressed_keys = []
        self.shift = False
        self.alt = False
        
        self.heat = {}
        for k in self.keys:
            self.heat[k] = 0

        if self.drawing:
            klawiatura.setup_drawing()

        palec.counter = 0
        self.palceL = [ palec(self) for i in range(5) ]
        self.palceR = [ palec(self) for i in range(5) ]

        self.map_char = self.map_char_dvorak if dvorak else self.map_char_qwerty

    @staticmethod
    def setup_drawing():
        klawiatura.surface = cairo.ImageSurface (cairo.FORMAT_ARGB32, 38 * C, 13 * C)
        klawiatura.ctx = cairo.Context (klawiatura.surface)
        klawiatura.ctx.set_source_rgb(1, 1, 1)
        klawiatura.ctx.paint()
        

    def map_char_qwerty(self, c):
        self.shift = c.isupper() or c in ['!', '@', '#', '$', '%', '^', '&',
                                          '*', '(', ')', '_', '+', '{', '}',
                                          ':', '"', '<', '>', '?', '|']
        
        self.alt = c in ['ę', 'Ę', 'ó', 'Ó', 'ą', 'Ą', 'ś', 'Ś', 'ł', 'Ł', 'ż',
                         'Ż', 'ź', 'Ź', 'ć', 'Ć', 'ń', 'Ń']


        if c in ['~', '`']: return 'A0'
        elif c in ['1', '!']: return 'A1'
        elif c in ['2', '@']: return 'A2'
        elif c in ['3', '#']: return 'A3'
        elif c in ['4', '$']: return 'A4'
        elif c in ['5', '%']: return 'A5'
        elif c in ['6', '^']: return 'A6'
        elif c in ['7', '&']: return 'A7'
        elif c in ['8', '*']: return 'A8'
        elif c in ['9', '(']: return 'A9'
        elif c in ['0', ')']: return 'A10'
        elif c in ['-', '_']: return 'A11'
        elif c in ['+', '=']: return 'A12'

        elif c in ['\t']: return 'B0'
        elif c in ['q', 'Q']: return 'B1'
        elif c in ['w', 'W']: return 'B2'
        elif c in ['e', 'E', 'ę', 'Ę']: return 'B3'
        elif c in ['r', 'R']: return 'B4'
        elif c in ['t', 'T']: return 'B5'
        elif c in ['y', 'Y']: return 'B6'
        elif c in ['u', 'U']: return 'B7'
        elif c in ['i', 'I']: return 'B8'
        elif c in ['o', 'O', 'ó', 'Ó']: return 'B9'
        elif c in ['p', 'P']: return 'B10'
        elif c in ['[', '{']: return 'B11'
        elif c in [']', '}']: return 'B12'
        elif c in ['\\', '|']: return 'B13'

        elif c in ['a', 'A', 'ą', 'Ą']: return 'C1'
        elif c in ['s', 'S', 'ś', 'Ś']: return 'C2'
        elif c in ['d', 'D']: return 'C3'
        elif c in ['f', 'F']: return 'C4'
        elif c in ['g', 'G']: return 'C5'
        elif c in ['h', 'H']: return 'C6'
        elif c in ['j', 'J']: return 'C7'
        elif c in ['k', 'K']: return 'C8'
        elif c in ['l', 'L', 'ł', 'Ł']: return 'C9'
        elif c in [':', ';']: return 'C10'
        elif c in ['\'', '"']: return 'C11'

        elif c in ['z', 'Z', 'ż', 'Ż']: return 'D1'
        elif c in ['x', 'X', 'ź', 'Ź']: return 'D2'
        elif c in ['c', 'C', 'ć', 'Ć']: return 'D3'
        elif c in ['v', 'V']: return 'D4'
        elif c in ['b', 'B']: return 'D5'
        elif c in ['n', 'N', 'ń', 'Ń']: return 'D6'
        elif c in ['m', 'M']: return 'D7'
        elif c in [',', '<']: return 'D8'
        elif c in ['.', '>']: return 'D9'
        elif c in ['/', '?']: return 'D10'

        elif c in ['\n']: return 'enter'
        elif c in [' ']: return 'space'

        else:
            print 'KEY NOT FOUND:', c
            return ''

    def map_char_dvorak(self, c):
        self.shift = c.isupper() or c in ['!', '@', '#', '$', '%', '^', '&',
                                          '_', ':', '"', '<', '>', '?', '|']
        
        self.alt = c in ['ę', 'Ę', 'ó', 'Ó', 'ą', 'Ą', 'ś', 'Ś', 'ł', 'Ł', 'ż',
                         'Ż', 'ź', 'Ź', 'ć', 'Ć', 'ń', 'Ń', '(', ')', '[', ']',
                         '{', '}', '+', '-', '*', '/', '=']


        if c in ['~', '`']: return 'A0'
        elif c in ['1', '!']: return 'A1'
        elif c in ['2', '@']: return 'A2'
        elif c in ['3', '#']: return 'A3'
        elif c in ['4', '$']: return 'A4'
        elif c in ['5', '%']: return 'A5'
        elif c in ['6', '^']: return 'A6'
        elif c in ['7', '&']: return 'A7'
        elif c in ['8']: return 'A8'
        elif c in ['9']: return 'A9'
        elif c in ['0']: return 'A10'
        #elif c in ['_']: return 'A11'

        elif c in ['\t']: return 'B0'
        elif c in ['\'', '"', '(']: return 'B1'
        elif c in [',', '<', ')']: return 'B2'
        elif c in ['.', '>', '[']: return 'B3'
        elif c in ['p', 'P', ']']: return 'B4'
        elif c in ['y', 'Y']: return 'B5'
        elif c in ['f', 'F']: return 'B6'
        elif c in ['g', 'G']: return 'B7'
        elif c in ['c', 'C','ć', 'Ć']: return 'B8'
        elif c in ['r', 'R']: return 'B9'
        elif c in ['l', 'L', 'ł', 'Ł']: return 'B10'
        elif c in ['/', '?']: return 'B11'
        #elif c in [']', '}']: return 'B12'
        elif c in ['\\', '|']: return 'B13'

        elif c in ['a', 'A', 'ą', 'Ą']: return 'C1'
        elif c in ['o', 'O', 'ó', 'Ó']: return 'C2'
        elif c in ['e', 'E', 'ę', 'Ę']: return 'C3'
        elif c in ['u', 'U', '+']: return 'C4'
        elif c in ['i', 'I', '-']: return 'C5'
        elif c in ['d', 'D']: return 'C6'
        elif c in ['h', 'H', '{']: return 'C7'
        elif c in ['t', 'T', '}']: return 'C8'
        elif c in ['n', 'N', 'ń', 'Ń']: return 'C9'
        elif c in ['s', 'S', 'ś', 'Ś']: return 'C10'
        elif c in ['_']: return 'C11'

        elif c in ['z', 'Z', 'ż', 'Ż']: return 'D1'
        elif c in ['q', 'Q', 'ź', 'Ź']: return 'D2'
        elif c in ['j', 'J', '*']: return 'D3'
        elif c in ['k', 'K', '/']: return 'D4'
        elif c in ['x', 'X', '=']: return 'D5'
        elif c in ['b', 'B']: return 'D6'
        elif c in ['m', 'M']: return 'D7'
        elif c in ['w', 'W']: return 'D8'
        elif c in ['v', 'V']: return 'D9'
        elif c in [':', ';']: return 'D10'

        elif c in ['\n']: return 'enter'
        elif c in [' ']: return 'space'

        else:
            print 'KEY NOT FOUND:', c
            return ''
        

    def ktory_palec(self, key):
        if key[1:] == '1' or key in ['A0', 'B0', 'lshift']:
            return self.palceL[0], 'L'

        if key[1:] == '2':
            return self.palceL[1], 'L'

        if key[1:] == '3':
            return self.palceL[2], 'L'

        if key[1:] in ['4', '5']:
            return self.palceL[3], 'L'

        if key[1:] in ['6', '7']:
            return self.palceR[0], 'R'

        if key[1:] == '8':
            return self.palceR[1], 'R'

        if key[1:] == '9':
            return self.palceR[2], 'R'

        if key[1:] in ['10', '11', '12', '13'] or key in ['enter', 'rshift']:
            return self.palceR[3], 'R'

        if key == 'space':
            return self.palceL[4], 'L'

        if key == 'backspace':
            return self.palceR[3], 'R'

        if key == 'alt':
            return self.palceR[4], 'R'



    def press(self, key):
        self.buffer.pop(0)
        self.pressed_keys.append( key )
        self.processed_text += 1
        hand = None

        self.heat[key] += 1

        p, hand = self.ktory_palec(key)
        p.move(key)
        p.moved = True
        p.hot = True

        if self.shift:
            if hand == 'L':
                self.pressed_keys.append('rshift')
                self.palceR[3].move('rshift')
                self.palceR[3].moved = True
            if hand == 'R':
                self.pressed_keys.append('lshift')
                self.palceL[0].move('lshift')
                self.palceL[0].moved = True

        if self.alt:
            self.pressed_keys.append('alt')
            self.palceR[4].move('alt')

        for pa in self.palceR:
            pa.turn()

        for pa in self.palceL:
            pa.turn()


        if key not in ['space', 'rshift', 'lshift']:
            if hand == 'L':
                self.leftHand += 1
            elif hand == 'R':
                self.rightHand += 1

        if key[0] == 'C':
            self.home_row += 1

        if (hand == self.last_hand) and (key != 'space'):
            self.current_combo += 1
        else:
            self.combo[self.current_combo] += 1
            self.current_combo = 0
        self.last_hand = hand

        if p == self.last_finger and key != self.last_key:
            self.current_comboF += 1
        else:
            self.comboF[self.current_comboF] += 1
            self.current_comboF = 0
        self.last_finger = p
        self.last_key = key

        if self.drawing:
            self.draw()
        #self.pressed_keys.remove( key )
        self.pressed_keys = []

        #if random.random() < 0.1:
        #    self.buffer.insert(0, 'backspace')

    @staticmethod
    def write_image():
        klawiatura.ctx.stroke()
        klawiatura.surface.write_to_png('anim%04i.png' % klawiatura.counter)

        klawiatura.ctx.set_source_rgb(1, 1, 1)
        klawiatura.ctx.paint()

        klawiatura.counter += 1


    def draw(self, nofingers = False):
        klawiatura.ctx.translate(2 * C, 2 * C)
        if self.dvorak:
            klawiatura.ctx.translate(17 * C, 0)

        for k in self.keys:
            self.draw_key(k, k in self.pressed_keys)

        if not nofingers:
            for p in self.palceR:
                p.draw(klawiatura.ctx)

            for p in self.palceL:
                p.draw(klawiatura.ctx)

        klawiatura.ctx.translate(-2 * C, -2 * C)


        if self.dvorak:
            klawiatura.ctx.translate(-17 * C, 0)

    def total_distance(self):
        d = []
        for p in self.palceR:
            d.append(p.distance)
        for p in self.palceL:
            d.append(p.distance)
        return sum(d)

    def stats(self):
        d = {}
        d['length'] = self.processed_text
        d['distance'] = self.total_distance()
        d['distPerChar'] =  float(self.total_distance()) / self.text_len
        d['leftHandPerc'] = self.leftHand * 100 / (self.leftHand + self.rightHand)
        d['rightHandPerc'] = self.rightHand * 100 / (self.leftHand + self.rightHand)
        d['homeRowPerc'] = self.home_row * 100 / self.processed_text
        d['combo'] = self.combo[:10]
        d['comboPerc'] = sum([n * i for n, i in enumerate(self.combo)]) * 100 / self.processed_text
        d['comboF'] = self.comboF[:10]
        d['comboPercF'] = float(sum([n * i for n, i in enumerate(self.comboF)]) * 100) / self.processed_text

        return d

    def heat_map(self, heat):
        maximum = max( [self.heat[key] for key in self.heat.keys()
                        if key not in ['space', 'backspace', 'enter'] ] )
        #relative = pl.sqrt(float(heat) / float(maximum))
        relative = float(min(heat, maximum)) / float(maximum)

        rgb = colorsys.hsv_to_rgb(0.6 - 0.6*relative, 0.2 * relative + 0.8, 1)

        #return (1, 1 - relative, 1 - relative)
        return rgb


    def draw_key(self, key, pressed = False):
        if key == 'space':
            coords = (4*C, 4*C, 6*C, 1*C)

        if key == 'backspace':
            coords = (13*C, 0*C, 2.4*C, 1*C)

        if key == 'alt':
            coords = (10*C, 4*C, 1*C, 1*C)

        if key == 'lshift':
            coords = (0*C, 3*C, 2.5*C, 1*C)

        if key == 'rshift':
            coords = (12.5*C, 3*C, 2.9*C, 1*C)

        if key == 'enter':
            coords = (12.9*C, 2*C, 2.5*C, 1*C)

        elif key[0] == 'A':
            coords = (eval(key[1:])*C, 0*C, 1*C, 1*C)

        elif key[0] == 'B':
            coords = ((eval(key[1:])+0.6)*C, 1*C, 1*C, 1*C)

        elif key[0] == 'C':
            coords = ((eval(key[1:])+0.9)*C, 2*C, 1*C, 1*C)

        elif key[0] == 'D':
            coords = ((eval(key[1:])+1.5)*C, 3*C, 1*C, 1*C)

        #if pressed:
        #    klawiatura.ctx.set_source_rgb(0.9, 0, 0)
        #    klawiatura.ctx.rectangle(*coords)
        #    klawiatura.ctx.fill()
        #    klawiatura.ctx.stroke()

        klawiatura.ctx.set_source_rgb( *self.heat_map(self.heat[key]) )
        klawiatura.ctx.rectangle(*coords)
        klawiatura.ctx.fill()
        klawiatura.ctx.stroke()

        klawiatura.ctx.set_source_rgb(0, 0, 0)
        klawiatura.ctx.rectangle(*coords)
        klawiatura.ctx.stroke()

    def read(self, text):
        self.text_len = len(text)
        self.buffer =  [self.map_char(c) for c in text]

    def read_now(self, text):
        self.read(text)
        while self.make_move() == 0:
            pass

    def make_move(self):
        if len(self.buffer) > 0:
            self.press( self.buffer[0] )
            return 0
        else:
            return 1

#title = 'costam.txt'
#title = 'gamma1.tex'
#title = 'klawiatury.py'
#title = 'game_classes.cpp'
title = 'alice.txt'
#title = 'rdz.txt'

f = codecs.open(title, encoding='utf-8')

#text = f.read()[:400]
text = f.read()[:300]

drawing = True
drawing_last = False

k = klawiatura(drawing = drawing)
k_dummy = klawiatura(drawing = False)
k_dummy
k_dummy.read_now(text)
k_stats = k_dummy.stats()
k.read( text )


k1 = klawiatura(dvorak = True, drawing = drawing)
k1_dummy = klawiatura(dvorak = True, drawing = False)
k1_dummy.read_now(text)
k1_stats = k1_dummy.stats()
k1.read( text )


stL = 12*C
stR = 24*C
stY = 8.5*C

def print2(x, y, string, al = 'l'):
    offsety = klawiatura.ctx.text_extents( string )[3] / 2
    if al == 'l':
        klawiatura.ctx.move_to(x, y + offsety)
    elif al == 'r':
        offset = klawiatura.ctx.text_extents( string )[2]
        klawiatura.ctx.move_to(x - offset, y + offsety)
    elif al == 'c':
        offset = klawiatura.ctx.text_extents( string )[2] / 2
        klawiatura.ctx.move_to(x - offset, y + offsety)
    klawiatura.ctx.show_text( string )
    klawiatura.ctx.stroke()

red1 = (1, 0.2, 0.2)
green1 = (0.2, 0.9, 0.2)

koniec = 0
while koniec == 0:
    koniec = k.make_move() or k1.make_move()

    if koniec != 0 and drawing_last:
        k.drawing = True
        k1.drawing = True
        klawiatura.setup_drawing()
        k.draw(nofingers = True)
        k1.draw(nofingers = True)

    if drawing or (koniec != 0 and drawing_last):
        klawiatura.ctx.set_font_size(1.5* C)
        klawiatura.ctx.set_source_rgb(*red1)
        print2(1*C, 10*C, 'QWERTY', 'l')
        klawiatura.ctx.set_source_rgb(*green1)
        print2(37*C, 10*C, 'Mod. Dvorak', 'r')

        klawiatura.ctx.set_font_size(1* C)
        klawiatura.ctx.set_source_rgb(0, 0, 0)
        print2((stR + stL) / 2, 0.8*C, title, 'c')

        klawiatura.ctx.set_font_size(0.4 * C)

        # całk dystans
        klawiatura.ctx.set_source_rgb(0, 0, 0)
        print2((stR + stL) / 2, stY - 0.4*C, 'Całkowyty dystans pokonany przez palce (1 - rozmiar klawisza)', 'c')

        klawiatura.ctx.set_source_rgb(*red1)
        print2(stL - 0.1*C, stY + 0.2*C, '%.0f' % k.stats()['distance'], 'r')
        klawiatura.ctx.set_source_rgb(*green1)
        print2(stR + 0.1*C, stY + 0.2*C, '%.0f' % k1.stats()['distance'], 'l')


        klawiatura.ctx.set_source_rgb(1, 0.8, 0.8)
        klawiatura.ctx.rectangle(stL, stY, stR-stL, 0.2*C)
        klawiatura.ctx.fill()
        klawiatura.ctx.stroke()
        klawiatura.ctx.set_source_rgb(*red1)
        klawiatura.ctx.rectangle(stL, stY, (stR-stL) * k.stats()['distance'] / k_stats['distance'], 0.2*C)
        klawiatura.ctx.fill()
        klawiatura.ctx.stroke()

        len2 = (stR-stL) * k1_stats['distance'] / k_stats['distance']
        klawiatura.ctx.set_source_rgb(0.8, 1, 0.8)
        klawiatura.ctx.rectangle(stL, stY + 0.2*C, len2, 0.2*C)
        klawiatura.ctx.fill()
        klawiatura.ctx.stroke()
        klawiatura.ctx.set_source_rgb(*green1)
        klawiatura.ctx.rectangle(stL, stY + 0.2*C, len2 * k1.stats()['distance'] / k1_stats['distance'], 0.2*C)
        klawiatura.ctx.fill()
        klawiatura.ctx.stroke()

        # home row
        klawiatura.ctx.set_source_rgb(0, 0, 0)
        print2((stR + stL) / 2, stY + 0.6*C, 'Udział uderzeń w środkowy rząd klawiszy', 'c')

        klawiatura.ctx.set_source_rgb(*red1)
        print2(stL - 0.1*C, stY + 1.1*C, '%.0f%%' % k.stats()['homeRowPerc'], 'r')
        klawiatura.ctx.set_source_rgb(*green1)
        print2(stR + 0.1*C, stY + 1.1*C, '%.0f%%' % k1.stats()['homeRowPerc'], 'l')

        klawiatura.ctx.set_source_rgb(1, 0.8, 0.8)
        klawiatura.ctx.rectangle(stL, stY + 0.9*C, stR-stL, 0.2*C)
        klawiatura.ctx.fill()
        klawiatura.ctx.stroke()
        klawiatura.ctx.set_source_rgb(*red1)
        klawiatura.ctx.rectangle(stL, stY + 0.9*C, (stR-stL) * k.stats()['homeRowPerc'] / 100, 0.2*C)
        klawiatura.ctx.fill()
        klawiatura.ctx.stroke()

        klawiatura.ctx.set_source_rgb(0.8, 1, 0.8)
        klawiatura.ctx.rectangle(stL, stY + 1.1*C, stR-stL, 0.2*C)
        klawiatura.ctx.fill()
        klawiatura.ctx.stroke()
        klawiatura.ctx.set_source_rgb(*green1)
        klawiatura.ctx.rectangle(stL, stY + 1.1*C, (stR-stL) * k1.stats()['homeRowPerc'] / 100, 0.2*C)
        klawiatura.ctx.fill()
        klawiatura.ctx.stroke()

        # balans
        klawiatura.ctx.set_source_rgb(0, 0, 0)
        print2((stR + stL) / 2, stY + 1.5*C, 'Balans lewa - prawa ręka', 'c')

        klawiatura.ctx.set_source_rgb(*red1)
        print2(stL - 0.1*C, stY + 2.0*C, '%.0f%% - %.0f%%' % (k.stats()['leftHandPerc'], k.stats()['rightHandPerc']), 'r')
        klawiatura.ctx.set_source_rgb(*green1)
        print2(stR + 0.1*C, stY + 2.0*C, '%.0f%% - %.0f%%' % (k1.stats()['leftHandPerc'], k1.stats()['rightHandPerc']), 'l')

        w = 0.5*C
        klawiatura.ctx.set_source_rgb(1, 0.8, 0.8)
        klawiatura.ctx.rectangle(stL, stY + 1.8*C, stR-stL, 0.2*C)
        klawiatura.ctx.fill()
        klawiatura.ctx.stroke()
        klawiatura.ctx.set_source_rgb(*red1)
        klawiatura.ctx.rectangle(stL + (stR - stL) * k.stats()['rightHandPerc'] / 100 - w/2, stY + 1.8*C, w, 0.2*C)
        klawiatura.ctx.fill()
        klawiatura.ctx.stroke()

        klawiatura.ctx.set_source_rgb(0.8, 1, 0.8)
        klawiatura.ctx.rectangle(stL, stY + 2.0*C, stR-stL, 0.2*C)
        klawiatura.ctx.fill()
        klawiatura.ctx.stroke()
        klawiatura.ctx.set_source_rgb(*green1)
        klawiatura.ctx.rectangle(stL + (stR - stL) * k1.stats()['rightHandPerc'] / 100 - w/2, stY + 2.0*C, w, 0.2*C)
        klawiatura.ctx.fill()
        klawiatura.ctx.stroke()


        # powtórzenia jedną ręką
        klawiatura.ctx.set_source_rgb(0, 0, 0)
        print2((stR + stL) / 2, stY + 2.4*C, 'Uderzenia jedną ręką w serii', 'c')

        klawiatura.ctx.set_source_rgb(*red1)
        print2(stL - 0.1*C, stY + 2.9*C, '%.0f%%' % k.stats()['comboPerc'], 'r')
        klawiatura.ctx.set_source_rgb(*green1)
        print2(stR + 0.1*C, stY + 2.9*C, '%.0f%%' % k1.stats()['comboPerc'], 'l')

        klawiatura.ctx.set_source_rgb(1, 0.8, 0.8)
        klawiatura.ctx.rectangle(stL, stY + 2.7*C, stR-stL, 0.2*C)
        klawiatura.ctx.fill()
        klawiatura.ctx.stroke()
        klawiatura.ctx.set_source_rgb(*red1)
        klawiatura.ctx.rectangle(stL, stY + 2.7*C, (stR-stL) * k.stats()['comboPerc'] / 100, 0.2*C)
        klawiatura.ctx.fill()
        klawiatura.ctx.stroke()

        klawiatura.ctx.set_source_rgb(0.8, 1, 0.8)
        klawiatura.ctx.rectangle(stL, stY + 2.9*C, stR-stL, 0.2*C)
        klawiatura.ctx.fill()
        klawiatura.ctx.stroke()
        klawiatura.ctx.set_source_rgb(*green1)
        klawiatura.ctx.rectangle(stL, stY + 2.9*C, (stR-stL) * k1.stats()['comboPerc'] / 100, 0.2*C)
        klawiatura.ctx.fill()
        klawiatura.ctx.stroke()

        # powtórzenia jednym palcem
        klawiatura.ctx.set_source_rgb(0, 0, 0)
        print2((stR + stL) / 2, stY + 3.3*C, 'Uderzenia jednym palcem w serii', 'c')

        klawiatura.ctx.set_source_rgb(*red1)
        print2(stL - 0.1*C, stY + 3.8*C, '%.1f%%' % k.stats()['comboPercF'], 'r')
        klawiatura.ctx.set_source_rgb(*green1)
        print2(stR + 0.1*C, stY + 3.8*C, '%.1f%%' % k1.stats()['comboPercF'], 'l')

        klawiatura.ctx.set_source_rgb(1, 0.8, 0.8)
        klawiatura.ctx.rectangle(stL, stY + 3.6*C, stR-stL, 0.2*C)
        klawiatura.ctx.fill()
        klawiatura.ctx.stroke()
        klawiatura.ctx.set_source_rgb(*red1)
        klawiatura.ctx.rectangle(stL, stY + 3.6*C, (stR-stL) * k.stats()['comboPercF'] / 100, 0.2*C)
        klawiatura.ctx.fill()
        klawiatura.ctx.stroke()

        klawiatura.ctx.set_source_rgb(0.8, 1, 0.8)
        klawiatura.ctx.rectangle(stL, stY + 3.8*C, stR-stL, 0.2*C)
        klawiatura.ctx.fill()
        klawiatura.ctx.stroke()
        klawiatura.ctx.set_source_rgb(*green1)
        klawiatura.ctx.rectangle(stL, stY + 3.8*C, (stR-stL) * k1.stats()['comboPercF'] / 100, 0.2*C)
        klawiatura.ctx.fill()
        klawiatura.ctx.stroke()

        #klawiatura.ctx.set_source_rgb(*red1)
        #print2((stL + stR) / 2 - 0.2*C, stY + 2.9*C,
        #       '1: %i   2: %i   3: %i   4: %i   5: %i' %
        #       (k.stats()['combo'][1], k.stats()['combo'][2], k.stats()['combo'][3], k.stats()['combo'][4], k.stats()['combo'][5]), 'r')
        #klawiatura.ctx.set_source_rgb(*green1)
        #print2((stL + stR) / 2 + 0.2*C, stY + 2.9*C,
        #       '1: %i   2: %i   3: %i   4: %i   5: %i' %
        #       (k1.stats()['combo'][1], k1.stats()['combo'][2], k1.stats()['combo'][3], k1.stats()['combo'][4], k1.stats()['combo'][5]), 'l')
    

        klawiatura.write_image()

for i,j in k.stats().items():
    print i,'\t', j
print ' '
for i,j in k1.stats().items():
    print i,'\t', j

f.close()
#k.draw()

if drawing:
    #system('animate -delay 15 -loop 0 anim*')
    system('convert -delay 15 -loop 1 anim* animacja_alice.gif')

if drawing_last:
    system('eog anim0000.png')
#system('convert -delay 5 anim* my_animation.gif')
#pl.show()
