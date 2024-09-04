
import SwiftUI
import Inject

struct ContentView: View {
    @ObserveInjection var inject
    
    var body: some View {
        Text("Hello, Jo! How are you")
            .enableInjection()
    }
}
