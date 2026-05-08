
import asyncio
import sys
import uvicorn
import os

async def main():
    config = uvicorn.Config("app.server.asgi:create_app", factory=True, port=8000, host="0.0.0.0", loop="asyncio")
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    # Ensure UTF-8 for Windows console
    os.environ["PYTHONUTF8"] = "1"
    os.environ["LITESTAR_DEBUG"] = "true"
    
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    # Add current dir to path to ensure 'app' is findable
    cwd = os.getcwd()
    if cwd not in sys.path:
        sys.path.append(cwd)
        
    print("Starting Litestar server with MANUAL SelectorEventLoop...")
    
    # Log to a file manually
    with open("server_debug.log", "w", encoding="utf-8") as f:
        sys.stdout = f
        sys.stderr = f
        try:
            asyncio.run(main())
        except KeyboardInterrupt:
            pass
