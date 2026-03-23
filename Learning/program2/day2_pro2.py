import asyncio

def greet(name: str):
	print(f"Starting greeting for {name}")

def main():
	coroutine_obj = greet("Bhaskar")
	print ("\n coroutine_obj >>>> ",coroutine_obj)
	# await coroutine_obj

asyncio.run(main())