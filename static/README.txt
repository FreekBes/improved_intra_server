Static files in this directory are served by the application itself
(Flask is configured with static_folder='../static' and static_url_path=''),
so adding a file or subdirectory here needs no further configuration.

static/banners/ holds user-uploaded banners. It is a Docker volume in the
compose setup, and is excluded from the repository and the image.
