from django.test import TestCase
from api.models import Document, Section, Author, Reference
from api.views import generate_latex_source


class GenerateLatexSourceTest(TestCase):
    def test_basic_document_structure(self):
        doc = Document.objects.create(title="Test Paper")
        latex = generate_latex_source(doc)
        self.assertIn(r"\documentclass[conference]{IEEEtran}", latex)
        self.assertIn(r"\title{Test Paper}", latex)
        self.assertIn(r"\begin{document}", latex)
        self.assertIn(r"\end{document}", latex)

    def test_abstract_section(self):
        doc = Document.objects.create(title="Test")
        Section.objects.create(
            document=doc, title="Abstract",
            section_type="abstract",
            content="<p>This is an abstract.</p>",
            order=1,
        )
        latex = generate_latex_source(doc)
        self.assertIn(r"\begin{abstract}", latex)
        self.assertIn("This is an abstract.", latex)
        self.assertIn(r"\end{abstract}", latex)

    def test_index_terms(self):
        doc = Document.objects.create(
            title="Test",
            index_terms="machine learning, radar"
        )
        Section.objects.create(
            document=doc, title="Abstract",
            section_type="abstract",
            content="<p>Abstract</p>",
            order=1,
        )
        latex = generate_latex_source(doc)
        self.assertIn(r"\begin{IEEEkeywords}", latex)
        self.assertIn("machine learning, radar", latex)
        self.assertIn(r"\end{IEEEkeywords}", latex)

    def test_regular_section(self):
        doc = Document.objects.create(title="Test")
        Section.objects.create(
            document=doc, title="Introduction",
            section_type="intro",
            content="<p>Intro text</p>",
            order=1,
        )
        latex = generate_latex_source(doc)
        self.assertIn(r"\section{Introduction}", latex)
        self.assertIn("Intro text", latex)

    def test_subsection(self):
        doc = Document.objects.create(title="Test")
        parent = Section.objects.create(
            document=doc, title="Methodology", order=1
        )
        Section.objects.create(
            document=doc, title="Data Collection",
            parent=parent, content="<p>Details</p>",
            order=1,
        )
        latex = generate_latex_source(doc)
        self.assertIn(r"\subsection{Data Collection}", latex)
        self.assertIn("Details", latex)

    def test_html_to_latex_conversion(self):
        doc = Document.objects.create(title="Test")
        Section.objects.create(
            document=doc, title="Intro",
            section_type="intro",
            content="<p><strong>Bold</strong> and <em>italic</em></p>",
            order=1,
        )
        latex = generate_latex_source(doc)
        self.assertIn(r"\textbf{Bold}", latex)
        self.assertIn(r"\textit{italic}", latex)

    def test_authors_block(self):
        doc = Document.objects.create(title="Test")
        Author.objects.create(
            document=doc, name="John Doe",
            department="CS", organization="MIT",
            city="Cambridge", country="USA",
            email="john@mit.edu", order=1,
        )
        latex = generate_latex_source(doc)
        self.assertIn(r"\author{", latex)
        self.assertIn(r"1\textsuperscript{st} John Doe", latex)
        self.assertIn(r"\textit{CS}", latex)
        self.assertIn(r"\textit{MIT}", latex)
        self.assertIn("Cambridge, USA", latex)
        self.assertIn("john@mit.edu", latex)

    def test_multiple_authors(self):
        doc = Document.objects.create(title="Test")
        Author.objects.create(
            document=doc, name="First", order=1
        )
        Author.objects.create(
            document=doc, name="Second", order=2
        )
        latex = generate_latex_source(doc)
        self.assertIn(r"1\textsuperscript{st} First", latex)
        self.assertIn(r"2\textsuperscript{nd} Second", latex)

    def test_references(self):
        doc = Document.objects.create(title="Test")
        Reference.objects.create(
            document=doc,
            citation_key="smith2023",
            bibtex="@article{smith2023, author={Smith}}",
        )
        latex = generate_latex_source(doc)
        self.assertIn(r"\bibliographystyle{IEEEtran}", latex)
        self.assertIn(r"\bibliography{refs}", latex)

    def test_empty_content(self):
        doc = Document.objects.create(title="Test")
        Section.objects.create(
            document=doc, title="Intro",
            section_type="intro",
            content="",
            order=1,
        )
        latex = generate_latex_source(doc)
        self.assertIn(r"\section{Intro}", latex)

    def test_placeholder_authors_when_none(self):
        doc = Document.objects.create(title="Test")
        latex = generate_latex_source(doc)
        self.assertIn(r"\IEEEauthorblockN", latex)
        self.assertIn("Given Name Surname", latex)
