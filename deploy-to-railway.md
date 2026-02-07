# Deploy Backend to Railway Using CLI

## Install Railway CLI

### On Windows (PowerShell):
```powershell
iwr https://railway.app/install.ps1 | iex
```

### On Mac/Linux:
```bash
curl -fsSL https://railway.app/install.sh | sh
```

## Deploy Steps

1. **Login to Railway**:
```bash
railway login
```

2. **Navigate to backend directory**:
```bash
cd Phase-2-Web-App/backend
```

3. **Initialize Railway project**:
```bash
railway init
```
- Select "Create new project"
- Name it: "todo-backend"

4. **Link to your project**:
```bash
railway link
```

5. **Add environment variables**:
```bash
railway variables set DATABASE_URL="postgresql+asyncpg://neondb_owner:npg_HvxfMqG5Fb7Y@ep-withered-sunset-a1kv12v0-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require"

railway variables set JWT_SECRET="b0e3cc396c2f15582a8f6ca6d0a2cb5f32e227cdd6e1d02d5517e215721f225c"

railway variables set BETTER_AUTH_SECRET="b0e3cc396c2f15582a8f6ca6d0a2cb5f32e227cdd6e1d02d5517e215721f225c"

railway variables set JWT_ALGORITHM="HS256"

railway variables set CORS_ORIGINS="http://localhost:3000"

railway variables set DEBUG="False"
```

6. **Deploy**:
```bash
railway up
```

7. **Get your URL**:
```bash
railway domain
```

## Advantages of CLI Method
- ✅ No need to find UI settings
- ✅ Deploys from correct directory automatically
- ✅ Full control over configuration
- ✅ Faster deployment
