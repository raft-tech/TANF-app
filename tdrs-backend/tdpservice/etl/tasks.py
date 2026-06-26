"""Celery tasks for ETL pipelines."""

from celery import shared_task

from tdpservice.etl.models import ETLPipelineRun
from tdpservice.etl.runner import NodeExecutor, PipelineRunScheduler
from tdpservice.etl.scheduler import schedule_statistical_weights_run


@shared_task(name="tdpservice.etl.tasks.launch_pipeline_run")
def launch_pipeline_run(pipeline_run_id: int):
    """Launch a pipeline run by queueing its execution graph."""
    result = PipelineRunScheduler.for_run_id(pipeline_run_id).launch()
    return {"pipeline_run_id": pipeline_run_id, "task_id": result.id}


@shared_task(name="tdpservice.etl.tasks.execute_node")
def execute_node(pipeline_run_id: int, node_key: str):
    """Execute one ETL node."""
    return NodeExecutor.for_run_id(pipeline_run_id, node_key).execute()


@shared_task(name="tdpservice.etl.tasks.finalize_pipeline_run")
def finalize_pipeline_run(pipeline_run_id: int):
    """Finalize a pipeline run."""
    return PipelineRunScheduler.for_run_id(pipeline_run_id).finalize()


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
