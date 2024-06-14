import logging
import sys

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
    Class representing a Job with attributes such as computation time, deadline, and period.

    Attributes:
        pk (str): The primary key or ID of the job.
        computation (int): The computation time required for the job.
        deadline (int): The deadline for the job.
        period (int): The period of the job.
    """
    def __init__(self, pk: str, computation: int, deadline: int, period: int):
        self.pk = pk
        self.computation = computation
        self.deadline = deadline
        self.period = period

    @property
    def utility(self) -> float:
        """
        Calculate the utility of the job.

        Returns:
            float: The utility of the job.
        """
        return self.computation / self.period

    def __str__(self):
        """
        String representation of the job.

        Returns:
            str: The primary key of the job.
        """
        return self.pk
