import Foundation
import CoreGraphics
let pid = Int32(CommandLine.arguments[1])!
let options: CGWindowListOption = [.optionOnScreenOnly, .excludeDesktopElements]
let windows = CGWindowListCopyWindowInfo(options, kCGNullWindowID) as? [[String:Any]] ?? []
let own = windows.filter { ($0[kCGWindowOwnerPID as String] as? Int32) == pid }
let data = try JSONSerialization.data(withJSONObject: own, options: [.prettyPrinted,.sortedKeys])
FileHandle.standardOutput.write(data)
