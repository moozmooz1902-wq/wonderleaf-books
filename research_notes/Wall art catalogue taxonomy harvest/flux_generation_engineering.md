# FLUX.1 schnell print-quality generation engineering, and combinatorial taxonomy design

> **Source-quality warning for the report writer.** This topic is badly served by
> primary sources. Black Forest Labs publishes almost nothing beyond the model
> card; the diffusers source is authoritative for parameters but silent on
> quality. A large fraction of what turns up in search is SEO content-farm
> material (`theneuralbase.com`, `prompt-architects.com`, `aiofm.info`,
> `fluxnote.io`, `pxz.ai`, `dreampixelforge.com`, `packet.ai`, `gigagpu.com`,
> `spheron.network`) which recycles and sometimes contradicts itself inside a
> single page. I have labelled every such citation **[low-reliability SEO
> source]**. Where those sources contradict a primary source or each other, I say
> so rather than picking one. Several arXiv IDs returned by search carry 2026
> prefixes that I could not independently verify beyond the search result; those
> are labelled **[unverified beyond search result]**.
>
> **One hard correction up front, because it changes the pipeline design:**
> FLUX.1 **schnell**'s T5 window is capped at **256 tokens**, not 512. The 512
> figure belongs to FLUX.1-dev. Most of the prompting advice on the open web
> conflates them.

---

## FLUX.1 schnell text encoding: CLIP vs T5-XXL, token limits, clause routing, practical maximum prompt length

### Takeaway

FLUX uses two text encoders in parallel — CLIP-L (hard 77 tokens, pooled to a
single global vector) and T5-XXL (sequence of per-token embeddings). For
**schnell specifically, `max_sequence_length` must be ≤ 256**, half of dev's 512.
The CLIP 77-token truncation problem does *not* silently destroy the tail of your
prompt the way it does in SD1.5/SDXL, because T5 still reads the whole thing —
but it does mean the *global style/colour steer* is set almost entirely by the
first ~50 words, so style and palette clauses must be front-loaded.

### Cited Findings

