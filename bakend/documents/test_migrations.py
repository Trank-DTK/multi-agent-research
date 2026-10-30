from django.db.migrations.loader import MigrationLoader
from django.test import SimpleTestCase


class DocumentMigrationGraphTests(SimpleTestCase):
    def test_document_migrations_have_no_conflicting_heads(self):
        loader = MigrationLoader(None)
        self.assertNotIn("documents", loader.detect_conflicts())
        self.assertEqual(len(loader.graph.leaf_nodes("documents")), 1)

    def test_final_plan_keeps_both_existing_migration_branches(self):
        loader = MigrationLoader(None)
        leaves = loader.graph.leaf_nodes("documents")
        self.assertEqual(len(leaves), 1)
        plan = loader.graph.forwards_plan(leaves[0])
        self.assertIn(("documents", "0002_enable_pgvector"), plan)
        self.assertIn(("documents", "0004_optional_embedding"), plan)
        self.assertIn(("documents", "0001_initial"), plan)
