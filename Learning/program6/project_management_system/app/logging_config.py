# app/logging_config.py
import logging
import sys


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )
# Use in routes/use cases
import logging
logger = logging.getLogger(__name__)

# Then log like this:
logger.info(f"Task created: id={task.id} owner={task.owner_id}")
logger.warning(f"Task limit reached for user {owner_id}")
logger.error(f"Failed to delete task {task_id}", exc_info=True)
