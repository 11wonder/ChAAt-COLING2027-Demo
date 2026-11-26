FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements-demo.txt .
RUN pip install -r requirements-demo.txt

COPY app_demo.py .
COPY data/questions_final_hard50_core_shuffled.json data/
COPY results/noweb_all/core50/paper_details.csv results/noweb_all/core50/
COPY results/noweb_all/core50/paper_summary.csv results/noweb_all/core50/
COPY .streamlit/config.toml .streamlit/

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8501/_stcore/health', timeout=3)"

CMD ["streamlit", "run", "app_demo.py"]
