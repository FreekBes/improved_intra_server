import sys

# This script allows for running a runner right away.

# Check if runner_name exists
if len(sys.argv) < 2:
	print('Usage: python3 run_runner.py <runner_name> [login]')
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


login = None
# Check if login is provided
if len(sys.argv) > 2:
	login = sys.argv[2]
	if not isinstance(login, str):
		print('Login must be a string')
		sys.exit(1)

# If login is provided, run the runner for that user, otherwise run a regular run
if login:
	if hasattr(runner, 'run_for_user'):
		runner.run_for_user(login)
	else:
		print('Runner {} does not support running for a specific user'.format(runner_name))
		sys.exit(1)
else:
	runner.run()
