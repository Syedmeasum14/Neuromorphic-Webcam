# Neuromorphic Webcam — See what an event camera Sees and how it works

```bash
python3 -m http.server 8000
```

Then open <http://localhost:8000>. Serve it rather than opening the file
directly — browsers only grant camera access to a real origin, and `file://`
is not one. No install, no build step, no dependencies.

A normal camera samples every pixel on a fixed clock and ships the whole frame,
whether or not anything happened. An **event camera** gives each pixel its own
trigger: report only when the light it sees changes, and stay silent otherwise.

This page implements that pixel model and runs it live on a demo scene, your
webcam, or any video file you drop in. Left viewport: the frame. Right
viewport: everything the sensor would actually have transmitted.

On the built-in scene at 240 × 180, roughly **1.6% of pixels fire per frame**,
and the event stream costs about **24× less data** than the equivalent
greyscale video stream. Point it at a still wall and that ratio runs away.

The page also draws **one pixel deciding when to fire** — its brightness over
three seconds, the stepped reference it remembers, and the events that come
out. It runs the same threshold rule as the simulation and redraws whenever
you move the contrast slider, so the control and the concept stay tied
together.

---

## The entire sensor, in four lines

Each pixel keeps a private memory of the log brightness it last reported. It
fires the moment the live value drifts past a threshold, updates that memory,
and forgets everything else. No clock, no frame, no coordination with its
neighbours.

```
L(x, y, t)  =  log( ε + I(x, y, t) )

if  L − L_ref  ≥  +C     emit ON  event,   L_ref ← L_ref + C
if  L − L_ref  ≤  −C     emit OFF event,   L_ref ← L_ref − C

each pixel then stays silent for a refractory period Δt_r
```

Implemented in [`src/app.html`](src/app.html) — see `integrate()`.

**Why the logarithm.** A fixed threshold on log intensity is a fixed threshold
on *relative* change, so a 20% change triggers identically in bright sun and in
near darkness. That one choice is where the ~120 dB dynamic range comes from,
against roughly 60 dB for a conventional sensor.

**Why `C` is the interesting dial.** Below ~0.1 the sensor picks up noise and
faint shading; above ~0.4 only hard edges in fast motion survive. Real devices
sit around 0.15–0.25, and it is not a software setting — it is fixed by a bias
current in the pixel circuit.

**Why the refractory period exists.** A pixel that has just fired needs time to
reset. Without that limit, one high-contrast edge sweeping the array saturates
the readout bus and events get dropped. The parameter that looks like a detail
is what keeps the sensor honest under fast motion.

---

## Reading the data-rate numbers

| Quantity | How it is computed |
|---|---|
| Frame stream | `width × height × 1 byte × fps` — 8-bit greyscale, uncompressed |
| Event stream | `events/s × 4 bytes` — 32-bit AER packet carrying x, y, timestamp, polarity |
| Data avoided | the ratio of the two |

Both are estimates of **transmitted payload only**: no compression, no protocol
overhead, no sensor readout circuitry. Frame rate is measured live, so the
comparison always uses the same rate for both sides.

The reduction is not a fixed property — it is a property of the scene. Point it
at a static wall and it goes to infinity. Point it at a fast, high-contrast,
full-field texture and the event stream can *exceed* the frame stream. Both
outcomes are real, and both are reachable with the sliders.

---

## What this is not

This page derives events from video frames, so it inherits your webcam's frame
rate. That hides the property that matters most in practice: a real event camera
resolves timing to **microseconds**, roughly ten thousand times finer than the
33 ms grid these events are quantised onto. The sparsity here is real. The
latency is not.

Simplified against real silicon:

- no per-pixel threshold mismatch (real arrays vary by 2–4%)
- no shot noise and no leak events
- no bandwidth-limited readout or arbiter contention
- no temporal interpolation between frames — the [v2e](https://arxiv.org/abs/2006.07722) approach, which this is a stripped-down version of, does model this

---

## Repo layout

```
src/app.html     the whole thing — model, rendering, UI, ~600 lines, zero dependencies
scripts/build.py wraps src/app.html into a standalone index.html
index.html       generated; what GitHub Pages serves
```

Rebuild after editing the source:

```bash
python3 scripts/build.py
```

---

## References

- **Lichtsteiner, Posch & Delbrück (2008).** [A 128×128 120 dB 15 µs Latency Asynchronous Temporal Contrast Vision Sensor](https://ieeexplore.ieee.org/document/4444573). *IEEE JSSC* — the original DVS.
- **Gallego et al. (2020).** [Event-based Vision: A Survey](https://arxiv.org/abs/1904.08405). *IEEE TPAMI* — the field's reference text.
- **Hu, Liu & Delbrück (2021).** [v2e: From Video Frames to Realistic DVS Events](https://arxiv.org/abs/2006.07722). *CVPRW* — realistic frame-to-event conversion.

Companion project: [event-snn-detection](../event-snn-detection) — spiking
networks trained on real event-camera data, with measured accuracy/energy
trade-offs.
