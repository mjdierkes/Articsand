# Articsand: XcodeGen Inject Setup with Auto-Update (Public Beta)

This project automates the setup and maintenance of an Xcode project using XcodeGen and the Inject library for hot reloading capabilities, with an added feature of automatic project updates.

## Features

- Automatically creates an Xcode project using XcodeGen
- Integrates the Inject library for hot reloading
- Sets up necessary configurations and build settings
- Creates a basic SwiftUI app structure
- Continuously monitors project files and updates the Xcode project automatically

## Prerequisites

- Xcode 14.0+
- Python 3.6+
- XcodeGen (install via Homebrew: `brew install xcodegen`)
- InjectionIII app (download from [GitHub releases](https://github.com/johnno1962/InjectionIII/releases))

## Installation

1. Clone this repository:

   ```
   git clone https://github.com/mjdierkes/Articsand.git
   cd Articsand
   ```

2. Install required Python packages:

   ```
   pip install pyyaml watchdog pbxproj
   ```

3. Download and install the InjectionIII app from the [GitHub releases page](https://github.com/johnno1962/InjectionIII/releases).

## Usage

1. Run the setup script with your desired project name:

   ```
   python create.py MyAwesomeApp
   ```

2. The script will:

   - Create a new directory for your project
   - Generate a `project.yml` file for XcodeGen
   - Create basic SwiftUI app files
   - Run XcodeGen to create the Xcode project
   - Open the newly created Xcode project

3. Launch the InjectionIII app and select your project workspace or directory to monitor.

4. To start the auto-update watcher:

   ```
   python watcher.py MyAwesomeApp
   ```

5. Your Xcode project will now be automatically updated when you add, modify, or delete files in the project directory, and the InjectionIII app will handle hot reloading.

Note: This is a public beta version. Please report any issues or feedback to help improve the project.
