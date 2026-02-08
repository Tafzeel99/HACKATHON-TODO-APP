# Phase 4 - Running Containers 🚀

**Status**: ✅ Both containers running successfully with ChatKit configured
**Date**: February 6, 2026
**Version**: Backend 4.0.0, Frontend 4.0.0

---

## 📦 Running Containers

### Current Status

| Container | Status | Port | Health | ChatKit |
|-----------|--------|------|--------|---------|
| todo-backend | ✅ Running | 127.0.0.1:8000 | ✅ Healthy | ✅ Ready |
| todo-frontend | ✅ Running | 127.0.0.1:3000 | ✅ Healthy | ✅ Configured |

⚠️ **IMPORTANT**: Containers are bound to `127.0.0.1` (not `0.0.0.0`) because OpenAI ChatKit requires this specific address.

---

## 🔗 Access Points

### Frontend (User Interface)

- 🌐 **Main Application**: http://127.0.0.1:3000
- 💬 **AI Chat Interface**: http://127.0.0.1:3000/chat
- 📊 **Analytics Dashboard**: http://127.0.0.1:3000/analytics
- 📅 **Calendar View**: http://127.0.0.1:3000/calendar
- 📁 **Projects**: http://127.0.0.1:3000/projects
- ⚙️ **Settings**: http://127.0.0.1:3000/settings

### Backend (API)

- 🏥 **Health Check**: http://127.0.0.1:8000/health
- 📚 **API Docs (Swagger)**: http://127.0.0.1:8000/docs
- 📖 **ReDoc**: http://127.0.0.1:8000/redoc
- 📄 **OpenAPI JSON**: http://127.0.0.1:8000/openapi.json
- 🤖 **ChatKit Endpoint**: http://127.0.0.1:8000/chatkit

---

## 🤖 ChatKit Configuration

### Domain Key Status
✅ **Configured and Active**

**Domain Key**: `domain_pk_696ffdeaf57c8197a912387a3d6cfeec07db6318cdf03509`

**Configuration Method**:
- Domain key is **baked into the Docker image** at build time
- Set via `--build-arg NEXT_PUBLIC_OPENAI_DOMAIN_KEY` during build
- Cannot be changed at runtime (Next.js limitation)

### Why 127.0.0.1?

OpenAI ChatKit **requires** applications to run on `127.0.0.1` specifically:
- ❌ `localhost` will NOT work
- ❌ `0.0.0.0` will NOT work
- ✅ `127.0.0.1` ONLY

This is a ChatKit security requirement for local development.

---

## 🚀 Running the Containers

### Backend Container

```bash
docker run -d \
  --name todo-backend \
  -p 127.0.0.1:8000:8000 \
  -e DATABASE_URL="sqlite+aiosqlite:///./todo_app.db" \
  -e BETTER_AUTH_SECRET="hackathon-todo-app-secret-key-minimum-32-characters-long" \
  -e BETTER_AUTH_URL="http://127.0.0.1:3000" \
  -e OPEN_ROUTER_KEY="sk-or-v1-test-key" \
  -e LLM_BASE_URL="https://openrouter.ai/api/v1" \
  -e LLM_MODEL="openai/gpt-4o-mini" \
  -e CORS_ORIGINS='["http://127.0.0.1:3000","http://localhost:3000"]' \
  -e RATE_LIMIT_REQUESTS="100" \
  -e RATE_LIMIT_WINDOW_SECONDS="60" \
  todo-backend:4.0.0
```

**Key Configuration**:
- Port binding: `127.0.0.1:8000:8000` (not `0.0.0.0`)
- Database: SQLite with async driver (`sqlite+aiosqlite://`)
- CORS: Includes both 127.0.0.1 and localhost
- Better Auth URL: Points to frontend on 127.0.0.1

### Frontend Container

```bash
docker run -d \
  --name todo-frontend \
  -p 127.0.0.1:3000:3000 \
  todo-frontend:4.0.0
```

