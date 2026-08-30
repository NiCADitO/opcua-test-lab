import asyncio
import logging
import random
from asyncua import ua, uamethod, Server

ENDPOINT = "opc.tcp://0.0.0.0:4840/freeopcua/server/"
NAMESPACE_URI = "http://examples.freeopcua.github.io"
SERVER_NAME = "FreeOpcUa Example Server"


# helper functions
def divide_numbers(x, y):
    if y == 0:
        raise ValueError("cannot divide by zero")
    else:
        return x / y


# async methods to be exposed through server
@uamethod
async def is_even_async(parent, x):
    result = x % 2 == 0
    if result:
        await asyncio.sleep(1)
    return result

@uamethod
async def multiply_async(parent, x, y):
    sleep_time = x * y
    print(f"Sleeping asynchronously for {x * y} seconds")
    await asyncio.sleep(sleep_time)
    return x * y


    
# methods to be exposed through server
# uses a decorator @uamethod to automatically convert to and from variants
@uamethod
def add(parent, x, y):
    print("Add method call with parameters: ", x, y)
    return x + y

@uamethod
def subtract(parent, x, y):
    print("Subtract method call with parameters: ", x, y)
    return x - y

@uamethod
def multiply(parent, x, y):
    print("multiply method call with parameters: ", x, y)
    return x * y

@uamethod
def divide(parent, x, y):
    print("Divide method call with parameters: ", x, y)
    return divide_numbers(x, y)

@uamethod
def is_even(parent, x):
    print("func method call with parameters: ", x)
    ret = False
    if x % 2 == 0:
        ret = True
    return ret



def _argument(name, data_type, description):
    """Build a named ua.Argument so clients show useful parameter names."""
    arg = ua.Argument()
    arg.Name = name
    arg.DataType = ua.NodeId(data_type)
    arg.ValueRank = -1
    arg.ArrayDimensions = []
    arg.Description = ua.LocalizedText(description)
    return arg

async def build_address_space(server):
    """Populate the server's address space.

    Kept separate from main() so tests can build a configured server

    Returns (namespace_index, my_variable_node).
    """
    idx = await server.register_namespace(NAMESPACE_URI)
    objects = server.nodes.objects

    await objects.add_folder(idx, "myEmptyFolder")
    obj = await objects.add_object(idx, "MyObject")

    my_variable = await obj.add_variable(idx, "MyVariable", 0)
    await my_variable.set_writable()
    await obj.add_variable(idx, "myarrayvar", [6.7, 8.9])
    await obj.add_variable(idx, "myStronglytTypedVariable", ua.Variant([], ua.VariantType.UInt32))
    await obj.add_property(idx, "MR. property", "I am MR. property!!!")

    arg_x = _argument("x", ua.ObjectIds.Int64, "First number x")
    arg_y = _argument("y", ua.ObjectIds.Int64, "Second number y")
    int_result = _argument("Result", ua.ObjectIds.Int64, "Integer result")
    # divide returns a float, so its output must be declared Double, not Int64.
    float_result = _argument("Result", ua.ObjectIds.Double, "Division result")

    await obj.add_method(idx, "add", add, [arg_x, arg_y], [int_result])
    await obj.add_method(idx, "subtract", subtract, [arg_x, arg_y], [int_result])
    await obj.add_method(idx, "multiply", multiply, [arg_x, arg_y], [int_result])
    await obj.add_method(idx, "divide", divide, [arg_x, arg_y], [float_result])
    await obj.add_method(idx, "is_even", is_even, [ua.VariantType.Int64], [ua.VariantType.Boolean])
    await obj.add_method(idx, "multiply_async", multiply_async, [arg_x, arg_y], [int_result])
    await obj.add_method(idx, "is_even_async", is_even_async, [ua.VariantType.Int64], [ua.VariantType.Boolean])

    return idx, my_variable

async def main():
    logging.basicConfig(level=logging.WARNING)

    server = Server()
    await server.init()
    server.set_endpoint(ENDPOINT)
    server.set_server_name(SERVER_NAME)

    _, my_variable = await build_address_space(server)

    async with server:
        while True:
            await asyncio.sleep(1)
            await my_variable.write_value(random.randint(0, 100))


if __name__ == "__main__":
    asyncio.run(main())
