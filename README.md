# Bayan Translation Platform

A complete real-time translation platform for mosques using LiveKit Cloud, designed to provide live Arabic-to-multiple-language translation services during religious gatherings.

## 🌟 Features

- **Real-time Translation**: Live Arabic transcription and translation using OpenAI and Speechmatics
- **Multi-language Support**: Support for Dutch, English, Spanish, French, German, Urdu, Turkish, Indonesian, and Malay
- **Admin Panel**: Complete dashboard for mosque administrators to manage rooms and sessions
- **LiveKit Cloud Integration**: Seamless integration with LiveKit Cloud for audio streaming
- **Session Management**: Start/stop recording sessions with transcript logging
- **Real-time Monitoring**: Live monitoring of participants and translations
- **Database Logging**: Automatic saving of transcripts to Supabase database
- **Multi-tenant**: Support for multiple mosques with proper isolation

## 🏗️ Architecture

```
┌─────────────────────┐    ┌──────────────────────┐    ┌─────────────────────┐
│   Admin Panel       │    │   Supabase Backend   │    │  LiveKit Cloud      │
│   (React/TypeScript)│◄──►│   (PostgreSQL +      │◄──►│  (Audio Streaming)  │
│                     │    │    Edge Functions)   │    │                     │
└─────────────────────┘    └──────────────────────┘    └─────────────────────┘
         │                           │                           │
         │                           │                           │
         ▼                           ▼                           ▼
┌─────────────────────┐    ┌──────────────────────┐    ┌─────────────────────┐
│  Translation Agent  │    │   WebSocket Logger   │    │  Display Server     │
│  (Python/LLM)       │    │   (Real-time sync)   │    │  (Public Display)   │
└─────────────────────┘    └──────────────────────┘    └─────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- LiveKit Cloud account
- Supabase account
- OpenAI API key
- Speechmatics API key

### 1. Clone the Repository

```bash
git clone <repository-url>
cd Jama-Translator
```

### 2. Configure Environment Variables

Copy the environment template:

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```bash
# LiveKit Configuration
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=your_api_key
LIVEKIT_API_SECRET=your_api_secret

# External APIs
SPEECHMATICS_API_KEY=your_speechmatics_key
OPENAI_API_KEY=your_openai_key

# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
WEBSOCKET_LOGGER_URL=https://your-project.supabase.co
```

### 3. Start the Platform

```bash
# Build and start all services
docker-compose up --build

# Or start in detached mode
docker-compose up -d
```

### 4. Access the Services

- **Admin Panel**: http://localhost:3000
- **Display Server**: http://localhost:8080
- **Database**: postgresql://postgres:postgres@localhost:5432/bayan_db

## 📁 Project Structure

```
Jama-Translator/
├── bayan-platform-admin/          # Admin panel (React/TypeScript)
│   ├── src/
│   │   ├── components/             # React components
│   │   ├── pages/                  # Page components
│   │   ├── hooks/                  # Custom hooks
│   │   └── integrations/           # Supabase integration
│   ├── supabase/                   # Supabase configuration
│   │   ├── functions/              # Edge functions
│   │   └── migrations/             # Database migrations
│   ├── Dockerfile                  # Docker configuration
│   └── nginx.conf                  # Nginx configuration
├── LiveKit-ai-translation/
│   └── server/                     # Python backend
│       ├── main.py                 # Main translation agent
│       ├── supabase_service.py     # Supabase integration
│       ├── web_server.py           # Display server
│       ├── requirements.txt        # Python dependencies
│       └── Dockerfile              # Docker configuration
├── docker-compose.yml              # Docker Compose configuration
├── init-db.sql                     # Database initialization
└── README.md                       # This file
```

## 🔧 Configuration

### Database Setup

The platform uses Supabase for the database. Run the migrations:

```bash
cd bayan-platform-admin
npx supabase db push
```

### LiveKit Cloud Setup

1. Create a LiveKit Cloud account
2. Create a new project
3. Copy the API keys and WebSocket URL
4. Add them to your `.env` file

### Admin Panel Configuration

The admin panel is configured through environment variables:

```typescript
// bayan-platform-admin/src/integrations/supabase/client.ts
const SUPABASE_URL = process.env.VITE_SUPABASE_URL;
const SUPABASE_ANON_KEY = process.env.VITE_SUPABASE_ANON_KEY;
```

## 🔄 Usage

### 1. Admin Panel

1. Access the admin panel at `http://localhost:3000`
2. Create a new room with transcription and translation languages
3. Start a recording session
4. Monitor live transcriptions and translations

### 2. Translation Agent

The Python backend automatically:
- Connects to LiveKit rooms
- Transcribes Arabic audio using Speechmatics
- Translates to target languages using OpenAI
- Saves transcripts to Supabase database
- Sends real-time updates to the admin panel

### 3. Display Server

The display server provides:
- Public display interface for translations
- Real-time updates via WebSocket
- Clean, readable interface for congregation

## 🛠️ Development

### Running in Development Mode

```bash
# Start admin panel in development
cd bayan-platform-admin
npm run dev

# Start Python backend
cd LiveKit-ai-translation/server
python main.py

# Start display server
python web_server.py
```

### Database Migrations

```bash
cd bayan-platform-admin
npx supabase migration new your_migration_name
npx supabase db push
```

### Adding New Languages

1. Update the `languages` object in `main.py`
2. Add language support in the admin panel
3. Update the database schema if needed

## 📊 Monitoring

### Health Checks

- **Admin Panel**: Check the dashboard for connection status
- **Translation Agent**: Monitor logs for processing status
- **Database**: Check Supabase dashboard for active sessions

### Logs

```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f bayan-livekit-backend
docker-compose logs -f bayan-admin-panel
```

## 🔒 Security

- All API keys are stored in environment variables
- Database access is protected with RLS (Row Level Security)
- Authentication is handled through Supabase Auth
- WebSocket connections are secured with proper CORS headers

## 📈 Scaling

### Production Deployment

1. Use a production-grade database (PostgreSQL)
2. Configure proper load balancing
3. Set up monitoring and alerting
4. Use environment-specific configurations

### Performance Optimization

- Enable Redis for caching
- Use CDN for static assets
- Optimize database queries
- Monitor LiveKit usage

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting guide
2. Review the logs
3. Open an issue on GitHub
4. Contact the development team

## 🔧 Troubleshooting

### Common Issues

1. **LiveKit Connection Failed**
   - Check API keys and URL
   - Verify room names match between systems

2. **Translation Not Working**
   - Verify OpenAI API key
   - Check Speechmatics configuration
   - Ensure proper language codes

3. **Database Connection Issues**
   - Check Supabase credentials
   - Verify database migrations are applied
   - Check network connectivity

### Debug Mode

Enable debug logging:

```bash
# In Python backend
export PYTHONPATH=/app
export DEBUG=1
python main.py

# In admin panel
export NODE_ENV=development
npm run dev
```

## 📋 Changelog

### v1.0.0
- Initial release with full LiveKit Cloud integration
- Complete admin panel with session management
- Real-time translation with multiple language support
- Docker containerization
- Supabase database integration #   J a m a - T r a n s l a t o r 
 
 
