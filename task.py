import logging
import sys
import time

from job import Job

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


class Task:
    """
    Class representing a Task derived from a Job.

    Attributes:
        job (Job): The job associated with the task.
        left_execution (int): Remaining execution time for the task.
        arrival (int): Arrival time of the task.
    """
    def __init__(self, job: Job, arrival: int):
        self.job = job
        self.left_execution = self.job.computation
        self.arrival = arrival

    @property
    def pk(self):
        """
        Primary key for the task, combining job ID and arrival time.

        Returns:
            str: The primary key.
        """
        return f'{self.job.pk} | {self.arrival}'

    @property
    def deadline(self):
        """
        Calculate the deadline for the task based on its arrival and job's deadline.

        Returns:
            int: The deadline.
        """
        return self.arrival + self.job.deadline

    def compute(self, exec_time: int):
        """
        Simulate the computation of the task for a given execution time.

        Args:
            exec_time (int): The time to run the task.
        """
        if self.left_execution <= 0:
            return
        if self.left_execution < exec_time:
            logger.info(f'TASK {self.pk} RUNNING FOR {self.left_execution}s...')
            time.sleep(self.left_execution)
        else:
            logger.info(f'TASK {self.pk} RUNNING FOR {exec_time}s...')
            time.sleep(exec_time)
        self.left_execution -= exec_time
        if self.left_execution <= 0:
            logger.info(f'TASK {self.pk} ENDED')

    def is_done(self):
        """
        Check if the task is done.

        Returns:
            bool: True if the task has no remaining execution time, False otherwise.
        """
        return self.left_execution <= 0

    def __str__(self):
        """
        String representation of the task.

        Returns:
            str: The primary key of the task.
        """
        return self.pk
