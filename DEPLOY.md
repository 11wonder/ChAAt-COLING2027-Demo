# Deploying the ChAAt reviewer demo

The demo reads bundled, precomputed results. It needs no API key and makes no
outbound network calls, so any free Streamlit host is enough. No server or
domain is required.

## Option A — Streamlit Community Cloud (recommended, ~10 minutes)

1. Create a GitHub repository and push this directory. A public repository is
   simplest; a private repository also works if you grant Streamlit access
   during sign-in.

   ```bash
   git init
   git add .
   git commit -m "ChAAt COLING 2027 demo"
   git branch -M main
   git remote add origin https://github.com/<account>/<repo>.git
   git push -u origin main
   ```

2. Sign in at <https://share.streamlit.io> with GitHub.
3. **New app** → choose the repository and branch → main file `app_demo.py`
   → Python 3.11 or 3.12 → **Deploy**.
4. Copy the resulting `https://<name>.streamlit.app` URL into:
   - `README_EN.md` (Live demo section),
   - `paper/main.tex` (Demo Plan and Software sections),
   - the COLING submission form.

The first build takes a few minutes. Free apps sleep after inactivity; the
first visit may show a wake-up button for ~30 seconds. Mention this in the
README so reviewers are not surprised.

## Option B — Hugging Face Spaces

1. Create a Space at <https://huggingface.co/new-space> with SDK **Streamlit**.
2. In the Space repository, add this project and make the entry point `app.py`:

   ```bash
   cp app_demo.py app.py
   ```

3. Add the following YAML frontmatter to the Space's `README.md`:

   ```yaml
   ---
   title: ChAAt
   emoji: 🀄
   colorFrom: red
   colorTo: blue
   sdk: streamlit
   sdk_version: 1.37.1
   app_file: app.py
   pinned: false
   ---
   ```

4. Commit and push; the Space builds automatically.

Spaces on free CPU also sleep after inactivity, but the URL is stable and
familiar to reviewers.

## Option C — Docker (only if you already have a host)

```bash
docker build -t chaat-demo .
docker run --rm -p 8501:8501 chaat-demo
```

## Pre-flight checklist

- [ ] `streamlit run app_demo.py` opens and **Load six-model results** works.
- [ ] No `.env`, API key, or local absolute path is committed.
- [ ] `results/noweb_all/core50/paper_details.csv`, `paper_summary.csv`, and
      `data/questions_final_hard50_core_shuffled.json` are present.
- [ ] The deployed page shows 100 / 92 / 82 / 77 / 66 / 31.
- [ ] The URL is added to the paper, README, and submission form.
- [ ] A cold-start note is visible to reviewers.
