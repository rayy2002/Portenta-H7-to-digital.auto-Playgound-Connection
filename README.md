# Connecting Arduino Portenta H7 to digital.auto Playground

This guide explains the step-by-step process to connect an **Arduino Portenta H7** with **digital.auto Playground** using a **Portenta X8**.

---

## Step 1: Flash Portenta H7

* Open Arduino IDE
* Connect the **Portenta H7**
* Flash the firmware file:

```text
H7_VSS_READWRITE.ino
```

This enables KUKSA communication on the H7.

---

## Step 2: Install ADB and Access Portenta X8

1. If not already installed, download and install **ADB (Android Debug Bridge)**.
2. Connect **Portenta X8** to your laptop using a USB cable.
3. Wait ~1 minute for the device to initialize.
4. Run the following command on your laptop terminal:

```bash
adb shell
```

This connects your terminal to the Portenta X8 shell.

---

## Step 3: Copy Docker Image to Portenta X8

Download the image from - https://drive.google.com/file/d/1uPaNE2s1IVmazpbtvj6aTL3zhmn3GbhC/view?usp=drive_link

From your **laptop terminal**, copy the Docker image archive to the X8:

```bash
adb push portenta-image.tar /var/rootdirs/home/fio
```
Make sure the terminal is open in the directory where the image file is
> You may change the destination path if needed, but `/var/rootdirs/home/fio` is commonly used.

---

## Step 4: Load the Docker Image on X8

On the **Portenta X8 terminal**, load the Docker image:

```bash
docker load -i /var/rootdirs/home/fio/portenta-image.tar
```

This imports the image into Docker.

---

## Step 5: Enable Web Access to Portenta X8

From your **laptop terminal**, run:

```bash
adb forward tcp:8080 tcp:80
```

Now open the following link in your browser:

```text
http://localhost:8080
```

Use this interface to connect the **Portenta X8 to Wi-Fi**.

---

## Step 6: Run SDV Runtime Container on X8

On the **Portenta X8**, run the following command **with sudo**:

```bash
sudo docker run -d \
  -e RUNTIME_NAME="MyRuntimeName" \
  -p 55555:55555 \
  ghcr.io/eclipse-autowrx/sdv-runtime:latest
```

* You may change `MyRuntimeName` to any name you prefer.
* This runtime will be visible in digital.auto Playground.
* Test it with the custom sdv-runtime by using this command, make sure you dont have any other runtime running.

```bash
sudo docker run -d \
  -e RUNTIME_NAME="MyRuntimeName" \
  -p 55555:55555 \
  ghcr.io/rayy2002/sdv-runtime
```

---

## Step 7: Add Runtime to digital.auto Playground

1. Open **digital.auto Playground**
2. Add a **new runtime**
3. Select the runtime name you configured in the previous step
4. Confirm the connection

---

## Step 8: Run the Portenta Image Container

Start the container created from `portenta-image`:

```bash
docker run -d --privileged --network host --user root --name portenta-container portenta-image
```

> Adjust the image name if it differs (use `docker images` to verify).

---

## Step 9: Connect H7 and X8 via Ethernet

* Connect **Portenta H7** and **Portenta X8** using an **Ethernet cable**
* Ensure both devices are powered
* Communication should now be established through the SDV runtime

---

## Done 🎉

Your **Portenta H7** is now connected to **digital.auto Playground** via **Portenta X8**.

