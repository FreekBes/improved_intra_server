This folder contains outstanding marks for all users who have used Improved Intra in the past.
A user has used Improved Intra in the past if their settings are stored on the server in the /settings folder.

Outstandings are saved in the following format:

```json
{
	"projects_user_id": {
		"current": 0,  // latest scoring try
		"best": 0,     // best scoring try
		"all": [
			0,         // first try
			0,         // second try
			0          // third try
		]
	}
}
```

Similar to how project marks are displayed on the Intranet, where the best score is displayed until you click on the dropdown arrow,
which expands all tries.
