# ChAAt Demo Video Script

Target length: **1:55–2:00**

Format: 16:9 screencast, 1080p, English narration.

The official CFP says that production quality is not important. A clear narrated screencast is sufficient. Do not show terminals, API keys, email, private paths, or browser tabs.

## Pre-recording setup

1. Run `streamlit run app_demo.py`.
2. Open the app at 100% browser zoom and hide bookmarks.
3. Confirm that **Load six-model results** opens the dashboard.
4. In **Failure explorer**, pre-check GPT-4o mini and Idiom.
5. Keep the cursor away from the sidebar during recording.
6. Record microphone and system audio together.
7. Record at least two complete takes and use the better one.

## Script

### 0:00–0:10 — Problem

**Screen:** ChAAt title and the unopened Demo Mode page.

**Narration:**

“A model can score well on general Chinese benchmarks and still misread an idiom, a classical word, or a Cantonese aspect marker. ChAAt exposes these hidden language-specific gaps.”

### 0:10–0:25 — Start the system

**Action:** Click **Load six-model results**.

**Narration:**

“This is an English-language demo mode. It loads six models, fifty hard items, and three repeated runs without using an API key or searching the web.”

### 0:25–0:48 — Overall view

**Action:** Point to the ranking bar chart, then the heatmap.

**Narration:**

“The overview ranks models from one hundred to thirty-one percent. The heatmap shows where capability breaks down. GPT-4o mini reaches only twenty-eight percent on idioms and thirteen percent on classical Chinese, while DeepSeek Flash is at one hundred percent.”

### 0:48–1:10 — Inspect a failure

**Action:** Open **Failure explorer**, select **GPT-4o mini**, then **Idiom**, and expand `FN-E8-03`.

**Narration:**

“ChAAt does not stop at a score. It retrieves the exact failed item. GPT-4o mini interprets *ceng ji he shi* as ‘a long time ago,’ but the idiom means ‘not long ago.’ The system shows the expected answer, the model output, and a source-grounded explanation.”

### 1:10–1:28 — Benchmark design

**Action:** Open **Benchmark design**.

**Narration:**

“The evaluation has three tiers: fifty source-verified hard items, forty-one exam-style items drawn mostly from public mock exams, and six open-ended tasks. Answer positions are balanced, scoring is reproducible, and external search is disabled.”

### 1:28–1:43 — Human evaluation

**Action:** Keep the method view visible and scroll to the validation description.

**Narration:**

“For open-ended answers, two raters independently scored every response, and a blind third rater then scored all thirty-six. Three-rater reliability was zero point nine six. This separates model performance from automatic scoring artifacts.”

### 1:43–2:00 — Close

**Action:** Return to the capability overview.

**Narration:**

“ChAAt helps researchers compare Chinese-specific capabilities, locate failure cases, and select models for real applications. The system is reproducible, extensible, and designed for both evaluation and linguistic diagnosis.”

## Recording fallback

If the browser or demo button fails:

1. Record the pre-generated interface screenshots as a silent slideshow.
2. Record the narration separately.
3. Combine the images and narration with:

```powershell
ffmpeg -framerate 1/8 -pattern_type glob -i "demo-shots/*.png" -i narration.wav -c:v libx264 -pix_fmt yuv420p -shortest demo.mp4
```

The final upload must be MP4 and must not exceed two minutes.
