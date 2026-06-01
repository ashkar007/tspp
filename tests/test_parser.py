import pytest
from tsil.engine.lexer import tokenize, TokenType, LexerError
from tsil.engine.parser import parse, ParseError
from tsil.engine.ast_nodes import (
    Program,
    Assignment,
    BinaryOp,
    UnaryOp,
    FunctionCall,
    Identifier,
    NumberLiteral,
    StringLiteral,
    ListLiteral,
)

def test_lexer():
    tokens = tokenize('x = IV(t("SPX"), 3.14, WGT_EQ) # comment')
    # Filter EOF out for simple assertion
    filtered = [t for t in tokens if t.type != TokenType.EOF]
    
    assert len(filtered) == 13
    assert filtered[0].type == TokenType.IDENTIFIER and filtered[0].value == "x"
    assert filtered[1].type == TokenType.EQUALS and filtered[1].value == "="
    assert filtered[2].type == TokenType.IDENTIFIER and filtered[2].value == "IV"
    assert filtered[3].type == TokenType.LPAREN
    assert filtered[4].type == TokenType.IDENTIFIER and filtered[4].value == "t"
    assert filtered[5].type == TokenType.LPAREN
    assert filtered[6].type == TokenType.STRING and filtered[6].value == "SPX"
    assert filtered[7].type == TokenType.RPAREN
    assert filtered[8].type == TokenType.COMMA
    assert filtered[9].type == TokenType.NUMBER and filtered[9].value == "3.14"
    assert filtered[10].type == TokenType.COMMA
    assert filtered[11].type == TokenType.IDENTIFIER and filtered[11].value == "WGT_EQ"
    assert filtered[12].type == TokenType.RPAREN
    
def test_lexer_full():
    tokens = tokenize('x = 100 + y')
    filtered = [t for t in tokens if t.type != TokenType.EOF]
    assert len(filtered) == 5
    assert filtered[0].type == TokenType.IDENTIFIER and filtered[0].value == "x"
    assert filtered[1].type == TokenType.EQUALS
    assert filtered[2].type == TokenType.NUMBER and filtered[2].value == "100"
    assert filtered[3].type == TokenType.PLUS
    assert filtered[4].type == TokenType.IDENTIFIER and filtered[4].value == "y"

def test_lexer_error():
    with pytest.raises(LexerError):
        tokenize("x = @123")

def test_parser_literals():
    prog = parse('123.45')
    assert isinstance(prog, Program)
    assert len(prog.statements) == 1
    stmt = prog.statements[0]
    assert isinstance(stmt, NumberLiteral)
    assert stmt.value == 123.45

    prog2 = parse('"hello"')
    assert isinstance(prog2.statements[0], StringLiteral)
    assert prog2.statements[0].value == "hello"

def test_parser_list():
    prog = parse('["SPX", "SX5E"]')
    stmt = prog.statements[0]
    assert isinstance(stmt, ListLiteral)
    assert len(stmt.elements) == 2
    assert isinstance(stmt.elements[0], StringLiteral)
    assert stmt.elements[0].value == "SPX"

def test_parser_binary_unary():
    prog = parse('-x ** 2 + y * 3')
    stmt = prog.statements[0]
    # operator precedence:
    # + is lowest, so top is BinaryOp(+)
    # Left side: -x ** 2
    # Right side: y * 3
    assert isinstance(stmt, BinaryOp)
    assert stmt.op == "+"
    
    # Left side: (-x) ** 2 because of unary being nested inside power base in this grammar
    left = stmt.left
    assert isinstance(left, BinaryOp)
    assert left.op == "**"
    assert isinstance(left.left, UnaryOp)
    assert left.left.op == "-"
    assert isinstance(left.left.operand, Identifier)
    assert left.left.operand.name == "x"
    assert isinstance(left.right, NumberLiteral)
    assert left.right.value == 2.0

    right = stmt.right
    assert isinstance(right, BinaryOp)
    assert right.op == "*"
    assert isinstance(right.left, Identifier)
    assert right.left.name == "y"
    assert isinstance(right.right, NumberLiteral)
    assert right.right.value == 3.0

def test_parser_function_call():
    prog = parse('IV(t("SPX"), e("3M"), strike=k("100%"))')
    stmt = prog.statements[0]
    assert isinstance(stmt, FunctionCall)
    assert stmt.name == "IV"
    assert len(stmt.args) == 2
    assert len(stmt.kwargs) == 1
    
    assert isinstance(stmt.args[0], FunctionCall)
    assert stmt.args[0].name == "t"
    
    assert "strike" in stmt.kwargs
    assert isinstance(stmt.kwargs["strike"], FunctionCall)
    assert stmt.kwargs["strike"].name == "k"

def test_parser_assignment():
    prog = parse('vol = 0.20')
    stmt = prog.statements[0]
    assert isinstance(stmt, Assignment)
    assert stmt.name == "vol"
    assert isinstance(stmt.value, NumberLiteral)
    assert stmt.value.value == 0.20

def test_parser_errors():
    with pytest.raises(ParseError):
        parse('IV(t("SPX")') # Missing closing parens or syntax error
    with pytest.raises(ParseError):
        parse("[1, 2") # Missing closing bracket
