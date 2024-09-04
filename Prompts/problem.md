# Problem Statement

The goal of this project is to create a streamlined environment for using Cursor AI with Xcode projects, focusing on reducing friction in the development process. Specifically, the project aims to:

1. Automatically set up an Xcode project with the Inject library integrated for hot reloading capabilities. https://github.com/krzysztofzablocki/Inject

2. Modify the Swift app file to include `@_exported import Inject`, enabling project-wide access to the Inject functionality.

3. Automatically add necessary code to the ContentView, including:

   - `@ObserveInjection var inject`
   - `.enableInjection()` modifier to the view's body

4. Utilize XcodeGen for project generation and management.

5. Create a seamless workflow that allows developers to leverage Cursor AI's capabilities within their Xcode projects.

6. Implement a file system watcher that monitors the Xcode project folder for changes, including:

   - New file additions
   - File removals
   - Directory structure changes

7. Automatically interact with XcodeGen to update the project configuration when changes are detected in the project folder.

The primary challenge is to automate these setup processes as much as possible, minimizing manual intervention and reducing the potential for configuration errors. The solution should be user-friendly and integrate smoothly with existing Xcode workflows, while maintaining an up-to-date project structure through continuous monitoring and automatic updates.
