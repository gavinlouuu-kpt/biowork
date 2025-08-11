import hashlib
import io
import json
import logging
import pathlib
import shutil
from datetime import datetime
from functools import reduce

import django_rq
from core.feature_flags import flag_set
from core.redis import redis_connected
from core.utils.common import batch
from core.utils.io import (
    SerializableGenerator,
    get_all_dirs_from_dir,
    get_all_files_from_dir,
    get_temp_dir,
)
from data_manager.models import View
from django.conf import settings
from django.core.files import File
from django.core.files import temp as tempfile
from django.db import transaction
from django.db.models import Prefetch
from django.db.models.query_utils import Q
from django.utils import dateformat, timezone
from label_studio_sdk.converter import Converter
from tasks.models import Annotation, AnnotationDraft, Task

ONLY = 'only'
EXCLUDE = 'exclude'


logger = logging.getLogger(__name__)


class ExportMixin:
    def has_permission(self, user):
        user.project = self.project  # link for activity log
        return self.project.has_permission(user)

    def get_default_title(self):
        return f"{self.project.title.replace(' ', '-')}-at-{dateformat.format(timezone.now(), 'Y-m-d-H-i')}"

    def _get_filtered_tasks(self, tasks, task_filter_options=None):
        """
        task_filter_options: None or Dict({
            view: optional int id or View
            skipped: optional None or str:("include|exclude")
            finished: optional None or str:("include|exclude")
            annotated: optional None or str:("include|exclude")
        })
        """
        if not isinstance(task_filter_options, dict):
            return tasks
        if 'view' in task_filter_options:
            try:
                value = int(task_filter_options['view'])
                prepare_params = View.objects.get(project=self.project, id=value).get_prepare_tasks_params(
                    add_selected_items=True
                )
                tab_tasks = Task.prepared.only_filtered(prepare_params=prepare_params).values_list('id', flat=True)
                tasks = tasks.filter(id__in=tab_tasks)
            except (ValueError, View.DoesNotExist) as exc:
                logger.warning(f'Incorrect view params {exc}')
        if 'skipped' in task_filter_options:
            value = task_filter_options['skipped']
            if value == ONLY:
                tasks = tasks.filter(annotations__was_cancelled=True)
            elif value == EXCLUDE:
                tasks = tasks.exclude(annotations__was_cancelled=True)
        if 'finished' in task_filter_options:
            value = task_filter_options['finished']
            if value == ONLY:
                tasks = tasks.filter(is_labeled=True)
            elif value == EXCLUDE:
                tasks = tasks.exclude(is_labeled=True)
        if 'annotated' in task_filter_options:
            value = task_filter_options['annotated']
            # if any annotation exists and is not cancelled
            if value == ONLY:
                tasks = tasks.filter(annotations__was_cancelled=False)
            elif value == EXCLUDE:
                tasks = tasks.exclude(annotations__was_cancelled=False)

        return tasks

    def _get_filtered_annotations_queryset(self, annotation_filter_options=None):
        """
        Filtering using disjunction of conditions

        annotation_filter_options: None or Dict({
            usual: optional None or bool:("true|false")
            ground_truth: optional None or bool:("true|false")
            skipped: optional None or bool:("true|false")
        })
        """
        queryset = Annotation.objects.all()
        if isinstance(annotation_filter_options, dict):
            q_list = []
            if annotation_filter_options.get('usual'):
                q_list.append(Q(was_cancelled=False, ground_truth=False))
            if annotation_filter_options.get('ground_truth'):
                q_list.append(Q(ground_truth=True))
            if annotation_filter_options.get('skipped'):
                q_list.append(Q(was_cancelled=True))
            if q_list:
                q = reduce(lambda x, y: x | y, q_list)
                queryset = queryset.filter(q)

        # pre-select completed_by user info
        queryset = queryset.select_related('completed_by')
        # prefetch reviews in LSE
        if hasattr(queryset.model, 'reviews'):
            from reviews.models import AnnotationReview

            queryset = queryset.prefetch_related(
                Prefetch('reviews', queryset=AnnotationReview.objects.select_related('created_by'))
            )

        return queryset

    @staticmethod
    def _get_export_serializer_option(serialization_options):
        options = {'expand': []}
        if isinstance(serialization_options, dict):
            if (
                'drafts' in serialization_options
                and isinstance(serialization_options['drafts'], dict)
                and not serialization_options['drafts'].get('only_id')
            ):
                options['expand'].append('drafts')
            if (
                'predictions' in serialization_options
                and isinstance(serialization_options['predictions'], dict)
                and not serialization_options['predictions'].get('only_id')
            ):
                options['expand'].append('predictions')
            if 'annotations__completed_by' in serialization_options and not serialization_options[
                'annotations__completed_by'
            ].get('only_id'):
                options['expand'].append('annotations.completed_by')
            options['context'] = {'interpolate_key_frames': settings.INTERPOLATE_KEY_FRAMES}
            if 'interpolate_key_frames' in serialization_options:
                options['context']['interpolate_key_frames'] = serialization_options['interpolate_key_frames']
            if serialization_options.get('include_annotation_history') is False:
                options['omit'] = ['annotations.history']
            # download resources
            if serialization_options.get('download_resources') is True:
                options['download_resources'] = True
        return options

    def get_task_queryset(self, ids, annotation_filter_options):
        annotations_qs = self._get_filtered_annotations_queryset(annotation_filter_options=annotation_filter_options)

        return (
            Task.objects.filter(id__in=ids)
            .select_related('file_upload')  # select_related more efficient for regular foreign-key relationship
            .prefetch_related(
                Prefetch('annotations', queryset=annotations_qs),
                Prefetch('drafts', queryset=AnnotationDraft.objects.select_related('user')),
                'comment_authors',
            )
        )

    def get_export_data(self, task_filter_options=None, annotation_filter_options=None, serialization_options=None):
        """
        serialization_options: None or Dict({
            drafts: optional
                None
                    or
                Dict({
                    only_id: true/false
                })
            predictions: optional
                None
                    or
                Dict({
                    only_id: true/false
                })
            annotations__completed_by: optional
                None
                    or
                Dict({
                    only_id: true/false
                })
        })
        """
        from .serializers import ExportDataSerializer

        logger.debug('Run get_task_queryset')

        start = datetime.now()
        with transaction.atomic():
            # TODO: make counters from queryset
            # counters = Project.objects.with_counts().filter(id=self.project.id)[0].get_counters()
            self.counters = {'task_number': 0}
            all_tasks = self.project.tasks
            logger.debug('Tasks filtration')
            task_ids = list(
                self._get_filtered_tasks(all_tasks, task_filter_options=task_filter_options)
                .distinct()
                .values_list('id', flat=True)
                .iterator(chunk_size=1000)
            )
            base_export_serializer_option = self._get_export_serializer_option(serialization_options)
            i = 0

            if flag_set('fflag_fix_back_plt_807_batch_size_26062025_short', self.project.organization.created_by):
                BATCH_SIZE = self.project.get_task_batch_size()
            else:
                BATCH_SIZE = settings.BATCH_SIZE

            for ids in batch(task_ids, BATCH_SIZE):
                i += 1
                tasks = list(self.get_task_queryset(ids, annotation_filter_options))
                logger.debug(f'Batch: {i*BATCH_SIZE}')
                if isinstance(task_filter_options, dict) and task_filter_options.get('only_with_annotations'):
                    tasks = [task for task in tasks if task.annotations.exists()]

                if serialization_options and serialization_options.get('include_annotation_history') is True:
                    task_ids = [task.id for task in tasks]
                    annotation_ids = Annotation.objects.filter(task_id__in=task_ids).values_list('id', flat=True)
                    base_export_serializer_option = self.update_export_serializer_option(
                        base_export_serializer_option, annotation_ids
                    )

                serializer = ExportDataSerializer(tasks, many=True, **base_export_serializer_option)
                self.counters['task_number'] += len(tasks)
                for task in serializer.data:
                    yield task
        duration = datetime.now() - start
        logger.info(
            f'{self.counters["task_number"]} tasks from project {self.project_id} exported in {duration.total_seconds():.2f} seconds'
        )

    def update_export_serializer_option(self, base_export_serializer_option, annotation_ids):
        return base_export_serializer_option

    @staticmethod
    def eval_md5(file):
        md5_object = hashlib.md5()   # nosec
        block_size = 128 * md5_object.block_size
        chunk = file.read(block_size)
        while chunk:
            md5_object.update(chunk)
            chunk = file.read(block_size)
        md5 = md5_object.hexdigest()
        return md5

    def save_file(self, file, md5):
        now = datetime.now()
        file_name = f'project-{self.project.id}-at-{now.strftime("%Y-%m-%d-%H-%M")}-{md5[0:8]}.json'
        file_path = f'{self.project.id}/{file_name}'  # finally file will be in settings.DELAYED_EXPORT_DIR/self.project.id/file_name
        file_ = File(file, name=file_path)
        self.file.save(file_path, file_)
        self.md5 = md5
        self.save(update_fields=['file', 'md5', 'counters'])

    def export_to_file(self, task_filter_options=None, annotation_filter_options=None, serialization_options=None):
        logger.debug(
            f'Run export for {self.id} with params:\n'
            f'task_filter_options: {task_filter_options}\n'
            f'annotation_filter_options: {annotation_filter_options}\n'
            f'serialization_options: {serialization_options}\n'
        )
        try:
            iter_json = json.JSONEncoder(ensure_ascii=False).iterencode(
                SerializableGenerator(
                    self.get_export_data(
                        task_filter_options=task_filter_options,
                        annotation_filter_options=annotation_filter_options,
                        serialization_options=serialization_options,
                    )
                )
            )
            with tempfile.NamedTemporaryFile(suffix='.export.json', dir=settings.FILE_UPLOAD_TEMP_DIR) as file:
                for chunk in iter_json:
                    encoded_chunk = chunk.encode('utf-8')
                    file.write(encoded_chunk)
                file.seek(0)

                md5 = self.eval_md5(file)
                self.save_file(file, md5)

            self.status = self.Status.COMPLETED
            self.save(update_fields=['status'])

        except Exception as e:
            self.status = self.Status.FAILED
            self.save(update_fields=['status'])
            logger.exception('Export was failed: %s', e)
        finally:
            self.finished_at = datetime.now()
            self.save(update_fields=['finished_at'])

    def run_file_exporting(self, task_filter_options=None, annotation_filter_options=None, serialization_options=None):
        if self.status == self.Status.IN_PROGRESS:
            logger.warning('Try to export with in progress stage')
            return

        self.status = self.Status.IN_PROGRESS
        self.save(update_fields=['status'])

        if redis_connected():
            queue = django_rq.get_queue('default')
            queue.enqueue(
                export_background,
                self.id,
                task_filter_options,
                annotation_filter_options,
                serialization_options,
                on_failure=set_export_background_failure,
                job_timeout='3h',  # 3 hours
            )
        else:
            self.export_to_file(
                task_filter_options=task_filter_options,
                annotation_filter_options=annotation_filter_options,
                serialization_options=serialization_options,
            )

    def convert_file(self, to_format, download_resources=False, hostname=None):
        with get_temp_dir() as tmp_dir:
            OUT = 'out'
            out_dir = pathlib.Path(tmp_dir) / OUT
            out_dir.mkdir(mode=0o700, parents=True, exist_ok=True)

            input_name = pathlib.Path(self.file.name).name
            input_file_path = pathlib.Path(tmp_dir) / input_name

            # Write snapshot JSON to local temp path
            with open(input_file_path, 'wb') as file_:
                file_.write(self.file.open().read())

            # Custom converter for mask statistics and crops
            if to_format == 'MASK_STATS':
                try:
                    self._convert_to_mask_stats(input_file_path, out_dir)
                except Exception as exc:
                    logger.exception('Failed to generate MASK_STATS: %s', exc)
                    return None
            else:
                # Fallback to standard converter
                converter = Converter(
                    config=self.project.get_parsed_config(),
                    project_dir=None,
                    upload_dir=out_dir,
                    download_resources=download_resources,
                    # for downloading resource we need access to the API
                    access_token=self.project.organization.created_by.auth_token.key,
                    hostname=hostname,
                )
                converter.convert(input_file_path, out_dir, to_format, is_dir=False)

            files = get_all_files_from_dir(out_dir)
            dirs = get_all_dirs_from_dir(out_dir)

            if len(files) == 0 and len(dirs) == 0:
                return None
            elif len(files) == 1 and len(dirs) == 0:
                output_file = files[0]
                filename = pathlib.Path(input_name).stem + pathlib.Path(output_file).suffix
            else:
                shutil.make_archive(out_dir, 'zip', out_dir)
                output_file = pathlib.Path(tmp_dir) / (str(out_dir.stem) + '.zip')
                filename = pathlib.Path(input_name).stem + '.zip'

            with open(output_file, mode='rb') as f:
                return File(
                    io.BytesIO(f.read()),
                    name=filename,
                )

    def _convert_to_mask_stats(self, input_file_path: pathlib.Path, out_dir: pathlib.Path) -> None:
        """Generate per-mask statistics and cropped images.

        Creates a text file mask_stats.txt alongside cropped PNGs in out_dir.
        """
        from PIL import Image, ImageDraw, ImageStat

        # Load tasks from snapshot JSON
        with open(input_file_path, 'r', encoding='utf-8') as fh:
            tasks_data = json.load(fh)

        stats_lines = [
            'task_id,annotation_id,mask_index,area_px,mean_intensity,bbox_width,bbox_height,crop_filename'
        ]

        for task_entry in tasks_data:
            task_id = task_entry.get('id')
            annotations = task_entry.get('annotations') or []

            # Resolve the task from DB to access the original uploaded file
            task_obj = Task.objects.filter(id=task_id).select_related('file_upload').first()
            if task_obj is None or getattr(task_obj, 'file_upload', None) is None:
                logger.warning('MASK_STATS: Skip task %s because original file is unavailable', task_id)
                continue

            try:
                file_field = task_obj.file_upload.file
                with file_field.open('rb') as image_fh:
                    image_bytes = image_fh.read()
                image = Image.open(io.BytesIO(image_bytes))
                # Preserve color information for crops; grayscale will be derived per-stat later
                if image.mode not in ('RGB', 'RGBA'):
                    image = image.convert('RGBA')
            except Exception as exc:
                logger.warning('MASK_STATS: Failed to open image for task %s: %s', task_id, exc)
                continue

            image_width, image_height = image.size

            mask_counter = 0
            for annotation in annotations:
                annotation_id = annotation.get('id')
                results = annotation.get('result') or []
                for result in results:
                    result_type = result.get('type')
                    value = result.get('value') or {}

                    # Build a binary mask aligned to the image size
                    mask = Image.new('L', (image_width, image_height), 0)
                    draw = ImageDraw.Draw(mask)

                    created_mask = False

                    if result_type == 'polygonlabels' and 'points' in value:
                        points = value.get('points') or []
                        if isinstance(points, list) and len(points) >= 3:
                            poly = []
                            for x, y in points:
                                # points can be either 0..100 or 0..1
                                if x <= 1.0 and y <= 1.0:
                                    px = x * image_width
                                    py = y * image_height
                                else:
                                    px = x / 100.0 * image_width
                                    py = y / 100.0 * image_height
                                poly.append((px, py))
                            draw.polygon(poly, fill=255)
                            created_mask = True

                    elif result_type == 'rectanglelabels' and all(k in value for k in ('x', 'y', 'width', 'height')):
                        # rectangle values are in percents 0..100
                        rx = value['x'] / 100.0 * image_width
                        ry = value['y'] / 100.0 * image_height
                        rw = value['width'] / 100.0 * image_width
                        rh = value['height'] / 100.0 * image_height
                        draw.rectangle([(rx, ry), (rx + rw, ry + rh)], fill=255)
                        created_mask = True

                    elif result_type == 'brushlabels' and 'rle' in value:
                        # Attempt to decode simple RLE provided as counts list with width/height
                        rle_counts = value.get('rle')
                        rle_height = value.get('height') or (value.get('size') or [None, None])[0]
                        rle_width = value.get('width') or (value.get('size') or [None, None])[1]
                        if isinstance(rle_counts, list) and rle_height and rle_width:
                            total = rle_height * rle_width
                            flat = []
                            current = 0
                            for idx, count in enumerate(rle_counts):
                                pixel_value = 255 if (idx % 2 == 1) else 0
                                flat.extend([pixel_value] * int(count))
                                current += int(count)
                                if current >= total:
                                    break
                            if len(flat) < total:
                                flat.extend([0] * (total - len(flat)))
                            # Build mask from flat list and resize to image size if needed
                            rle_mask = Image.frombytes('L', (rle_width, rle_height), bytes(flat))
                            if (rle_width, rle_height) != (image_width, image_height):
                                rle_mask = rle_mask.resize((image_width, image_height), resample=Image.NEAREST)
                            mask = rle_mask
                            created_mask = True

                    if not created_mask:
                        continue

                    bbox = mask.getbbox()
                    if not bbox:
                        continue

                    # Compute statistics
                    gray = image.convert('L')
                    stat = ImageStat.Stat(gray, mask=mask)
                    mean_intensity = stat.mean[0] if stat.count[0] > 0 else 0.0
                    area_px = int(ImageStat.Stat(mask).sum[0] / 255)

                    # Prepare crop with transparency outside the mask
                    x0, y0, x1, y1 = bbox
                    crop_image = image.crop(bbox).convert('RGBA')
                    crop_mask = mask.crop(bbox)
                    # Apply mask as alpha
                    crop_image.putalpha(crop_mask)

                    mask_counter += 1
                    crop_filename = f'task-{task_id}_ann-{annotation_id}_mask-{mask_counter}.png'
                    crop_path = out_dir / crop_filename
                    crop_image.save(crop_path, format='PNG')

                    bbox_width = x1 - x0
                    bbox_height = y1 - y0
                    stats_lines.append(
                        f'{task_id},{annotation_id},{mask_counter},{area_px},{mean_intensity:.4f},{bbox_width},{bbox_height},{crop_filename}'
                    )

        # Write the stats summary
        stats_path = out_dir / 'mask_stats.txt'
        with open(stats_path, 'w', encoding='utf-8') as sf:
            sf.write('\n'.join(stats_lines))


def export_background(
    export_id, task_filter_options, annotation_filter_options, serialization_options, *args, **kwargs
):
    from data_export.models import Export

    Export.objects.get(id=export_id).export_to_file(
        task_filter_options,
        annotation_filter_options,
        serialization_options,
    )


def set_export_background_failure(job, connection, type, value, traceback):
    from data_export.models import Export

    export_id = job.args[0]
    Export.objects.filter(id=export_id).update(status=Export.Status.FAILED)
