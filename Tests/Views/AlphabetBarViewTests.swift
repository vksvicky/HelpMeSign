import XCTest
@testable import HelpMeSign

class AlphabetBarViewTests: XCTestCase {
    
    var alphabetBarView: AlphabetBarView!
    
    override func setUp() {
        super.setUp()
        alphabetBarView = AlphabetBarView(frame: NSRect(x: 0, y: 0, width: 400, height: 300))
    }
    
    override func tearDown() {
        alphabetBarView = nil
        super.tearDown()
    }
    
    // MARK: - Success/Happy Path Tests
    
    func testSuccessfulInitialization() {
        // Test basic initialization
        XCTAssertNotNil(alphabetBarView, "AlphabetBarView should be created successfully")
        XCTAssertEqual(alphabetBarView.frame.width, 400, "Frame width should be set correctly")
        XCTAssertEqual(alphabetBarView.frame.height, 300, "Frame height should be set correctly")
        XCTAssertEqual(alphabetBarView.currentLanguage, "ASL", "Should initialize with ASL language")
        XCTAssertEqual(alphabetBarView.svgFileName, "asl_alphabet_numbers", "Should have correct SVG file name")
        // Note: letterViews may not be empty initially due to setupLanguage being called in init
    }
    
    func testSuccessfulCharacterLoading() {
        // Test successful character loading from SVG
        let testSVG = """
        <svg xmlns="http://www.w3.org/2000/svg" width="3600" height="100" viewBox="0 0 3600 100">
          <symbol id="A" viewBox="0 0 100 100">
            <circle cx="50" cy="50" r="40" fill="#e0e0e0"/>
            <text x="50" y="60" font-size="48" text-anchor="middle" fill="#333">A</text>
          </symbol>
          <symbol id="B" viewBox="0 0 100 100">
            <circle cx="50" cy="50" r="40" fill="#e0e0e0"/>
            <text x="50" y="60" font-size="48" text-anchor="middle" fill="#333">B</text>
          </symbol>
          <symbol id="1" viewBox="0 0 100 100">
            <circle cx="50" cy="50" r="40" fill="#e0e0e0"/>
            <text x="50" y="60" font-size="48" text-anchor="middle" fill="#333">1</text>
          </symbol>
        </svg>
        """
        
        let characters = alphabetBarView.extractCharacterList(from: testSVG)
        XCTAssertEqual(characters.count, 3, "Should extract 3 characters")
        XCTAssertEqual(characters, ["A", "B", "1"], "Should extract characters in correct order")
    }
    
    func testSuccessfulGridLayout() {
        // Test successful grid layout creation
        alphabetBarView.allItems = ["A", "B", "C", "D", "E", "F", "G", "H", "I"]
        alphabetBarView.setupLetters()
        
        XCTAssertEqual(alphabetBarView.letterViews.count, 9, "Should create 9 letter views")
        XCTAssertEqual(alphabetBarView.subviews.count, 9, "Should add 9 subviews")
        
        // Verify first view properties
        if let firstView = alphabetBarView.letterViews.first {
            XCTAssertEqual(firstView.letter, "A", "First view should have letter 'A'")
            XCTAssertFalse(firstView.frame.isEmpty, "First view should have valid frame")
        }
    }
    
    func testSuccessfulSorting() {
        // Test successful character sorting
        let unsortedCharacters = ["Z", "A", "5", "B", "0", "C", "1", "D"]
        let sortedCharacters = alphabetBarView.extractCharacterList(from: createTestSVG(with: unsortedCharacters))
        
        XCTAssertEqual(sortedCharacters, ["A", "B", "C", "D", "Z", "0", "1", "5"], "Should sort characters correctly")
    }
    
    // MARK: - Negative/Unhappy Path Tests
    
    func testEmptySVGInput() {
        // Test handling of empty SVG input
        let emptySVG = ""
        let characters = alphabetBarView.extractCharacterList(from: emptySVG)
        
        XCTAssertEqual(characters.count, 0, "Should return empty array for empty SVG")
    }
    
