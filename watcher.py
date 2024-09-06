import os
import time
import hashlib
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent
from pbxproj import XcodeProject

class XcodeProjectHandler(FileSystemEventHandler):
    def __init__(self, project_path, watch_folder):
        self.project_path = project_path
        self.watch_folder = watch_folder
        pbxproj_path = os.path.join(project_path, 'project.pbxproj')
        self.project = XcodeProject.load(pbxproj_path)
        self.ignored_paths = [
            'Sandstone.xcodeproj',
            '.DS_Store',
            '.git',
        ]
        self.file_hashes = {}
        self.last_event_time = {}
        self.debounce_time = 0.5  # 500ms debounce

    def on_any_event(self, event):
        if self.should_process_event(event):
            current_time = time.time()
            last_time = self.last_event_time.get(event.src_path, 0)
            if current_time - last_time > self.debounce_time:
                self.last_event_time[event.src_path] = current_time
                if self.has_content_changed(event):
                    print(f"Detected change: {event.src_path}")
                    self.update_project(event)

    def should_process_event(self, event):
        if not isinstance(event, FileSystemEvent):
            return False
        
        relative_path = os.path.relpath(event.src_path, self.watch_folder)
        return (
            not event.is_directory
            and event.src_path.endswith('.swift')
            and not any(ignored in relative_path for ignored in self.ignored_paths)
            and event.event_type in ['created', 'modified', 'deleted']
        )

    def has_content_changed(self, event):
        if event.event_type == 'deleted':
            return True
        try:
            with open(event.src_path, 'rb') as file:
                content = file.read()
                new_hash = hashlib.md5(content).hexdigest()
                old_hash = self.file_hashes.get(event.src_path)
                if new_hash != old_hash:
                    self.file_hashes[event.src_path] = new_hash
                    return True
        except Exception as e:
            print(f"Error reading file: {event.src_path}")
            print(f"Error details: {str(e)}")
        return False

    def update_project(self, event):
        relative_path = os.path.relpath(event.src_path, self.watch_folder)
        file_path = relative_path.replace('\\', '/')  # Ensure forward slashes
        
        print(f"Updating project: {event.event_type} {file_path}")
        
        if event.event_type in ['created', 'modified']:
            self.add_file_if_not_exists(file_path)
        elif event.event_type == 'deleted':
            self.remove_file_or_folder(file_path)

        self.project.save()
        print(f"Updated project: {event.event_type} {file_path}")

    def add_file_if_not_exists(self, path):
        try:
            full_path = os.path.join(self.watch_folder, path)
            existing_files = self.project.get_files_by_path(full_path)
            if not existing_files:
                # Determine the parent group based on the file's path
                parent_group = self.get_or_create_parent_group(full_path)
                if parent_group:
                    self.project.add_file(full_path, parent=parent_group)
                    print(f"Added file: {path}")
                else:
                    print(f"Failed to add file: {path}. Parent group not found.")
            else:
                print(f"File already exists in project: {path}")
        except Exception as e:
            print(f"Error processing file: {path}")
            print(f"Error details: {str(e)}")

    def remove_file_or_folder(self, path):
        try:
            files = self.project.get_files_by_path(path)
            for file in files:
                # Get all build files referencing this file
                build_files = self.project.get_build_files(file)
                for build_file in build_files:
                    # Remove the build file from all build phases
                    for build_phase in self.project.objects.get_objects_in_section('PBXBuildPhase'):
                        if build_file.id in build_phase.files:
                            build_phase.remove_build_file(build_file)
                # Remove the file reference
                self.project.remove_file_by_id(file.id)
            print(f"Removed file: {path}")
        except Exception as e:
            print(f"Error removing file: {path}")
            print(f"Error details: {str(e)}")

    def get_or_create_parent_group(self, file_path):
        # Get the main group of the project
        main_group = self.project.root_object().mainGroup
        print(f"Main group: {main_group.get_name() if main_group else 'None'}")

        dir_path = os.path.dirname(os.path.relpath(file_path, self.watch_folder))
        print(f"Directory path: {dir_path}")
        
        components = dir_path.split(os.sep)
        print(f"Path components: {components}")
        
        current_group = main_group
        
        for component in components:
            if component:
                print(f"Creating/getting group: {component}")
                new_group = self.project.get_or_create_group(component, parent=current_group)
                if new_group is not None:
                    current_group = new_group
                    print(f"Current group updated to: {current_group.get_name()}")
                else:
                    print(f"Failed to create/get group: {component}")
                    return main_group
        
        print(f"Final group: {current_group.get_name()}")
        return current_group

if __name__ == "__main__":
    project_file = './output/Sandstone/Sandstone.xcodeproj'
    watch_folder = './output/Sandstone/Sandstone' 


    event_handler = XcodeProjectHandler(project_file, watch_folder)
    observer = Observer()
    observer.schedule(event_handler, watch_folder, recursive=True)
    observer.start()

    try:
        print(f"Watching for changes in {watch_folder}...")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
