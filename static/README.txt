Any file that is static in here, any subdirectory, MUST be declared in deploy/nginx/snippets/iintra.nginx.snippet.conf!

------ deploy/nginx/snippets/iintra.nginx.snippet.conf:
...
# Static files
location ~ ^/(banners/|campus_specifics/|fonts/|favicon.ico)/ {
# ADD FILE/DIR HERE      ^^^^^^^^^^^^
    root              /usr/share/nginx/html/static;
    autoindex         off;
...
------
