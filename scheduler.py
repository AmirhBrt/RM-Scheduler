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


class Scheduler(abc.ABC):
    """
    Abstract base class for a Scheduler.

    Attributes:
        jobs (set[Job]): A set of jobs to be scheduled.
        tasks (set[Task]): A set of tasks generated from the jobs.
    """
    def __init__(self, data: list[dict[str: float]]):
        self.jobs = self.__create_jobs(data)
        self.tasks = self.__create_tasks()

    def __create_tasks(self) -> set[Task]:
        """
        Create tasks based on the jobs and their periods.

        Returns:
            set[Task]: A set of tasks created from the jobs.
        """
        hyper_period = self.get_hyper_period()
        tasks: set[Task] = set()
        for job in self.jobs:
            n = hyper_period // job.period
            for i in range(n):
                arrival = job.period * i
                tasks.add(Task(job, arrival))
        return tasks

    def get_hyper_period(self) -> int:
        """
        Calculate the hyper period of the jobs.

        Returns:
            int: The hyper period.
        """
        return math.lcm(*[job.period for job in self.jobs])

    @staticmethod
    def __create_jobs(data: list[dict[str: float]]) -> set[Job]:
        """
        Create jobs from the provided data.

        Args:
            data (list[dict[str: float]]): A list of dictionaries containing job details.

        Returns:
            set[Job]: A set of jobs created from the data.
        """
        jobs = set()
        for d in data:
            job = Job(
                pk=d['id'],
                computation=d['execution_time'],
                deadline=d['deadline'],
                period=d['period'],
            )
            jobs.add(job)
        return jobs

    @abc.abstractmethod
    def is_feasible(self) -> bool:
        """
        Check whether scheduling the jobs is feasible.

        Returns:
            bool: True if feasible, False otherwise.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def schedule(self) -> None:
        """
        Schedule the tasks in a hyper period.

        Returns:
            None
        """
        raise NotImplementedError


class EDFScheduler(Scheduler):
    """ EDF (Earliest Deadline First) Scheduler implementation."""

    def demand_bound_function(self, t: int) -> float:
        """
        Calculate the demand bound function for a given time t.

        Args:
            t (int): The time to calculate the demand bound function for.

        Returns:
            float: The value of the demand bound function.
        """
        total_sum = 0
        for job in self.jobs:
            total_sum += job.computation * math.floor((t + job.period - job.deadline) / job.period)
        return total_sum

    def get_total_utility(self) -> float:
        """
        Get the total utility of all jobs.

        Returns:
            float: The total utility.
        """
        return sum([job.utility for job in self.jobs])

    def get_max_deadline(self) -> int:
        """
        Get the maximum deadline among all tasks.

        Returns:
            int: The maximum deadline.
        """
        return max([task.deadline for task in self.tasks])

    def get_l_star(self) -> float:
        """
        Calculate the L* value for the jobs.

        Returns:
            float: The L* value.

        Raises:
            ValueError: If any job has a utility greater than 1.
        """
        total_sum = 0
        for job in self.jobs:
            if job.utility > 1:
                raise ValueError(f'JOB {job.pk} DEADLINE IS MORE THAN ITS PERIOD!')
            total_sum += (job.period - job.deadline) * job.utility
        return total_sum / self.get_total_utility()

    def is_feasible(self, log=True) -> bool:
        """
        Check if the jobs are schedulable using the EDF algorithm.

        Args:
            log (bool): Flag to enable logging. Defaults to True.

        Returns:
            bool: True if schedulable, False otherwise.
        """
        try:
            l_star = self.get_l_star()
        except ValueError as exc:
            logger.error(exc)
            return False
        max_d = min([self.get_hyper_period(), max([l_star, self.get_max_deadline()])])
        deadlines = [task.deadline for task in list(filter(lambda task: task.deadline <= max_d, self.tasks))]
        deadlines = sorted(deadlines)
        for t in deadlines:
            dbf = self.demand_bound_function(t)
            if log:
                print(f'L = {t} \t g(0, L) = {dbf} \t result = {dbf <= t}')
            if dbf > t:
                logger.error(f'DEMAND BOUND FUNCTION AT {t} IS {dbf} -- UNSCHEDULABLE')
                return False
        return True

    def schedule(self) -> None:
        """
        Schedule the tasks using the EDF algorithm.

        Returns:
            None
        """
        if not self.is_feasible(log=False):
            logger.error('TASKS ARE NOT SCHEDULABLE ACCORDING TO THE GIVEN CONFIG!')
            return
        queue = sorted(list(self.tasks), key=lambda t: t.deadline)
        now = 0
        while queue:
            logger.info(f'NOW = {now}')
            task = self.__get_task(queue, now)
            if task is None:
                now = self.__idle_cpu_task_arrives(queue, now)
                continue
            queue.remove(task)
            if len(queue) > 0:
                exec_time = self.get_task_exec_time(queue, task, now)
                logger.info(f'EXECUTING TASK {task.pk} FOR {exec_time}s...')
                now = self.execute_task(
                    exec_time=exec_time,
                    task=task,
                    now=now
                )
                if task.left_execution > 0:
                    queue.append(task)
                    queue = sorted(queue, key=lambda t: t.deadline)
            else:
                exec_time = self.get_task_exec_time(queue, task, now)
                logger.info(f'EXECUTING TASK {task.pk} FOR {exec_time}s...')
                now = self.execute_task(
                    exec_time=exec_time,
                    task=task,
                    now=now
                )

    @staticmethod
    def get_task_exec_time(queue: list[Task], task: Task, now: int) -> int:
        """
        Get the execution time for a task, considering higher priority tasks.

        Args:
            queue (list[Task]): The list of tasks.
            task (Task): The current task to execute.
            now (int): The current time.

        Returns:
            int: The execution time for the task.
        """
        high_priority_tasks: list[Task] = []
        for t in queue:
            if t.deadline < task.deadline:
                high_priority_tasks.append(t)
            else:
                break
        if high_priority_tasks:
            next_task = min(high_priority_tasks, key=lambda tsk: tsk.arrival)
            exec_time = min(next_task.arrival - now, task.left_execution)
        else:
            exec_time = task.left_execution
        return exec_time

    @staticmethod
    def execute_task(exec_time: int, task: Task, now: int) -> int:
        """
        Execute a task for the given execution time.

        Args:
            exec_time (int): The execution time.
            task (Task): The task to execute.
            now (int): The current time.

        Returns:
            int: The updated time after task execution.
        """
        task.compute(exec_time)
        now += exec_time
        return now

    @staticmethod
    def __idle_cpu_task_arrives(queue: list[Task], now: int) -> int:
        """
        Handle the CPU being idle until the next task arrives.

        Args:
            queue (list[Task]): The list of tasks.
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
    def __get_task(queue: list[Task], now: int) -> Task:
        """
        Get the next task to execute from the queue.

        Args:
            queue (list[Task]): The list of tasks.
            now (int): The current time.

        Returns:
            Task: The next task to execute.
        """
        next_task = None
        for task in queue:
            if next_task is not None:
                break
            elif task.arrival <= now:
                next_task = task
        return next_task
