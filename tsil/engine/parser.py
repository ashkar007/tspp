"""
Parser — recursive-descent parser for the TSIL expression language.

Transforms a flat list of Tokens into an AST (abstract syntax tree).

Grammar (informal):
    program      → statement*
    statement    → assignment | expression
    assignment   → IDENTIFIER '=' expression
    expression   → additive
    additive     → multiplicative (('+' | '-') multiplicative)*
    multiplicative → power (('*' | '/') power)*
    power        → unary ('**' unary)*
    unary        → ('-' unary) | call
    call         → primary ( '(' arguments? ')' )?
    primary      → NUMBER | STRING | IDENTIFIER | list | '(' expression ')'
    list         → '[' (expression (',' expression)*)? ']'
    arguments    → expression (',' expression)* (',' IDENTIFIER '=' expression)*
"""

from __future__ import annotations

from tsil.engine.ast_nodes import (
    ASTNode,
    Assignment,
    BinaryOp,
    FunctionCall,
    Identifier,
    ListLiteral,
    NumberLiteral,
    Program,
    StringLiteral,
    UnaryOp,
)
from tsil.engine.lexer import Token, TokenType, tokenize


class ParseError(Exception):
    """Raised when the parser encounters an unexpected token."""
    def __init__(self, message: str, token: Token | None = None) -> None:
        loc = f" at line {token.line}, col {token.col}" if token else ""
        super().__init__(f"{message}{loc}")
        self.token = token


class Parser:
    """Recursive-descent parser for TSIL."""

    def __init__(self, tokens: list[Token]) -> None:
        self._tokens = tokens
        self._pos = 0

    # -- helpers -------------------------------------------------------------

    def _peek(self) -> Token:
        return self._tokens[self._pos]

    def _advance(self) -> Token:
        tok = self._tokens[self._pos]
        self._pos += 1
        return tok

    def _expect(self, ttype: TokenType, message: str = "") -> Token:
        tok = self._peek()
        if tok.type != ttype:
            msg = message or f"Expected {ttype.name}, got {tok.type.name} ({tok.value!r})"
            raise ParseError(msg, tok)
        return self._advance()

    def _match(self, *types: TokenType) -> Token | None:
        if self._peek().type in types:
            return self._advance()
        return None

    def _skip_newlines(self) -> None:
        while self._peek().type == TokenType.NEWLINE:
            self._advance()

    # -- grammar rules -------------------------------------------------------

    def parse(self) -> Program:
        """Parse the full token stream into a Program AST."""
        self._skip_newlines()
        stmts: list[ASTNode] = []
        while self._peek().type != TokenType.EOF:
            stmts.append(self._statement())
            self._skip_newlines()
        return Program(statements=stmts)

    def _statement(self) -> ASTNode:
        """statement → assignment | expression"""
        # Look ahead for  IDENTIFIER '='
        if (
            self._peek().type == TokenType.IDENTIFIER
            and self._pos + 1 < len(self._tokens)
            and self._tokens[self._pos + 1].type == TokenType.EQUALS
        ):
            return self._assignment()
        return self._expression()

    def _assignment(self) -> Assignment:
        name_tok = self._expect(TokenType.IDENTIFIER)
        self._expect(TokenType.EQUALS)
        value = self._expression()
        return Assignment(name=name_tok.value, value=value)

    def _expression(self) -> ASTNode:
        return self._additive()

    def _additive(self) -> ASTNode:
        left = self._multiplicative()
        while self._peek().type in (TokenType.PLUS, TokenType.MINUS):
            op_tok = self._advance()
            right = self._multiplicative()
            left = BinaryOp(op=op_tok.value, left=left, right=right)
        return left

    def _multiplicative(self) -> ASTNode:
        left = self._power()
        while self._peek().type in (TokenType.STAR, TokenType.SLASH):
            op_tok = self._advance()
            right = self._power()
            left = BinaryOp(op=op_tok.value, left=left, right=right)
        return left

    def _power(self) -> ASTNode:
        base = self._unary()
        if self._peek().type == TokenType.POWER:
            self._advance()
            exp = self._unary()  # right-associative
            return BinaryOp(op="**", left=base, right=exp)
        return base

    def _unary(self) -> ASTNode:
        if self._peek().type == TokenType.MINUS:
            op_tok = self._advance()
            operand = self._unary()
            return UnaryOp(op="-", operand=operand)
        return self._call()

    def _call(self) -> ASTNode:
        node = self._primary()

        # Check for function call: primary '(' args ')'
        if isinstance(node, Identifier) and self._peek().type == TokenType.LPAREN:
            self._advance()  # consume '('
            args, kwargs = self._arguments()
            self._expect(TokenType.RPAREN, "Expected ')' after function arguments")
            return FunctionCall(name=node.name, args=args, kwargs=kwargs)

        return node

    def _arguments(self) -> tuple[list[ASTNode], dict[str, ASTNode]]:
        """Parse comma-separated arguments (positional and keyword)."""
        args: list[ASTNode] = []
        kwargs: dict[str, ASTNode] = {}

        if self._peek().type == TokenType.RPAREN:
            return args, kwargs

        # First argument
        self._parse_argument(args, kwargs)

        while self._peek().type == TokenType.COMMA:
            self._advance()  # consume ','
            if self._peek().type == TokenType.RPAREN:
                break  # trailing comma
            self._parse_argument(args, kwargs)

        return args, kwargs

    def _parse_argument(
        self,
        args: list[ASTNode],
        kwargs: dict[str, ASTNode],
    ) -> None:
        """Parse a single positional or keyword argument."""
        # Check for  identifier '=' expr  (keyword arg)
        if (
            self._peek().type == TokenType.IDENTIFIER
            and self._pos + 1 < len(self._tokens)
            and self._tokens[self._pos + 1].type == TokenType.EQUALS
        ):
            name_tok = self._advance()
            self._advance()  # consume '='
            value = self._expression()
            kwargs[name_tok.value] = value
        else:
            args.append(self._expression())

    def _primary(self) -> ASTNode:
        tok = self._peek()

        if tok.type == TokenType.NUMBER:
            self._advance()
            val = float(tok.value) if "." in tok.value else int(tok.value)
            return NumberLiteral(value=float(val))

        if tok.type == TokenType.STRING:
            self._advance()
            return StringLiteral(value=tok.value)

        if tok.type == TokenType.IDENTIFIER:
            self._advance()
            return Identifier(name=tok.value)

        if tok.type == TokenType.LBRACKET:
            return self._list()

        if tok.type == TokenType.LPAREN:
            self._advance()
            expr = self._expression()
            self._expect(TokenType.RPAREN, "Expected ')' after grouped expression")
            return expr

        raise ParseError(f"Unexpected token: {tok.value!r}", tok)

    def _list(self) -> ListLiteral:
        self._expect(TokenType.LBRACKET)
        elements: list[ASTNode] = []

        if self._peek().type != TokenType.RBRACKET:
            elements.append(self._expression())
            while self._peek().type == TokenType.COMMA:
                self._advance()
                if self._peek().type == TokenType.RBRACKET:
                    break  # trailing comma
                elements.append(self._expression())

        self._expect(TokenType.RBRACKET, "Expected ']' to close list")
        return ListLiteral(elements=elements)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def parse(source: str) -> Program:
    """Parse a TSIL source string into an AST.

    Args:
        source: One or more TSIL statements.

    Returns:
        A Program AST node.

    Raises:
        ParseError: on syntax errors.
    """
    tokens = tokenize(source)
    parser = Parser(tokens)
    return parser.parse()
