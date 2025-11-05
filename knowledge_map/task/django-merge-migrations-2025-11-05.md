# Resolve Django migration conflicts (projects, tasks)

Context: Docker logs showed conflicting migrations:
- projects: 0029_alter_project_label_config vs 0030_project_search_vector_index
- tasks: 0055_task_import_tags vs 0057_annotation_proj_result_octlen_idx_async

Action taken:
- Added manual merge migrations to repo (empty operations):
  - `label_studio/projects/migrations/0031_merge_20251105_0000.py` depends on 0029_alter_project_label_config and 0030_project_search_vector_index
  - `label_studio/tasks/migrations/0058_merge_20251105_0000.py` depends on 0055_task_import_tags and 0057_annotation_proj_result_octlen_idx_async
- Rebuilt containers: `docker compose up -d --build app`
- Verified migrations applied successfully in logs.

Notes:
- The container image doesn’t expose manage.py; manual merge migration files were created in repo and then image rebuilt so entrypoint could apply them automatically.
