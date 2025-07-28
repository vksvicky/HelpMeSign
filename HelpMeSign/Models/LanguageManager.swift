import Foundation

struct LanguageInfo {
    let code: String
    let name: String
    let flag: String
    let country: String
}

class LanguageManager {
    static let shared = LanguageManager()
    private(set) var languages: [LanguageInfo] = []
    
    private init() {
        loadLanguages()
    }
    
    private func loadLanguages() {
        guard let url = Bundle.main.url(forResource: "languages", withExtension: "json"),
              let data = try? Data(contentsOf: url),
              let json = try? JSONSerialization.jsonObject(with: data) as? [[String: Any]] else { return }
        languages = json.compactMap { dict in
            guard let code = dict["code"] as? String,
                  let name = dict["name"] as? String,
                  let flag = dict["flag"] as? String,
                  let country = dict["country"] as? String else { return nil }
            return LanguageInfo(code: code, name: name, flag: flag, country: country)
        }
    }
    
    func flag(for code: String) -> String {
        languages.first(where: { $0.code == code })?.flag ?? "🌐"
    }
    
    func name(for code: String) -> String {
        languages.first(where: { $0.code == code })?.name ?? code
    }
} 