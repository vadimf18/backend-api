from celery import Celery

# -------------------------------
# Celery app
# -------------------------------
celery_app = Celery(
    "worker",
    broker="amqp://guest@queue//",  # RabbitMQ broker URL
)

# -------------------------------
# Task routing
# -------------------------------
celery_app.conf.task_routes = {
    "app.worker.test_celery": {"queue": "main-queue"}
}

# Optional: additional configurations
celery_app.conf.update(
    task_acks_late=True,       # Acknowledge tasks after completion
    worker_prefetch_multiplier=1,  # Prevent task prefetching
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
)