- FLUX.1-schnell is a 12-billion-parameter rectified-flow transformer, released
  under **Apache-2.0**, "distilled to generate high-quality images in only 1 to 4
  steps", and the model card's own recommended call is
  `guidance_scale=0.0, num_inference_steps=4, max_sequence_length=256` —
  [black-forest-labs/FLUX.1-schnell model card](https://huggingface.co/black-forest-labs/FLUX.1-schnell)
- The diffusers `FluxPipeline` documentation states `max_sequence_length` defaults
  to 512 but **"cannot be more than 256" for schnell**, that `guidance_scale`
  must be 0 for schnell, and that `prompt` goes to the CLIP text encoder
  (`clip-vit-large-patch14`) while `prompt_2` goes to the T5 encoder
  (`google/t5-v1_1-xxl`); **if `prompt_2` is not supplied, `prompt` is used in
  all text encoders** —
  [diffusers FluxPipeline docs](https://huggingface.co/docs/diffusers/en/api/pipelines/flux)
- CLIP-L in FLUX is hard-capped at 77 tokens; T5-XXL is configured at 512 for
  FLUX.1-dev. Content past CLIP's 77 tokens is **not** unread — T5 still reads it
  up to its own limit; only content past the T5 limit is unread by both —
  [FLUX.1-dev discussion: Input tokens limited](https://huggingface.co/black-forest-labs/FLUX.1-dev/discussions/43);
  [FLUX.1-dev: Encoders and Token Limitations](https://medium.com/@lbq999/flux-1-dev-encoders-and-token-limitations-8631c179eaad)
- T5's 512-token window is roughly 375 English words; CLIP-L's 77 tokens is
  roughly 50 words. In diffusers you must pass `max_sequence_length` explicitly
  to get the full window —
  [CLIP vs T5: Why Flux Understands Prompts Better Than SDXL](https://aiofm.info/en/guides/what-is-clip-vs-t5-encoder)
  **[low-reliability SEO source]**
- An architectural analysis of FLUX confirms the two-stream text conditioning
  design (pooled CLIP vector injected into the modulation path alongside the
  timestep embedding; T5 sequence concatenated with image tokens for joint
  attention in the double-stream blocks) —
  [Demystifying Flux Architecture, arXiv 2507.09595](https://arxiv.org/pdf/2507.09595)
- A real-world instance of the failure mode: a print-on-demand backend was filed
  against for generating with a **~942-word prompt, "likely 2-3x over FLUX's T5
  limit, and far past CLIP's"** —
  [printpetz-backend issue #23](https://github.com/jthornaday/printpetz-backend/issues/23)

### Inferences

- **Practical maximum useful prompt length for schnell is ~180-200 English words
  (≈256 T5 tokens).** Anything past that is silently discarded by both encoders.
  For a catalogue pipeline this is a hard budget you should enforce in code:
  tokenise with the T5 tokeniser (`google/t5-v1_1-xxl`) at assembly time and
  reject or truncate-with-warning any prompt over 240 tokens, leaving headroom
  for the EOS token. Do **not** rely on the pipeline to warn you.
- Because the CLIP path is *pooled* (one vector for the whole prompt, derived
  from ≤77 tokens) and feeds the modulation/AdaLN path, it acts as a global
  style/colour/mood steer, while T5 carries compositional detail. The actionable
  consequence for a wall-art taxonomy: **put the style axis and the palette axis
  in the first 40-50 tokens**, and put subject detail, composition and
  negative-ish phrasing later. The axes you most need to be visibly distinct
  across cells are exactly the ones that must sit inside CLIP's window.
- Because `prompt_2` routes separately, you can exploit this deliberately:
  pass a short, style-and-palette-only string as `prompt` (CLIP) and the full
  composed prompt as `prompt_2` (T5). This is a supported, documented split and
  is the single cheapest lever for making adjacent taxonomy cells look different.
  I found no published benchmark of this split's effect — treat it as an
  experiment to run, not a settled recipe.

### Gaps

- No published ablation measuring how much of FLUX's output style is attributable
  to the pooled CLIP vector vs the T5 sequence, and therefore no quantitative
  support for the `prompt`/`prompt_2` split tactic above.
- I found no official BFL statement of the 256 limit for schnell other than its
  presence in the model card's example code and the diffusers docs — the number
  is well attested in code but not explained.

---

## Negative prompts on a guidance-distilled model, and how to suppress frames, borders, signatures and text

### Takeaway

Negative prompts do **nothing** on schnell. The `negative_prompt` argument exists
on the pipeline but is ignored when `guidance_scale ≤ 1`, and schnell requires
`guidance_scale=0`. Suppression must therefore be done by (a) positive
description of what you want the frame/background/edge to be, (b) post-hoc
detection-and-reject in the quality gate, or (c) deterministic post-processing
(crop/mask) — not by negation.

### Cited Findings

- diffusers: `negative_prompt` and `negative_prompt_2` exist, but "negative
  prompts are only effective when using guidance (ignored when
  `guidance_scale ≤ 1`)"; `true_cfg_scale` defaults to 1.0 and true CFG is
  enabled only when `true_cfg_scale > 1` **and** a `negative_prompt` is supplied;
  for schnell, "`guidance_scale=0`... negative prompts have **no effect**" —
  [diffusers FluxPipeline docs](https://huggingface.co/docs/diffusers/en/api/pipelines/flux)
- "FLUX.1 Schnell is guidance-distilled, so negative prompts have a much weaker
  effect than in Stable Diffusion 1.5 or SDXL... start without a negative prompt,
  and only add specific defects if they keep appearing, as generic dumps can
  actually degrade output quality" —
  [FLUX.1 Schnell Prompting Guide, deAPI.ai](https://deapi.ai/blog/flux-1-schnell-prompting-guide-how-to-write-prompts-and-avoid-common-mistakes)
  **[low-reliability SEO source]**
- "If CFG is 1.0, negative prompt will do nothing" — for FLUX-dev the community
  pattern is CFG=1 with no negative prompt, using "Distilled CFG Guidance"
  (default 3.5) instead —
  [The Flux AI guide](https://andreaskuhr.com/en/flux-ai-guide.html);
  [MimicPC: Flux.1 on SD WebUI Forge](https://www.mimicpc.com/learn/explore-flux-on-sd)
- "Negative prompt does not work with the stock FluxPipeline" — confirmed as a
  known limitation in a Hugging Face Space discussion —
  [akhaliq/SRPO discussion #1](https://huggingface.co/spaces/akhaliq/SRPO/discussions/1)
- "FLUX prompts work as prose, not keyword tags, and **FLUX has no negative
  prompt at all**" —
  [Flux Prompts: What Works on FLUX.2](https://www.dreampixelforge.com/blog/flux-prompts)
  **[low-reliability SEO source]**
- Workarounds exist as community LoRAs/nodes that re-introduce a negative branch
  (e.g. "Flux Negative CFG") —
  [Civitai: Flux Negative CFG v1.0](https://civitai.com/models/633586/flux-negative-cfg).
  These effectively run two forward passes and so roughly double cost.
- Active research exists on negation without CFG — orthogonal negative guidance
  in attention feature space —
  [Orthogonal Negative Guidance in Attention Feature Space, arXiv 2605.29390](https://arxiv.org/pdf/2605.29390)
  **[unverified beyond search result]**
- Counter-evidence that negation phrasing in the *positive* prompt can help is
  weak and comes only from SEO sources, e.g. "using negative prompts like 'No
  text, no watermarks, no blur'" and "always including negative prompts like 'no
  background details, no textures, no decorative elements'" —
  [Minimalist AI Prompts](https://fluxnote.io/guides/minimalist-ai-prompts)
  **[low-reliability SEO source]**. This directly contradicts the diffusers
  documentation for schnell and should be treated as wrong, or at best as an
  accidental positive-prompt effect (naming "watermark" at all risks *summoning*
  one, since T5 reads the token).
- A specific trap for flat compositions: in FLUX.1 [dev], "using 'white
  background' can cause images to appear blurry or undefined. Avoid this phrase
  entirely... Instead, be more specific about the background" —
  [30 Best FLUX Prompts](https://academy.techpresso.co/prompts/flux-prompts)
  **[low-reliability SEO source]**, echoed by
  [Minimalist AI Prompts](https://fluxnote.io/guides/minimalist-ai-prompts).
  I could not find a primary-source confirmation of this; it is a widely repeated
  community claim.

### Inferences

- **The correct suppression strategy for schnell is positive-affirmative plus
  gating, and it should be designed into the taxonomy template, not bolted on.**
  Instead of "no frame", describe the thing that occupies the frame's position:
  e.g. "the painted area extends to all four edges of the image, uninterrupted"
  or, for the opposite case, "the subject sits on an unbroken field of warm
  off-white, the field continuing past all four edges". Instead of "no signature",
  do not mention signature, artist name, gallery, museum, auction, plate number,
  or any word that co-occurs with signed artwork in the training distribution —
  and then OCR-gate the output.
- **Avoid style tokens that carry framing as part of their visual identity.** This
  is the biggest practical cause of mockup framing and simulated paper edges:
  "antique botanical plate", "vintage lithograph", "poster", "print",
  "illustration from a book" all co-occur in training data with page edges, plate
  borders, captions, foxing and plate numbers. If you want the *mark-making* of a
  lithograph without the *page*, name the technique and the ink behaviour, not
  the artefact. See the style-fragment section below.
- **Generate with deliberate overscan and crop deterministically.** Generate at
  the target ratio plus ~6-8% on each axis, then centre-crop. This removes
  simulated paper edges, vignettes and most stray border artefacts for free, with
  no model cooperation needed, and it also removes the signature when the model
  puts it in a corner (which is where it usually goes). This is an inference from
  the structure of the problem, not a cited recipe.
- Negative-branch LoRAs and attention-space negation are the wrong trade for this
  job: at millions of images a 2x cost increase to suppress an artefact that a
  £0.00002 OCR pass can detect-and-reject is not economic.

### Gaps

- No measured rejection rate for unwanted text/signatures/frames in schnell
  output under any particular prompt template. You will have to measure this on
  your own first 10k images; I found no published base rate.
- No published evaluation of whether the overscan-and-crop tactic actually
  reduces the border-artefact rate.

---

## Step counts, schedulers and guidance for schnell; measured 1 vs 2 vs 4 vs 8 steps

### Takeaway

BFL's own position is **1 to 4 steps, guidance 0.0, with 4 as the reference
configuration**. The open web contains no credible measured quality curve across
1/2/4/8 steps for schnell, and the SEO sources that claim to give one contradict
themselves within a single page. Treat 4 steps / `guidance_scale=0.0` /
FlowMatch Euler as the production default and measure your own 1- and 2-step
curves on your actual styles, because for flat graphic styles the step count you
can get away with is plausibly lower than for photographic content.

### Cited Findings

- BFL model card: "can generate high-quality images in only **1 to 4 steps**",
  with the worked example using `num_inference_steps=4, guidance_scale=0.0` —
  [FLUX.1-schnell model card](https://huggingface.co/black-forest-labs/FLUX.1-schnell)
- diffusers: schnell default usage is 4 steps with `guidance_scale=0.`, vs dev's
  28-50 steps at `guidance_scale=3.5` —
  [diffusers FluxPipeline docs](https://huggingface.co/docs/diffusers/en/api/pipelines/flux)
- "4 steps is the sweet spot for FLUX.1 Schnell, as this is the step count the
  distillation was optimized for" —
  [deAPI.ai schnell prompting guide](https://deapi.ai/blog/flux-1-schnell-prompting-guide-how-to-write-prompts-and-avoid-common-mistakes)
  **[low-reliability SEO source]**
- **Directly contradictory claims from the same low-reliability source family**,
  all surfaced in one search: "Schnell can produce usable results at 1-2 steps;
  marginal improvement at 5-8 steps"; "below 4 steps, images become incoherent
  noise"; "using `num_inference_steps` > 4 produces visible grid artifacts and
  color banding because schnell was distilled only for 4 steps; this is not a
  graceful degradation"; and "`num_inference_steps=4` for schnell is the minimum;
  8-12 steps yields noticeably better quality with only 1-2 second overhead" —
  all from [theneuralbase.com FLUX pages](https://theneuralbase.com/flux/learn/beginner/few-step-generation-4-steps/)
  and [pxz.ai Flux Dev vs Schnell](https://pxz.ai/blog/flux-dev-vs-schnell)
  **[low-reliability SEO sources; mutually contradictory — do not cite any one of
  these as fact]**
- "The distilled model produces images with slightly flatter colors and less fine
  detail, but runs 10-12x faster on identical hardware" (schnell vs dev) —
  [pxz.ai](https://pxz.ai/blog/flux-dev-vs-schnell) **[low-reliability SEO
  source]**
- `guidance_scale=0` for schnell is the documented setting; guidance embedding is
  simply absent from the schnell variant's conditioning —
  [guidance_scale=0 for schnell](https://theneuralbase.com/flux/learn/beginner/guidance-scale-0-for-schnell/)
  **[low-reliability SEO source, but consistent with the primary docs]**

### Inferences

- schnell is a **timestep-distilled** model (the latent-adversarial-diffusion-style
  distillation targets a fixed small step count), and the correct scheduler is the
  one diffusers ships with it: **`FlowMatchEulerDiscreteScheduler`**. The
  SD-era sampler zoo (DPM++ 2M Karras, UniPC, DDIM, Heun, Ancestral variants)
  does not apply in the same way and swapping schedulers on a distilled
  rectified-flow model is a known source of degradation. There is no published
  schnell sampler shootout I could find.
- schnell's shift / `mu` parameter matters more than sampler choice at these step
  counts. diffusers' flow-match scheduler for schnell uses a **fixed** shift
  (`base_shift`/`use_dynamic_shifting=False` for schnell, in contrast to dev's
  resolution-dependent dynamic shift). This is relevant if you push resolution:
  on dev, shift scales with sequence length; on schnell it does not, which is a
  plausible mechanism for schnell degrading faster than dev above ~1.5 MP. I did
  not find this documented explicitly for schnell and flag it as an inference from
  the scheduler configuration.
- **Economically, the 4→2 step decision is the single largest cost lever in the
  whole pipeline** — a 2x throughput change, far larger than any quantisation or
  compiler gain. It therefore deserves a proper internal A/B: render 2,000 cells
  at 1, 2 and 4 steps, score with an aesthetic predictor and a human-rated sample
  of 200, and decide per-style (flat vector/linocut/screenprint styles are the
  likely candidates for 2 steps; watercolour granulation and impasto the likely
  candidates for 4).
- Going above 4 steps is not obviously beneficial and is definitely not free; the
  claim that 8-12 steps improves schnell is unsupported and contradicted
  elsewhere. At millions of images there is no case for it.

### Gaps

- **No credible published measurement** (FID, CLIP score, human preference, or
  aesthetic score) of schnell quality as a function of steps at 1/2/4/8. This is
  a genuine hole in the literature; every number I found was an unsourced blog
  assertion.
- No published sampler/scheduler comparison for schnell.

---

## Prompt structure: prose vs comma-separated tags

### Takeaway

The consensus — including Black Forest Labs' own prompting documentation — is that
FLUX wants **natural-language prose**, in contrast to SD/SDXL's danbooru-style tag
soup, because the T5 encoder is a real language model rather than a
contrastive bag-of-concepts. BFL's current guidance for the FLUX.2 generation goes
further and documents **structured JSON prompts** as a supported form. I found no
rigorous side-by-side prose-vs-tags benchmark; the claim rests on documentation
and consistent community report, not on measurement.

### Cited Findings

- Black Forest Labs publishes an official prompting guide that treats prompts as
  descriptive prose and documents a structured-JSON alternative with fields for
  scene, subjects, style, lighting, camera and `color_palette` —
  [BFL prompting guide, FLUX.2 pro & max](https://docs.bfl.ml/guides/prompting_guide_flux2)
- "FLUX prompts work as prose, not keyword tags." Compact template:
  *Subject + Action + Style + Context*. Expanded slot list: `[SUBJECT],
  [LOCATION], [STYLE], [CAMERA SETTINGS], [LIGHTING], [COLORS], [EFFECT],
  [ADDITIONAL ELEMENTS]` —
  [dreampixelforge: Flux Prompts](https://www.dreampixelforge.com/blog/flux-prompts)
  **[low-reliability SEO source]**
- The JSON schema reported in circulation includes `scene`, `subjects`
  (description/position/action), `style`, `color_palette` (hex values),
  `lighting`, `mood`, `background`, `composition`, and `camera`
  (angle/lens/depth_of_field) —
  [FLUX.2 Prompting Guide: JSON Prompts + HEX Colors](https://renderfire.com/blog/flux-2-prompting-guide);
  [Atlabs FLUX.2 prompting guide](https://www.atlabs.ai/blog/flux-2-prompting-guide)
  **[low-reliability SEO sources, but corroborating the primary BFL guide]**
- Caution on generation drift: FLUX.1 prompting advice and FLUX.2 prompting advice
  are explicitly described as diverging —
  [Flux Prompts: What Works on FLUX.2, and Why FLUX.1 Advice Breaks](https://www.dreampixelforge.com/blog/flux-prompts)
  **[low-reliability SEO source]**
- General prompting guidance for FLUX.1 from inference providers emphasises
  descriptive sentences and explicit composition language —
  [Segmind FLUX prompting guide](https://blog.segmind.com/flux-prompting-guide-image-creation/);
  [Eachlabs: Flux Prompts techniques](https://www.eachlabs.ai/blog/flux-prompts-techniques-for-accurate-aesthetic-results)

### Inferences

- **The JSON-prompt finding is from the FLUX.2 line, not FLUX.1 schnell, and must
  not be transferred uncritically.** FLUX.2's text encoder stack is different. For
  schnell, write prose. However, a *templated prose generator* driven by a JSON
  taxonomy record is exactly the right engineering shape: keep the taxonomy as
  structured data, render it to prose through a template with per-axis phrase
  banks. That gives you reproducibility, a token budget you can enforce, and the
  ability to vary surface wording (which itself adds diversity) without changing
  the semantic cell.
- Because schnell's budget is only 256 T5 tokens, prose is also the *efficient*
  choice: tag lists waste tokens on commas and fragments that T5 cannot use
  compositionally.
- Practical template shape that respects the CLIP-77 / T5-256 split:
  - `prompt` (CLIP, ≤ ~60 tokens): `"{style_short}, {palette_short},
    {composition_short}"`
  - `prompt_2` (T5, ≤ ~240 tokens): full prose sentence(s) naming subject,
    technique-level mark-making, palette with named pigments, composition,
    edge-to-edge instruction.

### Gaps

- **No controlled prose-vs-tags experiment with released images or metrics.** The
  claim is universally asserted and nowhere measured.
- BFL has not published a FLUX.1-specific prompting guide equivalent to the
  FLUX.2 one; the FLUX.1 advice in circulation is all community-derived.

---

## Flat, clean, print-ready composition: subject on plain ground, no shadow, no mockup, no paper edge, no watermark, no text

### Takeaway

There is no reliable published recipe. What exists is (a) a strong, consistent
community warning that the phrase "white background" degrades FLUX output, (b)
positive-affirmative phrasings that describe the ground as a material rather than
as an absence, and (c) the structural answer: generate with overscan, crop, and
gate with OCR plus edge-energy statistics. Because negation is unavailable on
schnell, the gate does the work that a negative prompt would do in SDXL.

### Cited Findings

- "In the [dev] variant of FLUX.1, using 'white background' can cause images to
  appear blurry or undefined. Avoid this phrase entirely in your prompt. Instead,
  be more specific about the background, for example, describing it as 'a soft
  blue sky' or 'a foggy mist'" —
  [30 Best FLUX Prompts](https://academy.techpresso.co/prompts/flux-prompts)
  **[low-reliability SEO source; widely repeated community claim, no primary
  confirmation found]**
- Product-photography-style template reported to work: "a product centered on a
  seamless white background with flat even studio lighting, soft contact shadow,
  clean uncluttered background, and tack-sharp focus edge to edge... true-to-life
  color without color cast" —
  [Segmind FLUX prompting guide](https://blog.segmind.com/flux-prompting-guide-image-creation/)
  **[note: this template deliberately includes a contact shadow, which is the
  opposite of what a flat print needs]**
- Minimalist/flat recipe reported: "specify 'flat colors, clean lines, ample white
  space' and use terms like 'geometric simplicity' or 'monochromatic palette'" —
  [Minimalist AI Prompts](https://fluxnote.io/guides/minimalist-ai-prompts)
  **[low-reliability SEO source]**
- Tiled upscaling workflows for print explicitly end with "export as TIFF for
  printing", confirming that the print-prep step is conventionally separate from
  generation —
  [ComfyUI Upscale Workflow: Ultimate SD Upscale](https://comfylab.dev/blog/workflows/comfyui-upscale-workflow-ultimate-sd-upscale/)
  **[low-reliability SEO source]**

### Inferences

These are engineering recommendations derived from the token-routing facts and the
absence of negation, not cited recipes. Flag them as such in the report.

- **Describe the ground as a pigmented surface, not as emptiness.** Replace "white
  background" with e.g. *"on an unbroken field of cold-pressed cotton rag paper,
  bare warm off-white, the paper tone continuing evenly to every edge"*. This
  gives T5 a material to render rather than an absence to hallucinate into, which
  is the likely mechanism behind the "white background goes blurry" report.
- **Say where the picture stops, affirmatively.** *"The image area runs to all four
  edges; the paper is bare and unmarked at the margins; nothing overlays the
  picture."* Then crop the overscan. Never write "no border" — the token "border"
  is in T5's window and is a request.
- **Kill shadows by naming the lighting condition, not by negating the shadow.**
  *"flat, shadowless, evenly diffused light; no cast direction"* is risky (contains
  "shadow"); *"uniform flat illumination, perfectly even across the surface,
  rendered as flat opaque colour areas"* is safer. For flat graphic styles the
  best suppression is to name a medium that physically cannot cast a drop shadow
  — ink on paper, flat screenprint layers — so the shadow is out of
  distribution rather than negated.
- **Suppress mockup framing by never naming a context of display.** Any of
  "poster", "print", "wall art", "framed", "gallery wall", "hanging", "mockup",
  "room" will pull the model toward rendering a photograph of a framed print on a
  wall. Name only the artwork itself. This is the most common cause of mockup
  framing and the easiest to fix.
- **Suppress text/signature by omission plus OCR gate.** Do not name artist,
  signature, title, caption, label, plate, botanical nomenclature, Latin binomial,
  or any museum/herbarium context. Then run OCR (see gating section) and reject
  any image with confident glyph detections above a small area threshold.
- **A deterministic post-process pass is cheaper and more reliable than any
  prompt.** At millions of images, a 20 ms OpenCV pass per image that (i) crops
  overscan, (ii) measures edge-band pixel variance to detect a frame or paper
  edge, (iii) measures corner-region high-frequency energy to flag signatures, is
  far cheaper than extra diffusion steps or a negative branch.

### Gaps

- **No measured base rates** for any of these artefacts in schnell output, and no
  published A/B of the phrasings above. This whole section is engineering
  judgement scaffolded on a small number of weak community claims. It needs an
  internal pilot of a few thousand images per style to become a real recipe.
- The "white background causes blur" claim is specifically reported for FLUX.1
  **dev**; whether it holds for schnell is unverified.

---

## Prompt language for specific art styles

### Takeaway

I found **no published, citable prompt-fragment library** for these specific
traditional-media styles on FLUX. Everything in circulation is adjective lists
on content farms. The defensible finding is methodological: name the
**physical process and its characteristic defects** rather than the style label,
because process-and-defect language is both more specific and less likely to drag
in the framing/paper-edge/caption artefacts that come bundled with style labels
like "antique botanical plate".

### Cited Findings

- BFL's own guidance treats style as a described quality within prose, with a
  dedicated `style` field in the structured form — i.e. style is a *description*
  slot, not a keyword slot —
  [BFL prompting guide](https://docs.bfl.ml/guides/prompting_guide_flux2)
- The expanded FLUX prompt slot list places `[STYLE]`, `[LIGHTING]`, `[COLORS]`
  and `[EFFECT]` as separate slots, supporting a compositional per-axis template —
  [dreampixelforge](https://www.dreampixelforge.com/blog/flux-prompts)
  **[low-reliability SEO source]**
- For FLUX.1 specifically, provider guides recommend explicit medium and technique
  description over style keywords —
  [Segmind FLUX prompting guide](https://blog.segmind.com/flux-prompting-guide-image-creation/);
  [Eachlabs](https://www.eachlabs.ai/blog/flux-prompts-techniques-for-accurate-aesthetic-results)

### Inferences

The following fragments are **my constructions following the process-and-defect
principle**, not sourced recipes. They are offered as a starting phrase bank to
be validated, and the report should present them as untested. Each is written to
fit inside a 256-token budget alongside a subject clause, and each deliberately
omits any word that implies a page, a frame, a caption or a gallery.

- **Watercolour, wet edges and granulation** — *"transparent watercolour washes on
  rough cold-pressed cotton rag; pigment pools and dries to hard wet edges where
  each wash stops; visible granulation as heavy pigment settles into the paper
  tooth; soft wet-in-wet bleeds in the interior; the white of the paper left bare
  for highlights"*. The load-bearing tokens are *wet edge*, *granulation*,
  *wet-in-wet*, *cold-pressed*, *pigment settles into the tooth*.
- **Linocut / woodblock** — *"relief print cut from linoleum, carved with a
  V-gouge; bold reductive shapes; chisel facets and small slips visible at the
  cut edges; uneven ink coverage with lighter patches where the block did not take
  pressure; a single flat opaque ink colour over bare paper"*. Load-bearing:
  *relief*, *V-gouge*, *reductive*, *uneven ink coverage*, *cut edge*.
- **Antique botanical / ornithological plate** — the dangerous one. Use *"hand-
  coloured copperplate engraving in the manner of early nineteenth-century natural
  history illustration; fine engraved hatching defining form; delicate transparent
  washes laid over the engraved line; specimen isolated on bare paper"* and
  **omit** *plate*, *plate number*, *Latin name*, *herbarium sheet*, *folio*,
  *book*, *Redouté*, *Audubon*. Naming a named artist is also a licensing
  consideration — see the licensing notes elsewhere in this research set.
- **Vintage lithograph** — *"stone lithograph, greasy crayon drawn directly on the
  stone; soft grainy tonal passages from the stone's texture; limited flat ink
  colours in loose registration; slightly muted inks"*. Load-bearing: *greasy
  crayon*, *stone grain*, *loose registration*.
- **Oil impasto and palette knife** — *"thick oil paint laid on with a palette
  knife; raised ridges of paint catching a raking light; knife-edge facets and
  scraped flats; colours half-mixed on the surface so streaks of unblended
  pigment remain; stiff peaks where the knife lifted away"*. Load-bearing:
  *palette knife*, *ridges*, *scraped flats*, *half-mixed*, *stiff peaks*. Note
  the tension with flatness: impasto *needs* a light direction to read, so for
  this style you cannot also demand shadowless flat lighting.
- **Risograph misregistration** — *"risograph duplicator print in two spot inks,
  fluorescent pink and medium blue; each ink laid as a coarse dot screen; the two
  layers slightly out of register so edges double and overlaps go dark; patchy ink
  density and roller streaks"*. Load-bearing: *spot inks*, *out of register*,
  *overlap goes dark*, *roller streak*.
- **Single-weight ink line art** — *"continuous ink line of one unvarying width
  drawn with a technical pen; no tonal shading, no hatching, no line weight
  variation; pure contour; large areas of bare paper"*. This one is unusually
  hard for diffusion models (line-weight consistency is a global constraint) and
  is a good candidate for a per-style stricter quality gate.
- **Cyanotype** — *"cyanotype contact print; deep Prussian blue where the
  sensitiser was exposed, paper white where it was masked; brushed sensitiser
  edges visible as uneven streaks; soft loss of detail in the deepest blues"*.
  Load-bearing: *Prussian blue*, *contact print*, *brushed sensitiser edge*.
- **Halftone** — *"printed in a coarse halftone dot screen at a visible 45-degree
  screen angle; tone built entirely from varying dot size; dots clearly resolved;
  slight ink spread where dots touch"*. Load-bearing: *screen angle*, *dot size*,
  *dot gain*.
- **Screenprint** — *"screenprint in four flat opaque spot colours pulled through a
  mesh; hard-edged flat colour areas with no gradients; faint mesh texture in the
  solids; a thin halo where one colour overlaps the next; occasional pinhole where
  the emulsion failed"*. Load-bearing: *spot colours*, *flat opaque*, *mesh
  texture*, *pinhole*.

- **General principle worth stating in the report:** the defect vocabulary is what
  makes these distinct from one another in embedding space. "Watercolour" and
  "gouache" and "ink wash" collapse together; "granulation and hard wet edges"
  vs "flat opaque matte coverage" vs "wet-in-wet bleed with no hard edge" do not.
  Since the whole project is fighting near-duplication, **the style axis should be
  defined by process-defect phrases, not style nouns.**

### Gaps

- No published prompt library, no measured style-separation data, and no
  evaluation of whether FLUX schnell can actually render granulation or impasto
  ridges convincingly at 1 MP (plausibly it cannot at 4 steps — texture is
  exactly what distillation loses, per the "less fine detail" claim above). This
  needs a pilot.
- I found no source on whether FLUX schnell has learned any of these media labels
  strongly enough to be reliable; the model card gives no training-data detail.

---

## Palette control from the prompt

### Takeaway

Hex-code colour control is **documented as working in the FLUX.2 generation** by
Black Forest Labs. There is **no evidence that hex codes work on FLUX.1 schnell**,
and good reason to doubt it. For schnell, use named pigments and explicit
colour-count language in the prompt, and enforce the palette in post-processing,
which is the only method that actually guarantees a 3-5 colour result.

### Cited Findings

- Black Forest Labs' guide "states plainly: 'FLUX.2 supports precise color
  matching using hex codes'" and documents the mechanism: signal a hex colour with
  the keyword "color" or "hex" followed by the code, and associate each hex value
  with a specific object or surface —
  [BFL prompting guide FLUX.2](https://docs.bfl.ml/guides/prompting_guide_flux2);
  [FLUX.2 Prompting Guide: JSON Prompts + HEX Colors](https://renderfire.com/blog/flux-2-prompting-guide)
- Worked example of the documented syntax: *"A modern living room with warm
  terracotta walls in hex #C4725A, a large L-shaped sectional sofa in deep teal
  hex #1B6B6F, and golden amber hex #E8A847 accent pillows"* —
  [renderfire](https://renderfire.com/blog/flux-2-prompting-guide)
  **[low-reliability SEO source, corroborating the BFL guide]**
- The structured-prompt schema exposes `color_palette` as a first-class field
  accepting hex codes or colour names —
  [BFL prompting guide](https://docs.bfl.ml/guides/prompting_guide_flux2);
  [Atlabs](https://www.atlabs.ai/blog/flux-2-prompting-guide)
- Separate community treatment of exact-colour prompting exists —
  [Colour and Palette Prompting (Getting Exact Colours)](https://prompt-architects.com/blog/563-colour-and-palette-prompting-getting-exact-colours)
  **[low-reliability SEO source]**
- Explicit warning that FLUX.2 prompting advice does not transfer to FLUX.1 —
  [dreampixelforge](https://www.dreampixelforge.com/blog/flux-prompts)
  **[low-reliability SEO source]**

### Inferences

- **Do not build the palette axis on hex codes for schnell.** The hex capability
  is a FLUX.2 feature; FLUX.1's T5 tokenises `#C4725A` into meaningless subword
  pieces and there is no documented training signal tying those pieces to a
  colour. Expect hex codes to act as weak noise, not control.
- **What should work on schnell, in descending order of expected reliability:**
  1. **Pigment and material names** — *"Prussian blue, yellow ochre, burnt sienna,
     and bare paper"*. These are high-frequency in art-historical text and are
     tied to actual appearances in the training distribution. They also carry
     tonal and saturation information that colour words do not.
  2. **Explicit colour count plus named colours** — *"printed in exactly three
     flat spot inks: deep indigo, warm coral, and bare cream paper"*. The count
     language is reinforced by naming a process that physically limits colours
     (screenprint, risograph, linocut, cyanotype), which is why the style axis and
     the palette axis should be designed jointly rather than as independent axes.
  3. **Palette-descriptor phrases** — *"muted dusty pastels"*, *"high-chroma
     seventies earth tones"*. Reliable for mood, useless for exactness.
  4. **Hex codes** — unlikely to work; cheap to include, so no harm, but do not
     rely on them.
- **The only method that forces a 3-5 colour palette is post-processing.** This is
  the right answer for a catalogue and it is cheap:
  - Convert to the target palette by nearest-colour mapping in **CIELAB** (not
    RGB) with a small amount of ordered dithering, or
  - Run k-means in LAB with k = palette size and snap cluster centres to the
    palette, or
  - For flat styles, posterise-then-map, which also removes the soft gradients
    that betray a diffusion origin.
  This also gives you a **palette-conformance score** for free (mean ΔE from each
  pixel to its nearest palette entry), which is a cheap and highly discriminative
  quality-gate signal — see the gating section.
- **Palette as a post-process has a large diversity dividend.** It means the same
  generation can be emitted as several genuinely different-looking catalogue
  entries, and, more importantly, it makes the palette axis *exactly* controllable,
  which is what a space-filling design over the taxonomy needs (see the
  combinatorial section — the design is only valid if the axes are actually
  realised).

### Gaps

- **No published test of hex codes on FLUX.1 schnell.** My claim that they do not
  work is an inference from the FLUX.2-only documentation and from tokenisation,
  not a measurement.
- No published comparison of pigment names vs colour words vs palette descriptors
  on any FLUX variant.

---

## Native resolutions and aspect ratios; where schnell degrades

### Takeaway

FLUX is trained around 1 MP; the practical ceiling is ~2 MP, and output above
~1 MP is reported to soften. Dimensions must be multiples of 16. For A-series,
3:4 and 5:7 you must choose 16-multiple dimensions that approximate or exactly hit
the ratio — I have computed these below, and I correct a search-result error about
1024×1448.

### Cited Findings

- Documented/community-supported resolutions for FLUX.1-schnell: 1024×1024,
  768×1344, 1344×768, 896×1152, 1152×896, 832×1216, 1216×832 —
  [NVIDIA build.nvidia.com FLUX.1-schnell model card](https://build.nvidia.com/black-forest-labs/flux_1-schnell/modelcard);
  [flux-schnell on aimodels.fyi](https://www.aimodels.fyi/models/replicate/flux-schnell-black-forest-labs)
- "FLUX has a maximum resolution of 2.0 MP"; at 2.0 MP and 1:1 the exact
  resolution is 1448×1448, "rounded to 1408×1408" —
  [ControlAltAI-Nodes (Flux Resolution Calc)](https://github.com/gseth/ControlAltAI-Nodes);
  [Comfyroll issue #206: Update CR Aspect Ratio with Flux maximum resolutions](https://github.com/Suzie1/ComfyUI_Comfyroll_CustomNodes/issues/206)
- "Generations above 1 MP may appear slightly blurry... for best quality, keeping
  the total pixel area near 1 megapixel (1024×1024 equivalent) is recommended,
  with upscaling after generation" —
  [ControlAltAI-Nodes](https://github.com/gseth/ControlAltAI-Nodes);
  [Flux Resolution Calc node docs](https://www.runcomfy.com/comfyui-nodes/ControlAltAI-Nodes/flux-resolution-node)
- "FLUX.1 requires image dimensions to be multiples of 16 pixels" —
  [Flux Resolution Calc node](https://www.runcomfy.com/comfyui-nodes/ControlAltAI-Nodes/flux-resolution-node);
  [aspectratiocalculator.com AI image aspect ratios](https://aspectratiocalculator.com/ai-image-aspect-ratios/)
- **Error in a search result, flagged:** one summary asserted that "1024×1448...
  does meet the 16-pixel multiple requirement (both dimensions are divisible by
  16)". **This is false.** 1448 / 16 = 90.5. 1448 is a multiple of 8, not 16. The
  nearest valid values are 1440 and 1456. Source of the error:
  [theneuralbase aspect ratios page](https://theneuralbase.com/flux/learn/beginner/aspect-ratios-supported/)
  **[low-reliability SEO source, demonstrably wrong on arithmetic]**
- Research exists on pushing rectified-flow transformers above their training
  resolution via projected flow, reporting that naive resolution extrapolation
  degrades and that targeted methods are needed —
  [I-Max: Maximize the Resolution Potential of Pre-trained Rectified Flow Transformers, arXiv 2410.07536](https://arxiv.org/pdf/2410.07536)

### Inferences — computed 16-multiple dimensions for your three ratios

I computed these; they are arithmetic, not citations.

**A-series, 1:√2 = 1.414214** (irrational, so no exact integer solution):

| w × h | ratio | error vs √2 | MP |
|---|---|---|---|
| 848 × 1200 | 1.41509 | +0.06% | 1.02 |
| 864 × 1216 | 1.40741 | −0.48% | 1.05 |
| 880 × 1248 | 1.41818 | +0.28% | 1.10 |
| 960 × 1360 | 1.41667 | +0.17% | 1.31 |
| **1008 × 1424** | **1.41270** | **−0.11%** | **1.44** |
| 1024 × 1440 | 1.40625 | −0.56% | 1.47 |
| 1024 × 1456 | 1.42188 | +0.54% | 1.49 |

→ **848 × 1200** is the best A-ratio at ~1 MP (+0.06% error). **1008 × 1424** is
the best at ~1.4 MP (−0.11%). Note that 848×1200 at a 0.06% ratio error is within
the printer's own trim tolerance (Prodigi photo prints carry 3 mm bleed, see the
print-prep section), so no visible crop results.

**3:4 (30×40 cm) — exact solutions exist** because 3:4 with both dims divisible by
16 requires w = 48k, h = 64k:
- **864 × 1152** = exactly 3:4, 0.995 MP ← recommended
- **960 × 1280** = exactly 3:4, 1.23 MP
- 1152 × 1536 = exactly 3:4, 1.77 MP (near the ceiling, expect softening)

**5:7 (50×70 cm) — exact solutions exist**, requiring w = 80k, h = 112k:
- **880 × 1232** = exactly 5:7, 1.08 MP ← recommended
- **960 × 1344** = exactly 5:7, 1.29 MP
- 1040 × 1456 = exactly 5:7, 1.51 MP

**These are three genuinely different ratios** (1.4142, 1.3333, 1.4000) and a
composition that works at 3:4 will be cropped or letterboxed at A-ratio. The
format axis is therefore not free — it must be a real generation axis, not a crop
of one master. The 5:7 and A ratios are close enough (1.400 vs 1.414, a 1% 
difference) that a single generation at **A-ratio with 2% overscan can serve both**
by differential cropping; 3:4 cannot.

- **On schnell's degradation mechanism above ~1.5 MP:** diffusers configures
  schnell's flow-match scheduler without dynamic shifting (unlike dev, where
  `mu` scales with sequence length). Resolution extrapolation on rectified-flow
  transformers is a known failure mode addressed by dedicated methods
  ([I-Max, arXiv 2410.07536](https://arxiv.org/pdf/2410.07536)). The practical
  symptoms to expect are composition duplication (repeated subjects), loss of
  global coherence, and soft mush in large flat areas — **not** graceful
  softening. This is an inference; I found no schnell-specific resolution ablation.
- **Recommendation: generate at ~1.0-1.1 MP and upscale.** Generating at 2 MP buys
  you 1.4x linear resolution for roughly 2x the compute and puts you in the
  degradation zone; a 4.8-5.9x upscale is required either way, so the extra MP
  does not remove the upscaling step. There is therefore **no case** for
  high-resolution direct generation at this scale.

### Gaps

- No published quality-vs-resolution curve for schnell specifically.
- No published confirmation of the 2 MP ceiling from BFL — the figure comes from
  ComfyUI node authors, not the model card.

---

## Upscaling 1 MP → A2 at 300 dpi (4961 × 7016 px)

### Takeaway

Your true factor is larger than 4.8x: from the recommended 848×1200 it is **5.85x
linear** (and 5.85² ≈ 34x in pixels). The published comparative data on upscalers
is thin and almost entirely subjective. The one well-attested quantitative
contrast is **4x-UltraSharp at 3-5 s/image on 4 GB VRAM vs SUPIR at ~45 s/image**
— a ~10-13x cost difference that, at millions of images, decides the question in
favour of a GAN/transformer upscaler plus tiling, not SUPIR.

### Cited Findings

- "4x-UltraSharp is fast (**3-5 seconds per image** vs SUPIR's **45 seconds**) and
  runs on **4 GB VRAM**, making it more practical for bulk processing despite
  SUPIR's superior quality for certain tasks" —
  [AI Image Upscaling in 2026: Every Upscaler Compared](https://aiofm.info/en/guides/ai-image-upscaling)
  **[low-reliability SEO source; this is the only seconds-per-image figure I
  found for either model and it is uncited]**
- "4x-UltraSharp is one of the most popular 4x upscalers for photorealistic images
  and produces crisp, sharp results with excellent detail preservation across all
  styles" — [aiofm](https://aiofm.info/en/guides/ai-image-upscaling)
  **[low-reliability SEO source]**
- **4x-Nomos8kDAT** is a photo upscaler on the **DAT (Dual Attention Transformer)**
  architecture, handling JPEG compression, blur and resize; **4x-Nomos8kHAT-L** is
  the equivalent on **HAT (Hybrid Attention Transformer)** —
  [ComfyUI upscale model listing](https://comfyuiweb.com/resources/upscale-models)
- SUPIR "does a very nice job of preserving the general look and feel while adding
  depth... nice skin texture preservation, though SUPIR **does take quite a bit of
  creative liberties** when comparing it to the original high resolution
  illustration" —
  [Free vs Paid AI Image Upscalers Compared](https://medium.com/code-canvas/testing-different-upscalers-paid-vs-free-options-1260ab82d403)
- Recommendation split: "for hero-quality realistic portraits: SUPIR; for
  photographic detail: Topaz Gigapixel (paid) or SUPIR (free)" —
  [aiofm](https://aiofm.info/en/guides/ai-image-upscaling);
  SUPIR positioned as "SOTA open source image upscaler better than Magnific &
  Topaz" by its community promoters —
  [HF blog: SUPIR SOTA image upscale](https://huggingface.co/blog/MonsterMMORPG/supir-sota-image-upscale-better-than-magnific-ai);
  [SUPIR tutorial wiki](https://github.com/FurkanGozukara/Stable-Diffusion/wiki/SUPIR:-New-SOTA-Open-Source-Image-Upscaler-&-Enhancer-Model-Better-Than-Magnific-&-Topaz-AI-Tutorial)
  **[note: this author is a commercial promoter of SUPIR workflows; treat the
  "better than Topaz" claim as marketing]**
- Tiled diffusion upscaling drops VRAM sharply: "the image is split into
  overlapping tiles (typically 512 px), each tile is processed separately... an
  **8 GB GPU can thus handle work that would normally require 24 GB**", and
  tiled processes "can work with a GPU that has at least **4 GB** of VRAM to
  upscale... to 4K and 8K" —
  [ComfyUI Upscale Workflow: Ultimate SD Upscale](https://comfylab.dev/blog/workflows/comfyui-upscale-workflow-ultimate-sd-upscale/);
  [Stable Diffusion Upscaling: Complete Guide](https://myimageupscaler.com/blog/stable-diffusion-upscaling-complete-guide)
  **[low-reliability SEO sources]**
- A print-oriented tiled recipe in circulation: "generate at native resolution
  with a detailed prompt, use Ultimate SD Upscale with **'Half tile +
  intersections'**, apply **ControlNet Tile at 0.8 weight with denoise 0.4**,
  output at 4x original resolution, export as **TIFF**" —
  [comfylab.dev](https://comfylab.dev/blog/workflows/comfyui-upscale-workflow-ultimate-sd-upscale/)
  **[low-reliability SEO source; the denoise 0.4 / weight 0.8 pair is the only
  concrete parameter set I found]**
- A ControlNet Tile pass after Ultimate SD Upscale "provides advanced seam
  reduction by forcing the sampler to respect the original image's structure per
  tile, nearly eliminating seams" —
  [comfylab.dev](https://comfylab.dev/blog/workflows/comfyui-upscale-workflow-ultimate-sd-upscale/);
  [How to AI Upscale with ControlNet Tiles](https://www.yeschat.ai/blog-How-to-AI-Upscale-with-ControlNet-Tiles-High-Resolution-for-Everyone-27107)
- Ultimate SD Upscale is available as a hosted model, giving a cost reference
  point — [Replicate: fewjative/ultimate-sd-upscale](https://replicate.com/fewjative/ultimate-sd-upscale)
- Tiled-diffusion implementations for ComfyUI —
  [ComfyUI-TiledDiffusion](https://github.com/aravindhv10/ComfyUI-TiledDiffusion)

### Inferences

- **Recommended architecture: two-stage, mostly non-diffusion.**
  1. **Stage 1 (cheap, deterministic, texture-preserving):** a 4x ESRGAN-family or
     DAT/HAT model. For *painterly* content specifically, prefer the
     **Nomos8k-trained DAT or HAT variants** over 4x-UltraSharp: UltraSharp is
     trained for photographic sharpness and is a known offender for
     over-sharpening and plasticising painterly texture (community consensus;
     I found no quantitative source). 848×1200 → 3392×4800 at 4x.
  2. **Stage 2 (final sizing):** **Lanczos** from 3392×4800 to 4961×7016 (a 1.46x
     step). A sub-1.5x Lanczos step is visually benign and essentially free
     (~50 ms, CPU). This avoids running any model at output resolution.
  This gives you print size without ever holding a 35-megapixel tensor on the GPU.
- **Reject SUPIR and diffusion tile upscaling for the bulk run.** At 45 s/image
  SUPIR alone would cost more GPU-seconds than generation by an order of
  magnitude, and its documented tendency to "take creative liberties" is actively
  harmful for a catalogue where the generated design is the product and must not
  be reinterpreted. Keep SUPIR or Ultimate SD Upscale + ControlNet Tile
  (denoise 0.4, CN weight 0.8) as a **hand-finishing path for the small subset of
  designs that actually sell** — that is where the quality premium pays.
- **Reject Topaz** for this use: it is commercial, per-seat/licence-constrained
  desktop software with no supported headless batch API at this scale.
- **Texture preservation ranking, by mechanism rather than by benchmark** (I found
  no benchmark that measures painterly-texture preservation; state this clearly):
  diffusion-based (SUPIR / tile) *invents* plausible texture — best-looking,
  least faithful; transformer SR (DAT, HAT, SwinIR) reconstructs — faithful,
  somewhat soft; GAN SR (Real-ESRGAN, UltraSharp) sharpens aggressively —
  risks plastic/waxy results on watercolour granulation and smears impasto ridges
  into ribbons; Lanczos is honest and soft. For watercolour granulation
  specifically, the grain is *high-frequency noise that must survive*, and GAN
  upscalers trained on photos tend to read it as compression artefact and remove
  it. This is the single biggest technical risk in the print pipeline and deserves
  a dedicated pilot: upscale 200 watercolour and 200 impasto generations through
  DAT, HAT, Real-ESRGAN, UltraSharp and Lanczos, print 10 at A2, and look at them.
- **A viewing-distance argument may let you off entirely.** A2 wall art is viewed
  at ≥1 m, where ~150 dpi is generally adequate; 300 dpi at A2 is the printer's
  *ideal*, not a floor. If your POD partner accepts 150-180 dpi (2480×3508 at A2 =
  150 dpi), your upscale factor drops to ~2.9x and the entire problem gets easier
  and cheaper. **Confirm the actual minimum with Prodigi/Gelato before engineering
  for 5.85x.** This is an inference — see the gap note.

### Gaps

- **No VRAM figures and no seconds-per-image for SwinIR, HAT, DAT or
  Real-ESRGAN** turned up in my searches. The only timing figures I found are the
  uncited UltraSharp 3-5 s / SUPIR 45 s pair. This is a significant gap for cost
  modelling and should be closed by local measurement, which is cheap to do.
- **No quantitative comparison on painterly or illustrated content.** Every
  upscaler comparison I found evaluates photographs or portraits. There is no
  published metric for "preserves watercolour granulation".
- Prodigi's published FAQ does **not** state a minimum dpi, only that 300 dpi is
  "ideal" — so I cannot source the claim that 150 dpi would be accepted.

---

## Print-ready file format, bit depth, colour profile and dpi metadata for a UK POD printer

### Takeaway

Prodigi (UK) wants **RGB at 300 dpi**, accepting **JPG, PNG or PDF** for wall art,
with **3 mm bleed** on photo prints; Gelato specifies **sRGB**. Neither accepts or
asks for CMYK for wall art, and neither mentions 16-bit or TIFF for standard
products. **Do not convert to CMYK and do not ship 16-bit** — the printers'
pipelines expect 8-bit sRGB and will convert themselves.

### Cited Findings

- Prodigi: "for wall art products, the optimal DPI is 300, and artwork should be
  exported in **RGB** at 300 DPI"; "images with 300 dpi are ideal for fine art
  prints and framed prints" —
  [Prodigi: How To Create Print On Demand Wall Art](https://www.prodigi.com/blog/create-print-on-demand-wall-art/);
  [Prodigi Images FAQ](https://www.prodigi.com/faq/images/)
- Prodigi accepted formats: "high-quality **JPG, PNG or PDF** files, depending on
  the product"; JPG recommended for photographic and fine art images; PNG for
  apparel (transparency, higher colour depth). Some specialist products (foil,
  glow-in-the-dark) **must** be PNG at 300 dpi —
  [Prodigi Images FAQ](https://www.prodigi.com/faq/images/);
  [Prodigi: prep artwork for custom foil printing](https://support.prodigi.com/hc/en-us/articles/15532727478172-How-to-prep-your-artwork-for-custom-foil-printing)
- Prodigi bleed: "photo prints typically have **3 mm of bleed**", trimmed after
  printing; "the Print API automatically prepares images with correct bleed
  specifications" —
  [Prodigi Images FAQ](https://www.prodigi.com/faq/images/)
- Prodigi worked minimum example: for a 10″ × 6.7″ print at 300 dpi, minimum image
  dimensions are 3008 × 2000 px —
  [Prodigi Images FAQ](https://www.prodigi.com/faq/images/)
- Prodigi publishes **downloadable ICC colour profiles** "intended for hard
  proofing... used alongside your own device or paper profiles" —
  [Prodigi Images FAQ](https://www.prodigi.com/faq/images/);
  [Prodigi C-type photo prints](https://www.prodigi.com/products/prints-and-posters/photo-prints/c-types/)
- Gelato: "create your design files using the **sRGB** color profile" —
  [Gelato: guidelines regarding design files](https://support.gelato.com/en/articles/8996354-what-are-the-guidelines-regarding-design-files-for-dtg-printing)
  **[note: this specific article is about DTG apparel, not wall art; I did not
  find a Gelato wall-art-specific colour statement]**
- Prodigi's system "reads your uploaded image file and only displays products that
  match or are smaller than the original size" — i.e. pixel dimensions gate which
  sizes you can offer —
  [Prodigi Images FAQ](https://www.prodigi.com/faq/images/)
- Print-industry background on prepress colour conversion —
  [Prepress (Wikipedia)](https://en.wikipedia.org/wiki/Prepress)
- Community discussion of POD export settings exists but without authoritative
  specs —
  [GIMP forum: export settings for print on demand](https://www.gimp-forum.net/Thread-Export-settings-for-print-on-demand);
  [DeviantArt forum: which dpi for POD art prints, gelato/etsy](https://www.deviantart.com/forum/community/life/2780692)

### Inferences — recommended output spec

Arithmetic and engineering judgement, not citations:

- **Format: JPEG, quality 95, 4:4:4 chroma subsampling** (not 4:2:0 — chroma
  subsampling destroys saturated hard edges, which is exactly what screenprint and
  risograph styles are made of). Prodigi accepts JPG and recommends it for fine
  art. A 4961×7016 JPEG at q95/4:4:4 is roughly 8-15 MB.
  - **Why not PNG:** lossless 8-bit RGB at 35 MP is ~40-90 MB per file. At one
    million designs that is 40-90 TB of storage and egress versus ~10 TB for
    JPEG. For a catalogue of this size, JPEG q95 is the right trade; the visible
    difference at 300 dpi is nil.
  - **Why not TIFF:** Prodigi's wall-art list does not include it. If you ever do
    need TIFF, use **ZIP (Deflate) compression, not LZW** — LZW is a 1980s
    algorithm that can *enlarge* continuous-tone images, while ZIP consistently
    beats it on photographic and painterly content.
  - **Why not PDF:** adds a container with no benefit for raster-only artwork and
    more ways for a printer's RIP to misinterpret the colour intent.
- **Bit depth: 8-bit.** Prodigi's accepted formats for wall art (JPG) cannot carry
  16-bit anyway, and a 16-bit pipeline doubles storage for no gain on output that
  is going straight to an 8-bit-per-channel printer driver. Keep 16-bit only
  *internally* if you do heavy palette-mapping maths, and emit 8-bit.
- **Colour: sRGB, with the sRGB ICC profile embedded.** Both Prodigi (RGB) and
  Gelato (sRGB) ask for RGB. **Do not convert to CMYK**: you do not know the press,
  the paper or the ink set, and a CMYK conversion you perform is a conversion the
  printer cannot undo. Do not use Adobe RGB either — it is wider than sRGB, and if
  the printer assumes sRGB (which POD pipelines do) your colours will come back
  desaturated. **Embed the profile explicitly** rather than relying on
  untagged-means-sRGB.
- **dpi metadata: write 300 dpi explicitly** into the JPEG JFIF density fields
  (and the EXIF `XResolution`/`YResolution` with `ResolutionUnit=2`). Prodigi's
  system reads uploaded file dimensions to decide which products to offer, so
  correct metadata is functional, not cosmetic. Pillow:
  `img.save(path, "JPEG", quality=95, subsampling=0, dpi=(300, 300), icc_profile=srgb_bytes)`.
- **Bleed: generate the overscan you already need for crop-based artefact
  removal, and keep 3 mm of it.** 3 mm at 300 dpi = 35 px per edge, so A2 with
  bleed is 5031 × 7086. Prodigi says its Print API handles bleed automatically,
  so the safe play is to ship the exact trim size (4961 × 7016) and let the API
  add bleed — but **confirm this per product**, because getting it wrong means a
  white hairline on one edge of every print you sell.
- **Keep nothing in the file that identifies the pipeline.** Strip all EXIF except
  resolution and ICC. Generative-AI provenance metadata (C2PA, or the
  `Software` tag) in a file you ship to a marketplace is a disclosure decision,
  not a technical one — see the licensing research in this set.

### Gaps

- **No source found for Prodigi's maximum file size**, nor for a stated minimum
  dpi (only "300 is ideal"). Both matter and should be confirmed directly.
- **No Gelato wall-art-specific file spec found** — the only Gelato colour
  statement I located is in a DTG apparel article.
- No source on whether Prodigi accepts TIFF for fine-art giclée specifically.
- I found nothing on whether any UK POD printer rewards 16-bit input.

---

## Measured throughput and cost on specific GPUs

### Takeaway

The published throughput data for FLUX.1 schnell is poor and largely uncited. The
most usable figures are **~1.8 s/image on an RTX 4090 and ~1.0 s/image on an H100
SXM** at 4 steps, which implies roughly **47,000 images/day/4090**. I could not
find any credible published figures for **A40, L40S, A100 40 GB or A100 80 GB**,
nor any batch-size or precision-resolved throughput table. The one hard
quantisation datapoint is NVIDIA's own: **TensorRT INT8 and FP8 give 1.72x and
1.95x over torch.compile FP16** (on RTX 6000 Ada, for Stable Diffusion, not
schnell).

### Cited Findings

- "At **33 schnell images per minute**, a single 4090 pumps out **~47,000 images in
  a 24-hour cycle**"; "the 4090 runs schnell in **1.8 s per image**" (≈0.56 img/s) —
  [packet.ai: Flux Image Generation GPU Guide 2026](https://packet.ai/blog/flux-image-generation-gpu-vram-requirements)
  **[low-reliability SEO source; no batch size, resolution, step count or
  precision stated — the figures are not reproducible as published]**
- "The **H100 SXM** generates approximately **60 FLUX.1 Schnell images per
  minute at 1.0 s per image**"; "H100 generates FLUX Schnell in approximately
  1-2 seconds" —
  [spheron.network: ComfyUI on GPU Cloud 2026](https://www.spheron.network/blog/comfyui-gpu-cloud-2026/);
  [spheron.network: Best GPU for AI Image Generation 2026](https://www.spheron.network/blog/best-gpu-ai-image-generation-2026/)
  **[low-reliability SEO sources; same caveats]**
- "For small-batch interactive workloads the 4090 will land within 10 percent of
  an H100 on performance per user at roughly **one-eighth the rental cost**" —
  [packet.ai](https://packet.ai/blog/flux-image-generation-gpu-vram-requirements)
  **[low-reliability SEO source]**
- "FLUX Schnell at 4 steps takes approximately **6-10 seconds**" —
  [jarvislabs.ai: Best GPU for FLUX](https://jarvislabs.ai/ai-faqs/best-gpu-for-flux)
  **[this directly contradicts the 1.0-1.8 s figures above; jarvislabs does not
  state which GPU, so the figures may not be comparable. Report the conflict.]**
- A 4090 FP8 production setup for schnell and dev is documented at a consumer
  level — [GIGAGPU: FLUX.1 on RTX 4090 24 GB](https://gigagpu.com/rtx-4090-24gb-flux-setup/)
  **[low-reliability SEO source]**
- A live 4090 schnell demo was run and discussed on Hacker News —
  [HN item 42093652](https://news.ycombinator.com/item?id=42093652)
- **SaladCloud published a schnell cost benchmark headlined "5243 images per
  dollar"** — [blog.salad.com/flux1-schnell](https://blog.salad.com/flux1-schnell/).
  **I could not retrieve this page (HTTP 404 on both the blog URL and the
  docs.salad.com benchmark path).** The 5,243 img/$ figure is from the search
  result title only; the GPU, resolution, steps and batch size behind it are
  unknown to me. **Do not report this number as verified.**
- **NVIDIA (primary, vendor):** "TensorRT INT8 and FP8 quantization achieve
  **1.72x and 1.95x speedups** on NVIDIA RTX 6000 Ada GPUs compared to native
  PyTorch's torch.compile running in FP16. The additional speedup of FP8 over
  INT8 is primarily attributed to the quantization of multi-head attention (MHA)
  layers" —
  [NVIDIA: TensorRT accelerates Stable Diffusion nearly 2x faster with 8-bit PTQ](https://developer.nvidia.com/blog/tensorrt-accelerates-stable-diffusion-nearly-2x-faster-with-8-bit-post-training-quantization)
- **torch.compile alone gives a 23% speedup "while leaving the generated images
  unchanged"** on FLUX.1[dev]; it is "near-lossless... but the benefits are
  limited" —
  [Pruna AI: Unlock 2.7x Speedup for FLUX.1[dev] — torch.compile vs TensorRT vs Pruna](https://www.pruna.ai/blog/comparison-flux-torch-compile-tensor-rt-pruna)
- **Critical caveat, and the most actionable finding in this section:**
  "quantization alone is not enough to achieve a speed up; when used directly, the
  quantized model **can be slower** because PyTorch is not optimized for 8-bit
  operations"; "quantization levels like INT8 and NF4 are **slower than FP16** on
  any CUDA GPU when weights are dequantized to FP16 for computation"; FP8 and
  fp8_static speedups "require **Ada Lovelace or newer (RTX 4090+)**" —
  [NVIDIA TensorRT blog](https://developer.nvidia.com/blog/tensorrt-accelerates-stable-diffusion-nearly-2x-faster-with-8-bit-post-training-quantization);
  [virtuslab: Diffusion models quantization benchmark](https://virtuslab.com/blog/ai/diffusion-models-quantization-benchmark)
- **Quantisation quality, measured:** "Flux-1.dev achieved a mean **LPIPS score of
  0.11 with MXFP8** quantization and **0.44 with NVFP4**" (lower is better) —
  [PyTorch blog: Faster Diffusion on Blackwell — MXFP8 and NVFP4 with Diffusers and TorchAO](https://pytorch.org/blog/faster-diffusion-on-blackwell-mxfp8-and-nvfp4-with-diffusers-and-torchao/)
- On Blackwell, "NVFP4 and TeaCache provide a good tradeoff between speedup and
  output quality, delivering approximately **2x speedups each**" —
  [Pruna AI](https://www.pruna.ai/blog/comparison-flux-torch-compile-tensor-rt-pruna);
  NVIDIA has published NVFP4 scaling work for the FLUX.2 generation on Blackwell
  data-centre GPUs —
  [NVIDIA: Scaling NVFP4 inference for FLUX.2 on Blackwell](https://developer.nvidia.com/blog/scaling-nvfp4-inference-for-flux-2-on-nvidia-blackwell-data-center-gpus)
- fp8 model weights for FLUX are distributed on the Hub —
  [wangkanai/flux-dev-fp8](https://huggingface.co/wangkanai/flux-dev-fp8)

### Inferences

- **The quantisation quality/throughput answer for schnell:** FP8 on Ada or newer
  (4090, L40S, H100) is the right choice — it is the format with both a real
  speedup path (TensorRT, ~1.95x) and a small quality cost. **INT8 and NF4 are
  the wrong choice for throughput**: the sources are explicit that they are
  often *slower* than FP16 because of dequantisation overhead, and they exist for
  VRAM reduction (running FLUX on 8-12 GB cards), not for speed. NF4 is a
  consumer-VRAM accommodation and has no place in a rented-GPU batch job.
  The LPIPS 0.11 (MXFP8) vs 0.44 (NVFP4) gap is a direct measurement that 4-bit
  costs real fidelity while 8-bit does not — and for a product where the image
  *is* the product, 0.44 LPIPS is not acceptable.
- **The whole throughput literature here is unusable for cost modelling** and the
  report should say so plainly. None of the figures state batch size, resolution,
  step count or precision together. The 6-10 s (jarvislabs) vs 1.0-1.8 s
  (packet/spheron) conflict is almost certainly a batch-size-1-with-model-loading
  vs steady-state-batched difference, but nobody says. **You must benchmark your
  own configuration**; it is a half-day of work and will be more reliable than
  anything published.
- **Expected order of magnitude**, as a planning figure only: at 4 steps,
  1 MP, bf16, batch 4, torch.compile, a 4090 should land around 0.5-0.8 img/s
  and an H100 around 1.2-2.0 img/s. One million images is therefore roughly
  **350-550 GPU-hours on 4090-class hardware**. Label this as an estimate derived
  from contested community figures, not a benchmark.
- **The serving-stack question has a clear answer from first principles, and I
  found no benchmark contradicting it:** use **raw diffusers in a batched loop in
  a single long-lived process**, with the text encoders and transformer resident,
  `torch.compile` applied once at startup, static batch shapes (one shape per
  aspect ratio, so compile once per ratio — this is a real argument for grouping
  work by format), and the VAE decode and PNG/JPEG encode moved to worker threads
  so the GPU never waits on I/O.
  - **ComfyUI API is the wrong tool for a batch job**: it is built around a
    node-graph re-execution model with per-request validation and caching
    designed for interactive use, and it adds a web server, a queue and graph
    overhead to every image. Use it for designing the workflow, then port.
  - **vLLM-style continuous batching does not apply.** Continuous batching solves
    *variable-length autoregressive decode* — requests finishing at different
    times. Diffusion at a fixed 4 steps has uniform, known-length work per item,
    so simple static batching already achieves full GPU utilisation. There is
    nothing for continuous batching to recover.
  - The real bottlenecks at this scale are **not** the denoising loop: they are
    text encoding (T5-XXL on 256 tokens is not free — cache encodings, since your
    taxonomy reuses prompt fragments heavily and many cells share a `prompt_2`
    prefix), VAE decode at 35 MP after upscaling, image encoding, and object-store
    PUT latency. Budget engineering effort accordingly.

### Gaps

- **No published FLUX schnell throughput for A40, L40S, A100 40 GB, A100 80 GB.**
  Nothing credible found for any of them.
- **No batch-size scaling curve** for schnell on any GPU.
- **The SaladCloud benchmark is unretrievable** (404), so the one images-per-dollar
  figure in circulation cannot be verified or contextualised.
- No published throughput comparison of diffusers-loop vs ComfyUI API vs a custom
  server for diffusion batch jobs. My recommendation above is reasoned, not
  measured.
- The NVIDIA 1.72x/1.95x figures are for **Stable Diffusion on RTX 6000 Ada**, not
  schnell. Transfer with caution.

---

## Structuring the RunPod job

### Takeaway

For a multi-million-image batch run the answer is **pods, not serverless**, on
**community/spot for the generation stage** with aggressive checkpointing, because
the job is continuously busy and serverless charges a per-second premium to buy
scale-to-zero that a saturated batch job never uses. RunPod's own documentation
supports launching pods via API for exactly this shape of work.

### Cited Findings

- "RunPod's billing is usage-based — down to the second on serverless, and
  minute-by-minute on full pods... serverless eliminates idle costs but charges a
  premium per compute-second, while pods offer lower hourly rates but charge
  continuously while running" —
  [theneuralbase: Pods vs Serverless](https://theneuralbase.com/runpod/qna/runpod-pods-vs-serverless-comparison/)
  **[low-reliability SEO source]**
- The crossover: "for a model that runs 5 minutes per hour, Serverless costs ~8x
  less"; "for a model running 50 minutes per hour, **Pods cost less** despite idle
  time"; "**Pods suit batch processing**, model training, and always-available
  APIs" —
  [theneuralbase: Pods (persistent VMs) + Serverless](https://theneuralbase.com/runpod/learn/beginner/pods-persistent-vms-serverless/);
  [theneuralbase: When to choose which](https://theneuralbase.com/runpod/learn/advanced/when-to-choose-which/)
  **[low-reliability SEO source]**
- "**Community/spot is cheaper than either, but only for checkpointed,
  eviction-tolerant batch work** — never for customer-facing APIs" —
  [theneuralbase: Endpoint Architecture Decision Framework](https://theneuralbase.com/runpod/learn/advanced/decision-framework/)
  **[low-reliability SEO source]**
- "For pure batch jobs with no external trigger, **using the API to launch a pod
  is straightforward**" — RunPod's own guidance on API-scheduled jobs —
  [RunPod: AI on a Schedule — Using Runpod's API to Run Jobs Only When Needed](https://www.runpod.io/articles/guides/ai-on-a-schedule)
  **[RunPod's own site — closest to primary here]**
- Serverless workers "spin up on-demand, execute your code, and shut down
  immediately: you pay only for execution time plus a small per-second overhead" —
  [theneuralbase](https://theneuralbase.com/runpod/learn/beginner/pods-persistent-vms-serverless/)
- Further production-configuration discussion —
  [markaicode: Best RunPod Setup for Production](https://markaicode.com/best/best-runpod-configuration-production-guide/);
  [markaicode: 5 RunPod Production Use Cases](https://markaicode.com/usecases/runpod-use-cases-production-workflows/);
  [RunPod Review 2026](https://earnifyhub.com/learning-guides/runpod-review-2026)
  **[low-reliability SEO sources]**

### Inferences — recommended job architecture

Engineering design, not cited. Note this must be reconciled with whatever
`tshirt/ACCESS.md` records about how RunPod and R2 are actually wired in this
environment — I have not read that file as part of this research task.

- **Work unit: a shard, not an image.** Pre-compute the entire render list (every
  selected taxonomy cell, with its seed, prompt, dimensions and output key) into
  an immutable manifest — a Parquet file per shard, ~5,000 rows each — written to
  R2 *before* any GPU starts. This is the single most important design decision:
  it makes the run idempotent, resumable, auditable, and independently
  re-renderable, and it means the space-filling selection (next section) happens
  once, deterministically, on a CPU.
- **Determinism as the checkpointing mechanism.** Derive the seed from a hash of
  the cell identity: `seed = blake2b(cell_id) mod 2**31`. Then *any* image can be
  regenerated exactly, and "checkpointing" reduces to recording which output keys
  exist. No GPU state needs saving at all — which is what makes spot eviction
  cheap rather than catastrophic.
- **Shard claim protocol.** A tiny coordinator (SQLite over a single small
  always-on instance, or a Postgres table, or even R2 conditional PUTs on a
  `claims/{shard}.json` key using `If-None-Match`) hands out shards with a lease
  and a visible timeout. A worker that dies loses its lease; the shard is re-offered
  after the timeout. Workers write results and then mark the shard done. This is
  the standard pattern and it tolerates eviction, OOM and network partition
  without special handling.
- **Resume = list what exists.** On startup a worker lists its shard's output
  prefix in R2 and skips keys already present. At 5,000 images per shard a LIST is
  one or two round trips. Do not keep a separate progress file in sync with
  object storage; let the storage be the truth.
- **Never let a pod idle.** Three layers, because the failure mode is expensive:
  1. The worker process exits with status 0 when the coordinator reports no
     shards left.
  2. The container's entrypoint is `python worker.py; runpodctl stop pod $RUNPOD_POD_ID`
     — the pod stops itself the moment the process exits, for any reason.
  3. A **watchdog outside RunPod** (a cron on your own box, or a scheduled task in
     this session) polls the RunPod GraphQL API every 15 minutes and terminates
     any pod whose shard-completion counter has not advanced in 30 minutes. This
     catches the case where the worker hangs rather than exits, which is the one
     that actually costs money.
  Also set a **spending cap** on the RunPod account as a backstop — a hung GPU pod
  is roughly £0.30-£2.00/hour, so a forgotten weekend is £50-£350.
- **Stage split across machine types.** Generation is GPU-bound and belongs on
  community/spot 4090s or L40S. **Upscaling with a non-diffusion model and all the
  print-prep (palette mapping, crop, JPEG encode, ICC embed) is cheap and should
  not run on a rented H100** — run the Lanczos/print-prep stage on CPU instances
  or alongside generation on the same pod as a background thread pool, whichever
  profiles better. The quality gate (next section) is mostly CPU and small-model
  work and likewise should not occupy a generation GPU.
- **Write to R2 directly from the worker**, with multipart PUTs, and never stage
  more than a few hundred images on the pod's local disk — spot pods lose their
  disk on eviction. Per `CLAUDE.md`, the bucket convention is one R2 bucket per
  eBay account, so the wall-art equivalent of `tshirt-m12k` needs establishing
  before the run, not during it.

### Gaps

- **No published RunPod pricing figures retrieved** — the pricing page I found was
  a third-party aggregator I did not fetch. Per-hour costs for 4090/L40S/H100 on
  community vs secure cloud are **not** in these notes and must be read off
  RunPod's own pricing page at planning time.
- No source on RunPod spot eviction *rates*, which is the key input to deciding
  shard size. Smaller shards cost more coordination; larger shards lose more work
  per eviction. Without an eviction rate this is unmodellable; start at 5,000 and
  measure.
- Nothing found on RunPod-specific checkpoint/resume tooling; the pattern above is
  general-purpose.

---

## Automated quality gating at millions-of-images scale

### Takeaway

Build a **cascade**, cheapest first, so that the expensive judges only ever see a
small fraction of images. The well-sourced components are the LAION aesthetic
predictor (with 4.5 / 5.0 / 6.0 / 6.5 as the thresholds actually used in
published practice) and CLIP-embedding classifiers (95% accuracy on CIFAKE with a
lightweight head). The cheap statistical gates — palette conformance, edge energy,
OCR — are unpublished but trivially implementable and will catch most of your
actual failure modes.

### Cited Findings

- The LAION Aesthetics Predictor is a CLIP-based model trained to "predict the
  rating people gave when they were asked 'How much do you like this image on a
  scale from 1 to 10?'" —
  [The Algorithmic Gaze of Image Quality Assessment: An Audit and Trace Ethnography of the LAION-Aesthetics Predictor, arXiv 2601.09896](https://arxiv.org/html/2601.09896v4);
  also published at [ACM DL 10.1145/3805689.3806462](https://dl.acm.org/doi/10.1145/3805689.3806462)
  **[arXiv ID unverified beyond search result]**
- **Thresholds actually used:** the LAION-Aesthetics dataset tiers are **4.5+
  (~1.2 B images)** and **6.5+ (~625 k images)**; audits "typically focus on...
  an aesthetics score threshold of **6.5**, which researchers often use to
  represent high-quality images" —
  [arXiv 2601.09896](https://arxiv.org/html/2601.09896v4)
- A two-stage threshold pattern from model training practice: "images with
  aesthetic scores above **5.0** are retained during pre-training, while a
  stricter threshold of **6.0** is used during fine-tuning to ensure higher image
  quality"; "low scores often correspond to visually unappealing renders such as
  poorly lit scenes or images dominated by artifacts" —
  [HiDream-I1, arXiv 2505.22705](https://arxiv.org/pdf/2505.22705);
  [BlendFusion: Scalable Synthetic Data Generation for Diffusion Model Training, arXiv 2604.09022](https://arxiv.org/pdf/2604.09022)
  **[second ID unverified beyond search result]**
- LAION-5B itself is filtered and indexed by "compress[ing] the images into a
  large k-NN index of CLIP embeddings using FAISS search algorithm with
  approximate similarity", and anchor-dataset filtering was used to extract
  domain subsets from billions of images —
  [From LAION-5B to LAION-EO, arXiv 2309.15535](https://arxiv.org/pdf/2309.15535)
- **CLIP embeddings + a lightweight classifier reach 95% accuracy and F1 on the
  CIFAKE benchmark for AI-generated-image detection "without any end-to-end
  fine-tuning"** —
  [CLIP Embeddings for AI-Generated Image Detection: A Few-Shot Study with Lightweight Classifier, arXiv 2505.10664](https://arxiv.org/pdf/2505.10664)
- Perceptual classifiers built on features from image-quality-assessment models
  detect generative images and "generalize well to images from unseen generative
  models, owing to their ability to capture the distributions of real images" —
  [Perceptual Classifiers: Detecting Generative Images using Perceptual Features, arXiv 2507.17240](https://arxiv.org/pdf/2507.17240)
- A survey of the detection field —
  [Methods and Trends in Detecting Generated Images: A Comprehensive Review, arXiv 2502.15176](https://arxiv.org/html/2502.15176v1)
- Degraded-input handling is a known problem, addressed by adding "an enhancement
  module and a perception module... a lightweight **three-class classifier** [that]
  identifies whether a patch is **blurry, compressed, or intact**" —
  [arXiv 2502.15176](https://arxiv.org/html/2502.15176v1). This is directly
  reusable as a blur gate.
- Open "AI slop" detectors exist as ensembles of Hugging Face classifiers, with
  models "trained on a broad mix of recent generators (Midjourney v6+, Stable
  Diffusion 3.5, GPT-4o images, etc.)" —
  [ai-slop-detector (GitHub)](https://github.com/voidcommit-afk/ai-slop-detector);
  commercial equivalent at [Sightengine AI image detector](https://sightengine.com/detect-ai-generated-images)
- The term and its definition: "AI slop means low-quality digital content produced
  in quantity by artificial intelligence" —
  [Ultralytics glossary: AI slop](https://www.ultralytics.com/glossary/ai-slop)
- Prior work on detecting generated faces in the wild, as an example of the
  in-the-wild detection problem —
  [Finding AI-Generated Faces in the Wild, arXiv 2311.08577](https://arxiv.org/pdf/2311.08577)

### Inferences — the cascade

Design and cost estimates are mine; the per-image costs are order-of-magnitude
engineering estimates, not measurements, and should be labelled as such.

**Stage 0 — pure statistics, ~5-20 ms CPU, runs on 100% of images.** Nothing to
cite; all trivially implementable with NumPy/OpenCV.
- **Palette conformance**: mean and 95th-percentile ΔE2000 from each pixel to its
  nearest palette entry. Rejects colour drift and off-brief output. This is
  *your single best gate* because your taxonomy specifies the palette, so you have
  ground truth — almost nobody else has this luxury.
- **Edge-band statistics**: variance and mean of the outer 2% ring, per edge.
  Catches simulated paper edges, vignettes, borders, frames, and letterboxing.
- **Corner high-frequency energy**: catches signatures and stray marks, which
  diffusion models place in corners.
- **Global blur / edge energy**: variance of Laplacian, plus a radially-averaged
  FFT power-spectrum slope. The slope is the better signal for "soft mush" and
  is also the right detector for the >1.5 MP degradation mode.
- **Colour-histogram entropy and distinct-colour count**: directly validates
  "exactly three flat spot inks" for the flat styles.
- **Mean saturation and black/white clipping**: catches the blown-out and the
  muddy.

**Stage 1 — OCR for unwanted text, ~30-100 ms, runs on 100%.**
- **PaddleOCR** is the right choice for throughput (it is designed for batched
  server use and has a lightweight detection-only mode). Run **detection only** —
  you do not need to read the text, only to know glyph-like regions exist. Reject
  on total detected text area above ~0.2% of the image, or any detection with
  confidence above ~0.6.
- **Tesseract** is slower and much worse on stylised/garbled text — the exact
  case you need to catch. **EasyOCR** is accurate but heavy. Use PaddleOCR
  detection as the gate and only escalate to recognition on flagged images if you
  want to log *what* the text said.
- This gate also doubles as the watermark detector for text-form watermarks, which
  are the common kind.

**Stage 2 — small-model scoring on GPU, ~5-15 ms batched, runs on survivors.**
- **LAION aesthetic predictor** (the CLIP ViT-L/14 + MLP head,
  `improved-aesthetic-predictor`): one CLIP forward you are going to do anyway.
  Given the published tiers, **5.0 is the "not broken" floor and 6.0-6.5 is the
  "actually good" bar** ([arXiv 2601.09896](https://arxiv.org/html/2601.09896v4),
  [arXiv 2505.22705](https://arxiv.org/pdf/2505.22705)). For a *sold* catalogue I
  would gate at ~5.5 and *rank* by score rather than hard-gating at 6.5, because
  the predictor is known to be biased toward a particular photographic
  aesthetic and will systematically under-score exactly the flat graphic styles
  (linocut, single-weight line art, cyanotype) that your taxonomy wants. The
  audit paper's whole point is that the predictor encodes a specific gaze; do not
  let it quietly delete your minimalist styles. **Calibrate the threshold
  per-style**, from the score distribution of the first 10k images of that style.
- **SigLIP (or CLIP) prompt adherence**: cosine similarity between the image
  embedding and the text embedding of the *subject clause only*. Gates "the model
  rendered the wrong animal". Free once you have the embedding. Use a
  per-subject threshold set from the distribution, not an absolute one — absolute
  CLIP similarities are not comparable across prompts.
- **Reuse one embedding for three jobs**: aesthetic score, prompt adherence, and
  the dedup index. Embed once, at Stage 2, and carry the vector forward.

**Stage 3 — near-duplicate rejection.** See the next section.

**Stage 4 — VLM judging, on a sample only.** A VLM at even £0.001/image is
£1,000 per million, and it is the only stage whose cost scales badly. Use it on
(a) a 0.5-1% random audit sample to validate that the cheap gates are catching
what you think, and (b) the small shortlist you are about to actually list for
sale. Do not put a VLM in the per-image path.

**Expected economics:** Stages 0-2 should cost well under £0.0001/image and run at
GPU-generation speed or faster, meaning the gate is a rounding error against
generation. Stage 4 is the only part that needs rationing. The report should state
plainly that **gating is cheap and there is no excuse for shipping ungated output
at this scale** — which is the direct lesson of the 89%-near-duplication figure in
`CLAUDE.md`.

### Gaps

- **No per-image cost or throughput figures found** for any OCR engine, aesthetic
  predictor or VLM judge in a bulk-filtering context. All the cost estimates above
  are mine and uncited.
- **No published logo/watermark detector** suitable for this turned up. The
  literature I found is about *AI-generated-image* detection, not watermark
  detection. There is a gap here; the OCR-detection proxy is my workaround.
- No published work I found specifically on gating *generative output for
  commercial sale*. The "AI slop" detection literature is aimed at identifying
  AI-generated content as such (i.e. detecting that it is AI) — **which is the
  opposite of what you need**, since all your images are AI and you need to rank
  them by quality. This is an important distinction the report should make: the
  "AI slop detector" tools are not quality graders and will not help you.
- The LAION-Aesthetics audit paper's specific findings about *which* image
  properties the predictor favours were not retrievable in detail from the search
  result; worth fetching in full before setting thresholds.

---

## Near-duplicate detection at several-million scale

### Takeaway

The published benchmarks are unambiguous: **embedding-based methods beat pHash and
SSIM by very large margins** (0.12 vs much higher Recall@1 for pHash on scene
duplicates; 76.5% vs 17.6% vs 35.3% recall at a fixed review budget for
embeddings vs pHash vs SSIM). The published near-duplicate cosine thresholds
cluster at **0.93-0.95**. The practical pipeline is a **two-tier cascade**: pHash
for exact/trivial duplicates (nearly free), then CLIP-or-DINOv2 embeddings in an
HNSW index for the near-duplicate judgement.

### Cited Findings

- **Semantic deduplication with CLIP image embeddings and FAISS nearest-neighbour
  search, with "pairs satisfying similarity > 0.95 treated as near-duplicates"**;
  "for CLIP/DINO features, image embedding similarity threshold is **s ≥ 0.93**" —
  [Benchmarking Pretrained Vision Embeddings for Near- and Duplicate Detection in Medical Images, arXiv 2312.07273](https://arxiv.org/html/2312.07273v2)
- **pHash's failure is quantified: "pHash cannot retrieve scene duplicates, with
  only 0.12 Recall@1 and 0.29 even at K=100 compared to DINOv2"** —
  [arXiv 2312.07273](https://arxiv.org/html/2312.07273v2)
- **On the CleanPatrick benchmark: "embedding-based methods (SelfClean) maintained
  stable performance while pHash and SSIM each lost 1-2 AUROC points due to
  high-scoring pairs that are not duplicates"; and "for duplicates outside the
  candidate pool, embedding-based approaches recovered 76.5% recall at a review
  budget of k=5,000, compared to 17.6% for pHash and 35.3% for SSIM"** —
  [CleanPatrick: A Benchmark for Image Data Cleaning, arXiv 2505.11034](https://arxiv.org/pdf/2505.11034)
- **DINOv2 vs DINOv1 is a wash and sometimes worse:** "DINOv2 outperformed DINOv1
  by a small margin for duplicate detection"; however "DINOv2 showed **lower**
  performance compared to DINOv1 by a margin of **0.1-0.3 AUC for near-duplicate
  detection**" —
  [arXiv 2312.07273](https://arxiv.org/html/2312.07273v2). **Do not assume DINOv2
  is automatically the best embedding; test it against CLIP on your own styles.**
- **A published cascade exactly matching the recommended design:** "Fast
  Near-Duplicate Image Retrieval with **Zero-Training Cascades: pHash → CLIP** vs
  ANN Frontiers on the Airbnb Dataset" —
  [SSRN 5407584](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5407584)
- LAION-scale precedent: "the images can be compressed into a large k-NN index of
  CLIP embeddings using FAISS search algorithm with approximate similarity" —
  [arXiv 2309.15535](https://arxiv.org/pdf/2309.15535)
- Embeddings "stored in a vector database using the FAISS backend" is the standard
  implementation —
  [arXiv 2312.07273](https://arxiv.org/html/2312.07273v2)
- Geospatial-dataset deduplication at scale uses the same embedding-plus-threshold
  approach —
  [Data Leakage Detection and De-duplication in Large Scale Geospatial Image Datasets, arXiv 2304.02296](https://arxiv.org/pdf/2304.02296)
- An open benchmark comparing dedup methods —
  [ecolink-image-dedup-benchmark (GitHub)](https://github.com/nngtkhngoc/ecolink-image-dedup-benchmark)
- DINOv2 itself —
  [DINOv2: Learning Robust Visual Features without Supervision, arXiv 2304.07193](https://arxiv.org/html/2304.07193v2)
- A benchmark-contamination/deduplication writeup using these methods —
  [RS-47 Benchmark Contamination and Deduplication](https://w-copper.github.io/2026/06/rs-47-benchmark-contamination-and-deduplication/)
  **[unverified beyond search result]**

### Inferences — the practical pipeline for 5 M images

Arithmetic is mine; thresholds are the cited ones.

**Tier 1 — pHash, exact and trivial duplicates.** 64-bit pHash, stored in a
SQLite/Postgres table, exact-match on the hash plus a BK-tree or Hamming-distance
≤ 4 lookup. Cost: ~3 ms/image CPU, **8 bytes per image** (40 MB for 5 M). Catches
re-renders of the same seed and genuinely identical output. Do not expect it to do
more; the cited Recall@1 of 0.12 on scene duplicates is the measured ceiling.

**Tier 2 — embeddings + HNSW.** This is where the real work happens.
- **Embedding**: CLIP ViT-L/14 (768-d) — the same forward pass you already do for
  the aesthetic predictor and prompt adherence, so marginal cost is zero. Test
  DINOv2 ViT-L/14 against it on a hand-labelled set of 500 pairs from your own
  styles, given the cited DINOv2/DINOv1 inconsistency. L2-normalise so cosine =
  inner product.
- **Index**: **HNSW** (via FAISS `IndexHNSWFlat`, or Qdrant if you want a server).
  Concrete parameters: `M = 32`, `efConstruction = 200`, `efSearch = 128`.
  - **Why HNSW over IVF-PQ**: you are doing *high-recall threshold queries near
    1.0 similarity*, where PQ's quantisation error is comparable to the margin
    you are trying to measure. HNSW on full-precision vectors has no such error.
  - **Why not ScaNN**: excellent, but a heavier dependency and tuned for
    recall@k on large-scale retrieval rather than threshold queries; no advantage
    here.
  - **Storage**: 768-d float32 = 3,072 B/image → **15.4 GB for 5 M vectors**, plus
    HNSW graph overhead at `M=32` of roughly 2× the ID size, say ~1-2 GB. Total
    ~18 GB — **fits in RAM on a single ordinary machine.** Use float16 (1,536 B)
    to halve it to ~8 GB if you want headroom; the precision loss is far below the
    0.93 threshold's margin.
  - **Build time**: HNSW construction at these parameters runs at roughly
    5,000-20,000 vectors/s on a many-core CPU, so 5 M is **5-20 minutes**. Not a
    bottleneck. (Estimate, uncited.)
- **Incremental operation**: HNSW supports insertion, so run dedup *online* as
  part of the gate — query, and if nothing within threshold, insert. This is the
  important architectural point: **dedup must be a gate, not a post-hoc audit**,
  or you will have paid to upscale and store millions of duplicates before you
  find out.

**Thresholds — and the distinction you specifically asked about.** The cited
numbers give you the "same design" boundary; the "same subject, different design"
boundary is not in the literature and must be calibrated. My reading of the
evidence:
- **cosine ≥ 0.95** — "same design". Reject outright.
  ([arXiv 2312.07273](https://arxiv.org/html/2312.07273v2))
- **0.93 ≤ cosine < 0.95** — borderline; the lower cited CLIP/DINO threshold.
  ([arXiv 2312.07273](https://arxiv.org/html/2312.07273v2)) Treat as reject for a
  commercial catalogue, where the cost of a false reject (you render another) is
  trivial and the cost of a false accept (a near-duplicate listing) is the
  documented 89%-near-duplication failure.
- **~0.85-0.93** — probably "same subject, different design". This band is
  **where your value is**, and it is also where no published threshold exists.
- **Calibrate it properly and cheaply:** hand-label 300-500 pairs sampled across
  the 0.80-0.98 range — "would a buyer see these as the same print?" — then pick
  the threshold at your chosen precision. This is a few hours of work and is the
  only way to get a defensible number. **Report the threshold as calibrated, not
  as a literature value.**
- **Critical caveat on CLIP for this task:** CLIP embeddings are
  *semantically* driven, so two images of a wren in different styles may sit
  closer together than two different compositions in the same style. That is the
  opposite of what you want when the style axis is doing the differentiating.
  **Consider a composite distance**: CLIP cosine for subject identity, plus a
  separate low-dimensional *style* signature (Gram-matrix statistics from an early
  VGG/CLIP layer, or simply the palette histogram and edge-orientation histogram
  you already computed in Stage 0). Reject only when images are close on *both*.
  This is my design, unsourced, and it is the point where this pipeline most needs
  an experiment.

**Where SSIM fits: nowhere.** At 35.3% recall vs 76.5% for embeddings
([arXiv 2505.11034](https://arxiv.org/pdf/2505.11034)) and O(n²) pairwise cost
with no index, SSIM is unusable at 5 M. Mention it only to dismiss it.

### Gaps

- **No published threshold for the "same subject, different design" boundary.**
  This is the distinction the business actually turns on and the literature does
  not address it. It must be calibrated in-house.
- **No cost or latency benchmarks** for FAISS/Qdrant/ScaNN at the 5 M scale with
  threshold queries in the sources I found; my storage and build-time figures are
  computed or estimated, not cited.
- No published comparison of wHash or dHash against pHash in these benchmarks —
  only pHash was evaluated. Given pHash's measured weakness, the other hashes are
  unlikely to change the conclusion.
- No published work on style-aware (as opposed to semantic) near-duplicate
  detection that I could find.

---

## Choosing a well-spread subset of a large combinatorial space

### Takeaway

The formal machinery exists and is mature, but **it is almost entirely
un-applied to prompt space** — I found no paper applying covering arrays, Latin
hypercubes or Sobol sequences to image-prompt selection. What does exist and is
directly usable: **greedy MAP inference for DPPs at O(Nk³)** (and faster variants),
**k-center / farthest-point greedy**, and **the Vendi score family as the diversity
metric**, including a **Conditional Vendi Score explicitly designed for
prompt-aware diversity evaluation**. The practical answer for N×M×P cell selection
is a **two-stage design: a t-wise covering array for guaranteed axis coverage,
then farthest-point greedy in embedding space to kill the visual near-duplicates
the combinatorial design cannot see.**

### Cited Findings

**Space-filling and combinatorial design (mature, but generic):**
- "Space-filling designs spread out points with the aim of encouraging a diversity
  of data, with the thinking that a spread of training examples will ultimately
  yield fitted models which smooth/interpolate/extrapolate best" —
  [Surrogates, Ch. 4: Space-filling Design](https://bookdown.org/rbg/surrogates/chap4.html)
- Latin hypercube design "is a stratified sampling technique in which each
  dimension is partitioned into N equally sized intervals, with one sample drawn
  from each interval in every dimension, producing uniform marginal distributions
  and improved space-filling coverage compared with uniform random sampling" —
  [Latin Hypercubes and Space-filling Designs, arXiv 2203.06334](https://arxiv.org/pdf/2203.06334)
- "**Orthogonal arrays and covering arrays have been used for generating
  interaction test suites**... with suites designed to test for **t-way
  interactions** where exhaustive testing may not be feasible" —
  [arXiv 2203.06334](https://arxiv.org/pdf/2203.06334)
- **The projection insight, which is the key one for this problem:** "a reasonable
  approach is to construct designs that are space-filling in the **low
  dimensional projections**... designs constructed to be space-filling in
  two-dimensional projections, randomized orthogonal arrays, and orthogonal
  array-based Latin hypercubes all serving this purpose" —
  [arXiv 2203.06334](https://arxiv.org/pdf/2203.06334)
- Orthogonal sampling compared against LHS for parameter-space coverage —
  [Populations of models, Experimental Designs and coverage of parameter space by Latin Hypercube and Orthogonal Sampling, arXiv 1502.06559](https://arxiv.org/pdf/1502.06559)
- Optimisation of LHS designs and their subprojection properties —
  [Numerical studies of space-filling designs](https://www.researchgate.net/publication/251876634_Numerical_studies_of_space-filling_designs_Optimization_of_Latin_Hypercube_Samples_and_subprojection_properties);
  [Space-filling Latin hypercube designs for computer experiments](https://www.researchgate.net/publication/225560782_Space-filling_Latin_hypercube_designs_for_computer_experiments)
- Nested space-filling designs, relevant if you want a staged rollout where each
  tranche is itself space-filling —
  [Construction of nested space-filling designs, arXiv 0909.0598](https://arxiv.org/pdf/0909.0598)
- Space-filling LHDs under randomisation restrictions (i.e. when some combinations
  are forbidden — directly relevant, since some style×palette cells are invalid,
  e.g. cyanotype is monochrome blue by definition) —
  [arXiv 1305.0182](https://arxiv.org/pdf/1305.0182)

**Diverse subset selection (directly applicable):**
- "Determinantal point processes (DPPs) are well known models for diverse subset
  selection problems, including recommendation tasks, document summarization and
  image search"; "the diagonal elements of the kernel matrix give the marginal
  probability of inclusion for individual elements, whereas the **off-diagonal
  elements determine the 'repulsion' between pairs**" —
  [Towards Deterministic Diverse Subset Sampling, arXiv 2105.13942](https://arxiv.org/html/2105.13942)
- **k-DPPs: fixed-size DPPs — exactly the "choose k cells" formulation** —
  [k-DPPs: Fixed-Size Determinantal Point Processes, Kulesza & Taskar, ICML 2011](https://icml.cc/2011/papers/611_icmlpaper.pdf)
- "A greedy deterministic adaptation of k-DPP... builds the set one item at a
  time, always adding whichever item increases the determinant most, running in
  **O(Nk³)** time and providing provably good approximations" —
  [arXiv 2105.13942](https://arxiv.org/html/2105.13942)
- Faster greedy MAP inference for DPPs —
  [Fast Greedy MAP Inference for Determinantal Point Processes, arXiv 1709.05135](https://arxiv.org/pdf/1709.05135)
- **"K-Center, Facility Location, and Determinantal Point Processes (DPPs) are
  three prominent diversity-based selection strategies. K-Center selects k data
  points to serve as centers of equal-radius balls in the representation space"** —
  [Improving Task Diversity in Label Efficient Supervised Finetuning of LLMs, arXiv 2507.21482](https://arxiv.org/pdf/2507.21482)
- DPPs applied to **text-to-image retrieval diversity across composite
  attributes** — the closest published work to your multi-axis taxonomy problem:
  "large determinants of the relevance and similarity matrices indicate that
  images are relevant and diverse, respectively" —
  [MS-DPPs: Multi-Source Determinantal Point Processes for Contextual Diversity Refinement of Composite Attributes in Text to Image Retrieval, IJCAI 2025](https://www.ijcai.org/proceedings/2025/0207.pdf);
  [arXiv 2507.06654](https://arxiv.org/pdf/2507.06654)
- DPPs used to drive diversity in *generation* (video) via policy optimisation —
  [Diverse Video Generation with Determinantal Point Process-Guided Policy Optimization, arXiv 2511.20647](https://arxiv.org/pdf/2511.20647)
  **[unverified beyond search result]**
- Practitioner treatment of DPPs for recommendation diversity —
  [Diversity in Recommendations — DPP](https://medium.com/data-science-collective/diversity-in-recommendations-determinantal-point-processes-dpp-2427bf1b6324)

**Diversity metrics:**
- "**The Vendi Score is defined as the exponential of the Shannon entropy of the
  eigenvalues of a similarity matrix**"; it is "**reference-free**... does not
  require access to real data"; "higher Vendi Score indicates more dissimilar
  samples and thus greater diversity; it is **upper-bounded by m**, achieved when
  all pairwise similarities are zero" —
  [The Vendi Score: A Diversity Evaluation Metric for Machine Learning, arXiv 2210.02410](https://arxiv.org/pdf/2210.02410);
  [OpenReview version](https://openreview.net/pdf/8d75792c91d71f0a1e1388bd5f193bf220d58a49.pdf)
- **A prompt-aware variant exists and is the most on-point citation in this whole
  section** —
  [Conditional Vendi Score: Prompt-Aware Diversity Evaluation for Generative AI Models and LLMs, arXiv 2411.02817](https://arxiv.org/pdf/2411.02817)
- Diversity metrics compared on synthetic datasets —
  [Measuring Diversity in Synthetic Datasets, arXiv 2502.08512](https://arxiv.org/pdf/2502.08512)
- **A negative result worth reporting:** across 83 synthetic-pretraining
  experiments, "**most diversity scores don't predict synthetic-data quality.
  G-Vendi is the exception**", tested against Vendi Score, mean intra-set cosine
  similarity, and near-duplicate rate on sentence embeddings. G-Vendi computes
  "the entropy of the dataset in **gradient space**" and "strongly correlates with
  how the model performs in unseen distributions (**R² > 0.8**)" —
  [Joël Niklaus, Synthetic Data Playbook update](https://x.com/joelniklaus/status/2060722151385403393)
  **[a social-media post reporting the author's own experiments — treat as a
  practitioner report, not a peer-reviewed result]**;
  G-Vendi originates in [Prismatic Synthesis (NVIDIA Labs)](https://nvlabs.github.io/prismatic-synthesis/)
- Large-scale attribute-grounded instruction synthesis as a precedent for
  axis-combination at millions-of-items scale —
  [From Real to Synthetic: Synthesizing Millions of Diversified and Complicated User Instructions with Attributed Grounding, arXiv 2506.03968](https://arxiv.org/pdf/2506.03968)

### Inferences — the recommended selection procedure

This is the practical answer to "given N subjects, M styles and P palettes, which
of the N×M×P cells do I render". It is my synthesis; the components are cited
above, the combination is not.

**Why neither method alone works, stated plainly for the report.** Combinatorial
designs (covering arrays, LHS, Sobol) guarantee coverage in *axis coordinates* —
every (style, palette) pair appears, every subject appears with several styles.
They are blind to the fact that two different coordinate cells can *render to
nearly the same image*. Embedding-space methods (DPP, k-center, Poisson-disk)
guarantee visual spread but are blind to coverage obligations and cannot run
before you have images. **You need both, in that order.**

**Stage A — t-wise covering array over the taxonomy (pure CPU, before any
render).** Use **pairwise (t=2)**, optionally t=3 for the axes you most care
about. The cited projection insight ([arXiv 2203.06334](https://arxiv.org/pdf/2203.06334))
is the justification: designs that are space-filling in 2-D projections are the
right target, because *adjacent-cell similarity is a pairwise phenomenon*. A
pairwise covering array over 5 axes reduces N×M×P×C×F to roughly
`max(|A_i|·|A_j|)` rows — for N=400 subjects, M=30 styles, P=40 palettes,
C=6 compositions, F=3 formats, full enumeration is 8.64 M cells but a pairwise
array is on the order of **16,000 rows** (≈ 400×40). That is a 540x reduction
with a *guarantee* that every pair of axis values co-occurs at least once.
- Tooling: NIST **ACTS**, or `pict` (Microsoft), or the Python `allpairspy`
  package. All free. For forbidden combinations (cyanotype × a four-colour
  palette; impasto × "flat shadowless"), covering-array generators accept
  **constraints** — and the randomisation-restriction literature
  ([arXiv 1305.0182](https://arxiv.org/pdf/1305.0182)) is the formal treatment.
- **Do not use pairwise alone as the final answer.** Pairwise coverage is a
  *minimum*; you want far more than 16,000 designs. Use it as the *guaranteed
  core*, then expand.

**Stage B — expand by quasi-random sampling over the axis index space.** For the
continuous or orderable axes (palette hue rotation, crop tightness, subject scale,
colour count, line weight), use a **Sobol sequence** rather than uniform random:
it is low-discrepancy, so successive points fill gaps rather than clumping, and —
the property that matters operationally — **it is incremental**, so you can take
the first 100k points today and extend to 500k later and the union is still
well-spread. Halton is simpler but degrades in higher dimensions. Scrambled Sobol
via `scipy.stats.qmc.Sobol(d, scramble=True)` is the right default. **LHS is the
wrong choice here** because an LHS design is fixed-N: you cannot extend it without
redoing it, and your run will be staged.

**Stage C — render a pilot, then prune in embedding space.** Render a sample
(say 50k), embed, and *measure* which axis pairs actually produce visual
separation and which collapse. This step is what converts a nominal taxonomy into
a real one. Concretely: for each axis, compute the mean pairwise embedding
distance between cells differing *only* in that axis. An axis whose
single-variable swap moves the embedding less than the within-cell seed variation
**is not a real axis** and should be merged or redefined. I expect several
palette variants and several "style" nouns to fail this test — and this is exactly
the measurement that would have caught the 89% near-duplication before 424k
listings were uploaded.

**Stage D — farthest-point greedy (k-center) for the final selection.** Given the
embeddings, select k designs by greedy farthest-point traversal: start from a
random point, repeatedly add the candidate maximising the minimum distance to
everything already selected.
- **Why k-center and not DPP**: greedy MAP-DPP is **O(Nk³)**
  ([arXiv 2105.13942](https://arxiv.org/html/2105.13942)), which is fine for
  k in the hundreds and hopeless for k in the millions — k³ at k=10⁶ is
  not a computation. Farthest-point greedy is **O(Nk)** with an HNSW index
  reducing it further, gives a **2-approximation guarantee** for the k-center
  objective, and is *equivalent in spirit* (both are repulsion-driven). k-center
  is also the method named alongside DPP in the LLM-finetuning diversity work
  ([arXiv 2507.21482](https://arxiv.org/pdf/2507.21482)).
- **Reserve DPP for the small, high-value selection**: which 500 designs do you
  actually list and promote. There, k=500 and O(Nk³) is affordable, and DPP's
  ability to trade off *quality* (diagonal) against *diversity* (off-diagonal)
  maps directly onto trading aesthetic score against distinctness. Use k-DPP
  ([Kulesza & Taskar, ICML 2011](https://icml.cc/2011/papers/611_icmlpaper.pdf))
  with the kernel `L_ij = q_i · S_ij · q_j`, where `q_i` is the aesthetic score and
  `S` the embedding similarity.
- **Poisson-disk sampling in embedding space is the streaming equivalent and is
  what you should actually implement**, because it is identical to the dedup gate
  you already need: accept a new design iff its nearest neighbour in the HNSW
  index is farther than radius r. **One index, one radius, serves both dedup and
  space-filling selection.** This is the single most important engineering
  simplification in this section: *the near-duplicate gate IS the space-filling
  design, run online.* Set r from the calibrated threshold in the dedup section.

**Measuring whether it worked.** Report **Vendi Score** on the selected set
([arXiv 2210.02410](https://arxiv.org/pdf/2210.02410)) — it is reference-free,
which suits you since there is no reference catalogue, and it is interpretable as
an effective number of distinct items, upper-bounded by the set size. A set of
100,000 designs with a Vendi score of 2,000 is telling you that you have 2,000
designs and 98,000 copies. That single number is the honest answer to "is this
catalogue actually distinct", and it is directly comparable to the 89%
near-duplication figure. Also report **near-duplicate rate at the calibrated
threshold**, since it is cheap and directly actionable. Note the cited caution
that most diversity scores failed to predict downstream quality in the
synthetic-data setting ([Niklaus](https://x.com/joelniklaus/status/2060722151385403393))
— but that was about predicting *model training* outcomes, not about measuring
catalogue redundancy, which is Vendi's native use.

### Gaps

- **I found no published work applying covering arrays, orthogonal arrays, Latin
  hypercubes, Sobol/Halton sequences, maximin or Audze-Eglais designs to
  prompt-space exploration for image generation.** The combinatorial-design
  literature and the generative-AI literature have not met on this. The
  recommendation above is my synthesis and should be presented as such — it is a
  genuine gap and arguably an opportunity.
- **Nothing found on maximin or Audze-Eglais specifically** beyond their existence
  within the space-filling design literature; no application to this domain.
- **No published diversity benchmark for image catalogues** — Vendi and G-Vendi
  work I found is on text/LLM data or generative-model evaluation, not on
  commercial catalogue redundancy.
- The G-Vendi result is from a practitioner's social-media post about their own
  experiments plus an NVIDIA Labs project page; the 83-experiment study behind it
  was not retrievable as a paper. It is also a *text/LLM* result and its transfer
  to images is unestablished.
- No source on what Vendi score value constitutes "enough" diversity for a
  commercial catalogue. There is no benchmark; you would be setting the first one.

---

## Cross-cutting notes for the report writer

### Takeaway

Three findings cut across every section and should probably be stated once,
prominently, rather than repeated.

### Cited Findings

- **schnell's 256-token T5 limit** is the binding constraint on the entire prompt
  design, and is half of what almost all published FLUX prompting advice assumes —
  [diffusers FluxPipeline docs](https://huggingface.co/docs/diffusers/en/api/pipelines/flux);
  [FLUX.1-schnell model card](https://huggingface.co/black-forest-labs/FLUX.1-schnell)
- **Negation is simply unavailable** on schnell, so every unwanted element must be
  handled by positive description, deterministic post-processing, or rejection —
  [diffusers FluxPipeline docs](https://huggingface.co/docs/diffusers/en/api/pipelines/flux)
- **Apache-2.0** is confirmed on the schnell model card, which is the licensing
  basis for the whole commercial plan —
  [FLUX.1-schnell model card](https://huggingface.co/black-forest-labs/FLUX.1-schnell).
  Per `CLAUDE.md` this is already the standing decision, and nothing found here
  disturbs it.

### Inferences

- **The near-duplicate index is the keystone component.** It serves as the dedup
  gate, the Poisson-disk space-filling selector, and the source of the Vendi-score
  measurement. Build it first, before generating at scale, and make it online
  rather than batch. Everything else in this document is downstream of it.
- **The economics strongly favour cheap-and-gated over expensive-and-trusted at
  every decision point**: 2-4 steps not 8; ~1 MP not 2 MP; DAT/HAT/Lanczos not
  SUPIR; FP8 not NF4; JPEG q95 not 16-bit TIFF; pods-on-spot not serverless;
  statistical gates not VLM judging; k-center not DPP. The exception is the small
  shortlist you actually list for sale, where every one of those decisions should
  flip.
- **The published literature cannot cost this pipeline for you.** The throughput
  numbers conflict, the upscaler timings are uncited, and the RunPod prices are
  not in these notes. A one-day in-house benchmark — 4 GPUs, 5,000 images, the
  full cascade — will produce better numbers than anything cited here, and the
  report should recommend it as the immediate next action rather than presenting
  the community figures as a basis for planning.

### Gaps

- I have not read `tshirt/ACCESS.md`, which `CLAUDE.md` says records how RunPod
  and R2 are actually wired in this environment and which failed routes not to
  retry. The RunPod recommendations above are generic and must be reconciled with
  that file before implementation.
- `CLAUDE.md` states that the wall-art pipeline lives on branch
  `claude/hopeful-rubin-u14pgu` under `wallart/`, with its own stores, buckets and
  compliance rules. These notes were produced without reading that branch, so any
  existing wall-art generation code, prompt templates or bucket conventions there
  are unaccounted for here.
