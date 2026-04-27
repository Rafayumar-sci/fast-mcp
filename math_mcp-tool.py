from fastmcp import FastMCP

mcp = FastMCP("my math MCP server")


@mcp.tool()
def add(a: int, b: int) -> int:
    """"return sum"""
    print(f"Adding {a} and {b}")
    return a+b


@mcp.tool()
def greet(name: str) -> str:
    """return greeting message"""
    return f"Hello, {name}!"


@mcp.tool()
def send_email(to: str, subject: str, body: str) -> str:
    """send an email and return status"""
    # Here you would implement the actual email sending logic
    print(f"Sending email to {to} with subject '{subject}' and body '{body}'")
    return f"Email sent to {to} with subject '{subject}'"


if __name__ == "__main__":
    mcp.run(transport="http", port=8000)
