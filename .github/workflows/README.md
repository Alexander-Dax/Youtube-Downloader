# GitHub Actions Build Workflow Documentation

This document explains the automated build and release workflow for the YouTube Downloader application.

## Overview

The workflow automatically builds executable files for multiple platforms (Windows, Linux, macOS) whenever a new version tag is pushed to the repository. It creates cross-platform binaries and publishes them as a GitHub release.

## Workflow File: `release-build.yml`

### Trigger Condition

```yaml
on:
  push:
    tags:
      - "v[0-9]+.[0-9]+.[0-9]+"
```

**What it does**: The workflow only runs when you push a tag that matches semantic versioning (e.g., `v1.2.3`, `v2.0.1`).

**Why**: This ensures releases are only created for official version tags, not every code change.

---

## Job 1: Build (`build`)

This job creates executable files for all supported platforms.

### Build Matrix Strategy

```yaml
strategy:
  matrix:
    include:
      - os: "windows-latest"
        name: "windows"
      - os: "ubuntu-latest" # Ubuntu 24.04 LTS
        name: "ubuntu-latest"
      - os: "ubuntu-22.04" # Ubuntu 22.04 LTS
        name: "ubuntu-22.04"
      - os: "macos-latest"
        name: "macos"
```

**What it does**: Runs the build process in parallel on 4 different operating systems.

**Why Multiple Ubuntu Versions**:

- `ubuntu-latest` (24.04): For users with the newest systems
- `ubuntu-22.04`: For users with LTS systems requiring better compatibility

### Job Timeout

```yaml
timeout-minutes: 45
```

**What it does**: Kills the job if it takes longer than 45 minutes.

**Why**: Prevents hanging builds from consuming resources indefinitely.

---

### Step-by-Step Breakdown

#### Step 1: Checkout Repository

```yaml
- name: Checkout repository
  uses: actions/checkout@v3
```

**What it does**: Downloads the repository code to the runner.

**Why**: The runner needs access to your source code to build the application.

---

#### Step 2: Set up Python

```yaml
- name: Set up Python
  uses: actions/setup-python@v4
  with:
    python-version: "3.x"
```

**What it does**: Installs the latest Python 3.x version on the runner.

**Why**: The application is written in Python and requires Python to build.

---

#### Step 3: Install System Dependencies (Linux Only)

```yaml
- name: Install system dependencies (Linux)
  if: startsWith(matrix.os, 'ubuntu-')
  timeout-minutes: 10
  run: |
    sudo apt-get update
    # Install comprehensive PyQt6 dependencies
    sudo apt-get install -y \
      libxcb-xinerama0 libxcb-cursor0 libxkbcommon-x11-0 libxcb-icccm4 \
      libxcb-image0 libxcb-keysyms1 libxcb-randr0 libxcb-render-util0 \
      libxcb-shape0 libxcb-xfixes0 libopengl0 libxcb-xinput0 \
      '^libxcb.*-dev' libx11-xcb-dev libglu1-mesa-dev libxrender-dev \
      libxi-dev libxkbcommon-dev libgl1-mesa-dev xvfb
```

**What it does**: Installs system-level libraries needed for PyQt6 GUI applications on Linux.

**Why**:

- PyQt6 requires specific system libraries to function
- These libraries are not installed by default on Ubuntu runners
- `xvfb` provides a virtual display for headless GUI building

**Key Libraries**:

- `libxcb-*`: X11 protocol libraries for GUI rendering
- `xvfb`: Virtual framebuffer for headless display
- `libopengl0`: OpenGL libraries for graphics rendering

---

#### Step 4: Install Python Dependencies

```yaml
- name: Install dependencies
  timeout-minutes: 15
  run: |
    python -m pip install --upgrade pip setuptools wheel
    pip install -r requirements.txt
    pip install certifi
```

**What it does**: Installs Python packages needed for the application.

**Why**:

- Upgrades pip/setuptools for compatibility
- Installs all dependencies from `requirements.txt`
- Ensures `certifi` is available for SSL certificate handling

---

#### Step 5: Ubuntu 22.04 Specific Dependencies

