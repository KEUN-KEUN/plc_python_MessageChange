import asyncio
import time
from datetime import datetime, timezone
from asyncua import Client, ua

OPC_UA_ENDPOINT = "opc.tcp://keun90:48010"

# 서버 NamespaceArray에서 확인된 URI (당신 환경 기준)
TARGET_NAMESPACE_URI = "urn:UnifiedAutomation:CppDemoServer:UANodeSetXmlImport"

# 업데이트 대상 설비 경로
BASE = "Factory.LINE1.EQP1"

# 주기
INTERVAL_SEC = 1


async def get_ns_index(client: Client, namespace_uri: str) -> int:
    """서버 NamespaceArray(i=2255)에서 namespace_uri의 index(ns)를 찾는다."""
    ns_array = await client.get_node(
        ua.NodeId(ua.ObjectIds.Server_NamespaceArray)
    ).read_value()
    return ns_array.index(namespace_uri)


def node_id_str(ns: int, s: str) -> str:
    """ns=<runtimeIndex>;s=<identifier> 형태로 NodeId 문자열 생성"""
    return f"ns={ns};s={s}"


async def main():
    async with Client(OPC_UA_ENDPOINT) as client:
        ns = await get_ns_index(client, TARGET_NAMESPACE_URI)

        # 태그 노드 핸들 (한 번만 만들어 재사용)
        n_status = client.get_node(node_id_str(ns, f"{BASE}.Status"))
        n_temp   = client.get_node(node_id_str(ns, f"{BASE}.Temperature"))
        n_ts     = client.get_node(node_id_str(ns, f"{BASE}.LastUpdate"))
        n_seq    = client.get_node(node_id_str(ns, f"{BASE}.Seq"))
        n_raw    = client.get_node(node_id_str(ns, f"{BASE}.RawMessage"))

        seq = 0
        while True:
            seq += 1

            # ---- 값 생성 (의미 없는 로직 없이 최소) ----
            status = seq % 3  # 0,1,2 반복 (STOP/RUN/ALARM 같은 상태코드라고 가정)
            temp = 36.0 + (seq % 10) * 0.1  # 36.0 ~ 36.9
            ts = datetime.now(timezone.utc)

            raw = (
                f"LINE1|EQP1|status={status}|temp={temp:.2f}|"
                f"seq={seq}|ts={int(time.time())}"
            )

            # ---- 모든 태그 업데이트 ----
            # 모든 태그 업데이트 (Value only write)
            await n_status.write_attribute(
                ua.AttributeIds.Value,
                ua.DataValue(ua.Variant(status, ua.VariantType.UInt16))
            )
            await n_temp.write_attribute(
                ua.AttributeIds.Value,
                ua.DataValue(ua.Variant(temp, ua.VariantType.Double))
            )
            await n_ts.write_attribute(
                ua.AttributeIds.Value,
                ua.DataValue(ua.Variant(ts, ua.VariantType.DateTime))
            )
            await n_seq.write_attribute(
                ua.AttributeIds.Value,
                ua.DataValue(ua.Variant(seq, ua.VariantType.UInt32))
            )
            await n_raw.write_attribute(
                ua.AttributeIds.Value,
                ua.DataValue(ua.Variant(raw, ua.VariantType.String))
            )

            print("UPDATED", BASE, "seq", seq, "status", status, "temp", temp)
            await asyncio.sleep(INTERVAL_SEC)


if __name__ == "__main__":
    asyncio.run(main())
