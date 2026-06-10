import json
from tests.conftest import AuthTestCase
from api.models import Section


class DocumentLifecycleTest(AuthTestCase):
    def test_full_document_lifecycle(self):
        doc_resp = self.client.post(
            "/api/documents/",
            json.dumps({"title": "Integration Test Paper"}),
            content_type="application/json",
        )
        self.assertEqual(doc_resp.status_code, 201)
        doc_id = doc_resp.json()["id"]

        for title, stype in [
            ("Abstract", "abstract"),
            ("Introduction", "intro"),
            ("Methodology", "methodology"),
        ]:
            resp = self.client.post(
                f"/api/documents/{doc_id}/add_section/",
                json.dumps({"title": title, "section_type": stype}),
                content_type="application/json",
            )
            self.assertEqual(resp.status_code, 201)

        response = self.client.get(f"/api/documents/{doc_id}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["sections"]), 3)

        for name in ["Alice", "Bob"]:
            resp = self.client.post(
                "/api/authors/",
                json.dumps({
                    "document": doc_id,
                    "name": name,
                    "order": 1 if name == "Alice" else 2,
                }),
                content_type="application/json",
            )
            self.assertEqual(resp.status_code, 201)

        resp = self.client.post(
            "/api/references/",
            json.dumps({
                "document": doc_id,
                "citation_key": "ref2024",
                "bibtex": "@article{ref2024, author={Test}}",
                "order": 1,
            }),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 201)

        response = self.client.get(f"/api/document/{doc_id}/latex")
        self.assertEqual(response.status_code, 200)
        self.assertIn(r"\begin{document}", response.json()["latex"])

        response = self.client.get(f"/api/document/{doc_id}/export/latex")
        self.assertEqual(response.status_code, 200)

        response = self.client.delete(f"/api/documents/{doc_id}/")
        self.assertEqual(response.status_code, 204)

    def test_section_move_affects_order(self):
        resp = self.client.post(
            "/api/documents/",
            json.dumps({"title": "Reorder Test"}),
            content_type="application/json",
        )
        doc_id = resp.json()["id"]

        self.client.post(
            f"/api/documents/{doc_id}/add_section/",
            json.dumps({"title": "First", "section_type": "intro"}),
            content_type="application/json",
        )
        self.client.post(
            f"/api/documents/{doc_id}/add_section/",
            json.dumps({"title": "Second", "section_type": "intro"}),
            content_type="application/json",
        ).json()

        sections = Section.objects.filter(document_id=doc_id).order_by('order')
        s2 = sections.last()

        self.client.post(
            f"/api/sections/{s2.id}/move/",
            json.dumps({"direction": "up"}),
            content_type="application/json",
        )

        response = self.client.get(f"/api/documents/{doc_id}/")
        data = response.json()["sections"]
        self.assertEqual(data[0]["title"], "Second")
