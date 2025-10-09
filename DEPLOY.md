# Deployment Guide - Passport Photo WebApp

This guide provides step-by-step instructions for deploying the Passport Photo WebApp to production using free and paid hosting services.

## 🚀 Quick Deploy (Recommended)

### Option 1: Vercel (Frontend) + Render (Backend)

**Frontend Deployment (Vercel)**

1. **Connect Repository**
   ```bash
   # Install Vercel CLI
   npm i -g vercel
   
   # Login and connect project
   cd frontend
   vercel --prod
   ```
   
2. **Environment Variables in Vercel Dashboard**
   ```
   VITE_API_URL=https://your-backend-url.onrender.com
   VITE_ENVIRONMENT=production
   ```

**Backend Deployment (Render)**

1. **Create render.yaml**
   ```yaml
   services:
     - type: web
       name: passport-photo-backend
       env: python
       buildCommand: pip install -r requirements.txt
       startCommand: gunicorn main:app -w 2 -k uvicorn.workers.UvicornWorker
       envVars:
         - key: ENVIRONMENT
           value: production
         - key: CORS_ORIGINS
           value: https://your-frontend-domain.vercel.app
   ```

2. **Connect Repository**
   - Go to [render.com](https://render.com)
   - Connect your GitHub repository
   - Select the backend folder
   - Deploy automatically

### Option 2: Railway (Full Stack)

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

## 🐳 Docker Deployment

### Self-Hosted with Docker Compose

1. **Create docker-compose.yml**
   ```yaml
   version: '3.8'
   services:
     backend:
       build: ./backend
       ports:
         - "8000:8000"
       environment:
         - ENVIRONMENT=production
         - CORS_ORIGINS=http://localhost:3000
       volumes:
         - ./backend:/app
         
     frontend:
       build: ./frontend
       ports:
         - "3000:80"
       environment:
         - VITE_API_URL=http://localhost:8000
       depends_on:
         - backend
   ```

2. **Deploy**
   ```bash
   docker-compose up -d
   ```

## 🔧 Environment Configuration

### Production Environment Variables

**Backend (.env)**
```bash
ENVIRONMENT=production
LOG_LEVEL=info
HOST=0.0.0.0
PORT=8000

# Security
RATE_LIMIT_REQUESTS=50
RATE_LIMIT_WINDOW=60
MAX_FILE_SIZE=10485760

# CORS
CORS_ORIGINS=https://your-domain.com,https://your-domain.vercel.app
```

**Frontend (.env.production)**
```bash
VITE_API_URL=https://your-backend-domain.com
VITE_ENVIRONMENT=production
```

## 🧪 Testing Production Deployment

### Manual Testing Checklist

- [ ] File upload works (drag & drop, file browser, webcam)
- [ ] Face detection activates and shows overlay
- [ ] Image processing completes within 5 seconds
- [ ] A4 generation produces valid PDF
- [ ] All background colors work correctly
- [ ] Mobile responsiveness confirmed
- [ ] Error handling works for invalid files
- [ ] Rate limiting prevents abuse
- [ ] Privacy policy and terms are accessible

## 🚨 Troubleshooting

### Common Issues

1. **CORS Errors**
   ```bash
   # Update CORS_ORIGINS in backend
   CORS_ORIGINS=https://your-frontend-domain.com
   ```

2. **Memory Issues on Free Tiers**
   ```python
   # Optimize memory usage
   import gc
   gc.collect()  # After processing each image
   ```

3. **Cold Start Delays**
   ```bash
   # Use keep-alive ping
   curl https://your-backend.com/health
   ```

---

## 🚀 One-Click Deploy Buttons

### Render
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

### Railway
[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template)

### Vercel
[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone)

---

This deployment guide covers all major hosting options and configurations. Choose the option that best fits your needs and budget.