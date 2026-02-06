# 🚀 Hugging Face Deployment Guide

Complete guide to deploy both Phase 2 and Phase 3 backends to Hugging Face Spaces.

## 📦 What We're Deploying

1. **Phase 2 Backend** → `todo-backend-api` Space
   - REST API for task management
   - Auth, Projects, Comments, Shares, Activities

2. **Phase 3 Backend** → `todo-ai-chatbot` Space
   - AI-powered chatbot
   - OpenAI Agents SDK + MCP Tools + ChatKit

---

## 🎯 Pre-Deployment Checklist

- [x] Dockerfiles created
- [x] requirements.txt generated
- [x] .dockerignore configured
- [x] README with Space metadata
- [ ] Hugging Face account created
- [ ] Git configured
- [ ] Environment variables ready

---

## 📝 Step-by-Step Deployment

### **Part 1: Create Hugging Face Spaces**

#### 1.1 Create Phase 2 Space

1. Go to https://huggingface.co/new-space
2. Fill in details:
   - **Space name**: `todo-backend-api`
   - **License**: MIT
   - **SDK**: Docker
   - **Visibility**: Public or Private
3. Click **Create Space**

#### 1.2 Create Phase 3 Space

1. Go to https://huggingface.co/new-space
2. Fill in details:
   - **Space name**: `todo-ai-chatbot`
   - **License**: MIT
   - **SDK**: Docker
   - **Visibility**: Public or Private
3. Click **Create Space**

---

### **Part 2: Prepare Repositories**

#### 2.1 Rename README files

```bash
cd "/mnt/d/IT CLASSES pc/HACKATHON-TODO-APP"

# Phase 2
cd phase2/backend
mv README.md README_ORIGINAL.md
mv README_HUGGINGFACE.md README.md

# Phase 3
cd ../../phase3/backend
mv README.md README_ORIGINAL.md
mv README_HUGGINGFACE.md README.md
```

#### 2.2 Commit deployment files

```bash
cd "/mnt/d/IT CLASSES pc/HACKATHON-TODO-APP"

git add .
git commit -m "feat: add Hugging Face deployment configuration

- Add Dockerfiles for Phase 2 and Phase 3 backends
- Generate requirements.txt from pyproject.toml
- Add .dockerignore files
- Create Hugging Face Space README files
- Configure for port 7860 (HF default)"

git push origin main
```

---

### **Part 3: Deploy Phase 2 Backend**

#### 3.1 Initialize Git in Phase 2

```bash
cd "/mnt/d/IT CLASSES pc/HACKATHON-TODO-APP/phase2/backend"

# Initialize git (if not already done)
git init
git branch -M main
```

#### 3.2 Connect to Hugging Face

Replace `YOUR_USERNAME` with your HuggingFace username:

```bash
git remote add huggingface https://huggingface.co/spaces/YOUR_USERNAME/todo-backend-api
```

#### 3.3 Push to Hugging Face

```bash
git add .
git commit -m "Initial deployment to Hugging Face"
git push huggingface main --force
```

#### 3.4 Configure Environment Variables

1. Go to your Space: `https://huggingface.co/spaces/YOUR_USERNAME/todo-backend-api`
2. Click **Settings** tab
3. Scroll to **Repository secrets**
4. Add these variables:

```bash
DATABASE_URL=postgresql://user:password@ep-xxx.us-east-2.aws.neon.tech/dbname?sslmode=require
BETTER_AUTH_SECRET=your-secret-key-minimum-32-characters-long
BETTER_AUTH_URL=https://your-frontend.vercel.app
CORS_ORIGINS=https://your-frontend.vercel.app,http://localhost:3000
ENVIRONMENT=production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_DAYS=7
```

5. Click **Restart Space**

---

### **Part 4: Deploy Phase 3 Backend**

#### 4.1 Initialize Git in Phase 3

```bash
cd "/mnt/d/IT CLASSES pc/HACKATHON-TODO-APP/phase3/backend"

# Initialize git (if not already done)
git init
git branch -M main
```

#### 4.2 Connect to Hugging Face

Replace `YOUR_USERNAME` with your HuggingFace username:

```bash
git remote add huggingface https://huggingface.co/spaces/YOUR_USERNAME/todo-ai-chatbot
```

#### 4.3 Push to Hugging Face

```bash
git add .
git commit -m "Initial deployment to Hugging Face"
git push huggingface main --force
```

#### 4.4 Configure Environment Variables

