import os
import re
import io
import copy
import zipfile
import tempfile
import subprocess
import shutil

from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse
from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
import google.generativeai as genai

from .models import Document, Section, Author, PaperImage, Reference
from .serializers import DocumentSerializer, SectionSerializer, AuthorSerializer, PaperImageSerializer, ReferenceSerializer
from .permissions import IsOwnerOrReadOnly


def home(request):
    return render(request, 'index.html')


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def health_check(request):
    return Response({
        'status': 'ok',
        'version': '1.0.0',
    })


class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.none()
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        return Document.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=['post'])
    def add_section(self, request, pk=None):
        document = self.get_object()
        title = request.data.get('title')
        parent_id = request.data.get('parent')
        section_type = request.data.get('section_type', 'custom')

        if not title:
            return Response({'error': 'Title is required'}, status=status.HTTP_400_BAD_REQUEST)

        parent = None
        if parent_id:
            try:
                parent = Section.objects.get(id=parent_id, document=document)
            except Section.DoesNotExist:
                return Response({'error': 'Parent section not found'}, status=status.HTTP_404_NOT_FOUND)

        siblings = Section.objects.filter(document=document, parent=parent)
        order = siblings.count() + 1

        section = Section.objects.create(
            document=document,
            parent=parent,
            title=title,
            order=order,
            section_type=section_type,
        )
        return Response(SectionSerializer(section).data, status=status.HTTP_201_CREATED)


class SectionViewSet(viewsets.ModelViewSet):
    queryset = Section.objects.none()
    serializer_class = SectionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user_doc_ids = Document.objects.filter(owner=self.request.user).values_list('id', flat=True)
        qs = Section.objects.filter(document_id__in=user_doc_ids)
        doc_id = self.request.query_params.get('document')
        if doc_id:
            qs = qs.filter(document_id=doc_id)
        return qs

    @action(detail=True, methods=['post'])
    def move(self, request, pk=None):
        section = self.get_object()
        direction = request.data.get('direction')

        siblings = list(Section.objects.filter(
            document=section.document, parent=section.parent
        ).order_by('order'))
        for idx, s in enumerate(siblings):
            if s.order != idx:
                s.order = idx
                s.save()

        current_idx = siblings.index(section)
        if direction == 'up' and current_idx > 0:
            siblings[current_idx], siblings[current_idx-1] = siblings[current_idx-1], siblings[current_idx]
        elif direction == 'down' and current_idx < len(siblings) - 1:
            siblings[current_idx], siblings[current_idx+1] = siblings[current_idx+1], siblings[current_idx]
        else:
            return Response({'status': 'no_change'})

        for idx, s in enumerate(siblings):
            Section.objects.filter(id=s.id).update(order=idx)

        return Response({'status': 'ok'})


class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.none()
    serializer_class = AuthorSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user_doc_ids = Document.objects.filter(owner=self.request.user).values_list('id', flat=True)
        return Author.objects.filter(document_id__in=user_doc_ids)

    def perform_create(self, serializer):
        doc_id = self.request.data.get('document')
        if doc_id:
            doc = Document.objects.get(id=doc_id, owner=self.request.user)
            serializer.save(document=doc)
        else:
            serializer.save()


class PaperImageViewSet(viewsets.ModelViewSet):
    queryset = PaperImage.objects.all()
    serializer_class = PaperImageSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def get_queryset(self):
        user_doc_ids = Document.objects.filter(owner=self.request.user).values_list('id', flat=True)
        qs = PaperImage.objects.filter(document_id__in=user_doc_ids)
        doc_id = self.request.query_params.get('document')
        if doc_id:
            qs = qs.filter(document_id=doc_id)
        return qs


class ReferenceViewSet(viewsets.ModelViewSet):
    queryset = Reference.objects.none()
    serializer_class = ReferenceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user_doc_ids = Document.objects.filter(owner=self.request.user).values_list('id', flat=True)
        qs = Reference.objects.filter(document_id__in=user_doc_ids)
        doc_id = self.request.query_params.get('document')
        if doc_id:
            qs = qs.filter(document_id=doc_id)
        return qs


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def process_ai_command(request):
    command = request.data.get('command')
    selected_text = request.data.get('selected_text')
    section_context = request.data.get('section_context', "Academic Section")

    if not command or not selected_text:
        return Response({'error': 'Missing command or text'}, status=400)

    try:
        api_key = settings.GEMINI_API_KEY
        if not api_key:
            return Response({'error': 'GEMINI_API_KEY not configured'}, status=500)

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash')

        prompt = f"""
        You are an expert academic editor. Your task is to process the following text based on the user's command.

        Context (Section Type): {section_context}

        User Command: "{command}"

        Selected Text:
        "{selected_text}"

        Instructions:
        1. Return ONLY the modified text.
        2. Do not include any conversational filler.
        3. Maintain academic tone and standard formatting.
        """

        response = model.generate_content(prompt)
        return Response({'result': response.text.strip()})

    except Exception as e:
        return Response({'error': str(e)}, status=500)


