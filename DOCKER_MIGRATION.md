# Docker Migration Guide

This guide helps you transition from the manual 4-terminal setup to the new containerized Docker environment.

## 🎯 Why Migrate to Docker?

### Before: The "4-Terminal Problem"
```bash
# Terminal 1
cd LiveKit-ai-translation/server
python main.py dev

# Terminal 2  
cd quranic-verse-display
python websocket-server.py

# Terminal 3
cd jama-admin-panel
npm start

# Terminal 4
cd quranic-verse-display
npm run dev
```

### After: One Command
```bash
make up
# or
docker-compose up -d
```

## 🚀 Migration Steps

### Step 1: Backup Your Current Setup

Before migrating, ensure your current manual setup is working:

1. **Backup your environment variables**
   ```bash
   # Save your current .env files
   cp LiveKit-ai-translation/server/.env backup-server.env
   cp jama-admin-panel/.env backup-admin.env
   ```

2. **Note your current configuration**
   - LiveKit API keys and secrets
   - Any custom settings or modifications
   - Port configurations

### Step 2: Stop All Manual Services

Stop all running services from your 4-terminal setup:
- Press `Ctrl+C` in each terminal window
- Ensure all processes are stopped

### Step 3: Set Up Docker Environment

1. **Create the root .env file**
   ```bash
   # From project root
   make setup
   ```

2. **Copy your credentials**
   Edit the new `.env` file with your existing credentials:
   ```bash
   LIVEKIT_API_KEY=your_existing_api_key
   LIVEKIT_API_SECRET=your_existing_secret
   NEXT_PUBLIC_LIVEKIT_URL=your_existing_livekit_url
   ```

### Step 4: Build and Start Docker Services

1. **Build all images**
   ```bash
   make build
   ```

2. **Start all services**
   ```bash
   make up
   ```

3. **Verify everything is working**
   ```bash
   make health
   ```

### Step 5: Test the Migration

1. **Access the admin panel**: http://localhost:8081
2. **Access the display**: http://localhost:8080
3. **Create a test room and verify translation flow**

## 🔧 Troubleshooting Migration Issues

### Issue: Services won't start
```bash
# Check if ports are in use
make status

# Check logs for errors
make logs

# Clean and rebuild if needed
make rebuild
```

### Issue: Environment variables not loading
```bash
# Verify .env file exists in project root
ls -la .env

# Check if variables are set correctly
cat .env

# Restart services
make restart
```

### Issue: LiveKit connection fails
```bash
# Check LiveKit credentials
grep LIVEKIT .env

# View LiveKit agent logs
docker-compose logs livekit-agent
```

## 📊 Service Mapping

| Manual Setup | Docker Service | Docker Port |
|--------------|----------------|-------------|
| `python main.py dev` | `livekit-agent` | Internal |
| `python websocket-server.py` | `websocket-server` | 8765:8765, 8766:8766 |
| Admin backend `npm start` | `admin-backend` | Internal:3001 |
| Admin frontend `npm run dev` | `admin-ui` | 8081:80 |
| Display `npm run dev` | `display-ui` | 8080:80 |
| LiveKit web `pnpm dev` | `livekit-web` | 3000:3000 |

## 🎛️ Development Workflow Changes

### Before (Manual)
```bash
# Start each service manually
# Make code changes
# Manually restart affected services
# Check logs in multiple terminals
```

### After (Docker)
```bash
# Development with hot reload
make dev

# View all logs in one place
make logs

# Restart everything easily
make restart

# Check system health
make health
```

## 🚀 Advanced Docker Usage

### Development Mode
```bash
# Start with hot reloading and volume mounts
make dev

# Stop development environment
make dev-down
```

### Production Mode
```bash
# Start optimized production build
make up

# View production logs
make logs
```

### Maintenance
```bash
# View container status
make status

# Clean up everything
make clean

# Rebuild from scratch
make rebuild
```

## 💡 Benefits of Docker Migration

### ✅ **Operational Benefits**
- **One-command startup**: `make up` replaces 4 terminals
- **Consistent environment**: Same setup across all machines
- **Easy deployment**: Ready for production deployment
- **Simplified debugging**: Centralized logging with `make logs`

### ✅ **Development Benefits**
- **Hot reloading**: Development mode with live code changes
- **Isolated services**: Each service runs in its own container
- **Easy cleanup**: `make clean` removes everything
- **Network isolation**: Services communicate through Docker network

### ✅ **Production Benefits**
- **Scalability**: Easy to scale individual services
- **Monitoring**: Built-in health checks and status monitoring
- **Security**: Services isolated from host system
- **Portability**: Runs the same on any Docker-enabled machine

## 🔄 Rollback Plan

If you need to rollback to manual setup:

1. **Stop Docker services**
   ```bash
   make down
   ```

2. **Restore your backup environment files**
   ```bash
   cp backup-server.env LiveKit-ai-translation/server/.env
   cp backup-admin.env jama-admin-panel/.env
   ```

3. **Start manual services** using the original 4-terminal method

## 🎉 You're Done!

Congratulations! You've successfully migrated from the 4-terminal setup to a modern, containerized environment. Your Jama Translation System is now:

- ✅ **Easier to manage** with single-command operations
- ✅ **More reliable** with consistent environments
- ✅ **Production-ready** with proper containerization
- ✅ **Developer-friendly** with hot reloading and centralized logs

Enjoy your streamlined workflow! 