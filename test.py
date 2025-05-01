#!/usr/bin/env python3
"""
Debug client for Readium MCP server.
Mantiene la conexión SSE abierta, extrae el session_id del primer evento,
y gestiona toda la comunicación por ese canal.
"""

import asyncio
import json
import re
from typing import Any, Dict, Optional

import httpx

# Define colors for prettier output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"

def parse_sse_events(chunk: str):
    """
    Parse raw SSE chunk into a list of events.
    Each event is a dict with 'event' and 'data'.
    """
    events = []
    for raw_event in chunk.strip().split("\n\n"):
        if not raw_event.strip():
            continue
        event_type = None
        event_data = ""
        for line in raw_event.strip().split("\n"):
            if line.startswith("event:"):
                event_type = line[6:].strip()
            elif line.startswith("data:"):
                event_data += line[5:].strip()
            elif line.startswith(":"):
                # comment/ping, can be ignored or handled if needed
                pass
        if event_type and event_data:
            events.append({"event": event_type, "data": event_data})
    return events

async def sse_listener(url: str, session_id_future: asyncio.Future, result_queue: asyncio.Queue):
    """
    Listen to SSE events, extract session_id, and forward messages to result_queue.
    """
    print(f"{BLUE}Connecting to SSE endpoint: {url}{RESET}")
    async with httpx.AsyncClient(timeout=None) as client:
        try:
            async with client.stream("GET", url, headers={"Accept": "text/event-stream"}) as stream:
                print(f"{GREEN}SSE connection established{RESET}")
                async for chunk in stream.aiter_text():
                    print(f"{YELLOW}Received SSE chunk{RESET}")
                    for event in parse_sse_events(chunk):
                        print(f"{BLUE}Parsed event: {event['event']}{RESET}")
                        if event["event"] == "endpoint":
                            # Extract session_id from URL in data
                            match = re.search(r"session_id=([a-f0-9]+)", event["data"])
                            if match and not session_id_future.done():
                                session_id = match.group(1)
                                print(f"{GREEN}Received session_id: {session_id}{RESET}")
                                session_id_future.set_result(session_id)
                        elif event["event"] == "message":
                            # Forward message to result_queue
                            try:
                                msg = json.loads(event["data"])
                                await result_queue.put(msg)
                            except Exception as e:
                                print(f"{RED}Error parsing message event: {e}{RESET}")
                                print(f"{RED}Raw data: {event['data']}{RESET}")
        except Exception as e:
            print(f"{RED}Error in SSE connection: {e}{RESET}")
            if not session_id_future.done():
                session_id_future.set_exception(e)

async def check_server_health(base_url: str) -> bool:
    """Check if the server is healthy before attempting to connect"""
    health_url = f"{base_url}/health"
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(health_url)
            if resp.status_code == 200:
                data = resp.json()
                print(f"{GREEN}Server is healthy: {data}{RESET}")
                return True
            else:
                print(f"{RED}Server health check failed: {resp.status_code} {resp.text}{RESET}")
                return False
    except Exception as e:
        print(f"{RED}Error checking server health: {e}{RESET}")
        return False