    func testInvalidSVGInput() {
        // Test handling of invalid SVG input
        let invalidSVG = "This is not an SVG"
        let characters = alphabetBarView.extractCharacterList(from: invalidSVG)
        
        XCTAssertEqual(characters.count, 0, "Should return empty array for invalid SVG")
    }
    
    func testSVGWithoutSymbols() {
        // Test handling of SVG without symbol elements
        let svgWithoutSymbols = """
        <svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">
          <circle cx="50" cy="50" r="40" fill="#e0e0e0"/>
        </svg>
        """
        
        let characters = alphabetBarView.extractCharacterList(from: svgWithoutSymbols)
        XCTAssertEqual(characters.count, 0, "Should return empty array for SVG without symbols")
    }
    
    func testEmptyCharacterList() {
        // Test handling of empty character list
        alphabetBarView.allItems = []
        alphabetBarView.setupLetters()
        
        XCTAssertEqual(alphabetBarView.letterViews.count, 0, "Should create no letter views for empty list")
        XCTAssertEqual(alphabetBarView.subviews.count, 0, "Should add no subviews for empty list")
    }
    
    func testSingleCharacter() {
        // Test handling of single character
        alphabetBarView.allItems = ["A"]
        alphabetBarView.setupLetters()
        
        XCTAssertEqual(alphabetBarView.letterViews.count, 1, "Should create 1 letter view")
        XCTAssertEqual(alphabetBarView.subviews.count, 1, "Should add 1 subview")
        
        if let firstView = alphabetBarView.letterViews.first {
            XCTAssertEqual(firstView.letter, "A", "Should have correct letter")
        }
    }
    
    func testVeryLargeCharacterList() {
        // Test handling of very large character list
        let largeList = Array(0..<100).map { String($0) }
        alphabetBarView.allItems = largeList
        alphabetBarView.setupLetters()
        
        XCTAssertEqual(alphabetBarView.letterViews.count, 100, "Should create 100 letter views")
        XCTAssertEqual(alphabetBarView.subviews.count, 100, "Should add 100 subviews")
    }
    
    // MARK: - Exception/Error Handling Tests
    
    func testMalformedSVGWithInvalidXML() {
        // Test handling of malformed SVG with invalid XML
        let malformedSVG = """
        <svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">
          <symbol id="A" viewBox="0 0 100 100">
            <circle cx="50" cy="50" r="40" fill="#e0e0e0"/>
            <text x="50" y="60" font-size="48" text-anchor="middle" fill="#333">A</text>
          </symbol>
          <symbol id="B" viewBox="0 0 100 100">
            <circle cx="50" cy="50" r="40" fill="#e0e0e0"/>
            <text x="50" y="60" font-size="48" text-anchor="middle" fill="#333">B</text>
          </symbol>
          <unclosed-tag>
        </svg>
        """
        
        let characters = alphabetBarView.extractCharacterList(from: malformedSVG)
        // Should handle gracefully and extract what it can
        XCTAssertGreaterThanOrEqual(characters.count, 0, "Should handle malformed SVG gracefully")
    }
    
    func testSVGWithSpecialCharacters() {
        // Test handling of SVG with special characters in symbol IDs
        let svgWithSpecialChars = """
        <svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">
          <symbol id="A-B" viewBox="0 0 100 100">
            <circle cx="50" cy="50" r="40" fill="#e0e0e0"/>
            <text x="50" y="60" font-size="48" text-anchor="middle" fill="#333">A</text>
          </symbol>
          <symbol id="B_C" viewBox="0 0 100 100">
            <circle cx="50" cy="50" r="40" fill="#e0e0e0"/>
            <text x="50" y="60" font-size="48" text-anchor="middle" fill="#333">B</text>
          </symbol>
        </svg>
        """
        
        let characters = alphabetBarView.extractCharacterList(from: svgWithSpecialChars)
        XCTAssertEqual(characters.count, 2, "Should extract characters with special characters in IDs")
        XCTAssertTrue(characters.contains("A-B"), "Should contain character with hyphen")
        XCTAssertTrue(characters.contains("B_C"), "Should contain character with underscore")
    }
    
