import sys

# This script allows for running a runner right away.

# Check if runner_name exists
if len(sys.argv) < 2:
	print('Usage: python3 run_runner.py <runner_name>')
	sys.exit(1)

runner_name = sys.argv[1]
if runner_name not in ['events', 'outstandings', 'bannercleaning']:
	print('Usage: python3 run_runner.py <runner_name>')
	sys.exit(1)

# Import runner
if runner_name == 'events':
	from src.runners.events import EventsRunner
	runner = EventsRunner()
elif runner_name == 'outstandings':
	from src.runners.outstandings import OutstandingsRunner
	runner = OutstandingsRunner()
elif runner_name == 'bannercleaning':
	from src.runners.bannercleaning import BannerCleaningRunner
	runner = BannerCleaningRunner()

# Run the runner
runner.run()
