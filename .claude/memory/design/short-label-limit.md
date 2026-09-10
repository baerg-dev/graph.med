---
name: short-label-limit
description: A `short_label` is at most 60 characters, enforced by the schema; the target is 55, and a concept gets one only when its label exceeds about 45.
metadata:
  type: project
---

`short_label` has `maxLength: 60` in the schema (`$defs.short_text`); the
working target is 55 characters. A concept gets a short label only when its
full label is too long for an edge answer or an aim tag, about 45 characters.
Decided 2026-09-10 in chunk `short-labels-a` of pass 2.

**Why:** The physician's feedback asked for 40 to 55 characters, to be
calibrated on the longest statements. A box on the view page is 240 px wide
with 210 px of text at 12 px, about 32 characters a line, and two lines is what
a box should hold; 60 is two full lines, and the one statement that needed 56
("Keine mechanische Darmvorbereitung (oberer GI, Pankreas)") could not be
shortened without dropping the feature that tells it from its siblings. A hard
limit in the schema was chosen over a soft target so that a label that no
longer fits fails validation instead of overflowing a box.

**How to apply:** Write short labels under 55 where possible, never over 60;
keep the distinguishing feature (the procedure, the organ) when siblings share a
question; keep the direction word ("Keine …", "… erwägbar"). Leave concepts
with short labels alone. Related: [[document-structure-is-provenance]].
