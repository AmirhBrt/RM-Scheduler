import abc
import math

from job import Job
from task import Task


class BaseScheduler(abc.ABC):
    """
    Abstract base class for a Scheduler.

    Attributes:
        tasks (set[Task]): A set of Task to be scheduled.
        jobs (set[Job]): A set of Job generated from the tasks.
    """

    def __init__(self, data: list[dict[str: float]]):
        self.tasks = self.__create_tasks(data)
        self.jobs = self.__create_jobs()

    @staticmethod
    def __create_tasks(data: list[dict[str: float]]) -> set[Task]:
        """
        Create tasks from the provided data.

        Args:
            data (list[dict[str: float]]): A list of dictionaries containing tasks details.

        Returns:
            set[Task]: A set of tasks created from the data.
        """
        tasks = set()
        for d in data:
            task = Task(
                pk=d['id'],
                computation=d['exec_time'],
                period=d['period'],
            )
            tasks.add(task)
        return tasks

    def __create_jobs(self) -> set[Job]:
        """
        Create jobs based on the tasks and their periods.

        Returns:
            set[Job]: A set of jobs created from the tasks.
        """
        hyper_period = self.get_hyper_period()
        jobs: set[Job] = set()
        for task in self.tasks:
            n = hyper_period // task.period
            for i in range(n):
                arrival = task.period * i
                jobs.add(
                    Job(task, arrival)
                )
        return jobs

    def get_hyper_period(self) -> int:
        """
        Calculate the hyper period of the tasks.

        Returns:
            int: The hyper period.
        """
        return math.lcm(*[task.period for task in self.tasks])

    @abc.abstractmethod
    def is_feasible(self) -> bool:
        """
        Check whether scheduling the jobs are feasible.

        Returns:
            bool: True if feasible, False otherwise.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def schedule(self) -> None:
        """
        Schedule the jobs in a hyper period.

        Returns:
            None
        """
        raise NotImplementedError
