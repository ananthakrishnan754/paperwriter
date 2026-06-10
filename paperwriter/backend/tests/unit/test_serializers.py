from django.test import TestCase
from api.models import Document, Section, Author, PaperImage, Reference
from api.serializers import (
    DocumentSerializer,
    SectionSerializer,
    AuthorSerializer,
    PaperImageSerializer,
    ReferenceSerializer,
)


class ReferenceSerializerTest(TestCase):
    def test_contains_expected_fields(self):
        doc = Document.objects.create()
        ref = Reference.objects.create(
            document=doc,
            citation_key="test2023",
            description="Test ref",
            bibtex="@article{test2023, author={T}}",
        )
        serializer = ReferenceSerializer(ref)
        data = serializer.data
        self.assertIn("id", data)
        self.assertIn("citation_key", data)
        self.assertIn("description", data)
        self.assertIn("bibtex", data)
        self.assertIn("document", data)
        self.assertIn("order", data)
        self.assertIn("created_at", data)

    def test_created_at_read_only(self):
        data = {
            "document": 1,
            "citation_key": "test",
            "bibtex": "@article{}",
        }
        serializer = ReferenceSerializer(data=data)
        self.assertIn("created_at", serializer.fields)
        self.assertTrue(serializer.fields["created_at"].read_only)


class SectionSerializerTest(TestCase):
    def test_recursive_subsections(self):
        doc = Document.objects.create()
        parent = Section.objects.create(
            document=doc, title="Parent", order=1
        )
        Section.objects.create(
            document=doc, title="Child", parent=parent, order=1
        )
        serializer = SectionSerializer(parent)
        data = serializer.data
        self.assertIn("subsections", data)
        self.assertEqual(len(data["subsections"]), 1)
        self.assertEqual(data["subsections"][0]["title"], "Child")

    def test_contains_expected_fields(self):
        doc = Document.objects.create()
        section = Section.objects.create(
            document=doc, title="Intro", order=1
        )
        serializer = SectionSerializer(section)
        data = serializer.data
        self.assertIn("id", data)
        self.assertIn("title", data)
        self.assertIn("content", data)
        self.assertIn("order", data)
        self.assertIn("section_type", data)
        self.assertIn("parent", data)
        self.assertIn("subsections", data)


class AuthorSerializerTest(TestCase):
    def test_contains_expected_fields(self):
        doc = Document.objects.create()
        author = Author.objects.create(
            document=doc, name="John", order=1
        )
        serializer = AuthorSerializer(author)
        data = serializer.data
        self.assertIn("id", data)
        self.assertIn("name", data)
        self.assertIn("document", data)
        self.assertIn("department", data)
        self.assertIn("organization", data)
        self.assertIn("city", data)
        self.assertIn("country", data)
        self.assertIn("email", data)
        self.assertIn("order", data)


class PaperImageSerializerTest(TestCase):
    def test_image_url_null_without_request(self):
        doc = Document.objects.create()
        img = PaperImage.objects.create(
            document=doc,
            image="paper_images/test.png",
        )
        serializer = PaperImageSerializer(img)
        data = serializer.data
        self.assertIn("image_url", data)
        self.assertIsNone(data["image_url"])

    def test_contains_expected_fields(self):
        doc = Document.objects.create()
        img = PaperImage.objects.create(
            document=doc, image="paper_images/test.png"
        )
        serializer = PaperImageSerializer(img)
        data = serializer.data
        self.assertIn("id", data)
        self.assertIn("document", data)
        self.assertIn("section", data)
        self.assertIn("image", data)
        self.assertIn("image_url", data)
        self.assertIn("caption", data)
        self.assertIn("label", data)
        self.assertIn("width", data)
        self.assertIn("order", data)
        self.assertIn("uploaded_at", data)


class DocumentSerializerTest(TestCase):
    def test_nested_sections_only_top_level(self):
        doc = Document.objects.create()
        parent = Section.objects.create(
            document=doc, title="Parent", order=1
        )
        Section.objects.create(
            document=doc, title="Child", parent=parent, order=1
        )
        serializer = DocumentSerializer(doc)
        data = serializer.data
        self.assertIn("sections", data)
        self.assertEqual(len(data["sections"]), 1)
        self.assertEqual(data["sections"][0]["title"], "Parent")

    def test_nested_authors(self):
        doc = Document.objects.create()
        Author.objects.create(document=doc, name="John", order=1)
        serializer = DocumentSerializer(doc)
        data = serializer.data
        self.assertIn("authors", data)
        self.assertEqual(len(data["authors"]), 1)

    def test_nested_images(self):
        doc = Document.objects.create()
        PaperImage.objects.create(
            document=doc, image="paper_images/test.png"
        )
        serializer = DocumentSerializer(doc)
        data = serializer.data
        self.assertIn("images", data)
        self.assertEqual(len(data["images"]), 1)

    def test_nested_references(self):
        doc = Document.objects.create()
        Reference.objects.create(
            document=doc,
            citation_key="test",
            bibtex="@article{}",
        )
        serializer = DocumentSerializer(doc)
        data = serializer.data
        self.assertIn("references", data)
        self.assertEqual(len(data["references"]), 1)
