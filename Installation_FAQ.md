# BrickPi3 Installation FAQ
### For Raspberry Pi 3B+, 4, and 5

This guide is written for educators who want to use BrickPi3 with LEGO motors and sensors in their classroom.
The Raspberry Pi is assumed to be **headless** — no monitor, no keyboard attached. You will connect to it from your laptop over WiFi or ethernet using SSH.

---

## Which option is right for me?

| Situation | Recommended option |
|---|---|
| I want the simplest setup and I'm starting from scratch | **Option A** — `pip install` on a fresh Raspberry Pi OS |
| I want the full source code and example projects | **Option B** — Install via `git clone` |
| I have an ethernet cable + router handy, and want a fully pre-configured image | **Option C** — Download the ready-made image |

> **Why is the pre-made image not listed first?** When you download a ready-made image, there is no way to tell it your WiFi password before first boot. You will need an ethernet cable plugged into a router to connect. Options A and B use the official Raspberry Pi Imager, which lets you enter your WiFi details in advance so you can connect wirelessly right away.

---

## Option A — Install using `pip` on a fresh Raspberry Pi OS ✅ Easiest

This is the recommended approach for most users. You flash a standard Raspberry Pi OS image yourself (which means you can pre-configure WiFi), then install BrickPi3 with a single command.