def generate_latex_source(document):
    """Generate complete LaTeX source code for a document"""
    latex_content = [
        r"\documentclass[conference]{IEEEtran}",
        r"\IEEEoverridecommandlockouts",
        r"\usepackage{cite}",
        r"\usepackage{amsmath,amssymb,amsfonts}",
        r"\usepackage{algorithmic}",
        r"\usepackage{graphicx}",
        r"\usepackage{textcomp}",
        r"\usepackage{xcolor}",
        r"\def\BibTeX{{\rm B\kern-.05em{\sc i\kern-.025em b}\kern-.08em"
        r"    T\kern-.1667em\lower.7ex\hbox{E}\kern-.125emX}}",
        r"\begin{document}",
        r"\sloppy",
        "",
        f"\\title{{{document.title}}}",
        "",
    ]

    authors = document.authors.all().order_by('order')
    if authors.exists():
        author_blocks = []
        for idx, author in enumerate(authors, 1):
            ordinal = f"{idx}\\textsuperscript{{st}}" if idx == 1 else f"{idx}\\textsuperscript{{nd}}" if idx == 2 else f"{idx}\\textsuperscript{{rd}}" if idx == 3 else f"{idx}\\textsuperscript{{th}}"
            author_block = f"\\IEEEauthorblockN{{{ordinal} {author.name}}}"
            affiliation_parts = []
            if author.department:
                affiliation_parts.append(f"\\textit{{{author.department}}}")
            if author.organization:
                affiliation_parts.append(f"\\textit{{{author.organization}}}")
            if author.city or author.country:
                location = ", ".join(filter(None, [author.city, author.country]))
                affiliation_parts.append(location)
            if author.email:
                affiliation_parts.append(author.email)
            if affiliation_parts:
                author_block += "\n" + "\\IEEEauthorblockA{" + " \\\\\n".join(affiliation_parts) + "}"
            author_blocks.append(author_block)
        latex_content.append("\\author{" + "\n\\and\n".join(author_blocks) + "\n}")
    else:
        latex_content.extend([
            r"\author{\IEEEauthorblockN{1\textsuperscript{st} Given Name Surname}",
            r"\IEEEauthorblockA{\textit{dept. name of organization (of Aff.)} \\",
            r"\textit{name of organization (of Aff.)}\\",
            r"City, Country \\",
            r"email address or ORCID}",
            r"}",
        ])

    latex_content.extend(["", r"\maketitle"])

    all_images = list(document.images.all().order_by('order', 'uploaded_at'))
    section_images = {}
    for img in all_images:
        if img.section_id:
            section_images.setdefault(img.section_id, []).append(img)

    def emit_figure(img):
        filename = os.path.basename(img.image.name)
        label = img.label or f'fig{img.id}'
        caption = img.caption or ''
        width = max(0.1, min(1.0, img.width or 0.9))
        lines = [
            r"\begin{figure}[htbp]",
            r"\centering",
            f"\\includegraphics[width={width:.2f}\\columnwidth]{{{filename}}}",
        ]
        if caption:
            lines.append(f"\\caption{{{caption}}}")
        lines.append(f"\\label{{{label}}}")
        lines.append(r"\end{figure}")
        lines.append("")
        return lines

    def process_content_html(content):
        if not content:
            return ""
        text = re.sub(r'<p>(.*?)</p>', r'\1\n\n', content)
        text = re.sub(r'<h3>(.*?)</h3>', r'\1\n\n', text)
        text = re.sub(r'<h4>(.*?)</h4>', r'\1\n\n', text)
        text = re.sub(r'<strong>(.*?)</strong>', r'\\textbf{\1}', text)
        text = re.sub(r'<em>(.*?)</em>', r'\\textit{\1}', text)
        text = text.replace('&nbsp;', ' ').replace('&lt;', '<').replace('&gt;', '>')
        return text.strip()

    def emit_section(section, depth=1):
        lines = []
        processed_content = process_content_html(section.content)

        if section.section_type == 'abstract':
            lines.append(r"\begin{abstract}")
            lines.append(processed_content)
            lines.append(r"\end{abstract}")
            if document.index_terms:
                lines.append(r"\begin{IEEEkeywords}")
                lines.append(document.index_terms)
                lines.append(r"\end{IEEEkeywords}")
        elif section.section_type == 'references':
            if not document.references.exists():
                lines.append(r"\section{References}")
                lines.append(processed_content)
        else:
            cmd = "section" if depth == 1 else "subsection" if depth == 2 else "subsubsection"
            lines.append(f"\\{cmd}{{{section.title}}}")
            if processed_content:
                lines.append(processed_content)

        for img in section_images.get(section.id, []):
            lines.extend(emit_figure(img))

        subsections = section.subsections.all().order_by('order')
        for sub in subsections:
            lines.extend(emit_section(sub, depth + 1))

        return lines

    top_sections = document.sections.filter(parent=None).order_by('order')
    for section in top_sections:
        latex_content.extend(emit_section(section, depth=1))

    if document.references.exists():
        latex_content.append(r"\bibliographystyle{IEEEtran}")
        latex_content.append(r"\bibliography{refs}")

    latex_content.append(r"\end{document}")
    return "\n".join(latex_content)