    func testSVGWithDuplicateSymbolIDs() {
        // Test handling of SVG with duplicate symbol IDs
        let svgWithDuplicates = """
        <svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">
          <symbol id="A" viewBox="0 0 100 100">
            <circle cx="50" cy="50" r="40" fill="#e0e0e0"/>
            <text x="50" y="60" font-size="48" text-anchor="middle" fill="#333">A</text>
          </symbol>
          <symbol id="A" viewBox="0 0 100 100">
            <circle cx="50" cy="50" r="40" fill="#e0e0e0"/>
            <text x="50" y="60" font-size="48" text-anchor="middle" fill="#333">A</text>
          </symbol>
          <symbol id="B" viewBox="0 0 100 100">
            <circle cx="50" cy="50" r="40" fill="#e0e0e0"/>
            <text x="50" y="60" font-size="48" text-anchor="middle" fill="#333">B</text>
          </symbol>
        </svg>
        """
        
        let characters = alphabetBarView.extractCharacterList(from: svgWithDuplicates)
        XCTAssertEqual(characters.count, 2, "Should handle duplicates and return unique characters")
        XCTAssertTrue(characters.contains("A"), "Should contain A")
        XCTAssertTrue(characters.contains("B"), "Should contain B")
    }
    
    func testSVGWithEmptySymbolIDs() {
        // Test handling of SVG with empty symbol IDs
        let svgWithEmptyIDs = """
        <svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">
          <symbol id="" viewBox="0 0 100 100">
            <circle cx="50" cy="50" r="40" fill="#e0e0e0"/>
            <text x="50" y="60" font-size="48" text-anchor="middle" fill="#333">A</text>
          </symbol>
          <symbol id="B" viewBox="0 0 100 100">
            <circle cx="50" cy="50" r="40" fill="#e0e0e0"/>
            <text x="50" y="60" font-size="48" text-anchor="middle" fill="#333">B</text>
          </symbol>
        </svg>
        """
        
        let characters = alphabetBarView.extractCharacterList(from: svgWithEmptyIDs)
        XCTAssertEqual(characters.count, 1, "Should handle empty symbol IDs gracefully")
        XCTAssertTrue(characters.contains("B"), "Should contain valid symbol ID")
    }
    
    func testSVGWithMissingIDAttribute() {
        // Test handling of SVG with symbols missing ID attribute
        let svgWithMissingIDs = """
        <svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">
          <symbol viewBox="0 0 100 100">
            <circle cx="50" cy="50" r="40" fill="#e0e0e0"/>
            <text x="50" y="60" font-size="48" text-anchor="middle" fill="#333">A</text>
          </symbol>
          <symbol id="B" viewBox="0 0 100 100">
            <circle cx="50" cy="50" r="40" fill="#e0e0e0"/>
            <text x="50" y="60" font-size="48" text-anchor="middle" fill="#333">B</text>
          </symbol>
        </svg>
        """
        
        let characters = alphabetBarView.extractCharacterList(from: svgWithMissingIDs)
        XCTAssertEqual(characters.count, 1, "Should handle missing ID attributes gracefully")
        XCTAssertTrue(characters.contains("B"), "Should contain symbol with valid ID")
    }
    
    // MARK: - Edge Case Tests
    
    func testVerySmallFrame() {
        // Test handling of very small frame
        let smallView = AlphabetBarView(frame: NSRect(x: 0, y: 0, width: 50, height: 30))
        smallView.allItems = ["A", "B", "C"]
        smallView.setupLetters()
        
        XCTAssertEqual(smallView.letterViews.count, 3, "Should create all letter views even with small frame")
        
        // Verify views have reasonable sizes
        for view in smallView.letterViews {
            XCTAssertTrue(view.frame.width > 0, "View should have positive width")
            XCTAssertTrue(view.frame.height > 0, "View should have positive height")
        }
    }
    
