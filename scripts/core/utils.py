import time
import functools
import logging

# Configure basic logging for retry attempts
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def retry_on_exception(retries: int, delay_seconds: float, exceptions_to_catch: tuple):
    """
    A decorator to retry a function call if specific exceptions are caught.

    Args:
        retries (int): The maximum number of retry attempts.
        delay_seconds (float): The delay in seconds between retries.
        exceptions_to_catch (tuple): A tuple of exception classes to catch and retry on.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0
            while attempts <= retries:
                try:
                    return func(*args, **kwargs)
                except exceptions_to_catch as e:
                    attempts += 1
                    if attempts > retries:
                        logger.error(
                            f"Function '{func.__name__}' failed after {retries + 1} attempts. "
                            f"Last exception: {type(e).__name__}: {e}"
                        )
                        raise  # Re-raise the last exception
                    
                    logger.warning(
                        f"Attempt {attempts}/{retries + 1} for function '{func.__name__}' failed. "
                        f"Exception: {type(e).__name__}: {e}. Retrying in {delay_seconds}s..."
                    )
                    time.sleep(delay_seconds)
        return wrapper
    return decorator

if __name__ == '__main__':
    # Example usage (optional, for testing the decorator directly)
    class TransientError(Exception):
        pass

    class FatalError(Exception):
        pass

    fail_count = 0

    @retry_on_exception(retries=3, delay_seconds=0.1, exceptions_to_catch=(TransientError,))
    def potentially_flaky_operation(succeed_after_n_failures):
        global fail_count
        logger.info(f"Executing potentially_flaky_operation (current fail_count: {fail_count}, target: {succeed_after_n_failures})")
        if fail_count < succeed_after_n_failures:
            fail_count += 1
            raise TransientError(f"Simulated transient failure #{fail_count}")
        logger.info("Potentially_flaky_operation succeeded.")
        return "Success!"

    @retry_on_exception(retries=2, delay_seconds=0.1, exceptions_to_catch=(TransientError,))
    def always_fatal_operation():
        logger.info("Executing always_fatal_operation")
        raise FatalError("This is a fatal error, retries won't help.")

    @retry_on_exception(retries=2, delay_seconds=0.1, exceptions_to_catch=(TransientError,))
    def always_transient_fail_operation():
        logger.info("Executing always_transient_fail_operation")
        raise TransientError("This transient error will always occur.")

    print("\n--- Testing successful retry ---")
    fail_count = 0 # Reset for this test
    try:
        result = potentially_flaky_operation(succeed_after_n_failures=2)
        print(f"Result: {result}")
    except Exception as e:
        print(f"Caught exception after retries: {type(e).__name__}: {e}")
    
    print("\n--- Testing retry with non-caught fatal error ---")
    try:
        always_fatal_operation()
    except FatalError as e: # Expecting this to be caught outside
        print(f"Caught expected FatalError: {e}")
    except Exception as e:
        print(f"Caught unexpected exception: {type(e).__name__}: {e}")

    print("\n--- Testing retry exhaustion ---")
    try:
        always_transient_fail_operation()
    except TransientError as e: # Expecting this to be caught outside after retries
        print(f"Caught expected TransientError after retries: {e}")
    except Exception as e:
        print(f"Caught unexpected exception: {type(e).__name__}: {e}")
