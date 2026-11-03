#!/usr/bin/env python3
"""Génère un instrumental boom-bap original (style hip-hop US années 90).

Usage : python3 tools/musique_boom_bap.py SORTIE.wav [BPM] [NB_MESURES]

Structure : intro (mesure 1 sans basse), montée, breakdown sur le dernier temps de la
mesure 4, drop à la mesure 5 avec mélodie. Tout est synthétisé (aucun sample protégé).
"""
import sys
import numpy as np
from scipy.io import wavfile
from scipy.signal import lfilter

out = sys.argv[1] if len(sys.argv) > 1 else "boom_bap.wav"
BPM = float(sys.argv[2]) if len(sys.argv) > 2 else 100.0
BARS = int(sys.argv[3]) if len(sys.argv) > 3 else 7

sr = 44100
beat = 60.0 / BPM
step = beat / 4
bar_len = 4 * beat
total = BARS * bar_len
N = int(sr * (total + 0.4))
rng = np.random.default_rng(7)
L = np.zeros(N)
R = np.zeros(N)
SWING = 0.018
DROP_BAR = 4                      # le drop arrive à la mesure 5 (index 4)
BREAK_START = DROP_BAR * bar_len - beat   # dernier temps avant le drop


def put(buf, t0, w, g=1.0):
    i = int(t0 * sr)
    if i >= N or i < 0:
        return
    n = min(len(w), N - i)
    buf[i:i + n] += w[:n] * g


def both(t0, w, g=1.0, pan=0.0):
    put(L, t0, w, g * (1 - max(0, pan)))
    put(R, t0, w, g * (1 + min(0, pan)))


def kick():
    t = np.arange(int(0.45 * sr)) / sr
    f = 48 + 120 * np.exp(-t * 30)
    ph = 2 * np.pi * np.cumsum(f) / sr
    y = np.sin(ph) * np.exp(-t * 7.5) + 0.25 * np.sin(2 * ph) * np.exp(-t * 20)
    k = int(0.003 * sr)
    y[:k] *= np.linspace(0, 1, k)
    return np.tanh(1.6 * y)


def snare(v=1.0):
    t = np.arange(int(0.3 * sr)) / sr
    n = lfilter([1, -0.9], [1], rng.standard_normal(len(t)))
    y = n * np.exp(-t * 18) * 0.7 + np.sin(2 * np.pi * 185 * t) * np.exp(-t * 28) * 0.6
    m = int(0.02 * sr)
    for d in (0, 0.011, 0.022):
        k = int(d * sr)
        y[k:k + m] += 0.3 * n[:m]
    return np.tanh(1.3 * y) * v


def hat(open_=False, v=1.0):
    d = 0.35 if open_ else 0.06
    t = np.arange(int(d * sr)) / sr
    n = rng.standard_normal(len(t))
    n = lfilter([1, -1], [1], n)
    n = lfilter([1, -1], [1], n) * 0.5
    return n * np.exp(-t * (14 if open_ else 90)) * 0.35 * v


def crash(d=1.3, v=1.0):
    t = np.arange(int(d * sr)) / sr
    n = lfilter([1, -0.95], [1], rng.standard_normal(len(t)))
    return n * np.exp(-t * 3.2) * 0.35 * v


def riser(d):
    t = np.arange(int(d * sr)) / sr
    n = lfilter([1, -0.9], [1], rng.standard_normal(len(t)))
    return n * (t / d) ** 2 * 0.45


