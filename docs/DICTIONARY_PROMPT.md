# Dictionary Generation Prompt — 3D Word-Based Address Protocol

Hand this file to a capable language-model agent. Its job is to produce the real
27,000-word dictionary that replaces the placeholder list in `dictionary.py`.

---

## Your task

Produce a list of **exactly 27,000 unique English-readable words** to be used as the
vocabulary for a global 3D addressing system. Each word maps to one integer index
(0–26,999) purely by its line number, so the *order* of the list does not matter for
correctness — only the membership and quality of the set matter.

The words will be spoken aloud, typed on phones, read over radio/phone, and transcribed
by speech-to-text. Confusability between any two words is the enemy.

---

## Hard requirements (every word must satisfy all)

1. **Charset:** lowercase `a`–`z` only. No spaces, hyphens, apostrophes, digits, or accents.
2. **Length:** 3 to 7 letters. Favor 3–6. If needed warn me but can do more letters.
3. **Pronounceable** by a general international audience; simple, common syllable shapes.
4. **One unambiguous spelling.** Exclude words with common alternate spellings
   (e.g. color/colour, gray/grey, -ize/-ise). Pick words that are spelled one way.
5. **Concrete and ordinary.** Prefer everyday concrete nouns: animals, food, objects,
   materials, nature, tools, colors. These are easiest to recall and least ambiguous.
6. **Non-offensive and culturally neutral.** No profanity, slurs, sexual terms, violent
   terms, religious or political loaded words, or anything that is offensive in a major
   language. No brand names, trademarks, or proper nouns.
7. **No emotionally heavy or alarming words** (no death/disease/disaster vocabulary) —
   addresses appear in neutral, everyday contexts.

## Separation requirements (the set as a whole)

8. **No duplicates.**
9. **No homophones or near-homophones** within the set (e.g. not both `see` and `sea`,
   not both `flour` and `flower`, not both `to`, `too`, `two`).
10. **High edit-distance separation.** Avoid pairs that differ by a single letter or a
    single sound where confusion is likely (e.g. avoid having both `cat` and `cot` and
    `cut`; avoid `pin`/`pen`). Aim for most pairs to differ in 2+ letters.
11. **Avoid words that sound like letters or numbers** (`you`/U, `are`/R, `for`/4, `ate`/8).
12. **Avoid easily-confused minimal pairs** across `b/p`, `d/t`, `m/n`, `f/s/th`, `l/r`,
    and short vowels, which are the sounds most often lost over phone/radio.

---

## Output format

- Plain text. **One word per line. Exactly 27,000 lines. Nothing else** — no numbering,
  no commentary, no blank lines, no markdown.
- Save as `words.txt`. `dictionary.py` loads it automatically when present. dont worry about other files.

If you must generate in batches (recommended, ~1,000–2,000 at a time), keep a running
set to guarantee global uniqueness and separation, then concatenate. Do a final
deduplication and separation pass over the whole list before output.

---

## Self-check before returning (the list must pass all)

- Line count is exactly 27,000.
- Every line matches `^[a-z]{3,7}$`.
- Zero duplicates.
- No two words are homophones.
- Spot-check: no offensive terms, brand names, or alternate-spelling words.
- Few or no single-edit-distance pairs (the smaller this count, the better the dictionary).

A companion script, `validate_wordlist.py`, checks the mechanical rules (count, charset,
length, duplicates, and counts of risky single-edit pairs). Run your output through it and
iterate until it passes cleanly. The human-judgment rules (offensiveness, homophones,
cultural neutrality) are your responsibility — the script cannot fully verify them.

---

## Notes / rationale (for context, not output)

- 27,000 = 30³, matching the protocol's subdivision factor; the level-1 grid uses 25,460
  of these and leaves 1,540 unclaimed, so a list of exactly 27,000 fills the dictionary.
- Word indices are assigned by line order and are otherwise arbitrary. You do **not** need
  to sort or group the words.
- Aim for words a 10-year-old in any English-speaking country would recognize. When in
  doubt, choose the more common, more concrete, more phonetically distinct option.
- if you are out of common words use ones that sound as they look like. 