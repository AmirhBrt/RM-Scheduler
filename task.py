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


class Task:
    """
    Class representing a Task with attributes such as computation time and period.
    """
    def __init__(self, pk: str, computation: int, period: int):
        """
        Initialize the task with given arguments.
        Arguments:
            pk (str): The primary key or ID of the task.
            computation (int): The computation time required for the task.
            period (int): The period of the task.
        """
        self.pk = pk
        self.computation = computation
        self.period = period

    @property
    def utility(self) -> float:
        """
        Calculate the utility of the task.

        Returns:
            float: The utility of the task.
        """
        return self.computation / self.period

    def __str__(self):
        """
        String representation of the task.

        Returns:
            str: The primary key of the task.
        """
        return f'<T:{self.pk}>'
