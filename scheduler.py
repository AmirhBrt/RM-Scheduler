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
    def get_job(queue: list[Job], now: float) -> Job | None:
        """
        Get the next job to execute from the queue.

        Args:
            queue (list[Job]): The list of jobs.
            now (int): The current time.

        Returns:
            Job: The next task to execute.

        Raises:
            ValueError: when a job is not done until its deadline.
        """
        arrived_jobs: list[Job] = []
        for job in queue:
            if job.arrival > now:
                break
            arrived_jobs.append(job)
        for job in arrived_jobs:
            if job.deadline < now and not job.is_done():
                raise ValueError
        arrived_jobs.sort(key=lambda _: _.task.period)
        for j in arrived_jobs:
            print(j)
        try:
            return arrived_jobs.pop(0)
        except IndexError:
            return None

    @staticmethod
    def idle_cpu_until_next_job_arrives(queue: list[Job], now: int) -> int:
        """
        Handle the CPU being idle until the next job arrives.

        Args:
            queue (list[Job]): The list of jobs.
            now (int): The current time.

        Returns:
            int: The updated time after the CPU idle period.
        """
        next_arrival = min([t.arrival for t in queue])
        idle_time = next_arrival - now
        logger.info(f'CPU IS GOING IDLE FOR {idle_time}s UNTIL NEXT TASK ARRIVES')
        time.sleep(idle_time)
        now += idle_time
        return now

    @staticmethod
    def get_job_exec_time(queue: list[Job], job: Job, now: int) -> int:
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

    @staticmethod
    def execute_task(exec_time: int, job: Job, now: int) -> int:
        """
        Execute a job for the given execution time.

        Args:
            exec_time (int): The execution time.
            job (Job): The job to execute.
            now (int): The current time.

        Returns:
            int: The updated time after job execution.
        """
        job.compute(exec_time)
        now += exec_time
        return now

    def is_feasible(self, log=True) -> bool:
        utilization_sum = sum(task.utility for task in self.tasks)
        if utilization_sum < self.utilization_lub():
            if log:
                logger.info('TASKS ARE SCHEDULABLE DUE TO LEAST UPPER BOUND!')
            return True
        elif utilization_sum >= 1:
            if log:
                logger.error('TASKS ARE NOT SCHEDULABLE!')
            return False
        if log:
            logger.info('TASKS MIGHT BE SCHEDULABLE WITH RM SCHEDULER BUT NOT SURE!')
        return True

    def schedule(self) -> None:
        """
        Schedule the jobs using the EDF algorithm in a hyper-period.

        Returns:
            None
        """
        if not self.is_feasible(log=False):
            logger.error('TASKS ARE NOT SCHEDULABLE ACCORDING TO THE GIVEN CONFIG!')
            return

        queue = sorted(list(self.jobs), key=lambda _: _.arrival)
        now = 0
        while queue:
            logger.info(f'NOW = {now}')
            job = self.get_job(queue, now)
            if job is None:
                now = self.idle_cpu_until_next_job_arrives(queue, now)
                continue
            queue.remove(job)
            exec_time = self.get_job_exec_time(queue, job, now)
            logger.info(f'EXECUTING TASK {job.pk} FOR {exec_time}s...')
            now = self.execute_task(
                exec_time=exec_time,
                job=job,
                now=now
            )
            if job.left_execution > 0:
                queue.append(job)
                queue.sort(key=lambda _: _.arrival)
        logger.info(f'ENDED AT : {now}')
