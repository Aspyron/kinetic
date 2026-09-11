# The Kinetic Syntax Guide

This guide describes the 1.1.1 prototype. Kinetic explores readable systems-language syntax, but it does not yet provide a production memory-safety model.

Kinetic is designed to feel as easy and readable, but it compiles down to raw machine code via LLVM. Let's take a quick tour of how things work!

See the [documentation index](README.md) for installation and architecture guides.

## Declaration keywords

| Purpose | Keyword |
| --- | --- |
| Define a function | [`func`](../compiler/lexer.py:33) |
| Declare an immutable binding | [`let`](../compiler/lexer.py:34) |
| Declare a mutable binding | [`mut`](../compiler/lexer.py:35) |

Declaring a name, reassigning a value, and calling a function are separate
operations. A mutable declaration starts directly with its own keyword.

## 1. Variables (and why they are strict)

An immutable binding gives a name to a value and cannot be reassigned. Types are inferred from expressions; you do not need a type annotation.

```text
// The compiler automatically figures out `name` is a String and `age` is an Int.
let name = "Aspyron"
let age = 5
```

For a binding that can be reassigned, use [`mut`](../compiler/lexer.py:35) as the declaration keyword:

```text
mut counter = 0
counter = counter + 1 // Reassignment has no declaration keyword.
```

Binding immutability is not a general guarantee that referenced data is deeply
immutable or memory-safe. Version 1.0.0 supports integer-array reads, but does not implement
indexed assignment or a production memory-safety model.

## 2. Functions (doing things)

Functions are defined with [`func`](../compiler/lexer.py:33). We keep the syntax clean—no semicolons at the end of every line, and the last expression evaluated is automatically returned.

```text
func calculate_speed(distance, time) {
    distance / time // No 'return' keyword needed!
}
```

The `main` function is the entry point of your program. In the 1.1.1 prototype it has a fixed no-argument entry shape; declaring parameters on `main` is a compile-time error. When you run your executable, this is where the action starts.

```text
func main() {
    let speed = calculate_speed(120, 2)
    print(speed)
}
```

Defining a function does not call it. The entry point calls the calculation
function using its name and arguments. For the smallest complete program, see
the [Hello World example](../examples/01_hello.kn).

## 3. Control Flow (making decisions)

Our `if` and `else` statements look exactly how you'd expect, minus the clutter of unnecessary parentheses around the condition.

```text
let speed_limit = 70
let speed = 85

if speed > speed_limit {
    print("Uh oh, speeding ticket!")
} else {
    print("Safe driving!")
}
```

*(Note: comparisons cover `==`, `!=`, `<`, `>`, `<=`, and `>=`; see the operators section below.)*

## 4. Loops (doing things repeatedly)

Need to do something over and over? The `while` loop has your back. Just remember to use a mutable variable so you don't loop forever!

```text
mut i = 0

while i < 3 {
    print("Looping...")
    i = i + 1
}
```

## 5. Arrays (lists of things)

Version 1.0.0 arrays contain integers. Array literals and indexed reads are supported;
arrays of strings and mixed element types are not part of the current language.

```text
let high_scores = [100, 95, 80]

// Arrays are zero-indexed, meaning the first item is at position 0.
let top_score = high_scores[0] 
print(top_score)
```

The analyzer preserves a known array length through direct binding copies and
reassignment when the source length is known. Across conditionals and loops it
keeps that fact only when every possible path agrees, so a stale length is not
used for a later constant bounds diagnostic.

Behind the scenes, the LLVM backend uses pointer arithmetic to access array elements. This is a prototype implementation, not a guarantee of memory safety or zero runtime cost.

## 6. Operators (combining values)

Integers support arithmetic, remainder, bitwise, and shift operators:

```text
print(7 % 3)   // Remainder: 1
print(5 & 6)   // Bitwise AND: 4
print(5 | 6)   // Bitwise OR: 7
print(5 ^ 6)   // Bitwise XOR: 3
print(1 << 4)  // Shift left: 16
print(32 >> 2) // Shift right: 8
```

Precedence follows C: multiplicative (`* / %`) binds tightest, then additive
(`+ -`), shifts (`<< >>`), relational (`< > <= >=`), equality (`== !=`), and
finally `&`, `^`, `|` in that order. Comparisons yield booleans for `if` and
`while` conditions; every operator works on integers only. There is no unary
`!` or unary minus in 1.1.1.

---

That's the 1.1.1 language surface. Explore the [complete examples](../examples/README.md) to see these features together.
