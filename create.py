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
            },
            "createIntermediateGroups": True,
            "generateEmptyDirectories": True,
            "groupSortPosition": "top",
            "xcodeVersion": "14.0",
            "groupOrdering": [
                "README.md",
                "project.yml"
            ],
            "fileGroups": [
                "README.md",
                "project.yml"
            ],
            "excludedFiles": ["${PROJECT_NAME}.xcodeproj/**"],
            "transitivelyLinkDependencies": True,
            "groupOrdering": [
                "${PROJECT_NAME}",
                "Packages"
            ]
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
                "sources": ["."],  # This ensures all files in the current directory are included
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
    
    # Create output directory
    output_dir = "./output"
    os.makedirs(output_dir, exist_ok=True)
    
    # Create project directory inside output
    project_path = os.path.join(output_dir, project_name)
    os.makedirs(project_path, exist_ok=True)
    os.chdir(project_path)
    
    # Create app directory (this will be the Xcode group)
    app_dir = project_name
    os.makedirs(app_dir, exist_ok=True)
    
    # Create project.yml
    spec = create_project_spec(project_name)
    with open("project.yml", "w") as f:
        yaml.dump(spec, f)
        
    # Create files in the specified order
    app_file = f"""
import SwiftUI
@_exported import Inject

@main
struct {project_name}App: App {{
    var body: some Scene {{
        WindowGroup {{
            ContentView()
        }}
    }}
}}
"""
    with open(os.path.join(app_dir, f"{project_name}App.swift"), "w") as f:
        f.write(app_file)
    
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
    with open(os.path.join(app_dir, "ContentView.swift"), "w") as f:
        f.write(content_view)
    
    # Create Assets.xcassets
    os.makedirs(os.path.join(app_dir, "Assets.xcassets"), exist_ok=True)
    
    # Create Preview Content
    os.makedirs(os.path.join(app_dir, "Preview Content", "Preview Assets.xcassets"), exist_ok=True)
    
    # Create empty Info.plist inside app directory
    with open(os.path.join(app_dir, "Info.plist"), "w") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">\n<plist version="1.0">\n<dict/>\n</plist>')
    
    # Update project.yml to specify file order and hide Info.plist
    spec['targets'][project_name]['sources'] = [
        {'path': os.path.join(app_dir, f"{project_name}App.swift")},
        {'path': os.path.join(app_dir, "ContentView.swift")},
        {'path': os.path.join(app_dir, "Assets.xcassets")},
        {'path': os.path.join(app_dir, "Preview Content")},
        {'path': os.path.join(app_dir, "Info.plist"), 'type': 'file', 'buildPhase': 'none'}
    ]

    with open("project.yml", "w") as f:
        yaml.dump(spec, f)
    
    # Generate Xcode project
    run_command("xcodegen generate")
    
    # Open the Xcode project
    run_command(f"open {project_name}.xcodeproj")
    
    print(f"Xcode project '{project_name}' has been created in '{project_path}', configured with Inject, and opened in Xcode.")

if __name__ == "__main__":
    main()