from django.urls import reverse
from rest_framework import status


def test_segmentation_metrics_requires_task_id(db, client, django_user_model):
    # Basic smoke test to ensure the endpoint is wired and validates task_id
    user = django_user_model.objects.create(username="user", email="user@example.com", is_superuser=True, is_staff=True)
    client.force_login(user)

    # Create empty project via ORM to avoid depending on tavern fixtures
    from projects.models import Project

    project = Project.objects.create(title="Segmentation project", label_config="<View></View>")
    url = reverse("data_export:api-projects:project-segmentation-metrics", kwargs={"pk": project.id})

    response = client.get(url)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "task_id" in response.json()


def test_segmentation_metrics_not_found_task(db, client, django_user_model):
    user = django_user_model.objects.create(username="user2", email="user2@example.com", is_superuser=True, is_staff=True)
    client.force_login(user)

    from projects.models import Project

    project = Project.objects.create(title="Segmentation project 2", label_config="<View></View>")
    url = reverse("data_export:api-projects:project-segmentation-metrics", kwargs={"pk": project.id})

    response = client.get(url, {"task_id": 999999})
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_segmentation_metrics_empty_for_task_without_regions(db, client, django_user_model):
  user = django_user_model.objects.create(
      username="user3",
      email="user3@example.com",
      is_superuser=True,
      is_staff=True,
  )
  client.force_login(user)

  from projects.models import Project
  from tasks.models import Task

  project = Project.objects.create(title="Segmentation project 3", label_config="<View></View>")
  task = Task.objects.create(project=project, data={"image": "upload://test.png"})

  url = reverse("data_export:api-projects:project-segmentation-metrics", kwargs={"pk": project.id})
  response = client.get(url, {"task_id": task.id})

  assert response.status_code == status.HTTP_200_OK
  payload = response.json()
  assert payload["count"] == 0
  assert payload["results"] == []