**Key Configuration**:
- Port binding: `127.0.0.1:3000:3000` (not `0.0.0.0`)
- API URL: `http://127.0.0.1:8000` (baked in at build time)
- ChatKit Domain Key: Embedded in image at build time

**Note**: Frontend environment variables are set during **build**, not runtime. To change them, you must rebuild the image.

---

## 🔧 Container Management

### View Running Containers

```bash
docker ps
```

Expected output:
```
CONTAINER ID   IMAGE                 STATUS              PORTS
ebeb8ec09b24   todo-frontend:4.0.0   Up (healthy)        127.0.0.1:3000->3000/tcp
0f7150715182   todo-backend:4.0.0    Up (healthy)        127.0.0.1:8000->8000/tcp
```

### View Logs

**Live logs**:
```bash
docker logs -f todo-backend
docker logs -f todo-frontend
```

**Last 50 lines**:
```bash
docker logs --tail 50 todo-backend
docker logs --tail 50 todo-frontend
```

### Stop Containers

```bash
# Stop both
docker stop todo-backend todo-frontend

# Stop individually
docker stop todo-backend
docker stop todo-frontend
```

### Start Containers

```bash
# Start both
docker start todo-backend todo-frontend

# Start individually
docker start todo-backend
docker start todo-frontend
```

### Restart Containers

```bash
# Restart both
docker restart todo-backend todo-frontend

# Restart individually
docker restart todo-backend
docker restart todo-frontend
```

### Remove Containers

```bash
# Remove both (must be stopped first)
docker stop todo-backend todo-frontend
docker rm todo-backend todo-frontend

# Force remove (even if running)
docker rm -f todo-backend todo-frontend
```

### View Container Stats

```bash
# Real-time stats
docker stats todo-backend todo-frontend

# One-time stats
docker stats --no-stream todo-backend todo-frontend
```

### Execute Commands Inside Containers

**Backend (Python shell)**:
```bash
docker exec -it todo-backend python
```

**Backend (Bash)**:
```bash
docker exec -it todo-backend bash
```

**Frontend (Shell)**:
```bash
docker exec -it todo-frontend sh
```

**View environment variables**:
```bash
docker exec todo-backend env
docker exec todo-frontend env
```

---

## 🧪 Testing the Application

### Test Backend Health

```bash
curl http://127.0.0.1:8000/health
```
Expected: `{"status":"healthy","version":"4.0.0"}`

### Test Frontend

```bash
curl -I http://127.0.0.1:3000
```
Expected: `HTTP/1.1 200 OK`

### Test ChatKit Integration

**1. Open Browser**:
```
http://127.0.0.1:3000
```
⚠️ **Must use 127.0.0.1, NOT localhost**

**2. Register/Login**:
- Click "Sign Up" to create an account
- Or "Login" if you have existing credentials

**3. Navigate to Chat**:
```
http://127.0.0.1:3000/chat
```

**4. Verify ChatKit Loads**:
- ✅ Chat interface should appear
- ✅ No "Configuration Required" error
- ✅ Input field is active

**5. Test AI Commands**:
```
"Add a task: Buy groceries tomorrow"
"Show my tasks"
"Mark the first task as complete"
"What's my schedule for today?"
```

### Test API Endpoints

**List tasks** (requires authentication):
```bash
curl http://127.0.0.1:8000/api/tasks \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Create task** (requires authentication):
```bash
curl -X POST http://127.0.0.1:8000/api/tasks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"title":"Test Task","description":"Testing from Docker"}'
```

---

## 🐛 Troubleshooting

### ChatKit Not Working

**Problem**: ChatKit shows "Configuration Required" error

**Solutions**:

1. **Verify you're using 127.0.0.1**:
   - ❌ http://localhost:3000
   - ✅ http://127.0.0.1:3000

2. **Hard refresh browser**:
   - Windows/Linux: `Ctrl + Shift + R`
   - Mac: `Cmd + Shift + R`

3. **Check container logs**:
   ```bash
   docker logs todo-frontend --tail 50
   ```

4. **Verify frontend was rebuilt with domain key**:
   ```bash
   docker images | grep todo-frontend
   # Should show recent creation time
   ```

### Container Not Starting

**Check logs**:
```bash
docker logs todo-backend
docker logs todo-frontend
```

**Common issues**:
- Port already in use
- Database connection errors
- Missing environment variables

### Port Already in Use

**Check what's using the port**:
```bash
# Check port 8000
lsof -i :8000
netstat -an | grep 8000

