파마브로스 제품 개발 & 발주 관리 대시보드(AI) 일일 갱신 작업입니다.
매 실행은 새 세션에서 시작합니다. 세션 작업폴더에 이전 파일이 남아있다고 절대 가정하지 마세요 —
필요한 모든 것은 GitHub 저장소 안에 있습니다.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
■ 1단계 — 저장소 clone
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    cd /tmp && rm -rf ai-dashboard && git clone https://github.com/daisy3015/AI.git ai-dashboard && cd /tmp/ai-dashboard

`build/` 폴더가 없으면 여기서 중단하고 그 사실을 보고한 뒤 종료하세요.
clone 직후 `git rev-parse HEAD` 를 기록해 두세요 (7단계 보고에 씁니다).

시작 전 `build/README.md` 를 반드시 읽으세요. 아래 절차보다 README 가 최신입니다.
둘이 다르면 README 를 따르고, 차이가 있었다는 점을 보고에 적으세요.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
■ 2단계 — 노션 (읽기 전용)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Notion MCP 의 query-data-sources 로 실행:

    SELECT "url", "이름", "Status 1", "Status 2", "브랜드", "제조사", "유형", "담당자",
           "date:입고 목표일:start",
           "date:다음 확인 예정일:start",
           "createdTime", "최근 편집일"
    FROM "collection://b128c405-e301-82e9-aa21-87a5593d8393"

results 배열을 그대로 `/tmp/ai-dashboard/build/notion.json` 에 저장하세요.

⚠️ 컬럼명은 위처럼 전부 큰따옴표로 감싸고, `AS` 별칭을 붙이지 마세요.
· 따옴표가 없으면 쿼리가 파싱 실패합니다 (`could not be parsed safely`).
· `build.py` 는 원본 컬럼명(`date:입고 목표일:start`, `최근 편집일` 등)을 그대로 읽습니다.
  별칭을 붙여 저장하면 입고 목표일·다음 확인 예정일·최근 편집일이 경고 없이 전부 빈칸이 됩니다.
· 저장 후 `notion.json` 첫 항목에 `date:입고 목표일:start` 키가 있는지 한 번 확인하세요.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
■ 3단계 — 구글시트 (읽기 전용)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
`build/config.json` 의 시트 주소에서 CSV 를 받아 `/tmp/ai-dashboard/build/sheet_raw.csv` 로 저장한 뒤:

    python3 build/sync_sheet.py build/sheet_raw.csv

