import json
import logging
import sys

from scheduler import RMScheduler

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


def test_rm_scheduler(data, schedule=True):
    """
    Test the RM (the Rate Monotonic) scheduler with the provided data.

    Args:
        data (list): A list containing task information.
        schedule (bool): Flag to determine if scheduling should be performed. Defaults to True.

    Logs:
        Info: If the jobs are feasible with RM algorithm.
        Error: If the jobs are not feasible with RM algorithm.
        Info: When scheduling is being done.
    """
    scheduler = RMScheduler(data)
    is_feasible = scheduler.is_feasible()
    if is_feasible:
        logger.info('JOBS MIGHT BE FEASIBLE WITH RM ALGORITHM')
    else:
        logger.error('JOBS ARE NOT FEASIBLE WITH RM ALGORITHM')
        return

    if schedule:
        logger.info('SCHEDULING IS BEING DONE...')
        try:
            scheduler.schedule()
        except ValueError:
            return


def main():
    """
    Main function to load tasks from a JSON configuration file and test the RM scheduler.

    Loads the tasks from 'config.json' and passes them to the test_rm_scheduler function.
    """
    with open('config.json', 'r') as f:
        tasks = json.load(f)
    test_rm_scheduler(data=tasks)


if __name__ == '__main__':
    main()
