"""
Benchmark: Measure query count and response time for loading a task
with many polygon annotations (simulating FastSAM/SAM output).
"""
import json
import time

from django.test.utils import override_settings
from organizations.tests.factories import OrganizationFactory
from projects.tests.factories import ProjectFactory
from rest_framework.test import APITestCase
from tasks.models import Annotation
from tasks.tests.factories import TaskFactory


def make_polygon_result(num_points=30):
    """Create a polygon annotation result similar to FastSAM/SAM output."""
    points = [[i * (100.0 / num_points), (i * 7.3) % 100] for i in range(num_points)]
    return [
        {
            'id': f'poly_{id(points)}',
            'from_name': 'label',
            'to_name': 'image',
            'type': 'polygonlabels',
            'value': {
                'points': points,
                'polygonlabels': ['Object'],
            },
            'meta': {
                'area': 919,
                'bbox': {'x': 10, 'y': 20, 'width': 150, 'height': 200},
            },
        }
    ]


class TestAnnotationLoadingPerformance(APITestCase):
    NUM_ANNOTATIONS = 200

    @classmethod
    def setUpTestData(cls):
        cls.organization = OrganizationFactory()
        cls.project = ProjectFactory(organization=cls.organization)
        cls.user = cls.organization.created_by

        # Create a task with many polygon annotations
        cls.task = TaskFactory(
            project=cls.project,
            data={'image': 'https://example.com/image.jpg'},
        )
        annotations = []
        for i in range(cls.NUM_ANNOTATIONS):
            annotations.append(
                Annotation(
                    task=cls.task,
                    project=cls.project,
                    completed_by=cls.user,
                    result=make_polygon_result(num_points=30),
                )
            )
        Annotation.objects.bulk_create(annotations)

    def test_task_loading_query_count(self):
        """Measure the number of SQL queries when loading a task with 200 annotations."""
        from django.test.utils import CaptureQueriesContext
        from django.db import connection

        self.client.force_authenticate(user=self.user)

        with CaptureQueriesContext(connection) as ctx:
            t0 = time.perf_counter()
            response = self.client.get(f'/api/tasks/{self.task.id}/')
            elapsed_ms = (time.perf_counter() - t0) * 1000

        assert response.status_code == 200

        data = response.json()
        num_annotations = len(data.get('annotations', []))

        # Print metrics
        print(f'\n{"=" * 60}')
        print(f'ANNOTATION LOADING PERFORMANCE METRICS')
        print(f'{"=" * 60}')
        print(f'Annotations in task:     {num_annotations}')
        print(f'Total SQL queries:       {len(ctx)}')
        print(f'Response time:           {elapsed_ms:.1f} ms')
        print(f'Response size:           {len(json.dumps(data)) / 1024:.1f} KB')
        print(f'{"=" * 60}')

        # Print query breakdown
        query_tables = {}
        for q in ctx:
            sql = q['sql']
            # Rough table extraction
            if 'FROM' in sql:
                parts = sql.split('FROM')[1].strip().split()[0].strip('"')
                query_tables[parts] = query_tables.get(parts, 0) + 1

        print(f'\nQuery breakdown by table:')
        for table, count in sorted(query_tables.items(), key=lambda x: -x[1]):
            print(f'  {table}: {count} queries')

        # Show sample htx_user queries to debug N+1 patterns
        user_queries = [q['sql'] for q in ctx if 'htx_user' in q['sql']]
        if user_queries:
            print(f'\nhtx_user queries ({len(user_queries)} total, showing first 3):')
            for q in user_queries[:3]:
                if 'WHERE' in q:
                    where = q[q.index('WHERE'):]
                    print(f'  ...{where[:150]}')
                else:
                    print(f'  {q[:150]}')

        # Check for N+1 pattern: should NOT have one query per annotation
        # With the optimization, we should have far fewer than NUM_ANNOTATIONS queries
        assert len(ctx) < self.NUM_ANNOTATIONS, (
            f'Potential N+1 query detected: {len(ctx)} queries for {self.NUM_ANNOTATIONS} annotations'
        )

        # Check that annotations_results and predictions_results are empty strings
        # (confirming the expensive ArrayAgg was skipped)
        assert data.get('annotations_results') == '', (
            f"Expected annotations_results to be empty string, got: {data.get('annotations_results')!r}"
        )
        assert data.get('predictions_results') == '', (
            f"Expected predictions_results to be empty string, got: {data.get('predictions_results')!r}"
        )

        # Verify all annotations were returned correctly
        assert num_annotations == self.NUM_ANNOTATIONS, (
            f'Expected {self.NUM_ANNOTATIONS} annotations, got {num_annotations}'
        )

        # Check that annotation data is intact
        first_ann = data['annotations'][0]
        assert 'result' in first_ann
        assert first_ann['result'][0]['type'] == 'polygonlabels'
        assert len(first_ann['result'][0]['value']['points']) == 30
