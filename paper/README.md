# COLING 2027 System Demonstrations Submission

## Official sources

- Track: COLING 2027 System Demonstrations
- Call for papers: https://2027.coling-iccl.org/calls/system_demonstrations/
- Official LaTeX package: https://2027.coling-iccl.org/assets/templates/coling-2027-latex.zip
- Official proceedings instructions: https://2027.coling-iccl.org/assets/templates/coling-2027-proceedings-instructions.pdf
- Verified: 2026-11-26

This project uses the official files:

- `coling.sty`
- `coling_natbib.bst`

The paper is entirely in English. The generic `acl.sty` version is kept only in the separate legacy directory.

## Demo requirements

- At most six pages of main content.
- References and appendices do not count toward the page limit.
- Single-blind review.
- A demonstration video of at most two minutes is required.
- Accepted papers receive one additional page.

## Author

Yankai Wan  
Jilin University

## Demo video

- Final MP4: `demo_assets/video/ChAAt_COLING2027_Demo.mp4`
- English script: `DEMO_VIDEO_SCRIPT.md`
- English captions: `demo_assets/demo_captions.srt`
- Narration: `demo_assets/audio/narration.wav`
- Streamlit recording mode: root-level `app_demo.py`
- Recording automation: `record_demo_video.py`

The current audio is an offline synthesized English draft. Replace it with the
presenter's voice before submission if a human voice is preferred.

## Build

```powershell
xelatex main.tex
bibtex main
xelatex main.tex
xelatex main.tex
```

In Overleaf, upload the complete directory and select XeLaTeX.
