# Desktop-Compose README
## This readme needs to be updated as 1/31/2025
<span style="color:red">*Alpha build, not suitable for production use*.</span>

#I moved to linux with hyprland so I probabaly wont work on this ever again!

## Overview

Desktop-Compose is a powerful tool for managing virtual desktops and automating desktop application layouts and workflows. It uses YAML configurations to define how applications are arranged, launched, and managed across monitors and virtual desktops. Designed for power users, developers, and professionals, Desktop-Compose aims to optimize productivity by providing consistent and customizable desktop setups.

## Key Features

- **Customizable Application Layouts**: Define window positions, sizes, and zones for your applications.
- **Monitor and Virtual Desktop Support**: Simplifies the creation and switching of virtual desktops while seamlessly managing applications across multiple monitors and virtual desktops.
- **Configuration through YAML**: Use human-readable YAML files for flexible and repeatable setup.
- **Application Management**: Automatically launch, position, and manage multiple applications.
- **Template System**: Organize different configurations for various workflows, such as coding, designing, or gaming.

## How It Works

Virtual desktops are an integral part of the workflow, enabling isolated environments for specific templates and layouts. Configuration files link applications to virtual desktops seamlessly, ensuring consistent setups across sessions.

1. **Configuration Files**:

   - **Global Configuration (`~/.config/desktop-compose/config.yaml`)**: Defines directories for apps, templates, and zone layouts.
   - **App Configuration (`~/.config/desktop-compose/apps/*.yaml`)**: Specifies settings for individual applications, including executable paths and arguments.
   - **Zone Layout Configuration (`~/.config/desktop-compose/zone_configs/*.yaml`)**: Details monitor and zone layouts.
   - **Templates (`~/.config/desktop-compose/templates`)**: Combines app and zone configurations into a workflow template.

2. **Application Management**:

   - Apps are managed using global (`AppConfig`) and local (`LocalAppConfig`) configurations.
   - Supports custom arguments, window positions, and optional minimization on launch.

3. **Zone Layouts**:

   - Define zones within monitors to control where application windows appear.


4. **Template System**:

   - Templates bundle application settings and zone layouts for specific workflows.


5. **Execution**:

   - The `/bin/desktop-compose.py` script orchestrates the process:
     - Loads the selected template.
     - Creates a new virtual desktop.
     - Launches and positions applications as defined in the template.

## Prerequisites

- Python 3.8+
- Dependencies:
  - `pyvda`: For virtual desktop management.
  - `pywin32`: For window handling on Windows.
  - `PyYAML`: For YAML parsing.

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/Sean-P-May/desktop-compose.git
   cd desktop-compose
   pip install .
   ```



## Usage

1. Create a YAML template for your workflow in the `templates` directory.
2. Define application settings in the `apps` directory.
3. Specify zone layouts in the `zone_configs` directory.
4. Run Desktop-Compose with a selected template:
   ```bash
   desktop-compose template_name
   ```

## Example

A template (`~/.config/desktop-compose/templates/workflow.yaml`):

```yaml
name: Coding Workflow
description: Layout for coding with an IDE and a browser.
apps:
  - app: pycharm
    args: []
    zone: "0:0"
  - app: chrome
    args: [--new-window, https://docs.python.org/3/]
    zone: "0:1"
zone_file: single_monitor.yaml
```

A zone layout (`~/.config/desktop-compose/zone_configs/single_monitor.yaml`):

```yaml
- monitor: 
    - zones:
        - position:
            x: 0
            y: 0
            width: 960
            height: 1080
        - position:
            x: 960
            y: 0
            width: 960
            height: 1080
```
App configuration (`~/.config/desktop-compose/apps/chrome.yaml`):
```yaml
path: "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
default_args:
  - --new-window
default_position:
  x: 0
  y: 0
  width: 1920
  height: 400
```
Run the setup:

```bash
desktop-compose workflow
```


## License

This project is licensed under the MIT License. See `LICENSE` for details.


