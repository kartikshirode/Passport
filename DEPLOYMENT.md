# Deployment configurations and environment variables

## Frontend Deployment (Vercel)

### Build Settings
- Build Command: `npm run build`
- Output Directory: `dist`
- Install Command: `npm install`
- Node.js Version: `18.x`

### Environment Variables
```env
VITE_API_URL=https://your-backend-url.onrender.com
VITE_APP_NAME=Passport Photo Processor
VITE_ENABLE_ANALYTICS=true
```

### Domain Setup
- Production: `passport-photo-app.vercel.app`
- Staging: `passport-photo-staging.vercel.app`

## Backend Deployment (Render)

### Service Configuration
- Environment: Docker
- Build Command: Auto-deploy from Dockerfile
- Health Check Path: `/health`
- Auto-Deploy: Yes

### Environment Variables
```env
# Required
PYTHONPATH=/app
PYTHONUNBUFFERED=1
PORT=8000

# Performance
OMP_NUM_THREADS=4
ONNXRUNTIME_LOG_SEVERITY_LEVEL=3
WORKERS=2

# Optional - Analytics & Monitoring
SENTRY_DSN=your-sentry-dsn
ANALYTICS_ENABLED=true

# CORS (adjust for your domain)
CORS_ORIGINS=["https://passport-photo-app.vercel.app", "http://localhost:3000"]
```

### Resource Requirements
- **Free Tier**: 512 MB RAM, 0.1 CPU (suitable for testing)
- **Starter**: 1 GB RAM, 0.5 CPU (recommended for production)
- **Pro**: 2 GB RAM, 1 CPU (for high traffic)

## Railway Deployment (Alternative)

### Configuration
```toml
[build]
builder = "DOCKERFILE"
buildCommand = "echo 'Using Dockerfile'"

[deploy]
healthcheckPath = "/health"
healthcheckTimeout = 60
restartPolicyType = "ON_FAILURE"
```

## Docker Compose (Local Development)

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - PYTHONUNBUFFERED=1
      - CORS_ORIGINS=["http://localhost:3000"]
    volumes:
      - ./backend:/app
      - /app/__pycache__
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.dev
    ports:
      - "3000:3000"
    environment:
      - VITE_API_URL=http://localhost:8000
    volumes:
      - ./frontend:/app
      - /app/node_modules
    command: npm run dev -- --host 0.0.0.0

  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
```

## GitHub Secrets Required

### For CI/CD
```
DOCKER_USERNAME=your-docker-username
DOCKER_PASSWORD=your-docker-password
RENDER_DEPLOY_HOOK_STAGING=https://api.render.com/deploy/srv-...
RENDER_DEPLOY_HOOK_PRODUCTION=https://api.render.com/deploy/srv-...
VERCEL_TOKEN=your-vercel-token
VERCEL_ORG_ID=your-org-id
VERCEL_PROJECT_ID=your-project-id
SLACK_WEBHOOK_URL=your-slack-webhook (optional)
```

## Performance Optimizations

### Backend
1. **ONNX Model Conversion**
   - Convert U²-Net to ONNX for faster CPU inference
   - Use `convert_u2net_to_onnx.py` script
   - Store models in `/app/models/` directory

2. **Caching Strategy**
   - Cache processed masks for same input with different backgrounds
   - Use Redis for session-based caching (optional)

3. **Resource Management**
   - Set appropriate worker count based on CPU cores
   - Configure memory limits to prevent OOM

### Frontend
1. **Code Splitting**
   - MediaPipe loaded lazily
   - Color picker as separate chunk
   - Optimized bundle size

2. **Image Optimization**
   - Client-side compression before upload
   - Thumbnail generation for previews
   - Progressive image loading

## Monitoring & Analytics

### Error Tracking
- Sentry integration for backend error monitoring
- Frontend error boundary with reporting
- Custom error logging for critical paths

### Performance Monitoring
- API response time tracking
- Image processing duration metrics
- User interaction analytics

### Health Checks
- `/health` endpoint for service status
- Database connectivity checks
- Model loading verification

## Security Considerations

### API Security
- Rate limiting (10 requests/minute per IP)
- File size limits (8MB max)
- Content type validation
- CORS configuration

### Data Privacy
- No persistent storage of uploaded images
- Automatic cleanup of temporary files
- GDPR compliance headers
- Privacy policy integration

## Scaling Strategy

### Horizontal Scaling
1. **Load Balancing**
   - Multiple backend instances
   - Session affinity not required
   - Stateless design

2. **CDN Integration**
   - Static asset delivery
   - Global edge locations
   - Cache optimization

### Vertical Scaling
1. **Resource Optimization**
   - GPU acceleration (future)
   - Memory-efficient models
   - Async processing queues

## Cost Optimization

### Free Tier Limits
- **Vercel**: 100GB bandwidth, 1000 builds/month
- **Render**: 750 hours/month, 512MB RAM
- **Railway**: $5 credit, then usage-based

### Cost-Effective Architecture
1. Use free tiers for staging/development
2. Optimize image processing to reduce compute time
3. Implement smart caching to reduce API calls
4. Monitor usage patterns and scale accordingly

## Troubleshooting

### Common Issues
1. **Cold Start Delays**
   - Keep one instance warm with health checks
   - Optimize model loading time

2. **Memory Issues**
   - Monitor memory usage during image processing
   - Implement graceful degradation for large images

3. **CORS Errors**
   - Verify allowed origins configuration
   - Check environment-specific settings

### Debug Commands
```bash
# Check backend logs
render logs --tail -s your-service-name

# Test API locally
curl http://localhost:8000/health

# Check frontend build
npm run build && npm run preview
```