async def main():
    print(f"{BLUE}Starting Readium MCP Debug Client{RESET}")

    base_url = "http://localhost:8000"
    sse_url = f"{base_url}/sse"
    
    # Check server health first
    if not await check_server_health(base_url):
        print(f"{RED}Server is not responding or unhealthy. Exiting.{RESET}")
        return
    
    session_id_future = asyncio.get_event_loop().create_future()
    result_queue = asyncio.Queue()

    # Start SSE listener
    listener_task = asyncio.create_task(sse_listener(sse_url, session_id_future, result_queue))

    try:
        # Wait for session_id from SSE with timeout
        session_id = await asyncio.wait_for(session_id_future, timeout=30)
        print(f"{GREEN}Successfully obtained session_id: {session_id}{RESET}")
    except asyncio.TimeoutError:
        print(f"{RED}Timeout waiting for session_id from SSE{RESET}")
        listener_task.cancel()
        return
    except Exception as e:
        print(f"{RED}Error getting session_id: {e}{RESET}")
        listener_task.cancel()
        return

    # Espera antes de enviar el primer POST
    print(f"{BLUE}Waiting 5 seconds before initializing session...{RESET}")
    await asyncio.sleep(5)

    # Prepare HTTP client for POSTs
    async with httpx.AsyncClient(timeout=60.0) as client:
        # Prepare message endpoint URL with session_id
        message_url = f"{base_url}/messages/?session_id={session_id}"
        print(f"{BLUE}Messages endpoint URL: {message_url}{RESET}")
        
        # 1. Initialize session (with retry logic)
        init_message = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "1.0.0",
                "capabilities": {
                    "tools": {
                        "listChanged": True
                    },
                    "resources": {
                        "subscribe": True,
                        "listChanged": True
                    },
                    "prompts": {
                        "listChanged": True
                    },
                    "logging": {},
                    "completion": {}
                },
                "clientInfo": {
                    "name": "Readium Debug Client",
                    "version": "1.0.0"
                }
            }
        }
        max_attempts = 5
        for attempt in range(1, max_attempts + 1):
            print(f"{BLUE}Initializing MCP session (attempt {attempt}/{max_attempts})...{RESET}")
            resp = await client.post(message_url, json=init_message)
            if resp.status_code == 202:
                print(f"{GREEN}MCP session initialized successfully{RESET}")
                break
            else:
                print(f"{RED}Failed to initialize MCP session (attempt {attempt}): {resp.status_code}{RESET}")
                print(resp.text)
                if attempt < max_attempts:
                    print(f"{YELLOW}Waiting 2 seconds before retry...{RESET}")
                    await asyncio.sleep(2)
                    continue
                listener_task.cancel()
                return

        # 2. List available tools...
        list_tools_message = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        resp = await client.post(
            message_url,
            json=list_tools_message
        )
        if resp.status_code != 202:
            print(f"{RED}Failed to list tools: {resp.status_code}{RESET}")
            print(resp.text)
            listener_task.cancel()
            return
        print(f"{GREEN}Requested list of available tools{RESET}")

        # 3. Wait for tools list and process messages
        tools = []
        tool_found = False
        print(f"{BLUE}Waiting for tools list...{RESET}")
        try:
            while True:
                msg = await asyncio.wait_for(result_queue.get(), timeout=30)
                print(f"{YELLOW}Received message:{RESET}")
                print(json.dumps(msg, indent=2))
                # Check for result of our tools/list call (id == 2)
                if "result" in msg and msg.get("id") == 2:
                    tools = msg["result"]
                    print(f"{GREEN}Available tools:{RESET}")
                    for tool in tools:
                        print(f"  - {tool.get('name', '(unnamed)')}: {tool.get('description', '')}")
                    break
                # Check for error
                if "error" in msg:
                    print(f"{RED}Error received:{RESET}")
                    print(json.dumps(msg["error"], indent=2))
                    listener_task.cancel()
                    return
        except asyncio.TimeoutError:
            print(f"{RED}Timeout waiting for tools list{RESET}")
            listener_task.cancel()
            return

        # 4. Call analyze_docs tool if available
        analyze_tool = next((t for t in tools if t.get("name") == "analyze_docs"), None)
        if analyze_tool:
            tool_message = {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "call_tool",
                "params": {
                    "name": "analyze_docs",
                    "arguments": {
                        "path": "https://github.com/pablotoledo/AlGranoBot.git",
                        "use_markitdown": False
                    }
                }
            }
            resp = await client.post(
                message_url,
                json=tool_message
            )
            if resp.status_code != 202:
                print(f"{RED}Failed to call analyze_docs: {resp.status_code}{RESET}")
                print(resp.text)
                listener_task.cancel()
                return
            print(f"{GREEN}Tool call submitted successfully{RESET}")

            # 5. Wait for results from result_queue
            print(f"{BLUE}Waiting for tool result...{RESET}")
            try:
                while True:
                    msg = await asyncio.wait_for(result_queue.get(), timeout=120)
                    print(f"{YELLOW}Received message:{RESET}")
                    print(json.dumps(msg, indent=2))
                    # Check for result of our tool call (id == 3)
                    if "result" in msg and msg.get("id") == 3:
                        print(f"{GREEN}Tool call completed:{RESET}")
                        result = msg["result"]
                        if isinstance(result, dict) and "content" in result:
                            for item in result["content"]:
                                print(f"\n{BLUE}--- {item.get('type', 'text')} ---{RESET}")
                                text = item.get('text', '')
                                print(text[:500] + "..." if len(text) > 500 else text)
                        break
                    # Check for error
                    if "error" in msg:
                        print(f"{RED}Error received:{RESET}")
                        print(json.dumps(msg["error"], indent=2))
                        break
            except asyncio.TimeoutError:
                print(f"{RED}Timeout waiting for tool result{RESET}")
        else:
            print(f"{YELLOW}analyze_docs tool not found on server. No tool call made.{RESET}")

    listener_task.cancel()
    print(f"{BLUE}Debug client finished{RESET}")

if __name__ == "__main__":
    asyncio.run(main())