# Check port 3000
lsof -i :3000
netstat -an | grep 3000
```

**Stop conflicting containers**:
```bash
docker stop $(docker ps -q)
```

### Database Issues

**Problem**: Backend fails with database errors

**Solution**: Ensure `DATABASE_URL` uses async driver:
```bash
DATABASE_URL="sqlite+aiosqlite:///./todo_app.db"
```

Not:
```bash
DATABASE_URL="sqlite:///./todo_app.db"  # ❌ Wrong (sync driver)
```

### Frontend Can't Connect to Backend

**Check API URL in frontend**:
```bash
docker exec todo-frontend env | grep NEXT_PUBLIC_API_URL
```

Should show: `NEXT_PUBLIC_API_URL=http://127.0.0.1:8000`

**Check CORS on backend**:
```bash
docker exec todo-backend env | grep CORS
```

Should include: `http://127.0.0.1:3000`

### Container Keeps Restarting

**Check exit code**:
```bash
docker ps -a | grep todo
docker logs todo-backend
docker logs todo-frontend
```

**Common causes**:
- Database connection failed
- Port conflict
- Missing required environment variable
- Application crash

---

## 🔄 Rebuilding Images

### Rebuild Backend

```bash
cd phase4/backend
docker build -t todo-backend:4.0.0 -t todo-backend:latest .
```

### Rebuild Frontend

**Important**: Frontend env vars must be set at build time!

```bash
cd phase4/frontend
docker build --no-cache \
  --build-arg NEXT_PUBLIC_API_URL="http://127.0.0.1:8000" \
  --build-arg NEXT_PUBLIC_OPENAI_DOMAIN_KEY="your-domain-key-here" \
  -t todo-frontend:4.0.0 \
  -t todo-frontend:latest \
  .
```

### Redeploy After Rebuild

```bash
# Stop and remove old containers
docker stop todo-backend todo-frontend
docker rm todo-backend todo-frontend

# Run new containers (use commands from "Running the Containers" section above)
```

---

## 📊 Environment Variables

### Backend Environment Variables

**Required**:
- `DATABASE_URL`: Database connection (use `sqlite+aiosqlite://` for async)
- `BETTER_AUTH_SECRET`: JWT secret key (minimum 32 characters)
- `BETTER_AUTH_URL`: Frontend URL for auth callbacks
- `OPEN_ROUTER_KEY`: API key for AI features (use real key for production)

**Optional**:
- `LLM_BASE_URL`: LLM API endpoint (default: OpenRouter)
- `LLM_MODEL`: Model to use (default: gpt-4o-mini)
- `CORS_ORIGINS`: Allowed origins (JSON array)
- `RATE_LIMIT_REQUESTS`: Max requests per window (default: 100)
- `RATE_LIMIT_WINDOW_SECONDS`: Rate limit window (default: 60)

### Frontend Environment Variables

**Build-time only** (must be set during `docker build`):
- `NEXT_PUBLIC_API_URL`: Backend API URL
- `NEXT_PUBLIC_OPENAI_DOMAIN_KEY`: ChatKit domain key

**Cannot be changed at runtime!** Must rebuild image to change.

---

## 📈 Resource Usage

**Expected resources**:
- **Backend**: ~100-200 MB RAM, Low CPU
- **Frontend**: ~50-100 MB RAM, Low CPU

**Check current usage**:
```bash
docker stats --no-stream todo-backend todo-frontend
```

---

## 🚀 Next Steps

### 1. Test Full Application Flow

1. Open http://127.0.0.1:3000
2. Register a new account
3. Create some tasks
4. Test the AI chat at http://127.0.0.1:3000/chat
5. Verify tasks sync between chat and main app

