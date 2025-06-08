# pushdown-automata
A **Pushdown Automaton** (PDA) is a 6-tuple:  
**M = (Q, Σ, Γ, δ, q₀, F)**, where:

- **Q** is a finite set of **states**
- **Σ** is a finite set of **input symbols** (the **input alphabet**)
- **Γ** is a finite set of **stack symbols** (the **stack alphabet**)
- **δ** is the **transition function**:  
  **δ : Q × (Σ ∪ {ε}) × (Γ ∪ {ε}) → P(Q × (Γ ∪ {ε}))**  
  The PDA reads an input symbol (or ε), pops a stack symbol (or ε), and transitions to a new state with optional push onto the stack.
- **q₀ ∈ Q** is the **initial state**
- **F ⊆ Q** is the set of **accepting (final) states**

A PDA uses a stack to keep track of additional memory. It is capable of recognizing **context-free languages**, unlike DFAs which only recognize **regular languages**.

## 📑 Table of Contents
- [Definition Format](#definition-format)
- [Example Definition](#example-definition)
- [Error Handling](#error-handling)
- [PDA Emulator](#pda-emulator)
- [Folder Structure](#folder-structure)
- [Usage](#usage)
- [Bonus: PDA-Based Game - "Escape the Room"](#bonus-pda-based-game---escape-the-room)
- [How to Play (Run) the PDA Game](#-how-to-play-the-game-using-emulatepdapy)

## Definition Format

Each PDA is defined in a `.pda` or `.txt` file using the following clearly marked sections:

- `[States]` — all finite states of the PDA
- `[Sigma]` — all input symbols (input alphabet Σ)
- `[Stack Sigma]` — all symbols that can be pushed to or popped from the stack (stack alphabet Γ)
- `[Rules]` — transition rules written as:
  ```
  current_state, input_symbol, pop_symbol, push_symbol, next_state
  ```
- `[Start]` — the initial state (q₀)
- `[Accept]` — one or more accepting (final) states (subset of Q)

Notes:
- Use `epsilon` to represent ε transitions (empty string input or empty stack operations)
- A rule like `q1, epsilon, $, epsilon, q2` means:  
  From `q1`, if input is empty and top of stack is `$`, pop it and move to `q2` with no push


Each section must be terminated with the keyword `End`.

⚠️ This format is intentionally kept **consistent** with the format used in [this DFA project](https://github.com/06cezar/deterministic-finite-automata#clearly-defined-sections), with added support for stack operations unique to PDA.

### Comments

- Single-line comments: start with `#`
- Multi-line comments: wrap between `/* ... */`
- Comments may appear inside sections and will be ignored by the parser

---

# Example Definition

A PDA for the language {0<sup>n</sup>1<sup>n</sup> | n ∈ ℕ}, the first non regular, but context-free language usually studied, found in the `PDA Definition Files/notregular.pda` file.

```
[States]
q0
q1
q2
q3
qd
End

[Sigma]
0
1
End

[Stack Sigma]
0
$
End 

[Rules]
q0, epsilon, epsilon, $, q1
q1, 0, epsilon, 0, q1
q1, 1, 0, epsilon, q2 
q2, 0, epsilon, epsilon, qd 
q2, 1, 0, epsilon, q2 
q2, 1, $, epsilon, qd 
q2, epsilon, $, epsilon, q3
End

[Start]
q0
End

[Accept]
q3
End
```

## Error Handling

The PDA implementation uses custom exception classes to handle invalid formats, undefined symbols, and input mismatches in a clean and readable way.

### Defined Exceptions

| Exception | Description |
|----------|-------------|
| `UndefinedStartStateError` | Raised when the `[Start]` section is missing or the specified start state is undefined |
| `UndefinedAcceptStatesError` | Raised when the `[Accept]` section is missing or empty |
| `UndefinedAlphabetError` | Raised when either `[Sigma]` or `[Stack Sigma]` is missing or empty |
| `InvalidStateError` | Raised when a state used in `[Start]`, `[Accept]`, or `[Rules]` is not declared in `[States]` |
| `InvalidSymbolError` | Raised when a symbol used in `[Rules]` is not defined in either the input or stack alphabet |
| `EpsilonTransitionError` | Raised if the user explicitly includes `epsilon` or `ε` in `[Sigma]` or `[Stack Sigma]`, which is not needed |
| `InputStringError` | Raised when the input string contains characters not listed in the `[Sigma]` section |

### Notes

- There is **no Duplicate Rule Error**, since PDA rules can allow multiple stack manipulations and destination states for the same input.
- Epsilon transitions (written as `epsilon` or `ε`) **are handled automatically** and **should not** be declared in `[Sigma]` or `[Stack Sigma]`.
- Rules are verified to ensure the validity of:
  - Source and destination states
  - Input and stack symbols
  - Correct stack push/pop semantics
- If a state has no defined rule for a symbol, it is treated as a self-loop (no-op), **not an error**.
### Example Error Messages
```
UndefinedStartStateError: Start state is not defined
InvalidStateError: Start state q0 is not defined
UndefinedAcceptStatesError: Accept state is not defined
InvalidStateError: Accept state q3 is not defined
UndefinedAlphabetError: Alphabet is not defined
UndefinedAlphabetError: Stack alphabet is not defined
InvalidStateError: Source state q99 is not defined in the states list for the PDA
InvalidSymbolError: Symbol X is not defined in the alphabet for the PDA
InvalidSymbolError: Symbol $ is not defined in the stack alphabet for the PDA
EpsilonTransitionError: Epsilon doesn't need to be defined in the alphabet for the PDA (it includes it by default). You can use 'epsilon' or 'ε' in your rules without defining epsilon or ε.
InputStringError: Input string contains symbols not in the given alphabet of the PDA
```

## PDA Emulator

The PDA emulator consists of the `emulatePDA.py` script and the `PDA.py` module. It supports both **interactive** use and **command-line** execution. This script simulates a **Pushdown Automaton (PDA)** with stack-based memory and epsilon transitions.

It reads:
- a PDA definition file (e.g., `.pda` or `.txt`)
- an input string file
- and simulates the PDA to determine acceptance, with optional step-by-step output

---

### ✅ Features

- Supports epsilon transitions (`ε` or `epsilon`) for input and stack operations
- Uses a stack to track context and memory
- Verbose mode prints each transition, input symbol, stack operation, and current state
- Accepts custom input separators (`SPACE`, `NOSEPARATOR`, `,`, `;`, etc.)
- Gracefully handles invalid definitions and malformed input with detailed errors
- Compatible with structured `.pda` definition format similar to DFA/NFA projects

---

## Folder Structure

```
project/
│
├── PDA.py
├── emulatePDA.py
├── PDA Definition Files/
│ └── your_machine.pda
├── Input Files/
└── your_input.txt
```

- The emulator uses Python’s `os` module and `chdir` function to **dynamically change directories** at runtime. This avoids hardcoded paths and makes the project more **cross-platform friendly**.
- This allows running the script in any environment (Linux/macOS/Windows) without manually modifying file paths.

**Example paths**:

- On **Linux/macOS**:

```
PDA Definition Files/your_machine.pda
```

- On **Windows**:

```
PDA Definition Files\your_machine.pda
```

---


## 📦 Requirements

To run the PDA emulator successfully, ensure the following structure:

- All core Python scripts (`PDA.py`, `emulatePDA.py`) should be in the project root folder.
- PDA definitions should be placed inside the `PDA Definition Files/` subfolder.
- Input strings should be placed inside the `Input Files/` subfolder.
- You should run the script from the **project root directory** using the terminal or an IDE.
## Usage

### 🔹 Option 1: Interactive Mode

```
python3 emulatePDA.py
```
or press the Run button on an IDE.

You’ll be prompted for:
- **PDA definition file name** - from `PDA Definition Files/`
- **Input string file name** - from `Input Files/`
- **Verbosity level:**
  - `1` → print all intermediate steps taken by the PDA
  - `0` → only print final result: `Accepted` or `Rejected`
- **Separator used between input symbols:**
  - `SPACE` → separator is a space (`' '`)
  - `NOSEPARATOR` → no separator (e.g., `abba`)
  - or any custom string (e.g., `;`, `,`, `|`)

### 🔹 Option 2: Run via CLI

```
python3 emulatePDA.py <pda_filename> <input_filename> [verbosity] [separator]
```

- `<pda_filename>`: file in `PDA Definition Files/`
- `<input_filename>`: file in `Input Files/`

- `[verbosity]`: *(Optional)*  
  Use `1` to print steps, `0` to print only the final result.  
  Default is `0` (only displays Accepted/Rejected).

- `[separator]`: *(Optional)*  
  Use:
  - `SPACE` for `' '`
  - `NOSEPARATOR` for no separator
  - Or any other string like `;`, `,`, `|`
  
  Default value is no separator!

> ⚠️ If your separator is a shell-special character like ;, &, |, etc., wrap it in single quotes (';') to prevent shell misinterpretation.
```
python3 emulatePDA.py notregular.pda 0n1mInput 1 NoSeparator    
```

## Custom exceptions 
Custom exceptions are raised for:

- Missing PDA/input files

- Not enough CLI arguments

- Invalid working directories

# Bonus: PDA-Based Game - "Escape the Room"

This PDA simulates a mini *adventure puzzle* game. The player navigates through rooms, must **pick up a spoon**, and only then is allowed to reach the **Exit**.

Unlike the [DFA version](https://github.com/06cezar/deterministic-finite-automata#bonus-dfa-based-game---escape-the-room), the PDA uses a **stack** to remember if the player has the spoon — making the logic far cleaner and easier to extend.

## 🕹️ Game Map
```
            Secret Room
                |
                |
 Kitchen-----Hallway-----Library
  Spoon         |           |
                |           |
            Entrance       Exit SPOON NEEDED
```
---

## 🔑 Why PDA Instead of DFA?

In a DFA, we simulated inventory (like holding a spoon) by **duplicating all states**:
- `Kitchen No Spoon` → `Kitchen With Spoon`
- `Library No Spoon` → `Library With Spoon`
- etc.

This approach becomes tedious when you have:
- multiple items
- branching logic
- recursive memory (like nested puzzles)

A **Pushdown Automaton** solves this by giving the machine **memory**, in the form of a **stack**.

---

## 🧠 Stack = Inventory

The PDA uses its stack to simulate the inventory:

- When the player performs the action `PICK` in the Kitchen, the PDA **pushes `SPOON`** onto the stack.
- Later, when transitioning to the Exit room, the PDA **checks if `SPOON` is on top of the stack**.
- Only if the spoon is there, the PDA allows the transition to the accepting `Exit` state.

---

## ✅ Benefits Over DFA

- **No need to duplicate states**
- **Game logic is cleaner**
- Easily extendable for other items (e.g., key, sword, map)
- Can support nested mechanics with stack operations

---

## 🕹️ Game Objective

To win the game, the player must:
1. Navigate to the Kitchen
2. Use `PICK` to pick up the spoon
3. Reach the Exit via the Library
4. PDA checks stack → if `SPOON` is there, you win

**Valid input:**
```
UP LEFT PICK RIGHT RIGHT DOWN
```

## 📂 Where to Find It

You can find the PDA definition file for this game in:
`PDA Definition Files/escapeTheRoom.pda`.

You can check out the DFA version [here](https://github.com/06cezar/deterministic-finite-automata#bonus-dfa-based-game---escape-the-room).

### 🎮 How to Play the Game Using `emulatePDA.py`

To try out the game, use the PDA emulator script and follow these steps:

#### ▶️ Run in the IDE

Run the emulator:
```
python3 emulatePDA.py
```
or press the run button :)

When prompted:

- **PDA Definition file name**:  
  Enter: `escapeTheRoom.pda`

- **Input string file name**:  
  Enter the name of a `.txt` file from the `Input Files/` folder that contains your sequence of moves.

Example content of `my_input.txt`:
```
UP LEFT PICK RIGHT RIGHT DOWN
```

- **Verbosity**:  
  Enter `1` to see each step, or `0` to only see the result.

- **Input separator**:  
  Enter `SPACE` (without quotes) to treat moves as space-separated.

#### ⚙️ CLI Mode

You can also run the game directly from the command line:
```
python3 emulatePDA.py escapeTheRoom.pda gameInput 1 SPACE
```
(1 - for verbosity, 0 - just shows result)

Make sure:

- `escapeTheRoom.pda` is located in the `PDA Definition Files/` directory
- `gameInput` is located in the `Input Files/` directory
- The input file contains a valid sequence of moves

