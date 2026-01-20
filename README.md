# OPC-UA Local Test Environment                                                                                           
  로컬 PC에서 OPC-UA 통신을 테스트하기 위한 Python 기반 테스트 환경                                                       
  
  ## 프로젝트 목적

  실제 PLC 없이 로컬 환경에서 OPC-UA 서버와의 통신을 테스트하고 검증

  ## 주요 구성요소

  ### 1. PLC Simulator (`plc_simulator.py`)
  - OPC-UA 서버에 주기적으로 데이터 Write
  - 1초 간격으로 설비 데이터 업데이트 (상태, 온도, 시퀀스, 타임스탬프)
  - 실제 PLC 동작 시뮬레이션

  ### 2. Stress Test (`stressTest.py`)
  - 서버 부하 테스트 (20 writes/sec)
  - TPS(Transactions Per Second) 측정
  - 에러율 및 성능 모니터링

  ### 3. Subscription Test (`subscriber_stress.py`)
  - OPC-UA 서버 데이터 변경 구독
  - 알림 속도 및 데이터 품질 검증
  - 시퀀스 역전/중복 체크

  ### 4. Utility (`check_namespaces.py`)
  - OPC-UA 서버의 네임스페이스 확인 도구

  ## 테스트 대상

  - **Endpoint**: `opc.tcp://keun90:48010`
  - **Target Node**: `Factory.LINE1.EQP1`
  - **모니터링 태그**:
    - Status (UInt16)
    - Temperature (Double)
    - Seq (UInt32)
    - RawMessage (String)
    - LastUpdate (DateTime)

  ## 환경 설정

  ```bash
  # 가상환경 생성 및 활성화
  python -m venv .venv
  .venv\Scripts\activate  # Windows

  # 의존성 설치
  pip install asyncua

  실행 방법

  # 1. 네임스페이스 확인
  python check_namespaces.py

  # 2. PLC 시뮬레이터 실행
  python plc_simulator.py

  # 3. 부하 테스트 실행
  python stressTest.py

  # 4. 구독 테스트 실행 (별도 터미널)
  python subscriber_stress.py --pub_ms 250 --report_sec 10

  주요 의존성

  - asyncua: OPC-UA 클라이언트 라이브러리
