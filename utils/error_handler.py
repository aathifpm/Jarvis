import logging

logging.basicConfig(filename='jarvis.log', level=logging.INFO)

def handle_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.error(f"Error in {func.__name__}: {str(e)}")
            return f"I'm sorry, I encountered an error while processing your request: {str(e)}"
    return wrapper

# Usage example
@handle_error
def some_function():
    # function implementation
    pass
