# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **lightweight NLP parser** for text adventure games that provides:
- Fast natural language command parsing (4-8ms average)
- Pronoun resolution ("take the ball and kick it" → resolves "it" to "ball")
- Conversational wrapper handling ("I want to look at" → extracts "look at")
- Entity recognition for people, places, objects
- Contract-ready output format for blockchain/game integration

## Environment

- **Python version:** 3.13.2
- **Node.js version:** 18.20.8 (for tooling)
- **Key dependencies:** spaCy, transformers, pytest

## Architecture

### Core Components
- `parser.py` - Main NLP parser with `LightweightNLPParser` class
- `tests/test_parser_steps.py` - Comprehensive BDD test suite (12 scenarios)
- `features/parser.feature` - Gherkin BDD specifications

### Key Features
1. **Pronoun Resolution**: Links pronouns back to referenced nouns
2. **Conversational Filtering**: Ignores "I want to" and focuses on actions
3. **Entity Recognition**: Identifies people, objects, locations
4. **Multiple Output Formats**: Human-readable, JSON, and contract format

## Common Commands

### Running the Parser
```bash
# Parse a single command
python parser.py "take the ball and kick it at the window"

# Interactive mode
python parser.py --interactive

# JSON output
python parser.py "look at the door" --output json
```

### Testing
```bash
# Run all BDD tests
pytest tests/test_parser_steps.py -v

# Run specific test
pytest tests/test_parser_steps.py::test_parse_compound_command_with_pronoun_resolution -v
```

### Code Quality
```bash
# Style checking (configured for 100-char lines)
pycodestyle parser.py tests/

# Auto-format
autopep8 --in-place --max-line-length=100 parser.py
```

### Performance Profiling
```bash
# Full performance analysis
python profile_parser.py
```

## Development Notes

### Performance Characteristics
- **Initialization:** 0.19s (loads spaCy model)
- **Memory usage:** ~420MB (stable, no leaks)
- **Parsing speed:** 4.66ms (simple) to 7.92ms (complex)
- **Test suite:** 4.57s for 12 comprehensive tests

### Code Style
- **Line length:** 100 characters (configured in setup.cfg)
- **Style guide:** PEP 8 compliant
- **Import order:** Standard library, third-party, local imports

### Key Classes
- `LightweightNLPParser`: Main parser class
- `ParsedCommand`: Result dataclass with parsed components
- `Entity`: Named entity with confidence scores

### Test Coverage
All major parsing scenarios covered:
- Simple commands, pronoun resolution, compound commands
- Entity recognition, conversational wrappers, edge cases
- 100% test pass rate with BDD-style specifications