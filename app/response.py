from typing import Any, Dict

def ok(data: Any = None, message: str = "success") -> Dict[str, Any]:
    return {"code": 200, "message": message, "data": data}

def err(code: int, message: str) -> Dict[str, Any]:
    return {"code": code, "message": message}