### What you need
- A Raspberry Pi 3B+ *(recommended)*, 4, or 5
- A microSD card (16 GB or larger)
- A laptop with [Raspberry Pi Imager](https://www.raspberrypi.com/software/) installed

### Steps

1. **Flash Raspberry Pi OS to your microSD card**

   - Open **Raspberry Pi Imager**.
   - In the **Device** tab, select your Pi model (Raspberry Pi 3B+, 4, or 5). Click **Next**.
   - In the **OS** tab, choose **"Raspberry Pi OS (64-bit)"** for a full desktop, or **"Raspberry Pi OS (other)"** → **"Raspberry Pi OS Lite (64-bit)"** if you prefer a lighter, terminal-only system. Either works with BrickPi3. Click **Next**.
   - In the **Storage** tab, select your microSD card. Click **Next**.
   - Imager launches the **Customisation wizard** automatically. Go through each screen:
     - **Hostname** — enter a name for your Pi, e.g. `brickpi`. Click **Next**.
     - **Localisation** — choose your city (timezone and keyboard fill in automatically). Click **Next**.
     - **User** — enter a username and password you will remember. Click **Next**.
     - **Wi-Fi** — enter your WiFi network name (SSID) and password. Click **Next**.
     - **Remote Access** — toggle **Enable SSH** to on, then choose **"Use password authentication"**. Click **Next**.
   - On the summary screen, click **"Write"** and confirm.

2. **Insert the card, power on the Pi, and SSH in.**

   Insert the microSD card into the Pi and plug in power. After about a minute, open a terminal on your laptop and type:

   ```bash
   ssh yourusername@brickpi.local
   ```

   Replace `yourusername` and `brickpi` with whatever you set in the wizard. You will be asked for your password and then land at a command prompt on the Pi.

   > **If `brickpi.local` doesn't work**, you can find the Pi's IP address by logging into your router's admin page — open a browser on your laptop and try `192.168.1.1`, `192.168.0.1`, or `10.0.0.1` (these are the router's own admin addresses, not the Pi's). Look for a list of connected devices; the Pi will appear with the hostname you chose. Then SSH using its IP directly:
   > ```bash
   > ssh yourusername@192.168.x.x
   > ```

3. **Create and activate a virtual environment** (see the [Setting up a Python virtual environment](#setting-up-a-python-virtual-environment) section below):

   ```bash
   python3 -m venv ~/.venv/brickpi
   source ~/.venv/brickpi/bin/activate
   ```

4. **Install BrickPi3**:

   ```bash
   pip install brickpi3
   ```

5. **Run the setup script** to enable SPI, I2C, VNC, and other required interfaces.
   The script was installed alongside the package into your virtual environment:

   ```bash
   source ~/.venv/brickpi/lib/python3.*/site-packages/brickpi3/scripts/install_trixie.sh
   ```

   > The `python3.*` part matches whichever Python version is on your Pi (e.g. `python3.11`, `python3.12`). The `*` wildcard handles this automatically — no need to type the version number.

### Test it

```bash
python3 -c "import brickpi3; print('BrickPi3 installed successfully!')"
```

---

## Option B — Install using `git clone` (Full source + examples)

Use this if you want the complete source code and the sample projects folder.
The setup steps are identical to Option A — the only difference is how the library is installed.

### Steps

1. Flash Raspberry Pi OS and connect via SSH exactly as described in **Option A, steps 1 and 2**.

2. **Create and activate a virtual environment** (see the [Setting up a Python virtual environment](#setting-up-a-python-virtual-environment) section below):

   ```bash
   python3 -m venv ~/.venv/brickpi
   source ~/.venv/brickpi/bin/activate
   ```

3. **Clone the repository** into the directory of your choice, then enter it:

   ```bash
   git clone https://github.com/DexterInd/BrickPi3.git
   cd BrickPi3
   ```

4. **Run the setup script** to install BrickPi3 and enable SPI, I2C, VNC, and other required interfaces:

   ```bash
   source Software/Python/brickpi3/scripts/install_trixie.sh
   ```

### Explore the examples

The `Projects/` folder inside the cloned repository contains ready-to-run example programs for motors, sensors, and more.

---

## Setting up a Python virtual environment

Modern Raspberry Pi OS (Trixie / Debian 13) will refuse to install Python packages system-wide with `pip` by default. The clean solution is to use a **virtual environment** — a self-contained folder where Python packages are installed without touching the rest of the system.

You only need to do this once. Run these commands on the Pi after SSHing in:

```bash
# Create a virtual environment at ~/.venv/brickpi
python3 -m venv ~/.venv/brickpi

# Activate it (your prompt will change to show '(brickpi)')
source ~/.venv/brickpi/bin/activate
```

> **Every time you open a new SSH session**, you will need to activate the virtual environment again before running any Python code:
> ```bash
> source ~/.venv/brickpi/bin/activate
> ```
> To make this automatic on login, add that line to the end of your `~/.bashrc` file:
> ```bash
> echo 'source ~/.venv/brickpi/bin/activate' >> ~/.bashrc
> ```

---

## Option C — Download the ready-made image ⚠️ Requires ethernet cable + router

We provide a complete Raspberry Pi OS image with BrickPi3 already installed and configured —
SPI, I2C, SSH, and everything else is already set up.

> **Important:** Because this is a pre-built image, there is no way to enter your WiFi password before first boot.
> You **must** connect your Raspberry Pi to a router using an **ethernet cable** for the first boot.
> Once you are connected and logged in, you can configure WiFi from the command line.

### What you need
- A Raspberry Pi 3B+ *(recommended)*, 4, or 5
- A microSD card (16 GB or larger)
- An **ethernet cable** and access to a router
- A laptop with [Raspberry Pi Imager](https://www.raspberrypi.com/software/) installed

### Steps

1. **Download the image** (about 1–2 GB):

   👉 [brickpi3_4.0.9_trixie_2026-02.zip](https://dexteros.s3.us-west-1.amazonaws.com/BrickPi+Trixie/brickpi3_4.0.9_trixie_2026-02.zip)

2. **Write it to your microSD card**:

   - Open **Raspberry Pi Imager**.
   - In the **Device** tab, select your Pi model. Click **Next**.
   - In the **OS** tab, scroll to the bottom and select **"Use custom"** → select the zip file you downloaded. Click **Next**.
   - In the **Storage** tab, select your microSD card. Click **Next**.
   - When Imager starts the customisation wizard, click **"Skip customisation"** — do not modify the image, it is already configured.
   - On the summary screen, click **"Write"** and confirm with **"I understand, erase and write"**.

   > ⚠️ This will erase everything currently on the microSD card.

3. **Connect the Pi to your router with an ethernet cable**, insert the card, and power it on.

4. **Find the Pi's IP address** by logging into your router's admin page (usually `192.168.1.1` or `192.168.0.1` in a browser) and looking for a device named `brickpi` in the connected devices list.

5. **SSH into the Pi**:

   ```bash
   ssh brickpi@brickpi.local
   ```

   Default password: `robots1234`

6. *(Optional)* **Add your WiFi credentials** so you no longer need the ethernet cable:

   ```bash
   sudo nmcli device wifi connect "YourNetworkName" password "YourPassword"
   ```

   After this you can unplug the ethernet cable and reconnect over WiFi.

---

## Frequently Asked Questions

### Which Raspberry Pi models are supported?
All three options work on **Raspberry Pi 3B+**, **4**, and **5**. The **3B+** is the recommended model — it is well-tested with BrickPi3 and widely available second-hand.

> **⚠️ Raspberry Pi 5 caveats:**
> - The Pi 5 draws significantly more power than earlier models. It is **strongly recommended** to power the Pi 5 from its own USB-C power supply rather than letting the BrickPi3 power it.
> - Do **not** enclose a Pi 5 + BrickPi3 stack in the acrylic casing — the Pi 5 runs hotter and the enclosure will trap heat.
> - There is no space between the BrickPi3 board and the Pi 5 to fit a cooling fan. Ensure adequate airflow or use a heatsink on the Pi 5.

### Does it work with LEGO Mindstorms EV3 sensors and motors?
Yes. BrickPi3 connects LEGO NXT and EV3 motors and sensors to a Raspberry Pi.

> **LEGO® Education SPIKE Prime and SPIKE Essential are not compatible with BrickPi3.** SPIKE uses a different connector type and communication protocol. Only NXT and EV3 hardware is supported.

### What is SPI and I2C, and why do I need to enable them?
These are communication interfaces that let the Raspberry Pi talk to the BrickPi3 hardware. They are off by default on a fresh Raspberry Pi OS. The `install_trixie.sh` script in Options A and B takes care of enabling them automatically. The ready-made image (Option C) already has them enabled.

### I got a warning about "externally managed environment" when running `pip install`.
This means you are not inside a virtual environment. Activate yours first:

```bash
source ~/.venv/brickpi/bin/activate
```

If you haven't created one yet, see the [Setting up a Python virtual environment](#setting-up-a-python-virtual-environment) section earlier in this guide.
As a last resort you can force the install with `--break-system-packages`, but using a virtual environment is the right approach.

### My laptop can't find `brickpi.local`.
- Give the Pi a full minute to finish booting.
- Make sure your laptop is on the same WiFi network as the Pi.
- Try using the IP address instead: find it in your router's connected devices list.
- On Windows, you may need to install [Bonjour](https://support.apple.com/downloads/bonjour) for `.local` names to work.

### Something isn't working. How do I get help?
- Check the [BrickPi3 GitHub repository](https://github.com/DexterInd/BrickPi3) for open issues.
- Make sure the BrickPi3 board is firmly seated on the Raspberry Pi GPIO pins.
- Verify that both SPI and I2C are enabled.
