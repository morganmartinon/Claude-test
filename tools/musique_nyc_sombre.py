#!/usr/bin/env python3
"""Instrumental original, hip-hop new-yorkais sombre (esprit années 90).

Usage : python3 tools/musique_nyc_sombre.py SORTIE.wav [BPM] [NB_MESURES]

Piano grave et dissonant (secondes mineures), basse lourde, batterie sèche et sale.
Même structure que musique_boom_bap.py : breakdown sur le dernier temps de la mesure 4,
drop à la mesure 5 (carillon aigu + nappe sombre). Tout est synthétisé, aucun sample.
"""
import sys
import numpy as np
from scipy.io import wavfile
from scipy.signal import lfilter

out = sys.argv[1] if len(sys.argv) > 1 else "nyc_sombre.wav"
BPM = float(sys.argv[2]) if len(sys.argv) > 2 else 100.0
BARS = int(sys.argv[3]) if len(sys.argv) > 3 else 7

sr = 44100
beat = 60.0 / BPM
step = beat / 4
bar_len = 4 * beat
total = BARS * bar_len
N = int(sr * (total + 0.4))
rng = np.random.default_rng(11)
SWING = 0.02
DROP_BAR = 4
BREAK_START = DROP_BAR * bar_len - beat

DRUM_L, DRUM_R = np.zeros(N), np.zeros(N)
BASS = np.zeros(N)
PIANO = np.zeros(N)
PIANO_R = np.zeros(N)
PAD = np.zeros(N)
FX_L, FX_R = np.zeros(N), np.zeros(N)


def put(buf, t0, w, g=1.0):
    i = int(t0 * sr)
    if i >= N or i < 0:
        return
    n = min(len(w), N - i)
    buf[i:i + n] += w[:n] * g


def drum(t0, w, g=1.0, pan=0.0):
    put(DRUM_L, t0, w, g * (1 - max(0, pan)))
    put(DRUM_R, t0, w, g * (1 + min(0, pan)))


def mtof(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def kick():
    t = np.arange(int(0.4 * sr)) / sr
    f = 42 + 130 * np.exp(-t * 38)
    ph = 2 * np.pi * np.cumsum(f) / sr
    y = np.sin(ph) * np.exp(-t * 8.5) + 0.2 * np.sin(2 * ph) * np.exp(-t * 25)
    k = int(0.002 * sr)
    y[:k] *= np.linspace(0, 1, k)
    return np.tanh(2.0 * y)


def snare(v=1.0):
    t = np.arange(int(0.35 * sr)) / sr
    n = lfilter([1, -0.85], [1], rng.standard_normal(len(t)))
    y = n * np.exp(-t * 16) * 0.8 + np.sin(2 * np.pi * 200 * t) * np.exp(-t * 32) * 0.55
    # petite réverbération de salle
    for d, g in ((0.017, 0.35), (0.031, 0.25), (0.047, 0.15)):
        k = int(d * sr)
        y[k:] += g * y[:-k] * 0.6
    return np.tanh(1.5 * y) * v


def hat(v=1.0):
    t = np.arange(int(0.05 * sr)) / sr
    n = rng.standard_normal(len(t))
    n = lfilter([1, -1], [1], n)
    n = lfilter([1, -1], [1], n) * 0.5
    return n * np.exp(-t * 100) * 0.3 * v


def crash(d=1.4, v=1.0):
    t = np.arange(int(d * sr)) / sr
    n = lfilter([1, -0.95], [1], rng.standard_normal(len(t)))
    return n * np.exp(-t * 3.0) * 0.35 * v


def riser(d):
    t = np.arange(int(d * sr)) / sr
    n = lfilter([1, -0.9], [1], rng.standard_normal(len(t)))
    return n * (t / d) ** 2 * 0.45


def bass_note(f, d):
    t = np.arange(int(d * sr)) / sr
    fm = f * (1 + 0.35 * np.exp(-t * 45))
    ph = 2 * np.pi * np.cumsum(fm) / sr
    y = np.sin(ph) + 0.2 * np.sin(2 * ph)
    env = np.minimum(1, t / 0.004) * np.exp(-t * 1.1) * np.clip((d - t) / 0.04, 0, 1)
    return np.tanh(1.6 * y * env) * 0.75


def piano(midi, d):
    f = mtof(midi)
    t = np.arange(int(d * sr)) / sr
    y = np.zeros_like(t)
    for h, a, dec in ((1, 1.0, 1.8), (2, 0.5, 2.6), (3, 0.3, 4.0), (4, 0.2, 5.5), (5, 0.12, 7.5), (6, 0.08, 9.0)):
        fh = f * h * np.sqrt(1 + 0.0004 * h * h)
        for det in (1.0, 1.0025):
            y += a * np.sin(2 * np.pi * fh * det * t + rng.uniform(0, 6.28)) * np.exp(-t * dec)
    y *= np.minimum(1, t / 0.002) * np.clip((d - t) / 0.08, 0, 1)
    hm = int(0.012 * sr)
    y[:hm] += 0.15 * rng.standard_normal(hm) * np.exp(-np.arange(hm) / (0.003 * sr))
    return y * 0.09


def bell(midi, d=0.9):
    f = mtof(midi)
    t = np.arange(int(d * sr)) / sr
    y = np.sin(2 * np.pi * f * t) + 0.4 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t * 6)
    return y * np.exp(-t * 4.5) * np.minimum(1, t / 0.002) * 0.12


