# GitHub MCP 설정 가이드

GitHub MCP를 사용하여 자동으로 GitHub에 파일을 업로드할 수 있습니다.

## 🔑 1. GitHub Personal Access Token 생성

### Step 1: GitHub에서 토큰 생성
1. GitHub 웹사이트 접속: https://github.com
2. 우측 상단 프로필 클릭 → **Settings**
3. 왼쪽 메뉴에서 **Developer settings** 클릭
4. **Personal access tokens** → **Tokens (classic)** 클릭
5. **Generate new token** → **Generate new token (classic)** 클릭

### Step 2: 토큰 권한 설정
다음 권한들을 체크하세요:
- ✅ `repo` (전체 저장소 권한)
  - `repo:status`
  - `repo_deployment`
  - `public_repo`
  - `repo:invite`
  - `security_events`

### Step 3: 토큰 생성 및 복사
1. **Generate token** 버튼 클릭
2. 생성된 토큰을 **즉시 복사** (다시 볼 수 없습니다!)
3. 안전한 곳에 저장해두세요

## ⚙️ 2. Cursor에서 MCP 설정

### 방법 1: Cursor 설정 파일 수정

1. Cursor 설정 열기:
   - `Ctrl + ,` (설정)
   - 또는 `File` → `Preferences` → `Settings`

2. MCP 설정 찾기:
   - 검색창에 "MCP" 입력
   - 또는 설정 파일 직접 편집

3. 설정 파일 위치:
   - Windows: `%APPDATA%\Cursor\User\globalStorage\saoudrizwan.claude-dev\settings\cline_mcp_settings.json`
   - 또는 Cursor 설정에서 "MCP" 검색

4. GitHub MCP 설정 추가:
```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-github"
      ],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "여기에_토큰_붙여넣기"
      }
    }
  }
}
```

### 방법 2: 환경 변수 설정 (추천)

1. Windows 환경 변수 설정:
   - `Win + R` → `sysdm.cpl` 입력
   - **고급** 탭 → **환경 변수** 클릭
   - **시스템 변수**에서 **새로 만들기**
   - 변수 이름: `GITHUB_PERSONAL_ACCESS_TOKEN`
   - 변수 값: 생성한 토큰 붙여넣기
   - **확인** 클릭

2. Cursor 재시작:
   - Cursor를 완전히 종료하고 다시 시작

## 🧪 3. 설정 확인

Cursor에서 다음 명령어로 테스트:
```
GitHub 저장소 목록을 보여줘
```

또는:
```
내 GitHub 프로필 정보를 보여줘
```

정상 작동하면 설정이 완료된 것입니다!

## 📤 4. GitHub에 업로드하기

설정이 완료되면 다음과 같이 요청하세요:
```
GitHub에 image-editor-web 저장소를 만들고 github_release 폴더의 파일들을 업로드해줘
```

## ⚠️ 주의사항

1. **토큰 보안**:
   - 토큰을 절대 공개하지 마세요
   - GitHub에 토큰을 커밋하지 마세요
   - 토큰이 유출되면 즉시 GitHub에서 삭제하세요

2. **토큰 만료**:
   - 토큰은 만료일을 설정할 수 있습니다
   - 만료되면 새로 생성해야 합니다

3. **권한 최소화**:
   - 필요한 최소한의 권한만 부여하세요
   - `public_repo`만 체크해도 충분합니다

## 🔄 대안: 수동 업로드

MCP 설정이 어렵다면 수동으로 업로드할 수도 있습니다:

### 방법 1: GitHub 웹사이트에서
1. GitHub에서 새 저장소 생성
2. "uploading an existing file" 클릭
3. 파일들을 드래그 앤 드롭
4. 커밋

### 방법 2: Git 명령어
```bash
cd github_release
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/your-username/your-repo.git
git push -u origin main
```

## 📚 참고 자료

- GitHub Personal Access Tokens: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token
- MCP GitHub Server: https://github.com/modelcontextprotocol/servers/tree/main/src/github




