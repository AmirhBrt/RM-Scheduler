import json
import logging
import sys

from scheduler import EDFScheduler

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


def test_edf_scheduler(data, schedule=False):
    """
    Test the EDF (the Earliest Deadline First) scheduler with the provided data.

    Args:
        data (list): A list containing task information.
        schedule (bool): Flag to determine if scheduling should be performed. Defaults to False.

    Logs:
        Info: If the jobs are feasible with EDF algorithm.
        Error: If the jobs are not feasible with EDF algorithm.
        Info: When scheduling is being done.
    """
    scheduler = EDFScheduler(data)
    is_feasible = scheduler.is_feasible()
    if is_feasible:
        logger.info('JOBS ARE FEASIBLE WITH EDF ALGORITHM')
    else:
        logger.error('JOBS ARE NOT FEASIBLE WITH EDF ALGORITHM')
        return

    if schedule:
        logger.info('SCHEDULING IS BEING DONE...')
        scheduler.schedule()


def main():
    """
    Main function to load tasks from a JSON configuration file and test the EDF scheduler.

    Loads the tasks from 'config.json' and passes them to the test_edf_scheduler function.
    """
    with open('config.json', 'r') as f:
        tasks = json.load(f)
    test_edf_scheduler(data=tasks)


if __name__ == '__main__':
    main()
