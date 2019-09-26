# Installation

Adaptive Bitrate Broadcaster can be installed in Linux or macOS.

The following software(s) needs to be installed for Adaptive Bitrate Broadcaster to run properly.
- Xcode full version (only for macOS users). Also its license should have been accepted from its UI or from the command line.
To accept the Xcode license from command line run the the following commands.

```bash
sudo xcode-select -s /Applications/Xcode.app/Contents/Developer
sudo xcodebuild -license
```

The below installation procedure is tested on macOS High Sierra and Ubuntu 18.04. Some these steps might need a little modification if they don't work or apply for your OS version.

# Quick Install

If you are using macOS or Ubuntu OS, then the `install_mac.sh` or `install_ubuntu.sh` script automates all the install steps respectively. Just running that script will install all the required software and configure them. Follow the below steps for quick install

```bash
git clone https://github.com/jkarthic-akamai/ABR-Broadcaster
cd ABR-Broadcaster
```

On Ubuntu OS run the following command and enter sudo password when prompted.

```bash
./install_ubuntu.sh
```

On Mac OS run the following command and enter sudo password when prompted.

```bash
./install_mac.sh
```

If the above scripts runs without any errors then it means ABR-Broadcaster is installed successfully in your system. Read through [Usage Instructions](README.md#usage) for further steps.

The basic installation will install only your webcam as input capture device. If you want to use a Decklink capture card for professional video capture then additionally follow the section [Decklink Capture Install](#decklink-capture-install).

# Decklink Capture Install

To use a Decklink SDI-input capture card for professional video capture, follow the below steps.

- The Decklink drivers and the SDK are two separate packages. Download it from the BlackMagicDesign's official [site](https://www.blackmagicdesign.com/in/support/family/capture-and-playback). Download the 10.11.x versions for `Desktop Video` and `Desktop Video SDK`

- ffmpeg doesn't work with BlackMagic SDK 11.0. Till the [issue](https://trac.ffmpeg.org/ticket/7789) is resolved, it is not recommended to use the BlackMagic SDK 11.0 SDK.

- Uncompress the `Desktop Video` package. For example

```bash
tar -xvzf Blackmagic_Desktop_Video_Linux_10.11.2.tar.gz
```
The above command could change a little if you had downloaded a `Desktop Video` version different than above.

- Install the desktop video package relevant to your OS. For example if you are running Ubuntu 64-bit, run the below command to install it.

```bash
sudo dpkg -i Blackmagic_Desktop_Video_Linux_10.11.2/deb/x86_64/desktopvideo_10.11.2a3_amd64.deb
```

- Uncompress the `Desktop Video SDK` package. For example,

```bash
unzip Blackmagic_DeckLink_SDK_10.11.2.zip
```

- Copy the SDK header files to the system's include path so that ffmpeg can use it.

```
sudo cp Blackmagic\ DeckLink\ SDK\ 10.11.2/Linux/include/* /usr/local/include
```

- Rebuild and install ffmpeg with decklink plugin enabled.

```
install/ffmpeg.sh "--enable-decklink --enable-nonfree"
```

- In the Web UI interface of ABR-Broadcaster click on **"Refresh Input"** button to detect the presence of Decklink input device.