CSV 를 받지 못하면 이 단계만 건너뛰고 보고에 명시하세요 (시트 스펙은 어제 값 유지).

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
■ 4단계 — 슬랙 발주채널 (읽기 전용)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
채널 C09FCV7UHF1 (#상품기획-타임라인_발주의뢰) 에서 `build/orders.json` 의 최신 ts 이후
새 발주 메시지를 읽어 배열로 `/tmp/ai-dashboard/build/slack_new.json` 에 저장:

    ts, date, author, kind, product, vendor, qty, unit, due, slackUrl

⚠️ ts 는 메시지 원문 값을 소수점 6자리까지 그대로 쓰세요. 반올림하면 slackUrl
permalink 가 깨져 슬랙이 채널로 떨어집니다 (과거에 실제로 50건이 이 문제로 깨졌습니다).
slackUrl 은 `https://pharmabroshq.slack.com/archives/C09FCV7UHF1/p<ts에서 점 제거>` 입니다.

    python3 build/sync_orders.py build/slack_new.json

새 발주가 없으면 이 단계는 건너뛰어도 됩니다.

── 4B. 리뉴얼·변경사항 비고 (엄격 준수) ──
새로 읽은 메시지 중 리뉴얼이거나 변경사항이 명시된 건이 있으면
`build/order_notes.json` 에 추가하세요:

    "발주일|제품명": { "renewal": true, "note": "...", "src": "<슬랙 permalink URL>" }

[Key 매칭 및 데이터 엄격 규칙]
1. Key 형식 및 Normalization:
   · key는 `orders.json`의 `date|product` (예: `2026-05-19|파이토알엑스 트리플 아르기닌 액티브`)와 일치해야 합니다.
   · 문자열 처리 시 양쪽 텍스트의 앞뒤 공백 제거(trim) 및 중복 공백 정규화를 반드시 적용하여 매칭 누락을 방지하세요.
2. Flag 및 Note 입력:
   · 제목이나 본문에 리뉴얼이 명시된 건만 `renewal: true` (R 배지가 붙습니다).
   · 단가 인상·수량 조정처럼 리뉴얼이 아닌 변경은 `renewal: false`로 두고 비고(`note`)만 남기세요.
   · 원문에 적힌 수치/문구만 그대로 옮깁니다. 추측·의역·요약·단순'리뉴얼' 두글자 때우기 금지.
3. 원문 링크(src):
   · `src` 에는 슬랙 메시지의 정확한 permalink URL(`https://pharmabroshq.slack.com/archives/...`)을 연결해야 합니다.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
■ UI 및 렌더링 검증 규칙 (build.py / template.html)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. 메인 발주 테이블 UI:
   · R 배지 위치: `renewal: true`인 건은 메인 테이블의 [발주일] 컬럼 바로 오른쪽(예: `2026-05-19 [R]`)에 **단 1개만** 위치시킵니다. (제품명 우측 중복 렌더링 절대 금지)
   · R 배지 스타일: 진한 보라색 배경에 흰색 글씨 (`bg-purple-600 text-white font-bold rounded`)
   · NEW 배지: 최신 발주건의 [발주일] 컬럼 오른쪽에 빨간색 `NEW` 배지 유지.
   · 구분 컬럼: `renewal: true` 건은 연보라색 `리뉴얼` 뱃지로 표기.

2. 제품 상세 모달 UI:
   · 요소 순서: 발주 정보 항목 우측에 `[슬랙 아이콘 + 원문 버튼]` -> `[보라색 R 배지]` 순서로 배치합니다.
   · 원문 버튼: 슬랙(#) 아이콘이 포함된 콤팩트 뱃지 스타일로 구성하며, 클릭 시 `src` URL로 새 창(`target="_blank" rel="noopener noreferrer"`) 이동해야 합니다. (유효하지 않을 경우 슬랙 채널 fallback)
   · 리뉴얼 상세 비고 출력 (가장 중요): `order_notes.json`의 `note` 값이 존재하는 경우, 모달 하단 발주 내역에 `<div class="text-xs text-purple-600 mt-1 font-medium">리뉴얼 ${note}</div>` 형태로 전체 비고 문장을 100% 노출해야 합니다. (단순 '리뉴얼' 텍스트 단독 출력 금지)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
■ 5단계 — 빌드
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    cd /tmp/ai-dashboard && python3 build/build.py --notion build/notion.json

출력에 `중단:` 이 있으면 배포하지 말고 사유를 보고한 뒤 종료하세요. `--allow-empty` 로 우회하지 마세요.

`■ 경고` 블록은 실행을 막지 않지만 반드시 최종 보고에 포함하세요.
특히 "발주 비고 미적용(키 불일치)" 는 비고가 화면에서 사라진 상태라는 뜻입니다.

단, "YDY 리브라인" · "박약다식 리플렛" 의 발주 매칭 실패는 daisy 가 이미 확인한 건이라
`orders.json` 에 `match` 가 고정돼 있습니다. 혹시 다시 뜨더라도 보고하지 마세요.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
■ 6단계 — 전달
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
먼저 push 를 시도합니다.

    cd /tmp/ai-dashboard
    git config commit.gpgsign false
    git config user.name  "pb-dashboard bot"
    git config user.email "daisy@pharma-bros.com"
    git add -A
    git commit -m "일일 갱신 $(TZ=Asia/Seoul date +%Y-%m-%d)"
    git push origin main

── 6-A. push 성공 ──
push 직후 다음을 실행해 원격 커밋이 로컬 HEAD와 같은지 확인하세요.
    git fetch origin main
    test "$(git rev-parse HEAD)" = "$(git rev-parse origin/main)"

그 다음 WebFetch 로 https://daisy3015.github.io/AI/ 를 열어 확인하세요.
응답 HTML에 `최신 상태 업데이트`, `최근 업데이트`, `id="syncBtn"` 중 하나라도 남아 있으면 Pages 반영 전이므로 반영 완료라고 보고하지 마세요.

── 6-B. push 실패 (현재 기본 경로) ──
`access denied by the git proxy` 나 403 이 나오면 재시도하거나 토큰을 찾지 마세요.
바뀐 파일을 파일 하나씩 따로 전달합니다. zip 으로 묶지 마세요 —

    cd /tmp/ai-dashboard
    git diff --name-only origin/main HEAD   # 바뀐 파일 목록

SendUserFile 로 바뀐 파일을 하나씩 보내고, 각각 어느 경로에 올려야 하는지 명시하세요.
· 최상단 파일: https://github.com/daisy3015/AI/upload/main
· build 폴더:  https://github.com/daisy3015/AI/upload/main/build

⚠️ 다운로드된 파일 이름이 정확한지(`index_12.html` 처럼 숫자가 붙지 않았는지) 확인하라고 안내하세요.

업로드 후에는 `git fetch origin main` 으로 원격을 받아 sha256 지문을 대조해 파일이 제자리에 제대로 들어갔는지 확인하고 결과를 알려주세요.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
■ 7단계 — 보고 (한국어, 간결하게)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
· build.py 의 "■ 직전 대비 변경" 내용 그대로
· 새로 추가한 발주 건수 / 새로 적은 리뉴얼·변경 비고 (있으면 제품명만)
· 건너뛴 단계가 있으면 그 사실과 이유
· `■ 경고` 전체
· 전달 방식 (자동 push 성공 / 파일 개별 전달) 과 바뀐 파일 목록
· https://daisy3015.github.io/AI/

변경이 없고 push 도 필요 없으면 "변경 없음" 한 줄로 끝내세요.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
■ 절대 하지 말 것
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
· 노션 / 구글시트 / 슬랙 / Gmail 에 쓰기 — 전부 읽기 전용입니다
· index.html 을 직접 수정 — 반드시 build.py 로 생성 (UI 는 template.html)
· 안전장치가 걸렸는데 우회해서 배포하기
· 슬랙 원문에 없는 내용을 비고에 지어내거나 '리뉴얼' 두 글자로 요약해버리기
· ts 를 반올림하거나 임의로 만들어 내기
· R 배지를 발주일과 제품명 양쪽에 중복 렌더링하기