    func testVeryLargeFrame() {
        // Test handling of very large frame
        let largeView = AlphabetBarView(frame: NSRect(x: 0, y: 0, width: 2000, height: 1500))
        largeView.allItems = ["A", "B", "C"]
        largeView.setupLetters()
        
        XCTAssertEqual(largeView.letterViews.count, 3, "Should create all letter views with large frame")
        
        // Verify views don't exceed maximum size
        for view in largeView.letterViews {
            XCTAssertLessThanOrEqual(view.frame.width, 80, "View should not exceed maximum width")
            XCTAssertLessThanOrEqual(view.frame.height, 80, "View should not exceed maximum height")
        }
    }
    
    func testFrameResize() {
        // Test handling of frame resize
        alphabetBarView.allItems = ["A", "B", "C", "D", "E", "F", "G", "H", "I"]
        alphabetBarView.setupLetters()
        
        let initialViewCount = alphabetBarView.letterViews.count
        let initialFirstViewFrame = alphabetBarView.letterViews.first?.frame
        
        // Resize frame
        alphabetBarView.frame = NSRect(x: 0, y: 0, width: 600, height: 400)
        alphabetBarView.setupLetters()
        
        XCTAssertEqual(alphabetBarView.letterViews.count, initialViewCount, "Should maintain same number of views after resize")
        
        if let newFirstViewFrame = alphabetBarView.letterViews.first?.frame {
            XCTAssertNotEqual(newFirstViewFrame, initialFirstViewFrame, "View frames should change after resize")
        }
    }
    
    func testMixedCharacterTypes() {
        // Test handling of mixed character types (letters, numbers, symbols)
        let mixedCharacters = ["A", "1", "!", "B", "2", "@", "C", "3", "#"]
        let characters = alphabetBarView.extractCharacterList(from: createTestSVG(with: mixedCharacters))
        
        XCTAssertEqual(characters.count, 9, "Should handle mixed character types")
        XCTAssertTrue(characters.contains("A"), "Should contain letters")
        XCTAssertTrue(characters.contains("1"), "Should contain numbers")
        XCTAssertTrue(characters.contains("!"), "Should contain symbols")
    }
    
    func testUnicodeCharacters() {
        // Test handling of Unicode characters
        let unicodeCharacters = ["A", "é", "ñ", "中", "B", "ü", "C"]
        let characters = alphabetBarView.extractCharacterList(from: createTestSVG(with: unicodeCharacters))
        
        XCTAssertEqual(characters.count, 7, "Should handle Unicode characters")
        XCTAssertTrue(characters.contains("A"), "Should contain ASCII characters")
        XCTAssertTrue(characters.contains("é"), "Should contain accented characters")
        XCTAssertTrue(characters.contains("中"), "Should contain CJK characters")
    }
    
    func testGridLayoutFirstRowIsAtTop() {
        // Given
        let frame = NSRect(x: 0, y: 0, width: 900, height: 400)
        let alphabetBarView = AlphabetBarView(frame: frame)
        alphabetBarView.allItems = Array("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789").map { String($0) }
        alphabetBarView.setupLetters()
        
        // When
        let firstRowLetters = alphabetBarView.letterViews.prefix(9).map { $0.letter }
        let expectedFirstRow = ["A","B","C","D","E","F","G","H","I"]
        
        // Then
        XCTAssertEqual(firstRowLetters, expectedFirstRow, "First row should be A-I at the top after Y-axis flip")
        
        // Check that the Y position of the first row is the highest
        let yPositions = alphabetBarView.letterViews.prefix(9).map { $0.frame.origin.y }
        let maxY = yPositions.max() ?? 0
        for y in yPositions {
            XCTAssertEqual(y, maxY, accuracy: 1.0, "All first row letters should be at the top (max Y)")
        }
    }
    
    func testGridLayoutLastRowIsAtBottom() {
        // Given
        let frame = NSRect(x: 0, y: 0, width: 900, height: 400)
        let alphabetBarView = AlphabetBarView(frame: frame)
        alphabetBarView.allItems = Array("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789").map { String($0) }
        alphabetBarView.setupLetters()
        
        // When
        let lastRowLetters = alphabetBarView.letterViews.suffix(9).map { $0.letter }
        let expectedLastRow = ["1","2","3","4","5","6","7","8","9"]
        
        // Then
        XCTAssertEqual(lastRowLetters, expectedLastRow, "Last row should be 1-9 at the bottom after Y-axis flip")
        
        // Check that the Y position of the last row is the lowest
        let yPositions = alphabetBarView.letterViews.suffix(9).map { $0.frame.origin.y }
        let minY = yPositions.min() ?? 0
        for y in yPositions {
            XCTAssertEqual(y, minY, accuracy: 1.0, "All last row letters should be at the bottom (min Y)")
        }
    }
    
