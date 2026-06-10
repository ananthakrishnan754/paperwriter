from django.test import TestCase
from api.models import Document, Section, Author, PaperImage, Reference


class DocumentModelTest(TestCase):
    def test_create_document(self):
        doc = Document.objects.create(title="Test Paper")
        self.assertEqual(doc.title, "Test Paper")
        self.assertIsNotNone(doc.created_at)
        self.assertIsNotNone(doc.updated_at)

    def test_default_title(self):
        doc = Document.objects.create()
        self.assertEqual(doc.title, "Untitled Paper")

    def test_default_index_terms(self):
        doc = Document.objects.create()
        self.assertTrue(len(doc.index_terms) > 0)

    def test_str_representation(self):
        doc = Document.objects.create(title="My Paper")
        self.assertEqual(str(doc), "My Paper")

    def test_cascade_delete_sections(self):
        doc = Document.objects.create(title="Test")
        Section.objects.create(document=doc, title="Intro", order=1)
        self.assertEqual(Section.objects.count(), 1)
        doc.delete()
        self.assertEqual(Section.objects.count(), 0)


class SectionModelTest(TestCase):
    def setUp(self):
        self.doc = Document.objects.create(title="Test Paper")

    def test_create_section(self):
        section = Section.objects.create(
            document=self.doc, title="Introduction", order=1
        )
        self.assertEqual(section.title, "Introduction")
        self.assertEqual(section.document, self.doc)

    def test_section_ordering(self):
        Section.objects.create(document=self.doc, title="B", order=2)
        Section.objects.create(document=self.doc, title="A", order=1)
        sections = Section.objects.all()
        self.assertEqual(sections[0].title, "A")
        self.assertEqual(sections[1].title, "B")

    def test_recursive_parent(self):
        parent = Section.objects.create(
            document=self.doc, title="Methodology", order=1
        )
        child = Section.objects.create(
            document=self.doc, title="Data Collection", parent=parent, order=1
        )
        self.assertEqual(child.parent, parent)
        self.assertIn(child, parent.subsections.all())

    def test_section_type_choices(self):
        section = Section.objects.create(
            document=self.doc, title="Abstract", section_type="abstract", order=1
        )
        self.assertEqual(section.section_type, "abstract")

    def test_str_representation(self):
        section = Section.objects.create(
            document=self.doc, title="Intro", order=1
        )
        self.assertEqual(str(section), "Test Paper - Intro")


class AuthorModelTest(TestCase):
    def setUp(self):
        self.doc = Document.objects.create(title="Test Paper")

    def test_create_author(self):
        author = Author.objects.create(
            document=self.doc,
            name="John Doe",
            department="CS",
            organization="MIT",
            city="Cambridge",
            country="USA",
            email="john@mit.edu",
            order=1,
        )
        self.assertEqual(author.name, "John Doe")
        self.assertEqual(author.email, "john@mit.edu")

    def test_author_ordering(self):
        Author.objects.create(document=self.doc, name="B", order=2)
        Author.objects.create(document=self.doc, name="A", order=1)
        authors = Author.objects.all()
        self.assertEqual(authors[0].name, "A")

    def test_blank_fields(self):
        author = Author.objects.create(document=self.doc, name="John Doe", order=1)
        self.assertEqual(author.department, "")
        self.assertEqual(author.organization, "")
        self.assertEqual(author.email, "")

    def test_str_representation(self):
        author = Author.objects.create(
            document=self.doc, name="John Doe", order=1
        )
        self.assertIn("John Doe", str(author))
        self.assertIn("Test Paper", str(author))


class PaperImageModelTest(TestCase):
    def setUp(self):
        self.doc = Document.objects.create(title="Test Paper")

    def test_default_width(self):
        img = PaperImage.objects.create(
            document=self.doc,
            image="paper_images/test.png",
            caption="Test figure",
            label="fig:test",
        )
        self.assertEqual(img.width, 0.9)
        self.assertEqual(img.label, "fig:test")

    def test_width_constraints(self):
        img = PaperImage.objects.create(
            document=self.doc, image="paper_images/test.png", width=0.5
        )
        self.assertGreaterEqual(img.width, 0.1)
        self.assertLessEqual(img.width, 1.0)

    def test_str_representation(self):
        img = PaperImage.objects.create(
            document=self.doc,
            image="paper_images/test.png",
            caption="My Figure",
        )
        self.assertIn("My Figure", str(img))
        self.assertIn("Test Paper", str(img))


class ReferenceModelTest(TestCase):
    def setUp(self):
        self.doc = Document.objects.create(title="Test Paper")

    def test_create_reference(self):
        ref = Reference.objects.create(
            document=self.doc,
            citation_key="smith2023",
            description="Smith et al. 2023",
            bibtex="@article{smith2023, author={Smith, J}}",
        )
        self.assertEqual(ref.citation_key, "smith2023")
        self.assertIn("smith2023", str(ref))

    def test_ordering(self):
        Reference.objects.create(
            document=self.doc, citation_key="B", order=2,
            bibtex="@article{B, author={B}}"
        )
        Reference.objects.create(
            document=self.doc, citation_key="A", order=1,
            bibtex="@article{A, author={A}}"
        )
        refs = Reference.objects.all()
        self.assertEqual(refs[0].citation_key, "A")

    def test_created_at_auto(self):
        ref = Reference.objects.create(
            document=self.doc, citation_key="test",
            bibtex="@article{test, author={T}}"
        )
        self.assertIsNotNone(ref.created_at)
