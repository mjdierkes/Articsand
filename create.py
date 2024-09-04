import os
import subprocess
import yaml
import sys

def run_command(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output, error = process.communicate()
    if process.returncode != 0:
        print(f"Error executing command: {command}")
        print(error.decode('utf-8'))
        exit(1)
    return output.decode('utf-8')

def create_project_spec(project_name):
    spec = {
        "name": project_name,
        "options": {
            "bundleIdPrefix": f"com.example.{project_name.lower()}",
            "deploymentTarget": {
                "iOS": "14.0"
            }
        },
        "packages": {
            "Inject": {
                "url": "https://github.com/krzysztofzablocki/Inject.git",
                "from": "1.5.2"
            }
        },
        "targets": {
            project_name: {
                "type": "application",
                "platform": "iOS",
                "sources": ["."],
                "dependencies": [
                    {"package": "Inject"}
                ],
                "info": {
                    "path": "Info.plist",
                    "properties": {
                        "UILaunchStoryboardName": "LaunchScreen"
                    }
                }
            }
        },
        "settings": {
            "base": {
                "SWIFT_ACTIVE_COMPILATION_CONDITIONS": "DEBUG",
                "OTHER_LDFLAGS": [
                    "-Xlinker",
                    "-interposable"
                ]
            }
        }
    }
    return spec

def main():
    # Check if project name is provided as a command-line argument
    if len(sys.argv) > 1:
        project_name = sys.argv[1]
    else:
        project_name = input("Enter the project name: ")
    
    # Ask for output directory
    output_dir = input("Enter the output directory (press Enter for default 'output' folder): ").strip()
    if not output_dir:
        output_dir = "output"
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Create project directory inside output directory
    project_path = os.path.join(output_dir, project_name)
    os.makedirs(project_path, exist_ok=True)
    os.chdir(project_path)
    
    # Create project.yml
    spec = create_project_spec(project_name)
    with open("project.yml", "w") as f:
        yaml.dump(spec, f)
    
    # Create Assets.xcassets
    os.makedirs("Assets.xcassets", exist_ok=True)
    
    # Create Preview Content
    os.makedirs("Preview Content/Preview Assets.xcassets", exist_ok=True)
    
    # Modify ContentView.swift to include Injection
    content_view = f"""
import SwiftUI
import Inject

struct ContentView: View {{
    @ObserveInjection var inject
    
    var body: some View {{
        Text("Hello, World!")
            .enableInjection()
    }}
}}
"""
    with open("ContentView.swift", "w") as f:
        f.write(content_view)
    
    # Modify App file to include Injection bundle loading
    app_file = f"""
import SwiftUI
@_exported import Inject

@main
struct {project_name}App: App {{
    init() {{
        #if DEBUG
        Bundle(path: "/Applications/InjectionIII.app/Contents/Resources/iOSInjection.bundle")?.load()
        #endif
    }}

    var body: some Scene {{
        WindowGroup {{
            ContentView()
        }}
    }}
}}
"""
    with open(f"{project_name}App.swift", "w") as f:
        f.write(app_file)
    
    # Create empty Info.plist
    with open("Info.plist", "w") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">\n<plist version="1.0">\n<dict/>\n</plist>')
    
    # Generate Xcode project
    run_command("xcodegen generate")
    
    # Open the Xcode project
    run_command(f"open {project_name}.xcodeproj")
    
    print(f"Xcode project '{project_name}' has been created in '{project_path}', configured with Inject, and opened in Xcode.")

if __name__ == "__main__":
    main()