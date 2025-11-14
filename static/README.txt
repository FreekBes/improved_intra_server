Any file that is static in here, any subdirectory, MUST be declared in useful/intra.nginx.snippet.conf!

------ useful/intra.nginx.snippet.conf:
...
# Static files
location ~ ^/(banners/|campus_specifics/|fonts/|favicon.ico)/ {
# ADD FILE/DIR HERE      ^^^^^^^^^^^^
    root              /usr/share/nginx/html/static;
    autoindex         off;
...
------
