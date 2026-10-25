import os

from dotenv import dotenv_values

# Load config from .env files
config = {
	**dotenv_values(".public.env", verbose=True),  # load public, version-controlled defaults
	**dotenv_values(".private.env", verbose=True),  # load private secrets (gitignored)
	**os.environ,  # override loaded values with environment variables
}
