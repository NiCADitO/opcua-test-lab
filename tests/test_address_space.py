from asyncua import ua
from src import server_methods

EXPECTED_NODES_AND_TYPES = {
    "MyVariable": "Int64",
    "MyWritableVariable": "Int64",
    "myarrayvar": "Double",
    "myStronglytTypedVariable": "UInt32",
    "MR. property": "String",
    "add": None,
    "subtract": None,
    "multiply": None,
    "divide": None,
    "is_even": None,
    "multiply_async": None,
    "is_even_async": None,
}

#TODO Read a method's OutputArguments and assert the declared DataType matches what it really returns. This catches your divide bug — declared Int64, returns a float 
# def test_method_type():

#TODO check object returns expected node id
async def test_object_node_id():
    server = server_methods.Server()
    await server.init()
    idx, _ = await server_methods.build_address_space(server)
    obj = await server.nodes.objects.get_child(f"{idx}:MyObject")
    assert obj.nodeid.NamespaceIndex == 2

# Check object method divide output argument returns the expected type
async def test_out_arg_type():
    server = server_methods.Server()
    await server.init()
    idx, _ = await server_methods.build_address_space(server)
    obj = await server.nodes.objects.get_child([f"{idx}:MyObject"])
    method = await obj.get_child([f"{idx}:divide"])
    out = await method.get_child(["0:OutputArguments"])
    declared = await out.read_value()

    assert declared[0].DataType == ua.NodeId(ua.ObjectIds.Double)

#TODO Check MyObject exposes exactly the expected nodes and data types
async def test_exposed_object_nodes():
    server = server_methods.Server()
    await server.init()
    idx, _ = await server_methods.build_address_space(server)
    obj =  await server.nodes.objects.get_child(f"{idx}:MyObject")

    results = {}
    for n in await obj.get_children():
        name = (await n.read_browse_name()).Name
        if (await n.read_node_class()) == ua.NodeClass.Variable:
            results[name] = (await n.read_data_type_as_variant_type()).name
        else:
            results[name] = None

    # print("Results = " + str(results))

    assert results == EXPECTED_NODES_AND_TYPES

    

#TODO Subscribe to MyVariable, assert you receive expected number of updates inside a timeout

#TODO Check for wrong argument count. Writing to a read-only node

#TODO Write to MyVariable, read it back, confirm set_writable() works