def _get_user_document(request, doc_id):
    """Helper to get a document if the user owns it."""
    doc = Document.objects.get(id=doc_id, owner=request.user)
    return doc


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_latex_source(request, doc_id):
    try:
        document = _get_user_document(request, doc_id)
        latex_source = generate_latex_source(document)
        return Response({'latex': latex_source})
    except Document.DoesNotExist:
        return Response({'error': 'Document not found'}, status=404)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def export_pdf(request, doc_id):
    try:
        document = _get_user_document(request, doc_id)
        latex_source = generate_latex_source(document)

        with tempfile.TemporaryDirectory() as tmpdir:
            tex_path = os.path.join(tmpdir, 'paper.tex')
            with open(tex_path, 'w', encoding='utf-8') as f:
                f.write(latex_source)

            refs = document.references.all()
            if refs.exists():
                bib_path = os.path.join(tmpdir, 'refs.bib')
                with open(bib_path, 'w', encoding='utf-8') as f:
                    for ref in refs:
                        f.write(ref.bibtex + "\n\n")

            cls_source = os.path.join(settings.BASE_DIR.parent, 'ieee_format', 'IEEEtran.cls')
            if os.path.exists(cls_source):
                shutil.copy(cls_source, os.path.join(tmpdir, 'IEEEtran.cls'))

            for img in document.images.all():
                img_disk_path = img.image.path
                if os.path.exists(img_disk_path):
                    shutil.copy(img_disk_path, os.path.join(tmpdir, os.path.basename(img_disk_path)))

            try:
                env = copy.copy(os.environ)
                miktex_paths = [
                    r"C:\Program Files\MiKTeX\miktex\bin\x64",
                    r"C:\Users\DELL\AppData\Local\Programs\MiKTeX\miktex\bin\x64",
                    os.path.expanduser(r"~\AppData\Local\Programs\MiKTeX\miktex\bin\x64"),
                ]
                for miktex_path in miktex_paths:
                    if os.path.exists(miktex_path):
                        env['PATH'] = miktex_path + os.pathsep + env.get('PATH', '')
                        break

                subprocess.run(['pdflatex', '-interaction=nonstopmode', 'paper.tex'], cwd=tmpdir, capture_output=True, timeout=120, env=env)
                if refs.exists():
                    subprocess.run(['bibtex', 'paper'], cwd=tmpdir, capture_output=True, timeout=60, env=env)
                    subprocess.run(['pdflatex', '-interaction=nonstopmode', 'paper.tex'], cwd=tmpdir, capture_output=True, timeout=120, env=env)
                result = subprocess.run(['pdflatex', '-interaction=nonstopmode', 'paper.tex'], cwd=tmpdir, capture_output=True, timeout=120, env=env)

                pdf_path = os.path.join(tmpdir, 'paper.pdf')
                if os.path.exists(pdf_path):
                    with open(pdf_path, 'rb') as f:
                        pdf_content = f.read()
                    response = HttpResponse(pdf_content, content_type='application/pdf')
                    response['Content-Disposition'] = f'attachment; filename=paper_{doc_id}.pdf'
                    return response
                else:
                    stdout = result.stdout.decode('utf-8', errors='replace')
                    stderr = result.stderr.decode('utf-8', errors='replace')
                    return Response({'error': 'PDF compilation failed', 'log': stderr, 'full_log': stdout}, status=500)

            except FileNotFoundError:
                return Response({'error': 'LaTeX compiler not installed', 'message': 'Please install MiKTeX or TeX Live to enable PDF export'}, status=503)
            except subprocess.TimeoutExpired:
                return Response({'error': 'Compilation timeout'}, status=500)

    except Document.DoesNotExist:
        return Response({'error': 'Document not found'}, status=404)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def export_latex(request, doc_id):
    try:
        document = _get_user_document(request, doc_id)
        latex_source = generate_latex_source(document)

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr(f"paper_{doc_id}.tex", latex_source)

            refs = document.references.all()
            if refs.exists():
                bib_content = "\n\n".join([ref.bibtex for ref in refs])
                zip_file.writestr("refs.bib", bib_content)

            cls_path = os.path.join(settings.BASE_DIR.parent, 'ieee_format', 'IEEEtran.cls')
            if os.path.exists(cls_path):
                zip_file.write(cls_path, 'IEEEtran.cls')

            fig_path = os.path.join(settings.BASE_DIR.parent, 'ieee_format', 'fig1.png')
            if os.path.exists(fig_path):
                zip_file.write(fig_path, 'fig1.png')

            for img in document.images.all():
                img_disk_path = img.image.path
                if os.path.exists(img_disk_path):
                    zip_file.write(img_disk_path, os.path.basename(img_disk_path))

        response = HttpResponse(zip_buffer.getvalue(), content_type="application/zip")
        response['Content-Disposition'] = f'attachment; filename=paper_{doc_id}_project.zip'
        return response

    except Document.DoesNotExist:
        return Response({'error': 'Document not found'}, status=404)
