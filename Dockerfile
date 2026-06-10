FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    texlive-latex-base \
    texlive-latex-recommended \
    texlive-latex-extra \
    texlive-fonts-recommended \
    texlive-bibtex-extra \
    texlive-fonts-extra \
    texlive-science \
    latexmk \
    librsvg2-bin \
    && rm -rf /var/lib/apt/lists/*

COPY paperwriter/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn

COPY paperwriter/backend /app/backend
COPY paperwriter/ieee_format /app/ieee_format

WORKDIR /app/backend

RUN python manage.py migrate

EXPOSE 8000

CMD ["gunicorn", "paperwriter.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4"]
