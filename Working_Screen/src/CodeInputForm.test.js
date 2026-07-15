import { describe, it, expect } from "vitest";
import { detectLanguage, looksSyntacticallyBroken } from "./CodeInputForm";

describe("detectLanguage", () => {
  it("detects Python successfully", () => {
    // Rationale: Verify that standard Python syntax hints ('def', 'print') resolve to 'python'.
    expect(detectLanguage("def hello_world():\n    print('Hello')")).toBe("python");
  });

  it("detects JavaScript successfully", () => {
    // Rationale: Verify that ES6 arrow functions and 'const' declarations resolve to 'javascript'.
    expect(detectLanguage("const greet = () => {\n    console.log('Hi');\n};")).toBe("javascript");
  });

  it("returns null for ambiguous code", () => {
    // Rationale: Ensure that text or comments without language indicators return null (ambiguous).
    expect(detectLanguage("// ambiguous text only")).toBe(null);
  });
});

describe("looksSyntacticallyBroken", () => {
  it("flags unmatched single quotes", () => {
    // Rationale: Catch regression where open single quotes are not detected.
    expect(looksSyntacticallyBroken("const x = 'hello;")).toBe(true);
  });

  it("flags unmatched double quotes", () => {
    // Rationale: Catch regression where open double quotes are not detected.
    expect(looksSyntacticallyBroken('const x = "hello;')).toBe(true);
  });

  it("flags unmatched backticks", () => {
    // Rationale: Catch regression where open template literals/backticks are not detected.
    expect(looksSyntacticallyBroken('const x = `hello;')).toBe(true);
  });

  it("flags unmatched parentheses", () => {
    // Rationale: Catch syntax errors from unbalanced parentheses.
    expect(looksSyntacticallyBroken("function add(a, b {\n    return a + b;\n}")).toBe(true);
  });

  it("flags unmatched curly braces", () => {
    // Rationale: Catch syntax errors from unbalanced object literals or function blocks.
    expect(looksSyntacticallyBroken("function add(a, b) \n    return a + b;\n}")).toBe(true);
  });

  it("flags unmatched square brackets", () => {
    // Rationale: Catch syntax errors from unbalanced array literals.
    expect(looksSyntacticallyBroken("const arr = [1, 2, 3;")).toBe(true);
  });

  it("does not flag valid JavaScript code containing braces in strings", () => {
    // Rationale: Guard against false positives by ensuring brackets inside strings/comments are ignored.
    const validJs = `
      const x = "bracket [ inside string";
      function test() {
        return (x === 'bracket [ inside string');
      }
    `;
    expect(looksSyntacticallyBroken(validJs)).toBe(false);
  });

  it("does not flag valid Python code containing string brackets", () => {
    // Rationale: Guard against false positives by ensuring valid Python snippets with brackets inside strings are not flagged.
    const validPy = `
      def greet(name: str) -> str:
          if not name:
              return "Hello [stranger]"
          return f"Hello, {name}!"
    `;
    expect(looksSyntacticallyBroken(validPy)).toBe(false);
  });
});