def pad(midis, d):
    t = np.arange(int(d * sr)) / sr
    y = np.zeros_like(t)
    for m in midis:
        f = mtof(m)
        for det in (0.997, 1.003):
            for h in range(1, 6):
                y += np.sin(2 * np.pi * f * det * h * t + rng.uniform(0, 6.28)) / h
    y *= np.minimum(1, t / 0.4) * np.clip((d - t) / 0.4, 0, 1) * (1 + 0.2 * np.sin(2 * np.pi * 0.4 * t))
    return lfilter([0.12], [1, -0.88], y) * 0.05


def when(b, s):
    return b * bar_len + s * step + (SWING if s % 2 == 1 else 0)


def muted(t):
    return BREAK_START <= t < DROP_BAR * bar_len


K, S = kick(), snare()
ROOTS = ([29, 29, 30, 29, 29, 29, 30, 29] * 4)[:max(BARS, 8)]   # F1 F1 Gb1 F1 ... (répété)
BAR_F = [(0, [64, 65, 72], 6), (7, [61, 68], 3), (10, [65, 72], 4)]      # grappes de secondes mineures
BAR_G = [(0, [65, 66, 73], 6), (7, [62, 69], 3), (10, [66, 73], 4)]
BELL_CYCLE = [77, 76, 72, 76]

for b in range(BARS):
    kicks = [0, 7, 10] if b % 2 == 0 else [0, 5, 10, 13]
    for s in kicks:
        if not muted(when(b, s)):
            drum(when(b, s), K, 1.0)
    for s in (4, 12):
        if not muted(when(b, s)):
            drum(when(b, s), S, 0.85)
    for s in (2, 6, 10, 14):
        if not muted(when(b, s)):
            drum(when(b, s), hat(0.9 if s % 4 == 2 else 0.6), 0.8, pan=0.2)
    if b >= 1:
        for s, ln, up in ((0, 7, 0), (10, 3, 0), (14, 2, 12 if b % 2 else 0)):
            if not muted(when(b, s)):
                put(BASS, when(b, s), bass_note(mtof(ROOTS[b] + up), ln * step), 1.0)
    pattern = BAR_G if ROOTS[b] == 30 else BAR_F
    for s, notes, ln in pattern:
        if muted(when(b, s)):
            continue
        for m in notes:
            w = piano(m, ln * step)
            put(PIANO, when(b, s), w, 1.0)
            put(PIANO_R, when(b, s) + 0.007, w, 1.0)
    if b >= DROP_BAR:
        for i, s in enumerate(range(0, 16, 2)):
            w = bell(BELL_CYCLE[i % 4])
            t0 = when(b, s)
            put(FX_L, t0, w, 0.8)
            put(FX_R, t0 + 0.012, w, 0.6)
        put(PAD, b * bar_len, pad([53, 54, 60], bar_len), 1.0)

# impacts, montée et roulement de caisse claire avant le drop
drum(0.0, crash(0.6, 0.6), 0.8)
drum(BREAK_START, riser(beat), 0.9)
for i, v in enumerate((0.5, 0.65, 0.8, 1.0)):
    drum(BREAK_START + beat * 0.5 + i * beat / 8, S, 0.7 * v)
drum(DROP_BAR * bar_len, crash(1.6, 1.0), 0.9)
drum(DROP_BAR * bar_len, K, 1.0)

# piano poussiéreux : filtre passe-bas + écho sombre
for buf in (PIANO, PIANO_R):
    buf[:] = lfilter([0.35], [1, -0.65], buf)
    delayed = np.roll(buf, int(0.45 * sr)) * 0.35
    buf += lfilter([0.5], [1, -0.5], delayed)
drums_l, drums_r = np.tanh(1.4 * DRUM_L), np.tanh(1.4 * DRUM_R)

# craquement de vinyle et souffle de bande
imp = (rng.random(N) < 0.0005) * rng.uniform(-1, 1, N)
vin = lfilter([1], [1, -0.6], imp) * 0.18 + rng.standard_normal(N) * 0.003

L = drums_l + BASS + PIANO + PAD + FX_L + vin
R = drums_r + BASS + PIANO_R + PAD + FX_R + np.roll(vin, 41)
mix = np.tanh(1.1 * np.stack([L, R], axis=1))
mix = mix / np.max(np.abs(mix)) * 0.89
mix[:int(0.002 * sr)] *= np.linspace(0, 1, int(0.002 * sr))[:, None]
wavfile.write(out, sr, (mix * 32767).astype(np.int16))
print(f"{out} : {len(mix) / sr:.2f} s, {BPM:g} BPM, {BARS} mesures, drop à {DROP_BAR * bar_len:.2f} s")
