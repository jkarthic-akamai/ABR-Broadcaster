# Detailed Step-by-Step Install

We recommend usage of the quick install scripts explained in the default [INSTALL](INSTALL.md) document. But if you are on some OS other than Ubuntu, macOS or if you need understand and control of the install steps then please follow the detailed but longer install procedure explained below.

The following additional software(s) will be installed as part of the steps explained below.
- Xcode full version (only for macOS users)
- Curl, YASM, V4L Utils and Libasound (only for Linux users)
- Python 2.7.x
- Python modules - mod_wsgi, webapp2, webob, psutil
- nasm
- libx264
- ffmpeg 4.0 or above (configured with a x264 video encoder)
- A webserver with WSGI support(Apache2 preferred)

## Get the source

Get the source of ABR Broadcaster.

```bash
git clone https://github.com/jkarthic-akamai/ABR-Broadcaster
cd ABR-Broadcaster
```

As a recommended procedure all the further commands in this guide should be executed from this `ABR-Broadcaster` folder. The present working directory where the ABR-Broadcaster is downloaded will be mentioned as ``<working directory>`` in this guide subsequently. All instances of ``<working directory>`` in this guide should be replaced with the correct path before using it.

Say for the below example, ``<working directory>`` should be replaced by ``/home/akamai/ABR-Broadcaster``

```bash
$ pwd
/home/akamai/ABR-Broadcaster
```

## Xcode (macOS only)

Full version of Xcode is required to be installed (not just the command line tools).
Go to Apple app store and install the Xcode app. After installation is complete run the following command.

```bash
$ xcode-select -p
```

If the above command returns ``/Applications/Xcode.app/Contents/Developer`` then it means the Xcode installation in successful.
Also one needs to "Accept" the Xcode license either from the UI or from running the below command.

```bash
$ sudo xcodebuild -license
```

## YASM, V4L Utils and Libasound (Linux only)

Install the YASM, V4L Utils and Libasound with the following command.

```bash
sudo apt install v4l-utils libasound-dev yasm
```

## Python

### macOS
macOS comes preinstalled with Python 2.7.x. Python version can be verified with the following command.

```bash
$ python --version
```

If the python version is something other than 2.7.x, it means some other version of python is also installed. Either uninstall the incompatible python version or modify the system's PATH settings so that the default python executable is version 2.7.x

Install pip for python

```bash
sudo easy_install pip
```

On older versions of macOS, pip installation might fail with an error `Download error on https://pypi.python.org/simple/pip/: [SSL: TLSV1_ALERT_PROTOCOL_VERSION] tlsv1 alert protocol version (_ssl.c:590) -- Some packages may not be found!`
In such cases, follow the below steps to install pip.

```bash
curl https://bootstrap.pypa.io/get-pip.py | sudo python
```

### Linux

On Ubuntu, install python and pip with the following command(if it is not installed already).

```bash
sudo apt update
sudo apt install python
sudo apt install python-pip
```

If installation of python-pip throws an error `Unable to locate package python-pip` then update `/etc/apt/sources.list` file to include "universe" category.

```bash
sudo vi /etc/apt/sources.list
```
then add "universe" at the end of each line, like this:

```bash
deb http://archive.ubuntu.com/ubuntu bionic main universe
deb http://archive.ubuntu.com/ubuntu bionic-security main universe
deb http://archive.ubuntu.com/ubuntu bionic-updates main universe
```

## Python modules (macOS and Linux)

Run the following commands to install the required python module dependencies

```bash
sudo pip install webapp2 webob psutil
```

## nasm (macOS and Linux)

Run the following commands to download, build and install nasm-2.13.03.

```
curl -O https://www.nasm.us/pub/nasm/releasebuilds/2.13.03/nasm-2.13.03.tar.bz2
tar -xvjf nasm-2.13.03.tar.bz2
cd nasm-2.13.03
./configure --prefix=/usr/local
make -j4
sudo make install
cd ..
```

## libx264 (macOS and Linux)
Run the following commands to download, build and install the latest version of [x264](http://www.videolan.org/developers/x264.html).

```bash
git clone http://git.videolan.org/git/x264.git
cd x264
./configure --enable-shared
make -j4
sudo make install
cd ..
```

Alternatively on Ubuntu platforms x264 can be installed easily with the following command.

```bash
sudo apt install libx264-dev
```

## ffmpeg (macOS and Linux)

Run the following commands to download, build and install the latest version of [ffmpeg](http://ffmpeg.org/download.html).

```bash
git clone https://git.ffmpeg.org/ffmpeg.git
cd ffmpeg
./configure --enable-libx264 --enable-gpl
make -j4
sudo make install
cd ..
```

## Apache2 (Linux only)

macOS comes preinstalled with Apache2. On Linux apache2 can be installed with the following command

```bash
sudo apt install apache2 libapache2-mod-wsgi
```

Add apache2's user `www-data` to video and audio group so that it has permissions to access AV capture devices. Run the following commands to achieve the same

```bash
sudo adduser www-data video
sudo adduser www-data audio
```

## Enable Virtual Hosts (macOS only)

Uncomment(or add) the following two lines in `/etc/apache2/httpd.conf` to enable Virtual Hosts

```
LoadModule vhost_alias_module libexec/apache2/mod_vhost_alias.so
Include /private/etc/apache2/extra/httpd-vhosts.conf
```

## Install and Enable WSGI module (macOS only)

Install WSGI module with the following command

```bash
sudo pip install mod_wsgi
```

and then run the following command

```bash
$ mod_wsgi-express module-config
```

It will output something like 

```
LoadModule wsgi_module "/Library/Python/2.7/site-packages/mod_wsgi/server/mod_wsgi-py27.so"
WSGIPythonHome "/System/Library/Frameworks/Python.framework/Versions/2.7"
```

Add the above two lines to ``/etc/apache2/httpd.conf``

## Add Directory (macOS and Linux)

The directory in which ABR-Broadcaster was downloaded needs to be added to Apache's configuration with relevant permissions and settings. Append the lines in `install/directory.conf` to `/etc/apache2/httpd.conf`(macOS) or `/etc/apache2/apache2.conf`(Ubuntu) after replacing `<working directory>` appropriately.

## Add Virtual Hosts (macOS and Linux)

Let us add a Virtual Host for ABR-Broadcaster. Append the lines in `install/vhost.conf` to `/etc/apache2/extra/httpd-vhosts.conf`(macOS) or `/etc/apache2/sites-enabled/000-default.conf`(Ubuntu) after replacing `<working directory>` appropriately.

## Configuration Sub-Directory (macOS and Linux)

We need to create a sub-directory for broadcaster's configuration information to be stored and edited by the WSGI web application. Run the following commands to achieve the same.

```
cd <working directory>
mkdir wsgi-scripts/db
chmod 777 wsgi-scripts/db
```

## Restart Apache2 (macOS and Linux)

In macOS run the following command to restart Apache2 server

```bash
sudo apachectl restart
```

In Ubuntu run the following command to restart Apache2 server

```bash
sudo service apache2 reload
```