1. Go to your Space: `https://huggingface.co/spaces/YOUR_USERNAME/todo-ai-chatbot`
2. Click **Settings** tab
3. Scroll to **Repository secrets**
4. Add these variables:

```bash
# Database (same as Phase 2)
DATABASE_URL=postgresql://user:password@ep-xxx.us-east-2.aws.neon.tech/dbname?sslmode=require

# OpenRouter API
OPEN_ROUTER_KEY=sk-or-v1-your-openrouter-key-here
LLM_BASE_URL=https://openrouter.ai/api/v1
LLM_MODEL=google/gemini-flash-1.5-8b

# Auth (same as Phase 2)
BETTER_AUTH_SECRET=your-jwt-secret-key
BETTER_AUTH_URL=https://your-frontend.vercel.app

# CORS
CORS_ORIGINS=https://your-frontend.vercel.app,http://localhost:3000

# Environment
ENVIRONMENT=production

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW_SECONDS=60
```

5. Click **Restart Space**

---

## ✅ Verify Deployment

### Phase 2 Backend

1. Visit: `https://huggingface.co/spaces/YOUR_USERNAME/todo-backend-api`
2. Wait for build to complete (5-10 minutes)
3. Test health endpoint: `https://YOUR_USERNAME-todo-backend-api.hf.space/health`
4. Visit API docs: `https://YOUR_USERNAME-todo-backend-api.hf.space/docs`

### Phase 3 Backend

1. Visit: `https://huggingface.co/spaces/YOUR_USERNAME/todo-ai-chatbot`
2. Wait for build to complete (5-10 minutes)
3. Test health endpoint: `https://YOUR_USERNAME-todo-ai-chatbot.hf.space/health`
4. Visit API docs: `https://YOUR_USERNAME-todo-ai-chatbot.hf.space/docs`

---

## 🔧 Update Frontend Configuration

Update your frontend `.env` files with the new backend URLs:

### Phase 2 Frontend (.env.production)

```bash
NEXT_PUBLIC_API_URL=https://YOUR_USERNAME-todo-backend-api.hf.space/api
```

### Phase 3 Frontend (chat integration)

```bash
NEXT_PUBLIC_CHAT_API_URL=https://YOUR_USERNAME-todo-ai-chatbot.hf.space
```

---

## 🔄 Future Updates

To update your deployments:

```bash
# Phase 2
cd "/mnt/d/IT CLASSES pc/HACKATHON-TODO-APP/phase2/backend"
git add .
git commit -m "Update: your changes"
git push huggingface main

# Phase 3
cd "/mnt/d/IT CLASSES pc/HACKATHON-TODO-APP/phase3/backend"
git add .
git commit -m "Update: your changes"
git push huggingface main
```

Hugging Face will automatically rebuild and redeploy!

---

## 🐛 Troubleshooting

### Build Fails

1. Check Space logs in the Hugging Face UI
2. Verify all environment variables are set
3. Check Dockerfile syntax
4. Ensure requirements.txt is valid

### Database Connection Error

- Verify DATABASE_URL is correct
- Check Neon PostgreSQL is accessible
- Whitelist Hugging Face IPs if needed

### CORS Issues

- Add Hugging Face Space URL to CORS_ORIGINS
- Update frontend to use correct backend URLs

### Port Issues

- Hugging Face requires port 7860
- Both Dockerfiles are configured correctly

---

## 📊 Space URLs

After deployment:

- **Phase 2 API**: `https://YOUR_USERNAME-todo-backend-api.hf.space`
- **Phase 3 Chatbot**: `https://YOUR_USERNAME-todo-ai-chatbot.hf.space`
- **Phase 2 Docs**: `https://YOUR_USERNAME-todo-backend-api.hf.space/docs`
- **Phase 3 Docs**: `https://YOUR_USERNAME-todo-ai-chatbot.hf.space/docs`

---

## 🎉 Success!

Both backends are now deployed on Hugging Face Spaces!

- ✅ Phase 2 REST API deployed
- ✅ Phase 3 AI Chatbot deployed
- ✅ Environment variables configured
- ✅ Health checks passing
- ✅ API documentation available

**Next Steps:**
1. Update frontend to use new backend URLs
2. Test all API endpoints
3. Monitor Space logs
4. Share your Space URLs!

---

## 🔗 Useful Links

- [Hugging Face Spaces Docs](https://huggingface.co/docs/hub/spaces)
- [Docker SDK Guide](https://huggingface.co/docs/hub/spaces-sdks-docker)
- [Environment Variables](https://huggingface.co/docs/hub/spaces-overview#managing-secrets-and-environment-variables)
