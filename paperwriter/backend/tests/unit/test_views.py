import json
from tests.conftest import AuthTestCase
from api.models import Document, Section, Author, Reference


class DocumentViewSetTest(AuthTestCase):
    def test_list_documents(self):
        Document.objects.create(title="My Paper", owner=self.user)
        response = self.client.get("/api/documents/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)

    def test_list_returns_only_owned(self):
        other = type(self.user).objects.create_user('other', password='pass123')
        Document.objects.create(title="Mine", owner=self.user)
        Document.objects.create(title="Theirs", owner=other)
        response = self.client.get("/api/documents/")
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]["title"], "Mine")

    def test_create_document(self):
        response = self.client.post(
            "/api/documents/",
            json.dumps({"title": "New Paper"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["title"], "New Paper")
        self.assertEqual(response.json()["owner"], self.user.id)

    def test_get_document(self):
        doc = Document.objects.create(title="Test Paper", owner=self.user)
        response = self.client.get(f"/api/documents/{doc.id}/")
        self.assertEqual(response.status_code, 200)

    def test_cannot_get_others_document(self):
        other = type(self.user).objects.create_user('other', password='pass123')
        doc = Document.objects.create(title="Theirs", owner=other)
        response = self.client.get(f"/api/documents/{doc.id}/")
        self.assertEqual(response.status_code, 404)

    def test_update_document(self):
        doc = Document.objects.create(title="Test Paper", owner=self.user)
        response = self.client.patch(
            f"/api/documents/{doc.id}/",
            json.dumps({"title": "Updated Title"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["title"], "Updated Title")

    def test_delete_document(self):
        doc = Document.objects.create(title="Test Paper", owner=self.user)
        response = self.client.delete(f"/api/documents/{doc.id}/")
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Document.objects.count(), 0)

    def test_add_section_action(self):
        doc = Document.objects.create(title="Test Paper", owner=self.user)
        response = self.client.post(
            f"/api/documents/{doc.id}/add_section/",
            json.dumps({"title": "Introduction", "section_type": "intro"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["title"], "Introduction")

    def test_add_section_missing_title(self):
        doc = Document.objects.create(title="Test Paper", owner=self.user)
        response = self.client.post(
            f"/api/documents/{doc.id}/add_section/",
            json.dumps({}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_add_section_with_parent(self):
        doc = Document.objects.create(title="Test Paper", owner=self.user)
        parent = Section.objects.create(document=doc, title="Parent", order=1)
        response = self.client.post(
            f"/api/documents/{doc.id}/add_section/",
            json.dumps({"title": "Child", "parent": parent.id}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["parent"], parent.id)


class SectionViewSetTest(AuthTestCase):
    def setUp(self):
        super().setUp()
        self.doc = Document.objects.create(title="Test Paper", owner=self.user)
        self.section = Section.objects.create(document=self.doc, title="Intro", order=1)

    def test_list_sections(self):
        response = self.client.get("/api/sections/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)

    def test_filter_by_document(self):
        response = self.client.get(f"/api/sections/?document={self.doc.id}")
        self.assertEqual(response.status_code, 200)

    def test_create_section(self):
        response = self.client.post(
            f"/api/documents/{self.doc.id}/add_section/",
            json.dumps({"title": "Methodology", "section_type": "methodology"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)

    def test_update_section(self):
        response = self.client.patch(
            f"/api/sections/{self.section.id}/",
            json.dumps({"content": "<p>New content</p>"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)

    def test_delete_section(self):
        response = self.client.delete(f"/api/sections/{self.section.id}/")
        self.assertEqual(response.status_code, 204)

    def test_move_section_up(self):
        Section.objects.create(document=self.doc, title="Second", order=2)
        sections = Section.objects.filter(document=self.doc).order_by('order')
        last = sections.last()
        response = self.client.post(
            f"/api/sections/{last.id}/move/",
            json.dumps({"direction": "up"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    def test_move_section_down(self):
        Section.objects.create(document=self.doc, title="Second", order=2)
        response = self.client.post(
            f"/api/sections/{self.section.id}/move/",
            json.dumps({"direction": "down"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)

    def test_move_section_no_change_at_edge(self):
        response = self.client.post(
            f"/api/sections/{self.section.id}/move/",
            json.dumps({"direction": "up"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)


class AuthorViewSetTest(AuthTestCase):
    def setUp(self):
        super().setUp()
        self.doc = Document.objects.create(title="Test Paper", owner=self.user)

    def test_create_author(self):
        response = self.client.post(
            "/api/authors/",
            json.dumps({"document": self.doc.id, "name": "John Doe", "order": 1}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["name"], "John Doe")

    def test_list_authors(self):
        Author.objects.create(document=self.doc, name="John", order=1)
        response = self.client.get("/api/authors/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)

    def test_update_author(self):
        author = Author.objects.create(document=self.doc, name="John", order=1)
        response = self.client.patch(
            f"/api/authors/{author.id}/",
            json.dumps({"email": "john@test.com"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["email"], "john@test.com")

    def test_delete_author(self):
        author = Author.objects.create(document=self.doc, name="John", order=1)
        response = self.client.delete(f"/api/authors/{author.id}/")
        self.assertEqual(response.status_code, 204)


class PaperImageViewSetTest(AuthTestCase):
    def setUp(self):
        super().setUp()
        self.doc = Document.objects.create(title="Test Paper", owner=self.user)

    def test_list_images(self):
        response = self.client.get("/api/images/")
        self.assertEqual(response.status_code, 200)

    def test_filter_images_by_document(self):
        response = self.client.get(f"/api/images/?document={self.doc.id}")
        self.assertEqual(response.status_code, 200)


class ReferenceViewSetTest(AuthTestCase):
    def setUp(self):
        super().setUp()
        self.doc = Document.objects.create(title="Test Paper", owner=self.user)

    def test_create_reference(self):
        response = self.client.post(
            "/api/references/",
            json.dumps({
                "document": self.doc.id,
                "citation_key": "smith2023",
                "bibtex": "@article{smith2023, author={Smith}}",
                "order": 1,
            }),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)

    def test_list_references(self):
        Reference.objects.create(document=self.doc, citation_key="test", bibtex="@article{}")
        response = self.client.get("/api/references/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)

    def test_filter_references_by_document(self):
        response = self.client.get(f"/api/references/?document={self.doc.id}")
        self.assertEqual(response.status_code, 200)


class AICommandViewTest(AuthTestCase):
    def test_ai_command_missing_params(self):
        response = self.client.post(
            "/api/ai/command",
            json.dumps({}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_ai_command_missing_text(self):
        response = self.client.post(
            "/api/ai/command",
            json.dumps({"command": "rewrite"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)


class ExportViewsTest(AuthTestCase):
    def setUp(self):
        super().setUp()
        self.doc = Document.objects.create(title="Test Paper", owner=self.user)

    def test_get_latex_nonexistent_doc(self):
        response = self.client.get("/api/document/999/latex")
        self.assertEqual(response.status_code, 404)

    def test_export_pdf_nonexistent_doc(self):
        response = self.client.get("/api/document/999/export/pdf")
        self.assertEqual(response.status_code, 404)

    def test_export_latex_nonexistent_doc(self):
        response = self.client.get("/api/document/999/export/latex")
        self.assertEqual(response.status_code, 404)

    def test_cannot_access_others_latex(self):
        other = type(self.user).objects.create_user('other', password='pass123')
        other_doc = Document.objects.create(title="Theirs", owner=other)
        response = self.client.get(f"/api/document/{other_doc.id}/latex")
        self.assertEqual(response.status_code, 404)

    def test_get_latex_source_returns_latex(self):
        Section.objects.create(
            document=self.doc, title="Abstract",
            section_type="abstract", content="<p>Abstract text</p>", order=1
        )
        response = self.client.get(f"/api/document/{self.doc.id}/latex")
        self.assertEqual(response.status_code, 200)
        self.assertIn("latex", response.json())

    def test_export_latex_returns_zip(self):
        response = self.client.get(f"/api/document/{self.doc.id}/export/latex")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/zip")


class AuthEndpointsTest(AuthTestCase):
    def test_health_check(self):
        self.client.force_authenticate(user=None)
        response = self.client.get("/api/health/")
        self.assertEqual(response.status_code, 200)

    def test_register(self):
        self.client.force_authenticate(user=None)
        response = self.client.post(
            "/api/auth/register/",
            json.dumps({
                "username": "newuser",
                "email": "new@test.com",
                "password": "StrongPass123!",
                "password2": "StrongPass123!",
            }),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertIn("id", response.json())

    def test_register_password_mismatch(self):
        self.client.force_authenticate(user=None)
        response = self.client.post(
            "/api/auth/register/",
            json.dumps({
                "username": "newuser",
                "password": "StrongPass123!",
                "password2": "DifferentPass123!",
            }),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_login_returns_tokens(self):
        self.client.force_authenticate(user=None)
        response = self.client.post(
            "/api/auth/login/",
            json.dumps({"username": self.username, "password": self.password}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.json())
        self.assertIn("refresh", response.json())

    def test_login_invalid_credentials(self):
        self.client.force_authenticate(user=None)
        response = self.client.post(
            "/api/auth/login/",
            json.dumps({"username": self.username, "password": "wrong"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 401)

    def test_me_endpoint(self):
        response = self.client.get("/api/auth/me/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["username"], self.username)
