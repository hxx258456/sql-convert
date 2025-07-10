from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlglot import parse, transpile
from sqlglot.dialects import MySQL, Oracle
import uvicorn
from typing import Optional, List, Dict, Any
import json

app = FastAPI(
    title="SQL Converter",
    description="Convert MySQL SQL to Oracle SQL using sqlglot",
    version="1.0.0"
)

class SQLConvertRequest(BaseModel):
    mysql_sql: str
    pretty: Optional[bool] = True

class SQLConvertResponse(BaseModel):
    mysql_sql: str
    oracle_sql: str
    success: bool
    error_message: Optional[str] = None

class SQLParseRequest(BaseModel):
    mysql_sql: str

class SQLParseResponse(BaseModel):
    mysql_sql: str
    parsed_structure: Dict[str, Any]
    success: bool
    error_message: Optional[str] = None

@app.get("/")
async def root():
    return {
        "message": "SQL Converter API",
        "description": "Convert MySQL SQL to Oracle SQL",
        "endpoints": {
            "/convert": "POST - Convert MySQL SQL to Oracle SQL",
            "/parse": "POST - Parse MySQL SQL and return structure",
            "/convert/batch": "POST - Convert multiple MySQL SQL statements",
            "/parse/batch": "POST - Parse multiple MySQL SQL statements",
            "/health": "GET - Health check"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "sql-converter"}

@app.post("/convert", response_model=SQLConvertResponse)
async def convert_sql(request: SQLConvertRequest):
    """
    Convert MySQL SQL to Oracle SQL
    
    Args:
        request: SQLConvertRequest containing MySQL SQL and formatting options
        
    Returns:
        SQLConvertResponse with converted Oracle SQL or error message
    """
    try:
        # Parse MySQL SQL
        parsed = parse(request.mysql_sql, dialect=MySQL)
        
        # Transpile to Oracle
        oracle_sql = transpile(
            parsed, 
            dialect=Oracle, 
            pretty=request.pretty
        )
        
        # Join multiple statements if any
        if isinstance(oracle_sql, list):
            oracle_sql = ";\n".join(oracle_sql)
        
        return SQLConvertResponse(
            mysql_sql=request.mysql_sql,
            oracle_sql=oracle_sql,
            success=True
        )
        
    except Exception as e:
        return SQLConvertResponse(
            mysql_sql=request.mysql_sql,
            oracle_sql="",
            success=False,
            error_message=str(e)
        )

@app.post("/parse", response_model=SQLParseResponse)
async def parse_sql(request: SQLParseRequest):
    """
    Parse MySQL SQL and return the parsed structure
    
    Args:
        request: SQLParseRequest containing MySQL SQL
        
    Returns:
        SQLParseResponse with parsed structure or error message
    """
    print(f"{request=}")
    try:
        # Parse MySQL SQL
        parsed = parse(request.mysql_sql, dialect=MySQL)
        
        
        # Convert parsed structure to dictionary
        def node_to_dict(node):
            if node is None:
                return None
            
            # Get basic node info
            node_info = {
                "type": node.__class__.__name__,
                "sql": str(node)
            }
            
            # Add specific attributes based on node type
            if hasattr(node, 'key') and hasattr(node, 'value'):
                node_info["key"] = str(node.key)
                node_info["value"] = node_to_dict(node.value)
            elif hasattr(node, 'args') and node.args:
                node_info["args"] = [node_to_dict(arg) for arg in node.args]
            elif hasattr(node, 'expression') and node.expression:
                node_info["expression"] = node_to_dict(node.expression)
            
            # Add common attributes
            if hasattr(node, 'alias') and node.alias:
                node_info["alias"] = str(node.alias)
            if hasattr(node, 'name') and node.name:
                node_info["name"] = str(node.name)
            if hasattr(node, 'table') and node.table:
                node_info["table"] = str(node.table)
            if hasattr(node, 'column') and node.column:
                node_info["column"] = str(node.column)
            
            return node_info
        
        # Handle multiple statements
        if isinstance(parsed, list):
            parsed_structure = {
                "statements": [node_to_dict(stmt) for stmt in parsed],
                "statement_count": len(parsed)
            }
        else:
            parsed_structure = {
                "statement": node_to_dict(parsed),
                "statement_count": 1
            }
        
        return SQLParseResponse(
            mysql_sql=request.mysql_sql,
            parsed_structure=parsed_structure,
            success=True
        )
        
    except Exception as e:
        return SQLParseResponse(
            mysql_sql=request.mysql_sql,
            parsed_structure={},
            success=False,
            error_message=str(e)
        )

@app.post("/convert/batch")
async def convert_sql_batch(requests: list[SQLConvertRequest]):
    """
    Convert multiple MySQL SQL statements to Oracle SQL
    
    Args:
        requests: List of SQLConvertRequest objects
        
    Returns:
        List of SQLConvertResponse objects
    """
    results = []
    for request in requests:
        result = await convert_sql(request)
        results.append(result)
    
    return results

@app.post("/parse/batch")
async def parse_sql_batch(requests: list[SQLParseRequest]):
    """
    Parse multiple MySQL SQL statements and return parsed structures
    
    Args:
        requests: List of SQLParseRequest objects
        
    Returns:
        List of SQLParseResponse objects
    """
    results = []
    for request in requests:
        result = await parse_sql(request)
        results.append(result)
    
    return results

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

