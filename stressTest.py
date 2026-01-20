import asyncio
import time
from asyncua import Client, ua

# ====== 환경 설정 ======
ENDPOINT = "opc.tcp://keun90:48010"

# 반드시 UAExpert에서 NodeId 확인 후 그대로 입력 (예시는 형식만)
NODE_STATUS = "ns=7;s=Factory.LINE1.EQP1.Status"
NODE_TEMP   = "ns=7;s=Factory.LINE1.EQP1.Temperature"
NODE_SEQ    = "ns=7;s=Factory.LINE1.EQP1.Seq"
NODE_RAW    = "ns=7;s=Factory.LINE1.EQP1.RawMessage"
# DateTime은 서버 구현체에 따라 Write 제약이 있을 수 있어(호환성 이슈),
# 스트레스 테스트 1차에서는 제외하고, 2차에서만 추가 권장.
# NODE_LAST  = "ns=7;s=Factory.LINE1.EQP1.LastUpdate"

# 부하 파라미터 (필요 최소)
WRITE_INTERVAL_SEC = 0.02   # 20 writes/sec (프로세스 1개 기준)
REPORT_INTERVAL_SEC = 10    # 10초마다 리포트


async def stress_writer():
    async with Client(ENDPOINT) as client:
        n_status = client.get_node(NODE_STATUS)
        n_temp   = client.get_node(NODE_TEMP)
        n_seq    = client.get_node(NODE_SEQ)
        n_raw    = client.get_node(NODE_RAW)

        ok = 0
        fail = 0
        seq = 0
        t0 = time.time()
        last_report = t0

        while True:
            seq += 1
            try:
                # "부하 목적"이므로: 한 사이클에 여러 태그를 갱신(현장 PLC 패턴)
                await n_status.write_attribute(
                    ua.AttributeIds.Value,
                    ua.DataValue(ua.Variant(seq % 5, ua.VariantType.UInt16))
                )
                await n_temp.write_attribute(
                    ua.AttributeIds.Value,
                    ua.DataValue(ua.Variant(20.0 + (seq % 100) * 0.1, ua.VariantType.Double))
                )
                await n_seq.write_attribute(
                    ua.AttributeIds.Value,
                    ua.DataValue(ua.Variant(seq, ua.VariantType.UInt32))
                )
                await n_raw.write_attribute(
                    ua.AttributeIds.Value,
                    ua.DataValue(ua.Variant(f"RAW_{seq}", ua.VariantType.String))
                )
                ok += 4  # 태그 4개 write 성공으로 카운트
            except Exception:
                fail += 1

            now = time.time()
            if now - last_report >= REPORT_INTERVAL_SEC:
                elapsed = now - last_report
                tps = ok / elapsed
                total = ok + fail
                err_rate = (fail / total) * 100 if total else 0.0
                print(f"[{int(now-t0)}s] TPS={tps:.1f} writes/s, ok={ok}, fail={fail}, err={err_rate:.2f}%")

                # 리포트 주기마다 카운터 리셋 (구간 TPS 측정)
                ok = 0
                fail = 0
                last_report = now

            await asyncio.sleep(WRITE_INTERVAL_SEC)


if __name__ == "__main__":
    asyncio.run(stress_writer())