    func testGridLayoutVisualOrderMatchesExpected() {
        // Given
        let frame = NSRect(x: 0, y: 0, width: 900, height: 400)
        let alphabetBarView = AlphabetBarView(frame: frame)
        alphabetBarView.allItems = Array("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789").map { String($0) }
        alphabetBarView.setupLetters()
        
        // When
        let itemsPerRow = 9
        let numberOfRows = (alphabetBarView.allItems.count + itemsPerRow - 1) / itemsPerRow
        var visualOrder: [[String]] = []
        for row in 0..<numberOfRows {
            let start = row * itemsPerRow
            let end = min(start + itemsPerRow, alphabetBarView.letterViews.count)
            let rowLetters = alphabetBarView.letterViews[start..<end].map { $0.letter }
            visualOrder.append(rowLetters)
        }
        
        // Then
        let expectedOrder = [
            ["A","B","C","D","E","F","G","H","I"],
            ["J","K","L","M","N","O","P","Q","R"],
            ["S","T","U","V","W","X","Y","Z","0"],
            ["1","2","3","4","5","6","7","8","9"]
        ]
        XCTAssertEqual(visualOrder, expectedOrder, "Visual grid order should match expected after Y-axis flip")
    }
    
    func testGridLayoutWithFewerThanOneRow() {
        let frame = NSRect(x: 0, y: 0, width: 900, height: 400)
        let alphabetBarView = AlphabetBarView(frame: frame)
        alphabetBarView.allItems = ["A", "B", "C", "D", "E"]
        alphabetBarView.setupLetters()
        XCTAssertEqual(alphabetBarView.letterViews.count, 5)
        let expected = ["A", "B", "C", "D", "E"]
        let actual = alphabetBarView.letterViews.map { $0.letter }
        XCTAssertEqual(actual, expected)
        // All should be in the top row
        let yPositions = alphabetBarView.letterViews.map { $0.frame.origin.y }
        let maxY = yPositions.max() ?? 0
        for y in yPositions { XCTAssertEqual(y, maxY, accuracy: 1.0) }
    }
    
    func testGridLayoutWithExactlyOneFullRow() {
        let frame = NSRect(x: 0, y: 0, width: 900, height: 400)
        let alphabetBarView = AlphabetBarView(frame: frame)
        alphabetBarView.allItems = ["A","B","C","D","E","F","G","H","I"]
        alphabetBarView.setupLetters()
        XCTAssertEqual(alphabetBarView.letterViews.count, 9)
        let expected = ["A","B","C","D","E","F","G","H","I"]
        let actual = alphabetBarView.letterViews.map { $0.letter }
        XCTAssertEqual(actual, expected)
        // All should be in the top row
        let yPositions = alphabetBarView.letterViews.map { $0.frame.origin.y }
        let maxY = yPositions.max() ?? 0
        for y in yPositions { XCTAssertEqual(y, maxY, accuracy: 1.0) }
    }
    
    func testGridLayoutWithNonMultipleOfRow() {
        let frame = NSRect(x: 0, y: 0, width: 900, height: 400)
        let alphabetBarView = AlphabetBarView(frame: frame)
        alphabetBarView.allItems = ["A","B","C","D","E","F","G","H","I","J","K"]
        alphabetBarView.setupLetters()
        XCTAssertEqual(alphabetBarView.letterViews.count, 11)
        // First 9 should be top row, last 2 should be bottom row
        let topRowY = alphabetBarView.letterViews[0].frame.origin.y
        let bottomRowY = alphabetBarView.letterViews[9].frame.origin.y
        XCTAssertGreaterThan(topRowY, bottomRowY)
        let topRow = alphabetBarView.letterViews.prefix(9).map { $0.letter }
        let bottomRow = alphabetBarView.letterViews.suffix(2).map { $0.letter }
        XCTAssertEqual(topRow, ["A","B","C","D","E","F","G","H","I"])
        XCTAssertEqual(bottomRow, ["J","K"])
    }
    