```yaml
- name: Install Ubuntu 22.04 specific dependencies
  if: matrix.os == 'ubuntu-22.04'
  run: |
    pip install testresources
```

**What it does**: Installs additional packages needed specifically for Ubuntu 22.04.

**Why**: `testresources` package is required for PyQt6 compatibility on some older Ubuntu versions.

---

#### Step 6: Locate SSL Certificates

```yaml
- name: Locate certifi CA bundle
  id: certifi
  shell: bash
  run: |
    echo "CERTIFI_CA_BUNDLE=$(python -m certifi)" >> $GITHUB_ENV
```

**What it does**: Finds the location of SSL certificate bundle and stores it in an environment variable.

**Why**: PyInstaller needs to bundle SSL certificates with the executable for HTTPS requests to work.

---

#### Step 7: Build Application

This is the most complex step that creates the actual executable files.

##### Windows Build

```yaml
if [ "${{ matrix.os }}" == "windows-latest" ]; then
pyinstaller --noconsole --onefile --add-data "$CERTIFI_CA_BUNDLE;certifi" \
--hidden-import=PyQt6.QtCore --hidden-import=PyQt6.QtGui \
--hidden-import=PyQt6.QtWidgets --name video_downloader main.py
mv dist/video_downloader.exe video_downloader_windows.exe
```

**PyInstaller Options Explained**:

- `--noconsole`: No command prompt window appears when running
- `--onefile`: Creates a single executable file instead of a folder
- `--add-data`: Bundles SSL certificates with the executable (Windows uses `;` separator)
- `--hidden-import`: Explicitly includes PyQt6 modules that might not be auto-detected
- `--name`: Sets the output executable name

##### Linux Builds

```yaml
elif [ "${{ matrix.os }}" == "ubuntu-latest" ]; then
export QT_QPA_PLATFORM=offscreen
export DISPLAY=:99
export PYTHONFAULTHANDLER=1
pyinstaller --noconsole --onefile --add-data "$CERTIFI_CA_BUNDLE:certifi" \
--hidden-import=PyQt6.QtCore --hidden-import=PyQt6.QtGui \
--hidden-import=PyQt6.QtWidgets --name video_downloader main.py
mv dist/video_downloader video_downloader_linux.bin
chmod +x video_downloader_linux.bin
```

**Environment Variables**:

- `QT_QPA_PLATFORM=offscreen`: Tells Qt to run without a real display
- `DISPLAY=:99`: Sets a virtual display number
- `PYTHONFAULTHANDLER=1`: Enables better error reporting

**Linux-Specific Changes**:

- Uses `:` instead of `;` for `--add-data` separator
- Makes the file executable with `chmod +x`
- Adds `.bin` extension to indicate it's a binary

##### Ubuntu 22.04 Specific Build

Similar to ubuntu-latest but creates a separate binary file named `video_downloader_linux_ubuntu22.04.bin` for LTS compatibility.

##### macOS Build

```yaml
elif [ "${{ matrix.os }}" == "macos-latest" ]; then
pyinstaller --noconsole --onefile --add-data "$CERTIFI_CA_BUNDLE:certifi" \
--hidden-import=PyQt6.QtCore --hidden-import=PyQt6.QtGui \
--hidden-import=PyQt6.QtWidgets --name video_downloader main.py
mv dist/video_downloader video_downloader_macos
chmod +x video_downloader_macos
```

**macOS-Specific**: Uses Unix-style separators and makes executable, but no file extension.

---

#### Steps 8-11: Upload Artifacts

```yaml
- name: Upload Windows artifact
  if: matrix.os == 'windows-latest'
  uses: actions/upload-artifact@v4
  with:
    name: video_downloader_${{ matrix.os }}
    path: video_downloader_windows.exe
```

**What it does**: Uploads the built executable files as "artifacts" that can be downloaded later.

**Why**: The build and release jobs run separately, so we need to pass files between them.

**Artifacts Created**:

- `video_downloader_windows.exe` (Windows)
- `video_downloader_linux.bin` (Ubuntu 24.04+)
- `video_downloader_linux_ubuntu22.04.bin` (Ubuntu 22.04 LTS)
- `video_downloader_macos` (macOS)

---

## Job 2: Release (`release`)

This job downloads all the built files and creates a GitHub release.

### Dependencies

```yaml
needs: build
runs-on: ubuntu-latest
```

**What it does**: Only runs after the build job completes successfully.

**Why**: We need all the executables before we can create a release.

---

### Release Steps

#### Steps 1-4: Download Artifacts

```yaml
- name: Download Windows artifact
  uses: actions/download-artifact@v4
  with:
    name: video_downloader_windows-latest
```

**What it does**: Downloads each executable file from the build job.

**Why**: The release job runs on a fresh runner, so it needs to download the files created by the build job.

---

#### Step 5: Publish Release

```yaml
- name: Publish Release
  uses: ncipollo/release-action@v1
  with:
    artifacts: |
      video_downloader_windows.exe
      video_downloader_linux.bin
      video_downloader_linux_ubuntu22.04.bin
      video_downloader_macos
    token: ${{ secrets.GITHUB_TOKEN }}
    tag: ${{ github.ref_name }}
    name: Release ${{ github.ref_name }}
    body: |
      A new release is available...
```

**What it does**: Creates a new GitHub release with all the executable files attached.

**Components**:

- `artifacts`: List of files to attach to the release
- `token`: Authentication token (automatically provided by GitHub)
- `tag`: Uses the git tag that triggered the workflow
- `name`: Sets the release title
- `body`: Release description with download instructions

---

## Key Features and Optimizations

### 1. **SABR Streaming Fix**

The workflow includes yt-dlp client configuration to avoid YouTube's SABR streaming issues:

- Uses alternative YouTube clients (`tv_embedded`, `android`, `ios`, `mweb`)
- Reduces warning messages during downloads
- Improves video format availability

### 2. **Cross-Platform Compatibility**

- **Windows**: Creates `.exe` executable
- **Linux (Ubuntu 24.04+)**: Modern systems binary
- **Linux (Ubuntu 22.04 LTS)**: LTS compatibility binary
- **macOS**: Universal macOS binary

### 3. **Robust Error Handling**

- Individual step timeouts prevent hanging
- Comprehensive system dependency installation
- Fault handling enabled for debugging
- Proper headless display configuration for GUI applications

### 4. **Build Optimization**

- Parallel builds across all platforms
- Minimal PyInstaller bundles with only necessary files
- SSL certificate bundling for HTTPS support
- Hidden import declarations for PyQt6 modules

---

## How to Trigger a Release

1. **Commit your changes** to the main branch
2. **Create and push a version tag**:
   ```bash
   git tag v1.2.3
   git push origin v1.2.3
   ```
3. **Wait for the workflow** to complete (usually 10-15 minutes)
4. **Check the releases page** on GitHub for your new release with all platform binaries

---

## Troubleshooting Common Issues

### Build Fails on Ubuntu

- **Cause**: Missing system dependencies
- **Solution**: Update the system dependencies list in the workflow

### Windows Build Fails

- **Cause**: Platform-specific commands in cross-platform steps
- **Solution**: Use separate steps with proper conditionals

### PyQt6 Import Errors

- **Cause**: Missing hidden imports in PyInstaller
- **Solution**: Add missing modules to `--hidden-import` flags

### SSL Certificate Errors

- **Cause**: Missing certifi bundle in executable
- **Solution**: Verify `--add-data` includes the correct certifi path

### Release Creation Fails

- **Cause**: Artifact names don't match between upload and download
- **Solution**: Ensure artifact names are consistent in both build and release jobs

---

## Maintenance Notes

- **GitHub Actions Updates**: Regularly update action versions (checkout@v3, setup-python@v4, etc.)
- **Ubuntu Version Updates**: When GitHub deprecates older Ubuntu versions, update the matrix
- **Dependency Updates**: Keep system dependencies current with PyQt6 requirements
- **PyInstaller Updates**: Monitor PyInstaller compatibility with new Python/PyQt6 versions
