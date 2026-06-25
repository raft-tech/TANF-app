"""Celery tasks for ETL pipelines."""

from celery import shared_task

from tdpservice.etl import runner
from tdpservice.etl.models import ETLPipelineRun
from tdpservice.etl.scheduler import schedule_statistical_weights_run


@shared_task(name="tdpservice.etl.tasks.launch_pipeline_run")
def launch_pipeline_run(pipeline_run_id: int):
    """Launch a pipeline run by queueing its first execution layer."""
    result = runner.launch_pipeline_run(pipeline_run_id)
    return {"pipeline_run_id": pipeline_run_id, "task_id": result.id}


@shared_task(name="tdpservice.etl.tasks.advance_pipeline_run")
def advance_pipeline_run(pipeline_run_id: int, layer_index: int):
    """Queue the next ETL layer after the prior layer succeeds."""
    return runner.advance_pipeline_run(pipeline_run_id, layer_index)


@shared_task(name="tdpservice.etl.tasks.execute_node")
def execute_node(pipeline_run_id: int, node_key: str):
    """Execute one ETL node."""
    return runner.execute_node(pipeline_run_id, node_key)


@shared_task(name="tdpservice.etl.tasks.finalize_pipeline_run")
def finalize_pipeline_run(pipeline_run_id: int):
    """Finalize a pipeline run."""
    return runner.finalize_pipeline_run(pipeline_run_id)


@shared_task(name="tdpservice.etl.tasks.schedule_statistical_weights")
def schedule_statistical_weights():
    """Run the daily scheduler check for statistical weights."""
    pipeline_run = schedule_statistical_weights_run()
    if not pipeline_run:
        return {"created": False}

    launch_pipeline_run.delay(pipeline_run.id)
    return {"created": True, "pipeline_run_id": pipeline_run.id}


def enqueue_pipeline_run(pipeline_run: ETLPipelineRun):
    """Queue a pipeline run launcher task."""
    return launch_pipeline_run.delay(pipeline_run.id)