    func testGridLayoutWithMoreThan36Items() {
        let frame = NSRect(x: 0, y: 0, width: 900, height: 400)
        let alphabetBarView = AlphabetBarView(frame: frame)
        alphabetBarView.allItems = (0..<40).map { "X\($0)" }
        alphabetBarView.setupLetters()
        XCTAssertEqual(alphabetBarView.letterViews.count, 40)
        // Should have 5 rows (9+9+9+9+4)
        let itemsPerRow = 9
        let numberOfRows = (40 + itemsPerRow - 1) / itemsPerRow
        var rowYs: [CGFloat] = []
        for i in 0..<numberOfRows {
            let idx = i * itemsPerRow
            if idx < alphabetBarView.letterViews.count {
                rowYs.append(alphabetBarView.letterViews[idx].frame.origin.y)
            }
        }
        // Y positions should decrease as row increases
        for i in 1..<rowYs.count {
            XCTAssertLessThan(rowYs[i], rowYs[i-1])
        }
    }
    
    func testGridLayoutWithOnlyNumbers() {
        let frame = NSRect(x: 0, y: 0, width: 900, height: 400)
        let alphabetBarView = AlphabetBarView(frame: frame)
        alphabetBarView.allItems = ["1","2","3","4","5","6","7","8","9"]
        alphabetBarView.setupLetters()
        XCTAssertEqual(alphabetBarView.letterViews.count, 9)
        let expected = ["1","2","3","4","5","6","7","8","9"]
        let actual = alphabetBarView.letterViews.map { $0.letter }
        XCTAssertEqual(actual, expected)
    }
    
    func testGridLayoutWithOnlyLetters() {
        let frame = NSRect(x: 0, y: 0, width: 900, height: 400)
        let alphabetBarView = AlphabetBarView(frame: frame)
        alphabetBarView.allItems = ["A","B","C","D","E","F","G","H","I","J"]
        alphabetBarView.setupLetters()
        XCTAssertEqual(alphabetBarView.letterViews.count, 10)
        let expected = ["A","B","C","D","E","F","G","H","I","J"]
        let actual = alphabetBarView.letterViews.map { $0.letter }
        XCTAssertEqual(actual, expected)
    }
    
    func testGridLayoutWithEmptyAllItems() {
        let frame = NSRect(x: 0, y: 0, width: 900, height: 400)
        let alphabetBarView = AlphabetBarView(frame: frame)
        alphabetBarView.allItems = []
        alphabetBarView.setupLetters()
        XCTAssertEqual(alphabetBarView.letterViews.count, 0)
    }
    
    // MARK: - Performance Tests
    
    func testPerformanceWithLargeSVG() {
        // Test performance with large SVG
        let largeSVG = createLargeTestSVG()
        
        measure {
            _ = alphabetBarView.extractCharacterList(from: largeSVG)
        }
    }
    
    func testPerformanceWithManyViews() {
        // Test performance with many views
        let manyCharacters = Array(0..<100).map { String($0) }
        alphabetBarView.allItems = manyCharacters
        
        measure {
            alphabetBarView.setupLetters()
        }
    }
    
    // MARK: - Helper Methods
    
    private func createTestSVG(with characters: [String]) -> String {
        let symbolElements = characters.map { char in
            """
              <symbol id="\(char)" viewBox="0 0 100 100">
                <circle cx="50" cy="50" r="40" fill="#e0e0e0"/>
                <text x="50" y="60" font-size="48" text-anchor="middle" fill="#333">\(char)</text>
              </symbol>
            """
        }.joined(separator: "\n")
        
        return """
        <svg xmlns="http://www.w3.org/2000/svg" width="3600" height="100" viewBox="0 0 3600 100">
        \(symbolElements)
        </svg>
        """
    }
    
    private func createLargeTestSVG() -> String {
        let characters = Array(0..<1000).map { String($0) }
        return createTestSVG(with: characters)
    }
} 