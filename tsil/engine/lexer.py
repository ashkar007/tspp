"""
Lexer — tokeniser for the TSIL expression language.

Breaks an input string into a flat stream of Token objects ready
for the recursive-descent parser.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum, auto
from typing import Iterator


class TokenType(Enum):
    # Literals
    NUMBER     = auto()
    STRING     = auto()
    IDENTIFIER = auto()

    # Delimiters
    LPAREN     = auto()   # (
    RPAREN     = auto()   # )
    LBRACKET   = auto()   # [
    RBRACKET   = auto()   # ]
    COMMA      = auto()   # ,

    # Operators
    PLUS       = auto()   # +
    MINUS      = auto()   # -
    STAR       = auto()   # *
    SLASH      = auto()   # /
    POWER      = auto()   # **
    EQUALS     = auto()   # =

    # Control
    NEWLINE    = auto()
    EOF        = auto()


@dataclass
class Token:
    type: TokenType
    value: str
    line: int
    col: int

    def __repr__(self) -> str:
        return f"Token({self.type.name}, {self.value!r}, L{self.line}:{self.col})"


# ---------------------------------------------------------------------------
# Lexer
# ---------------------------------------------------------------------------

# Order matters: longer patterns first (e.g. ** before *)
_TOKEN_SPEC: list[tuple[str, TokenType | None]] = [
    (r"[ \t]+",            None),           # whitespace — skip
    (r"#[^\n]*",           None),           # line comment — skip
    (r"\n",                TokenType.NEWLINE),
    (r"\*\*",              TokenType.POWER),
    (r"\+",                TokenType.PLUS),
    (r"-",                 TokenType.MINUS),
    (r"\*",                TokenType.STAR),
    (r"/",                 TokenType.SLASH),
    (r"=",                 TokenType.EQUALS),
    (r"\(",                TokenType.LPAREN),
    (r"\)",                TokenType.RPAREN),
    (r"\[",                TokenType.LBRACKET),
    (r"\]",                TokenType.RBRACKET),
    (r",",                 TokenType.COMMA),
    # String literal (double-quoted, with basic escapes)
    (r'"(?:[^"\\]|\\.)*"', TokenType.STRING),
    # Number: integer or float
    (r"\d+(?:\.\d+)?",     TokenType.NUMBER),
    # Identifier: letters, digits, underscores, dots (for Reuters tickers)
    (r"[A-Za-z_][A-Za-z0-9_.]*", TokenType.IDENTIFIER),
]

_MASTER_RE = re.compile(
    "|".join(f"(?P<G{i}>{pat})" for i, (pat, _) in enumerate(_TOKEN_SPEC))
)


class LexerError(Exception):
    """Raised when the lexer encounters an unexpected character."""
    def __init__(self, char: str, line: int, col: int) -> None:
        super().__init__(f"Unexpected character {char!r} at line {line}, col {col}")
        self.char = char
        self.line = line
        self.col = col


def tokenize(source: str) -> list[Token]:
    """Tokenise a TSIL source string into a list of Tokens.

    Args:
        source: TSIL expression or multi-line program.

    Returns:
        List of Token objects (always ends with EOF).

    Raises:
        LexerError: on unrecognised characters.
    """
    tokens: list[Token] = []
    line = 1
    line_start = 0

    for mo in _MASTER_RE.finditer(source):
        kind_index = mo.lastindex  # 1-based
        if kind_index is None:
            continue

        idx = kind_index - 1  # 0-based index into _TOKEN_SPEC
        _, token_type = _TOKEN_SPEC[idx]
        value = mo.group()
        col = mo.start() - line_start + 1

        if token_type is None:
            # Skip whitespace / comments
            continue

        if token_type == TokenType.NEWLINE:
            line += 1
            line_start = mo.end()
            # Only emit newlines between statements, skip consecutive
            if tokens and tokens[-1].type != TokenType.NEWLINE:
                tokens.append(Token(TokenType.NEWLINE, "\\n", line - 1, col))
            continue

        if token_type == TokenType.STRING:
            # Strip quotes and unescape
            value = value[1:-1].replace('\\"', '"').replace("\\\\", "\\")

        tokens.append(Token(token_type, value, line, col))

    # Check for un-tokenised characters
    covered = set()
    for mo in _MASTER_RE.finditer(source):
        covered.update(range(mo.start(), mo.end()))
    for i, ch in enumerate(source):
        if i not in covered and ch not in (" ", "\t", "\n", "\r"):
            # Compute line/col for error
            err_line = source[:i].count("\n") + 1
            err_col = i - source[:i].rfind("\n")
            raise LexerError(ch, err_line, err_col)

    tokens.append(Token(TokenType.EOF, "", line, 0))
    return tokens
