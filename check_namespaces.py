import asyncio
from asyncua import Client, ua

async def check_namespaces():
    async with Client("opc.tcp://keun90:48010") as client:
        ns_array = await client.get_node(
            ua.NodeId(ua.ObjectIds.Server_NamespaceArray)
        ).read_value()

        for i, uri in enumerate(ns_array):
            print(i, uri)

if __name__ == "__main__":
    asyncio.run(check_namespaces())
