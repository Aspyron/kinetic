# The Kinetic Syntax Guide

Hey there! 👋 Welcome to Kinetic. 

If you're reading this, you probably want to write some blazing-fast systems code without having to fight a borrow checker or manage memory manually. You're in the right place. 

Kinetic is designed to feel as easy and readable as Python or JavaScript, but it compiles down to raw machine code via LLVM. Let's take a quick tour of how things work!

## 1. Variables (and why they are strict)

By default, everything in Kinetic is immutable. That means once you set a variable, it's locked in. This prevents a whole class of messy bugs where data changes unexpectedly.

```rust
// The compiler automatically figures out `name` is a String and `age` is an Int.
let name = "Aspyron"
let age = 5
```

Need a variable to change later? No problem, just tell the compiler upfront by using `mut` (short for mutable):

```rust
let mut counter = 0
counter = counter + 1 // This works perfectly!
```

## 2. Functions (doing things)

Functions are defined with the `fn` keyword. We keep the syntax clean—no semicolons at the end of every line, and the last expression evaluated is automatically returned.

```rust
fn calculate_speed(distance, time) {
    distance / time // No 'return' keyword needed!
}
```

The `main` function is the entry point of your program. When you run your executable, this is where the action starts.

```rust
fn main() {
    let speed = calculate_speed(120, 2)
    print(speed)
}
```

## 3. Control Flow (making decisions)

Our `if` and `else` statements look exactly how you'd expect, minus the clutter of unnecessary parentheses around the condition.

```rust
let speed_limit = 70
let speed = 85

if speed > speed_limit {
    print("Uh oh, speeding ticket!")
} else {
    print("Safe driving!")
}
```

*(Note: In V1, we currently support `==`, `<`, and `>` for comparisons).*

## 4. Loops (doing things repeatedly)

Need to do something over and over? The `while` loop has your back. Just remember to use a mutable variable so you don't loop forever!

```rust
let mut i = 0

while i < 3 {
    print("Looping...")
    i = i + 1
}
```

## 5. Arrays (lists of things)

Sometimes you have a bunch of related data. You can group them in an Array. Kinetic Arrays are strongly typed, meaning you can't mix numbers and strings in the same list. 

```rust
let high_scores = [100, 95, 80]

// Arrays are zero-indexed, meaning the first item is at position 0.
let top_score = high_scores[0] 
print(top_score)
```

Behind the scenes, Kinetic is doing pointer math (`gep`) via LLVM to fetch your data straight from memory at zero cost!

---

That's it for V1! You now know everything you need to start building fast, safe applications in Kinetic. Go check out the `examples/` folder and have fun coding! 🚀
