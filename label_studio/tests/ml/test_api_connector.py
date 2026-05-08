import pytest

from label_studio.tests.utils import make_project
from ml.api_connector import MLApi


@pytest.mark.django_db
def test_ml_api_setup_uses_organization_context_and_owner_token(business_client, ml_backend):
    project = make_project(
        config=dict(
            title='test_ml_api_setup_org_context',
            label_config='<View><Text name="text" value="$text"/></View>',
        ),
        user=business_client.user,
        use_ml_backend=False,
    )

    api = MLApi(url='http://localhost:9090')
    previous_requests_count = len(ml_backend.request_history)
    response = api.setup(project)

    assert not response.is_error
    setup_requests = [
        request for request in ml_backend.request_history[previous_requests_count:] if request.url.endswith('/setup')
    ]
    assert len(setup_requests) == 1

    payload = setup_requests[0].json()
    assert payload['organization']['id'] == project.organization_id
    assert payload['organization']['title'] == project.organization.title
    assert payload['organization']['created_by_id'] == project.organization.created_by_id
    assert payload['access_token'] == project.organization.created_by.auth_token.key