def mtof(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def bass_note(f, d):
    t = np.arange(int(d * sr)) / sr
    y = np.sin(2 * np.pi * f * t) + 0.3 * np.sin(4 * np.pi * f * t)
    env = np.minimum(1, t / 0.006) * np.exp(-t * 1.6)
    rel = np.clip((d - t) / 0.03, 0, 1)
    return np.tanh(1.4 * y * env * rel) * 0.7


def keys(midis, d):
    t = np.arange(int(d * sr)) / sr
    y = np.zeros_like(t)
    for m in midis:
        f = mtof(m)
        for det in (1.0, 1.004):
            for h, a in ((1, 1.0), (2, 0.35), (3, 0.12), (4, 0.05)):
                y += a * np.sin(2 * np.pi * f * det * h * t + rng.uniform(0, 6.28)) * np.exp(-t * (3 + 1.5 * h))
    y *= (1 + 0.15 * np.sin(2 * np.pi * 5 * t)) * np.minimum(1, t / 0.004) * np.clip((d - t) / 0.05, 0, 1)
    return y * 0.05


def pluck(f, d=0.5):
    t = np.arange(int(d * sr)) / sr
    y = (np.sin(2 * np.pi * f * t) + 0.5 * np.sin(4 * np.pi * f * t) * np.exp(-t * 10)
         + 0.25 * np.sin(6 * np.pi * f * t) * np.exp(-t * 14))
    return y * np.exp(-t * 7) * np.minimum(1, t / 0.003) * 0.25


def when(b, s):
    return b * bar_len + s * step + (SWING if s % 2 == 1 else 0)


def muted(t):
    return BREAK_START <= t < DROP_BAR * bar_len


K, S = kick(), snare()
ROOTS = [33, 33, 29, 31, 33, 33, 29, 31, 33, 33, 29, 31]            # A1 A1 F1 G1 ...
CHORDS = [[57, 60, 64, 67], [57, 60, 64, 67], [53, 57, 60, 64], [55, 59, 62, 65]] * 3
HOOK_A = [(0, 69), (3, 72), (6, 76), (8, 74), (10, 72), (14, 69)]
HOOK_B = [(0, 72), (3, 76), (6, 79), (8, 76), (10, 74), (12, 72)]

for b in range(BARS):
    kicks = [0, 7, 10] if b % 2 == 0 else [0, 6, 7, 10]
    for s in kicks:
        if not muted(when(b, s)):
            both(when(b, s), K, 0.95)
    for s in (4, 12):
        if not muted(when(b, s)):
            both(when(b, s), S, 0.8)
    if b % 2 == 1 and not muted(when(b, 15)):
        both(when(b, 15), S, 0.22)
    for s in range(0, 16, 2):
        if muted(when(b, s)):
            continue
        v = [1.0, 0.55, 0.75, 0.55][(s // 2) % 4]
        both(when(b, s), hat(False, v), 0.8, pan=0.25)
    if b >= DROP_BAR:
        for s in range(1, 16, 2):
            both(when(b, s), hat(False, 0.35), 0.7, pan=-0.25)
    if b % 2 == 1 and not muted(when(b, 14)):
        both(when(b, 14), hat(True, 0.8), 0.7, pan=-0.2)
    # basse (absente à la première mesure)
    if b >= 1:
        for s, ln, up in ((0, 6, 0), (10, 3, 0), (14, 2, 12 if b % 2 else 0)):
            if not muted(when(b, s)):
                both(when(b, s), bass_note(mtof(ROOTS[b] + up), ln * step), 0.9)
    # accords poussiéreux
    for s, ln in ((0, 5), (6, 2), (10, 4)):
        if muted(when(b, s)):
            continue
        w = keys(CHORDS[b], ln * step)
        put(L, when(b, s), w, 1.0)
        put(R, when(b, s) + 0.008, w, 1.0)
    # mélodie du drop
    if b >= DROP_BAR:
        for s, m in (HOOK_A if b % 2 == 0 else HOOK_B):
            w = pluck(mtof(m))
            t0 = when(b, s)
            both(t0, w, 0.9, pan=0.1)
            both(t0 + 0.3, w, 0.3, pan=-0.5)
            both(t0 + 0.6, w, 0.13, pan=0.5)

# impacts, montée et roulement de caisse claire avant le drop
both(0.0, crash(0.6, 0.6), 0.8)
both(BREAK_START, riser(beat), 0.9)
for i, v in enumerate((0.5, 0.65, 0.8, 1.0)):
    both(BREAK_START + beat * 0.5 + i * beat / 8, S, 0.7 * v)
both(DROP_BAR * bar_len, crash(1.5, 1.0), 0.9)
both(DROP_BAR * bar_len, K, 1.0)

# craquement de vinyle
imp = (rng.random(N) < 0.0004) * rng.uniform(-1, 1, N)
vin = lfilter([1], [1, -0.6], imp) * 0.15 + rng.standard_normal(N) * 0.002
L += vin
R += np.roll(vin, 37)

mix = np.stack([L, R], axis=1)
mix = np.tanh(1.1 * mix)
mix = mix / np.max(np.abs(mix)) * 0.89
mix[:int(0.002 * sr)] *= np.linspace(0, 1, int(0.002 * sr))[:, None]
wavfile.write(out, sr, (mix * 32767).astype(np.int16))
print(f"{out} : {len(mix) / sr:.2f} s, {BPM:g} BPM, {BARS} mesures, drop à {DROP_BAR * bar_len:.2f} s")
