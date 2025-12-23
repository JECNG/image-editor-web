# N8N Render.com 무료 배포 가이드

N8N을 Render.com의 Free 플랜으로 배포하는 방법입니다.

## 🚀 빠른 배포 (Docker 이미지 사용)

### 방법 1: Render Dashboard에서 직접 생성

1. **Render 대시보드 접속**: https://dashboard.render.com
2. **New +** 버튼 클릭 → **Web Service** 선택
3. **Public Git repository** 선택
4. **Repository URL** 입력:
   ```
   https://github.com/n8n-io/n8n
   ```
   또는 Docker 이미지 직접 사용:
   ```
   n8nio/n8n
   ```

### 방법 2: Docker 이미지 직접 사용 (추천)

1. **New +** → **Web Service**
2. **Environment**: `Docker` 선택
3. **Docker Image**: `n8nio/n8n:latest` 입력
4. **Name**: `n8n` (원하는 이름)
5. **Region**: `Oregon` (또는 원하는 지역)

## ⚙️ 필수 설정

### 1. Start Command
```
n8n start
```

### 2. Environment Variables

**필수 변수:**
```
N8N_HOST=0.0.0.0
N8N_PORT=$PORT
N8N_PROTOCOL=https
WEBHOOK_URL=https://your-n8n-service.onrender.com/
```

**선택 변수 (데이터 저장용):**
```
N8N_BASIC_AUTH_ACTIVE=true
N8N_BASIC_AUTH_USER=admin
N8N_BASIC_AUTH_PASSWORD=your-secure-password
```

**데이터베이스 (선택, 영구 저장용):**
```
DB_TYPE=postgres
DB_POSTGRESDB_HOST=your-postgres-host.onrender.com
DB_POSTGRESDB_PORT=5432
DB_POSTGRESDB_DATABASE=n8n
DB_POSTGRESDB_USER=your-user
DB_POSTGRESDB_PASSWORD=your-password
```

### 3. Health Check Path
```
/healthz
```

## 📝 상세 설정 단계

### Step 1: Web Service 생성

1. Render 대시보드 → **New +** → **Web Service**
2. **Public Git repository** 선택
3. **Repository**: `https://github.com/n8n-io/n8n` 입력
4. **Branch**: `master` 또는 `main`
5. **Name**: `n8n` (또는 원하는 이름)
6. **Region**: `Oregon (US West)`
7. **Instance Type**: `Free`

### Step 2: Build & Deploy 설정

**Build Command:**
```
npm ci
```

**Start Command:**
```
npm start
```

또는 Docker 사용 시:
```
docker run -it --rm --name n8n -p $PORT:$PORT -e N8N_HOST=0.0.0.0 -e N8N_PORT=$PORT n8nio/n8n
```

### Step 3: Environment Variables 추가

**Settings** → **Environment Variables**에서 추가:

| Key | Value | 설명 |
|-----|-------|------|
| `N8N_HOST` | `0.0.0.0` | 모든 인터페이스에서 접근 허용 |
| `N8N_PORT` | `$PORT` | Render가 제공하는 포트 사용 |
| `N8N_PROTOCOL` | `https` | HTTPS 프로토콜 사용 |
| `WEBHOOK_URL` | `https://your-n8n.onrender.com/` | 웹훅 URL (서비스 URL로 변경) |
| `N8N_BASIC_AUTH_ACTIVE` | `true` | 기본 인증 활성화 (보안) |
| `N8N_BASIC_AUTH_USER` | `admin` | 로그인 사용자명 |
| `N8N_BASIC_AUTH_PASSWORD` | `your-password` | 로그인 비밀번호 |

### Step 4: PostgreSQL 데이터베이스 연결 (선택, 영구 저장)

1. **New +** → **PostgreSQL**
2. **Name**: `n8n-db`
3. **Database**: `n8n`
4. **User**: 자동 생성
5. **Password**: 자동 생성
6. **Internal Database URL** 복사

**Environment Variables에 추가:**
```
DB_TYPE=postgres
POSTGRES_DB_HOST=your-db-host.onrender.com
POSTGRES_DB_PORT=5432
POSTGRES_DB_DATABASE=n8n
POSTGRES_DB_USER=your-user
POSTGRES_DB_PASSWORD=your-password
```

또는 단일 URL 사용:
```
DATABASE_URL=postgresql://user:password@host:5432/n8n
```

## 🔒 보안 설정

### 기본 인증 활성화 (필수)

```
N8N_BASIC_AUTH_ACTIVE=true
N8N_BASIC_AUTH_USER=admin
N8N_BASIC_AUTH_PASSWORD=강력한-비밀번호-설정
```

### 암호화 키 설정 (선택)

```
N8N_ENCRYPTION_KEY=your-32-character-encryption-key
```

## 📊 무료 플랜 제한사항

- ✅ **서비스 개수**: 제한 없음
- ⚠️ **월간 실행 시간**: 750시간 (모든 무료 서비스 공유)
- ⚠️ **15분 비활성 시 sleep**: 첫 요청 시 30-50초 지연
- ✅ **메모리**: 512MB RAM
- ✅ **PostgreSQL**: 1개 무료 (N8N 데이터 저장용)

## 🎯 배포 후 확인

1. **서비스 URL 접속**: `https://your-n8n.onrender.com`
2. **로그인**: 설정한 `N8N_BASIC_AUTH_USER` / `N8N_BASIC_AUTH_PASSWORD`
3. **워크플로우 생성 테스트**

## 💡 유용한 팁

### 1. Sleep 방지 (Keep-alive)

무료 플랜의 sleep을 방지하려면:
- 외부 cron 서비스 (예: cron-job.org)에서 주기적으로 health check 호출
- 또는 Render의 Scheduled Jobs 사용 (유료 플랜 필요)

### 2. 데이터 백업

PostgreSQL 없이 사용하면 데이터가 영구 저장되지 않습니다:
- 정기적으로 워크플로우를 JSON으로 Export
- 또는 PostgreSQL 연결 권장

### 3. 웹훅 URL 설정

**Environment Variables**에서:
```
WEBHOOK_URL=https://your-n8n.onrender.com/
```

이 URL은 N8N 웹훅 트리거에서 사용됩니다.

## 🔧 문제 해결

### 포트 오류
- `N8N_PORT=$PORT` 확인
- Render가 자동으로 `$PORT` 환경 변수 제공

### 데이터 손실
- PostgreSQL 연결 필수
- 또는 정기적으로 Export

### Sleep 지연
- 첫 요청 시 30-50초 대기
- 이후 요청은 정상 속도

## 📚 참고 자료

- N8N 공식 문서: https://docs.n8n.io/
- Render 문서: https://render.com/docs
- N8N GitHub: https://github.com/n8n-io/n8n

