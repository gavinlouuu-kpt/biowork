import json

import pytest
from django.test import TestCase
from django.urls import reverse
from django.utils.http import urlencode
from io_storages.tests.factories import S3ImportStorageFactory
from rest_framework import status
from rest_framework.test import APIClient
from tasks.models import Task

from .factories import ProjectFactory


class TestProjectCountsListAPI(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.project_1 = ProjectFactory()
        cls.project_2 = ProjectFactory(organization=cls.project_1.organization)
        Task.objects.create(project=cls.project_1, data={'text': 'Task 1'})
        Task.objects.create(project=cls.project_1, data={'text': 'Task 2'})
        Task.objects.create(project=cls.project_2, data={'text': 'Task 3'})

    def get_url(self, **params):
        return f'{reverse("projects:api:project-counts-list")}?{urlencode(params)}'

    def test_get_counts(self):
        client = APIClient()
        client.force_authenticate(user=self.project_1.created_by)
        response = client.get(self.get_url(include='id,task_number,finished_task_number,total_predictions_number'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 2)
        expected = [
            {
                'id': self.project_1.id,
                'task_number': 2,
                'finished_task_number': 0,
                'total_predictions_number': 0,
            },
            {
                'id': self.project_2.id,
                'task_number': 1,
                'finished_task_number': 0,
                'total_predictions_number': 0,
            },
        ]
        actual = sorted(response.json()['results'], key=lambda d: d['id'])
        self.assertEqual(actual, expected)


@pytest.fixture
def run_inference_jobs_inline(mocker):
    def run_inline(job, *args, **kwargs):
        kwargs.pop('queue_name', None)
        kwargs.pop('job_timeout', None)
        return job(*args, **kwargs)

    mocker.patch('projects.api.start_job_async_or_sync', side_effect=run_inline)


@pytest.mark.django_db
def test_yolo_sam2_inference_endpoint_triggers_external_pipeline(
    settings,
    mocker,
    run_inference_jobs_inline,
):
    settings.BIOWORK_INFERENCE_PIPELINE_URL = 'https://pipeline.example/run'
    settings.BIOWORK_INFERENCE_PIPELINE_TOKEN = 'secret-token'
    settings.BIOWORK_MLFLOW_TRACKING_URI = 'https://mlflow.example'
    settings.BIOWORK_MLFLOW_EXPERIMENT_NAME = 'biowork-yolo-training'
    settings.BIOWORK_MLFLOW_PROJECT_EXPERIMENT_NAME_TEMPLATE = '/data/server/yolo_autotrain/project_{project_id}/runs'
    settings.BIOWORK_MLFLOW_MODEL_ARTIFACT_PATH = 'weights'

    project = ProjectFactory(
        label_config='<View><Image name="image" value="$image"/></View>',
        title='pipeline project',
    )
    storage = S3ImportStorageFactory(
        project=project,
        title='RustFS dataset',
        bucket='datasets',
        prefix=f'biowork/projects/{project.id}',
        s3_endpoint='https://rustfs.example',
    )
    client = APIClient()
    client.force_authenticate(user=project.created_by)

    run_payload = {
        'info': {
            'run_id': 'e58d20c1e77f4cd0894e91c82974f368',
            'status': 'FINISHED',
            'start_time': 123456789,
            'artifact_uri': 's3://mlflow-artifacts/1/e58d20c1e77f4cd0894e91c82974f368/artifacts',
        },
        'data': {
            'params': [
                {'key': 'project_id', 'value': str(project.id)},
                {'key': 'model_version', 'value': 'custom-yolo-2026-05-18'},
            ],
            'tags': [
                {'key': 'biowork.project_id', 'value': str(project.id)},
                {'key': 'mlflow.runName', 'value': 'project training run'},
            ],
        },
    }
    mlflow_response = mocker.Mock()
    mlflow_response.raise_for_status.return_value = None
    mlflow_response.json.side_effect = [
        {'experiment': {'experiment_id': '7'}},
        {'experiment': {'experiment_id': '8'}},
        {'runs': [run_payload]},
        {'runs': [run_payload]},
        {'runs': []},
        {'runs': []},
    ]
    mlflow_request_mock = mocker.patch('projects.api.requests.request', return_value=mlflow_response)

    response_mock = mocker.Mock()
    response_mock.status_code = status.HTTP_202_ACCEPTED
    response_mock.json.return_value = {'job_id': 'pipeline-1'}
    response_mock.raise_for_status.return_value = None
    post_mock = mocker.patch('projects.api.requests.post', return_value=response_mock)

    response = client.post(
        f'/api/projects/{project.id}/yolo-sam2-inference/',
        data=json.dumps(
            {
                'dataset_storage_key': f's3:{storage.id}',
                'model_run_id': 'e58d20c1e77f4cd0894e91c82974f368',
                'parameters': {'confidence': 0.4},
            }
        ),
        content_type='application/json',
    )

    assert response.status_code == status.HTTP_200_OK
    payload = response.json()
    assert payload['status'] == 'triggered'
    assert payload['pipeline_response']['status_code'] == status.HTTP_202_ACCEPTED
    assert payload['pipeline_response']['response'] == {'job_id': 'pipeline-1'}

    assert mlflow_request_mock.call_count == 6
    assert mlflow_request_mock.call_args_list[0].kwargs['params']['experiment_name'] == 'biowork-yolo-training'
    assert mlflow_request_mock.call_args_list[1].kwargs['params']['experiment_name'] == (
        f'/data/server/yolo_autotrain/project_{project.id}/runs'
    )
    assert mlflow_request_mock.call_args_list[2].kwargs['json']['filter'] == (
        f"tags.`biowork.project_id` = '{project.id}'"
    )
    assert mlflow_request_mock.call_args_list[3].kwargs['json']['filter'] == f"params.`project_id` = '{project.id}'"

    post_mock.assert_called_once()
    _, kwargs = post_mock.call_args
    assert kwargs['headers']['Authorization'] == 'Bearer secret-token'
    assert kwargs['json']['project_id'] == project.id
    assert kwargs['json']['project_title'] == 'pipeline project'
    assert kwargs['json']['dataset_prefix'] == f'biowork/projects/{project.id}'
    assert kwargs['json']['dataset_storage']['key'] == f's3:{storage.id}'
    assert kwargs['json']['dataset_storage']['bucket'] == 'datasets'
    assert kwargs['json']['dataset_storage']['endpoint_url'] == 'https://rustfs.example'
    assert kwargs['json']['model_uri'] == 'runs:/e58d20c1e77f4cd0894e91c82974f368/weights'
    assert kwargs['json']['model_run']['run_id'] == 'e58d20c1e77f4cd0894e91c82974f368'
    assert kwargs['json']['label_config'] == project.label_config
    assert kwargs['json']['parameters'] == {'confidence': 0.4}


@pytest.mark.django_db
def test_yolo_sam2_inference_endpoint_lists_project_context(settings, mocker):
    settings.BIOWORK_MLFLOW_TRACKING_URI = 'https://mlflow.example'
    settings.BIOWORK_MLFLOW_EXPERIMENT_NAME = 'biowork-yolo-training'
    settings.BIOWORK_MLFLOW_PROJECT_EXPERIMENT_NAME_TEMPLATE = '/data/server/yolo_autotrain/project_{project_id}/runs'
    settings.BIOWORK_MLFLOW_MODEL_ARTIFACT_PATH = 'weights'

    project = ProjectFactory(label_config='<View></View>', title='pipeline project')
    storage = S3ImportStorageFactory(
        project=project,
        title='RustFS dataset',
        bucket='datasets',
        prefix=f'biowork/projects/{project.id}',
        s3_endpoint='https://rustfs.example',
    )
    run_payload = {
        'info': {'run_id': 'run-1', 'status': 'FINISHED', 'start_time': 123456789},
        'data': {
            'params': [{'key': 'project_id', 'value': str(project.id)}],
            'tags': [{'key': 'biowork.project_id', 'value': str(project.id)}],
        },
    }
    mlflow_response = mocker.Mock()
    mlflow_response.raise_for_status.return_value = None
    mlflow_response.json.side_effect = [
        {'experiment': {'experiment_id': '7'}},
        {'experiment': {'experiment_id': '8'}},
        {'runs': []},
        {'runs': []},
        {'runs': [run_payload]},
        {'runs': []},
    ]
    mocker.patch('projects.api.requests.request', return_value=mlflow_response)

    client = APIClient()
    client.force_authenticate(user=project.created_by)

    response = client.get(f'/api/projects/{project.id}/yolo-sam2-inference/')

    assert response.status_code == status.HTTP_200_OK
    payload = response.json()
    assert payload['dataset_storage']['key'] == f's3:{storage.id}'
    assert payload['dataset_storages'][0]['uri'] == f's3://datasets/biowork/projects/{project.id}'
    assert payload['model_runs'][0]['run_id'] == 'run-1'
    assert payload['model_runs'][0]['model_uri'] == 'runs:/run-1/weights'
    assert payload['mlflow']['experiment_name'] == 'biowork-yolo-training'
    assert payload['mlflow']['project_experiment_name'] == f'/data/server/yolo_autotrain/project_{project.id}/runs'


@pytest.mark.django_db
def test_yolo_sam2_inference_endpoint_requires_model_run_id(settings):
    settings.BIOWORK_INFERENCE_PIPELINE_URL = 'https://pipeline.example/run'
    project = ProjectFactory(label_config='<View></View>', title='pipeline project')
    client = APIClient()
    client.force_authenticate(user=project.created_by)

    response = client.post(
        f'/api/projects/{project.id}/yolo-sam2-inference/',
        data=json.dumps({}),
        content_type='application/json',
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'model_run_id' in response.json()
