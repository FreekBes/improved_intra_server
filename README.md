# Back-end for Improved Intra
This repository contains the back-end for use with the [Improved Intra](https://github.com/FreekBes/improved_intra) browser extension.


## Setup
### Keep in mind...
The extension only talks directly with the [https://darkintra.freekb.es](https://darkintra.freekb.es/) domain. This means you cannot set this server up without forking the extension's source code and changing all references to this domain to whatever domain you choose to run this back-end code on. Or, you can redirect calls to this domain to your domain - that might also work.


### Actual setup
Set up a web server to use PHP. This script was written with PHP 7.3 in mind, so I suggest you also install this version or later. Also, make sure to allow all Intra origins for requests (CORS) (e.g. by adding an Apache rule: `Header set Access-Control-Allow-Origin "*"`)

Fill in the required details in the file *include/nogit.php.example* and rename it to *include/nogit.php*.

Next, make sure to not allow access to any file in the *db* and *include* folders, as these folders are intended for internal use by the back-end code only. They may contain trivial information about the users connecting to your server, such as access tokens and more. Therefore, again, make sure this entire folder is *completely inaccessible* to the outside world. To see examples of how to do this, view the example configuration files for [Apache2](apache2.example.conf) and [Nginx](nginx.example.conf).

Then, move the contents of this repository to the web-accessible folder of your web server (usually */var/www/html*). Make sure that the folders *banners*, *db* and *settings* are writable for the user(s) your webserver and php-fpm run as, otherwise users will be unable to save certain settings.

That should be all! The extension should now be able to talk with your server and synchronize settings there, etc.
