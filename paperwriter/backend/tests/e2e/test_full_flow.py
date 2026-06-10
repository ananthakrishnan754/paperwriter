import json
from tests.conftest import AuthTestCase


class FullE2EFlowTest(AuthTestCase):
    def test_create_edit_export_flow(self):
        resp = self.client.post(
            "/api/documents/",
            json.dumps({"title": "E2E Test Paper"}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 201)
        doc_id = resp.json()["id"]

        resp = self.client.post(
            f"/api/documents/{doc_id}/add_section/",
            json.dumps({"title": "Abstract", "section_type": "abstract"}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 201)
        abstract = resp.json()

        self.client.patch(
            f"/api/sections/{abstract['id']}/",
            json.dumps({"content": "<p>This is the abstract of our paper.</p>"}),
            content_type="application/json",
        )

        resp = self.client.post(
            f"/api/documents/{doc_id}/add_section/",
            json.dumps({"title": "Introduction", "section_type": "intro"}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 201)
        intro = resp.json()

        self.client.post(
            "/api/sections/",
            json.dumps({
                "document": doc_id,
                "title": "Background",
                "parent": intro["id"],
                "order": 1,
            }),
            content_type="application/json",
        )

        self.client.post(
            "/api/authors/",
            json.dumps({
                "document": doc_id,
                "name": "Dr. Researcher",
                "department": "Computer Science",
                "organization": "University",
                "email": "dr@uni.edu",
                "order": 1,
            }),
            content_type="application/json",
        )

        self.client.post(
            "/api/references/",
            json.dumps({
                "document": doc_id,
                "citation_key": "e2e2024",
                "description": "E2E Test Reference",
                "bibtex": "@article{e2e2024,\n  author={Test},\n  title={E2E}\n}",
                "order": 1,
            }),
            content_type="application/json",
        )

        response = self.client.get(f"/api/documents/{doc_id}/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data["sections"]), 2)
        self.assertEqual(len(data["authors"]), 1)
        self.assertEqual(len(data["references"]), 1)

        response = self.client.get(f"/api/document/{doc_id}/latex")
        self.assertEqual(response.status_code, 200)
        latex = response.json()["latex"]
        self.assertIn(r"\begin{abstract}", latex)
        self.assertIn("This is the abstract", latex)
        self.assertIn(r"\section{Introduction}", latex)
        self.assertIn(r"\subsection{Background}", latex)
        self.assertIn(r"1\textsuperscript{st} Dr. Researcher", latex)

        response = self.client.get(f"/api/document/{doc_id}/export/latex")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/zip")
