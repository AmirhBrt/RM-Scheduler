import abc
import logging
import math
import sys
import time

from job import Job
from task import Task

# Setup logging handlers for writing logs to a file and outputting to the console.
handlers = [
    logging.FileHandler(filename='tmp.log'),
    logging.StreamHandler(stream=sys.stdout),
]

logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s',
    handlers=handlers
)

logger = logging.getLogger()


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


class RMScheduler(BaseScheduler):
    def utilization_lub(self):
        n = len(self.tasks)
        return n * (2 ** (1 / n) - 1)

    @staticmethod
    def get_arrived_jobs(sorted_jobs: list[Job], now: float):
        arrived_jobs: list[Job] = []
        for job in sorted_jobs:
            if job.arrival > now:
                break
            arrived_jobs.append(job)
        arrived_jobs.sort(key=lambda j: j.task.period)
        return arrived_jobs

    @staticmethod
    def get_task_exec_time(queue: list[Job], job: Job, now: int) -> int:
        """
        Get the execution time for a job, considering higher priority jobs.

        Args:
            queue (list[Job]): The list of jobs.
            job (Job): The current job to execute.
            now (int): The current time.

        Returns:
            int: The execution time for the job.
        """
        high_priority_jobs: list[Job] = []
        for j in queue:
            if j.arrival < job.deadline and j.task.period < job.task.period and not j.is_done():
                high_priority_jobs.append(j)
        if high_priority_jobs:
            next_job = min(high_priority_jobs, key=lambda _: _.arrival)
            exec_time = min(next_job.arrival - now, job.left_execution)
        else:
            exec_time = job.left_execution
        return exec_time

    def is_feasible(self) -> bool:
        utilization_sum = sum(task.utility for task in self.tasks)
        if utilization_sum < self.utilization_lub():
            logger.info('TASKS ARE SCHEDULABLE DUE TO LEAST UPPER BOUND!')
            return True
        elif utilization_sum >= 1:
            logger.error('TASKS ARE NOT SCHEDULABLE!')
            return False
        logger.info('TASKS MIGHT BE SCHEDULABLE WITH RM SCHEDULER BUT NOT SURE!')
        return True

    def schedule(self) -> None:
        hyper_period = self.get_hyper_period()
        jobs = list(self.jobs)
        jobs.sort(key=lambda j: j.arrival)

        start_time = time.time()
        while jobs:
            now = time.time()
            if round(now - start_time) > hyper_period:
                raise ValueError
            arrived_jobs = self.get_arrived_jobs(
                jobs, round(now - start_time)
            )
            job = arrived_jobs.pop(0)
            jobs.remove(job)

            exec_time = self.get_task_exec_time(jobs, job, round(now - start_time))
            logger.info(f'EXECUTING JOB {job.pk} FOR {exec_time}s...')
            job.compute(exec_time)
            if len(jobs) > 0:
                if job.left_execution > 0:
                    jobs.append(job)
                    jobs = sorted(jobs, key=lambda j: j.arrival)
