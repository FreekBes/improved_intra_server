import os

from dotenv import dotenv_values

# Load config from .env files
config = {
	**dotenv_values(".shared.env", verbose=True),  # load shared development variables
	**dotenv_values(".secret.env", verbose=True),  # load sensitive variables
	**os.environ,  # override loaded values with environment variables
}
