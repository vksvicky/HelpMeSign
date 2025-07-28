import Foundation

struct LanguageInfo {
    let code: String
    let name: String
    let flag: String
    let country: String
    let nativeName: String?
    let speakers: Int?
    let difficulty: String?
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
            
            // Extract speakers and difficulty from metadata
            let metadata = dict["metadata"] as? [String: Any]
            let speakers = metadata?["speakers"] as? Int
            let difficulty = metadata?["difficulty"] as? String
            let nativeName = dict["nativeName"] as? String
            
            return LanguageInfo(
                code: code,
                name: name,
                flag: flag,
                country: country,
                nativeName: nativeName,
                speakers: speakers,
                difficulty: difficulty
            )
        }
    }
    
    func flag(for code: String) -> String {
        languages.first(where: { $0.code == code })?.flag ?? "🌐"
    }
    
    func name(for code: String) -> String {
        languages.first(where: { $0.code == code })?.name ?? code
    }
    
    func speakers(for code: String) -> Int? {
        languages.first(where: { $0.code == code })?.speakers
    }
    
    func difficulty(for code: String) -> String? {
        languages.first(where: { $0.code == code })?.difficulty
    }
} 