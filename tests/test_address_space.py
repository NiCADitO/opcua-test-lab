import pytest
import pytest_asyncio
from asyncua import Client, Server, ua
from src import server_methods

EXPECTED_NODES_AND_TYPES = {
    "MyVariable": "Int64",
    "MyWritableVariable": "Int64",
    "myarrayvar": "Double",
    "myStronglyTypedVariable": "UInt32",
    "MR. property": "String",
    "add": None,
    "subtract": None,
    "multiply": None,
    "divide": None,
    "is_even": None,
    "multiply_async": None,
    "is_even_async": None,
}


@pytest_asyncio.fixture(scope="module")
async def run_server():
    server = Server()
    await server.init()
    server.set_endpoint("opc.tcp://127.0.0.1:0/freeopcua/server/")
    await server_methods.build_address_space(server)
    async with server:
        yield server


@pytest_asyncio.fixture(scope="module")
async def client(run_server):
    url = f"opc.tcp://127.0.0.1:{run_server.bserver.port}/freeopcua/server/"
    async with Client(url) as client:
        yield client


@pytest_asyncio.fixture(scope="module")
async def my_object(client):
    idx = await client.get_namespace_index(server_methods.NAMESPACE_URI)
    return await client.nodes.objects.get_child(f"{idx}:MyObject"), idx


async def test_object_node_id():
    server = server_methods.Server()
    await server.init()
    idx, _ = await server_methods.build_address_space(server)
    obj = await server.nodes.objects.get_child(f"{idx}:MyObject")
    assert obj.nodeid.NamespaceIndex == idx


async def test_out_arg_type():
    server = server_methods.Server()
    await server.init()
    idx, _ = await server_methods.build_address_space(server)
    obj = await server.nodes.objects.get_child([f"{idx}:MyObject"])
    method = await obj.get_child([f"{idx}:divide"])
    out = await method.get_child(["0:OutputArguments"])
    declared = await out.read_value()

    assert declared[0].DataType == ua.NodeId(ua.ObjectIds.Double)


async def test_exposed_object_types():
    server = server_methods.Server()
    await server.init()
    idx, _ = await server_methods.build_address_space(server)
    obj = await server.nodes.objects.get_child(f"{idx}:MyObject")

    results = {}
    for n in await obj.get_children():
        name = (await n.read_browse_name()).Name
        if (await n.read_node_class()) == ua.NodeClass.Variable:
            results[name] = (await n.read_data_type_as_variant_type()).name
        else:
            results[name] = None

    assert results == EXPECTED_NODES_AND_TYPES


# Uses prebuilt server, client, objects for tests
async def test_writable_variable_takes_values(my_object):
    obj, idx = my_object
    var = await obj.get_child(f"{idx}:MyWritableVariable")
    await var.write_value(121)
    assert await var.read_value() == 121


async def test_read_only_variable_rejects_writes(my_object):
    obj, idx = my_object
    var = await obj.get_child(f"{idx}:MyVariable")
    with pytest.raises(ua.UaStatusCodeError):
        await var.write_value(55)
