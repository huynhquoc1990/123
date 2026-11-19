"""Synthesize a royalty-free corporate/tech background track that follows the video's scene timeline.
Usage: python3 music.py out.wav [duration_seconds]
"""
import sys, wave
import numpy as np

SR = 44100
OUT = sys.argv[1] if len(sys.argv) > 1 else 'music.wav'
DUR = float(sys.argv[2]) if len(sys.argv) > 2 else 82.0
# scene start times (from timing.js written by build_voice.py, else defaults)
SC = {'s1': 0, 's2': 5.8, 's3': 11.9, 's4': 34.9, 's5': 40.9, 's6': 54.9, 's7': 67.9, 's8': 74.9}
if len(sys.argv) > 3:
    import json, re
    tm = json.loads(re.search(r'=\s*(\{.*\})', open(sys.argv[3]).read(), re.S).group(1))
    SC = {k: v[0] for k, v in tm['scenes'].items()}
    DUR = tm['duration']
BPM = 100
BEAT = 60 / BPM
BAR = 4 * BEAT
N = int(SR * DUR)
L = np.zeros(N); R = np.zeros(N)
rng = np.random.default_rng(7)

def mf(m): return 440.0 * 2 ** ((m - 69) / 12)

def put(sig, t0, gain=1.0, pan=0.0):
    i0 = int(t0 * SR)
    if i0 >= N: return
    sig = sig[: N - i0]
    l = np.cos((pan + 1) * np.pi / 4); r = np.sin((pan + 1) * np.pi / 4)
    L[i0:i0 + len(sig)] += sig * gain * l
    R[i0:i0 + len(sig)] += sig * gain * r

def env(n, a, r, sus=1.0):
    e = np.ones(n) * sus
    na, nr = int(a * SR), int(r * SR)
    e[:na] = np.linspace(0, sus, na)
    if nr: e[-nr:] *= np.linspace(1, 0, nr)
    return e

def pad_voice(f, dur):
    n = int(dur * SR); t = np.arange(n) / SR
    s = np.zeros(n)
    for det in (-0.12, 0.0, 0.11):
        ff = f * 2 ** (det / 12)
        for k, w in ((1, 1), (2, .45), (3, .22), (4, .12), (5, .06)):
            s += w * np.sin(2 * np.pi * ff * k * t + det * 10)
    return s / 6 * env(n, .6, .9)

def pluck(f, dur=.45):
    n = int(dur * SR); t = np.arange(n) / SR
    s = np.sin(2 * np.pi * f * t) + .35 * np.sin(2 * np.pi * 2 * f * t) + .12 * np.sin(2 * np.pi * 3 * f * t)
    return s * np.exp(-t * 9) * env(n, .003, .05)

def kick():
    n = int(.35 * SR); t = np.arange(n) / SR
    f = 48 + 90 * np.exp(-t * 28)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9)

def hat():
    n = int(.06 * SR); x = rng.standard_normal(n); x = np.diff(x, prepend=0)
    return x * np.exp(-np.arange(n) / SR * 70) * .5

def clap():
    n = int(.18 * SR); x = rng.standard_normal(n)
    x = np.convolve(x, np.ones(6) / 6, 'same') - np.convolve(x, np.ones(40) / 40, 'same')
    return x * np.exp(-np.arange(n) / SR * 22)

def whoosh(dur=.9):
    n = int(dur * SR); x = rng.standard_normal(n)
    x = np.convolve(x, np.ones(12) / 12, 'same')
    e = np.sin(np.pi * np.linspace(0, 1, n)) ** 2
    return x * e

def boom():
    n = int(1.6 * SR); t = np.arange(n) / SR
    return (np.sin(2 * np.pi * (40 + 30 * np.exp(-t * 6)) * t) * np.exp(-t * 2.5) +
            .3 * np.convolve(rng.standard_normal(n), np.ones(30) / 30, 'same') * np.exp(-t * 8))

# Am - F - C - G
CH = [[57, 60, 64], [53, 57, 60], [48, 52, 55, 60], [50, 55, 59]]
BASS = [45, 41, 48, 43]

def section_level(t):
    """intensity 0..1 by video section"""
    if t < SC['s2']: return .35
    if t < SC['s3']: return .7
    if t < SC['s7']: return 1.0
    if t < SC['s8']: return .55
    return .9

nbars = int(DUR / BAR) + 1
for b in range(nbars):
    t0 = b * BAR
    if t0 >= DUR: break
    ci = b % 4
    lvl = section_level(t0)
    for m in CH[ci]:
        put(pad_voice(mf(m), BAR + 1.0), t0, .16, pan=(m % 3 - 1) * .4)
    # bass
    if t0 >= SC['s2'] - .1:
        for k in range(8):
            tb = t0 + k * BEAT / 2
            n = int(BEAT / 2 * SR * .9); tt = np.arange(n) / SR
            s = np.sin(2 * np.pi * mf(BASS[ci]) * tt) + .3 * np.sin(2 * np.pi * mf(BASS[ci]) * 2 * tt)
            put(s * env(n, .005, .08) * (1 if k % 2 == 0 else .6), tb, .22 * lvl)
    # arp
    if t0 >= SC['s3'] - .4:
        notes = [n + 12 for n in CH[ci]]
        seq = [notes[0], notes[1], notes[2], notes[1] + 12 if len(notes) < 4 else notes[3], notes[2], notes[1], notes[0] + 12, notes[1]]
        for k, m in enumerate(seq):
            put(pluck(mf(m)), t0 + k * BEAT / 2, .11 * lvl, pan=-.5 if k % 2 else .5)
    # drums
    for k in range(4):
        tb = t0 + k * BEAT
        if SC['s2'] <= tb < SC['s7'] or SC['s8'] <= tb < DUR - 2.5:
            put(kick(), tb, .55 * (lvl if tb < SC['s3'] else 1))
        if SC['s3'] <= tb < SC['s7'] or SC['s8'] <= tb < DUR - 2.5:
            put(hat(), tb + BEAT / 2, .25, pan=.3)
            put(hat(), tb + BEAT / 4 * 3, .1, pan=-.3)
            if k in (1, 3) and tb >= SC['s4']: put(clap(), tb, .22)

# riser into the reveal at 6s
n = int(2.5 * SR); t = np.arange(n) / SR
riser = np.sin(2 * np.pi * (200 + 600 * (t / 2.5) ** 2) * t) * (t / 2.5) ** 2 * .3 + np.convolve(rng.standard_normal(n), np.ones(8) / 8, 'same') * (t / 2.5) ** 3 * .5
put(riser, SC['s2'] - 2.4, .35)
put(boom(), SC['s2'] + .1, .7)
for ts in [SC[k] for k in ('s3', 's4', 's5', 's6', 's7', 's8')]:
    put(whoosh(), ts - .45, .35, pan=0)
put(boom(), SC['s8'], .5)

mix = np.stack([L, R], 1)
mix = np.tanh(mix * 1.3)
fade_in = np.clip(np.arange(N) / (SR * 1.0), 0, 1)
fade_out = np.clip((DUR - np.arange(N) / SR) / 3.0, 0, 1)
mix *= (fade_in * fade_out)[:, None]
mix /= np.max(np.abs(mix)) + 1e-9
mix *= 10 ** (-1.5 / 20)
pcm = (mix * 32767).astype('<i2')
with wave.open(OUT, 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print('music ->', OUT)