### 2. Configure Production API Key

For full AI functionality, update backend with real OpenRouter key:

```bash
docker stop todo-backend
docker rm todo-backend

docker run -d \
  --name todo-backend \
  -p 127.0.0.1:8000:8000 \
  -e DATABASE_URL="sqlite+aiosqlite:///./todo_app.db" \
  -e BETTER_AUTH_SECRET="hackathon-todo-app-secret-key-minimum-32-characters-long" \
  -e BETTER_AUTH_URL="http://127.0.0.1:3000" \
  -e OPEN_ROUTER_KEY="sk-or-v1-YOUR-REAL-KEY-HERE" \
  -e LLM_BASE_URL="https://openrouter.ai/api/v1" \
  -e LLM_MODEL="openai/gpt-4o-mini" \
  -e CORS_ORIGINS='["http://127.0.0.1:3000","http://localhost:3000"]' \
  todo-backend:4.0.0
```

### 3. Production Deployment

When deploying to production:
- Use PostgreSQL instead of SQLite
- Get new ChatKit domain key for production domain
- Rebuild frontend with production domain key
- Configure proper secrets management
- Set up SSL/TLS certificates
- Add resource limits to containers
- Set up monitoring and logging

---

## ✅ Verification Checklist

- [x] Backend container running on 127.0.0.1:8000
- [x] Frontend container running on 127.0.0.1:3000
- [x] Backend health check passing
- [x] Frontend accessible (HTTP 200)
- [x] ChatKit domain key configured
- [x] CORS configured for 127.0.0.1
- [ ] User can register/login via browser
- [ ] Tasks can be created via UI
- [ ] ChatKit loads without errors
- [ ] AI chat responds to messages
- [ ] Tasks created via chat appear in task list

---

## 📝 Important Notes

### Database Persistence

**Current Setup**: SQLite database inside container
- Data persists while container is running
- Data is **lost** when container is removed

**For Production**: Use external database or mount volume:
```bash
docker run -d \
  --name todo-backend \
  -p 127.0.0.1:8000:8000 \
  -v $(pwd)/data:/app/data \
  -e DATABASE_URL="sqlite+aiosqlite:////app/data/todo_app.db" \
  # ... other env vars
  todo-backend:4.0.0
```

### Security Considerations

**Current Setup** (Development):
- ✅ Non-root users in containers
- ✅ Health checks enabled
- ✅ CORS configured
- ⚠️ Using test API keys
- ⚠️ SQLite database (not production-ready)
- ⚠️ Bound to 127.0.0.1 (local only)

**For Production**:
- Use real secrets (not placeholder values)
- Use PostgreSQL with proper authentication
- Add SSL/TLS termination
- Implement proper rate limiting
- Add monitoring and alerting
- Use container orchestration (Kubernetes)

### Build vs Runtime Configuration

**Build-time** (must rebuild to change):
- `NEXT_PUBLIC_API_URL`
- `NEXT_PUBLIC_OPENAI_DOMAIN_KEY`
- All frontend environment variables

**Runtime** (can change with `docker run -e`):
- All backend environment variables
- Database URL
- API keys
- CORS settings

---

## 🎯 Quick Reference

### Start Everything
```bash
docker start todo-backend todo-frontend
```

### Stop Everything
```bash
docker stop todo-backend todo-frontend
```

### Restart Everything
```bash
docker restart todo-backend todo-frontend
```

### View All Logs
```bash
docker logs -f todo-backend &
docker logs -f todo-frontend
```

### Check Health
```bash
curl http://127.0.0.1:8000/health
curl -I http://127.0.0.1:3000
```

### Access URLs
- Frontend: http://127.0.0.1:3000
- Chat: http://127.0.0.1:3000/chat
- API Docs: http://127.0.0.1:8000/docs

---

**Containers are running and ready for use! 🎉**

**Remember**: Always use `127.0.0.1` (not `localhost`) for ChatKit compatibility! 🎯
