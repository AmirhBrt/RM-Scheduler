import logging
import sys
import time

from task import Task

# Setup logging handlers for writing logs to a file and outputting to the console.
handlers = [
    logging.FileHandler(filename='tmp.log'),
    logging.StreamHandler(stream=sys.stdout)
]

logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s',
    handlers=handlers
)

logger = logging.getLogger()


class Job:
    """
    Class representing a Job derived from a Task.

    Attributes:
        task (Task): The task associated with the job.
        left_execution (int): Remaining execution time for the job.
        arrival (int): Arrival time of the job.
    """
    def __init__(self, task: Task, arrival: int):
        self.task = task
        self.left_execution = self.task.computation
        self.arrival = arrival

    @property
    def pk(self):
        """
        Primary key for the job, combining task ID and arrival time.

        Returns:
            str: The primary key.
        """
        return f'{self.task.pk} | {self.arrival}'

    @property
    def deadline(self):
        """
        Calculate the deadline for the job based on its arrival and task's period.

        Returns:
            int: The deadline.
        """
        return self.arrival + self.task.period

    def compute(self, exec_time: int):
        """
        Simulate the computation of the job for a given execution time.

        Args:
            exec_time (int): The time to run the job.
        """
        if self.left_execution <= 0:
            return
        run_time = min(self.left_execution, exec_time)
        logger.debug(f'JOB {self.pk} RUNNING FOR {run_time}s...')
        time.sleep(run_time)
        self.left_execution -= exec_time
        if self.left_execution <= 0:
            logger.info(f'TASK {self.pk} ENDED')

    def is_done(self):
        return self.left_execution <= 0

    def __str__(self):
        """
        String representation of the job.

        Returns:
            str: The primary key of the job.
        """
        return f'<J:{self.pk}>'
