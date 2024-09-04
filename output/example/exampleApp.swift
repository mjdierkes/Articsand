
import SwiftUI
@_exported import Inject

@main
struct exampleApp: App {
    init() {
        Bundle(path: "/Applications/InjectionIII.app/Contents/Resources/iOSInjection.bundle")?.load()
    }

    var body: some Scene {
        WindowGroup {
            ContentView()
        }
    }
}
