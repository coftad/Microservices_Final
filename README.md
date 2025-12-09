# Microservices URL Shortener with Real-Time Analytics

A production-ready microservices application featuring URL shortening, user authentication, and real-time analytics powered by Kafka event streaming.

## Architecture

This application demonstrates a complete microservices architecture with:

- **3 Core Services**: Authentication, URL Shortening, Analytics
- **Event-Driven Architecture**: Kafka for real-time event streaming
- **Containerized Deployment**: Docker Compose orchestration
- **Cloud Deployment**: Running on DigitalOcean
- **Monitoring**: Real-time endpoint performance metrics

### System Diagram

```
┌─────────────┐
│   Frontend  │ (Nginx)
│  (Port 80)  │
└──────┬──────┘
       │
       ├──────────────┬──────────────┬──────────────┐
       │              │              │              │
┌──────▼──────┐ ┌────▼─────┐ ┌──────▼───────┐ ┌───▼────────┐
│Auth Service │ │Shortener │ │  Analytics   │ │ PostgreSQL │
│  (Port 8001)│ │(Port8000)│ │ (Port 8002)  │ │ (Port 5432)│
└──────┬──────┘ └────┬─────┘ └──────▲───────┘ └────────────┘
       │             │               │
       │             │               │
       └─────────────┴───────────────┘
                     │
              ┌──────▼──────┐
              │    Kafka    │
              │  (Port 9092)│
              │             │
              │  Topics:    │
              │  - url_hits │
              │  - endpoint │
              │    _metrics │
              └─────────────┘
```

## Features

### Authentication Service (Port 8001)
- User registration and login
- JWT token-based authentication
- Secure password hashing with bcrypt
- User profile management

### URL Shortener Service (Port 8000)
- Create shortened URLs (authenticated users only)
- Retrieve user's URLs
- Redirect short codes to original URLs
- Track click statistics via Kafka

### Analytics Service (Port 8002)
- Real-time Kafka consumer for URL hits and endpoint metrics
- Administrative dashboard with endpoint performance statistics
- Metrics include:
  - Total requests per endpoint
  - Average response latency
  - Service-level breakdown

### Frontend
- User-friendly web interface
- Dashboard for URL management
- Admin panel for performance monitoring
- Real-time statistics updates

## Installation & Deployment

### Prerequisites
- Docker & Docker Compose
- Git
- A cloud VM (DigitalOcean, AWS, etc.) with ports 80, 8000-8002, 5432, 9092, 29092 open

### Local Development

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd Microservices_Final
```

2. **Set environment variables** (optional)
```bash
# Create .env file
cat > .env << EOF
DB_PASSWORD=your_secure_password
JWT_SECRET_KEY=your_jwt_secret_key
DATABASE_URL=postgresql://postgres:password@db:5432/main
AUTH_DATABASE_URL=postgresql://postgres:password@db:5432/main
EOF
```

3. **Build and run services**
```bash
docker-compose up -d --build
```

4. **Verify all services are running**
```bash
docker-compose ps
```

5. **Check Kafka topics were created**
```bash
docker exec -it kafka kafka-topics --list --bootstrap-server kafka:9092
```

You should see:
- `url_hits`
- `endpoint_metrics`
- `__consumer_offsets`

6. **Access the application**
- Frontend: http://localhost
- Auth API: http://localhost:8001
- Shortener API: http://localhost:8000
- Analytics API: http://localhost:8002

### Cloud Deployment (DigitalOcean)

1. **Create a Droplet**
   - Ubuntu 22.04 LTS
   - Minimum 2GB RAM, 2 vCPUs
   - Enable all required ports in firewall

2. **SSH into your server**
```bash
ssh root@your_server_ip
```

3. **Install Docker**
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
```

4. **Install Docker Compose**
```bash
apt install docker-compose -y
```

5. **Clone and deploy**
```bash
git clone <your-repo-url>
cd Microservices_Final

# Update IP addresses in docker-compose.yml
sed -i 's/159.223.136.60/YOUR_SERVER_IP/g' docker-compose.yml
sed -i 's/159.223.136.60/YOUR_SERVER_IP/g' frontend/app.js
sed -i 's/159.223.136.60/YOUR_SERVER_IP/g' shortener_service/app/main.py

# Deploy
docker-compose up -d --build
```

6. **Monitor logs**
```bash
docker-compose logs -f
```

## API Documentation

### Authentication Service (Port 8001)

#### Register User
```http
POST /auth/register
Content-Type: application/json

{
  "email": "john@example.com",
  "password": "securepassword123"
}
```

**Response:**
```json
{
  "id": 1,
  "email": "john@example.com"
}
```

#### Login
```http
POST /auth/login
Content-Type: application/json

{
  "username": "john@example.com",
  "password": "securepassword123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### Get Current User
```http
GET /auth/me
Authorization: Bearer <token>
```

**Response:**
```json
{
  "id": 1,
  "username": "john@example.com",
}
```

### URL Shortener Service (Port 8000)

#### Create Short URL
```http
POST /shorten
Authorization: Bearer <token>
Content-Type: application/json

{
  "original_url": "https://www.example.com/very/long/url"
}
```

**Response:**
```json
{
  "short_url": "http://159.223.136.60:8000/abc123",
  "created_at": "2025-12-09T00:00:00Z"
}
```

#### Redirect Short URL
```http
GET /{short_code}
Authorization: Bearer <token>
```

**Response:**
```json
[
  {
    "original_url": "https://www.example.com/very/long/url",
  }
]
```

**Response:** 307 Redirect to original URL

**Side Effects:**
- Increments click counter
- Publishes event to `url_hits` Kafka topic
- Tracks user agent and timestamp

### Analytics Service (Port 8002)

#### Get Endpoint Statistics
```http
GET /endpoint-stats?hours=24
```

**Query Parameters:**
- `hours` (optional): Number of hours to look back (1-168, default: 24)

**Response:**
```json
[
  {
    "service": "shortener_service",
    "endpoint": "/shorten",
    "total_requests": 150,
    "avg_latency_ms": 45.23,
    "success_rate": 98.67
  },
  {
    "service": "auth_service",
    "endpoint": "/auth/login",
    "total_requests": 89,
    "avg_latency_ms": 123.45,
    "success_rate": 100.0
  }
]
```

##  Use Cases

### Use Case 1: User Creates and Shares a Short URL

1. **User registers**
```bash
curl -X POST http://localhost:8001/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","email":"alice@example.com","password":"pass123"}'
```

2. **User logs in**
```bash
TOKEN=$(curl -X POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"pass123"}' | jq -r '.access_token')
```

3. **User creates short URL**
```bash
curl -X POST http://localhost:8000/shorten \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"original_url":"https://github.com/my-awesome-project"}'
```

4. **Share short URL with others**
```
http://your-server-ip:8000/abc123
```

5. **Track clicks in real-time**
```bash
curl -X GET http://localhost:8000/urls \
  -H "Authorization: Bearer $TOKEN"
```

### Use Case 2: Administrator Monitors Service Performance

1. **Access admin dashboard**
```
http://your-server-ip/admin.html
```

2. **View endpoint statistics**
```bash
curl http://localhost:8002/endpoint-stats?hours=24
```

3. **Analyze metrics**
   - Identify slow endpoints (high avg_latency_ms)
   - Find failing endpoints (low success_rate)
   - Monitor request volume per service

##  Monitoring & Troubleshooting

### View Service Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f analytics_service
docker-compose logs -f kafka
```

### Check Kafka Topics
```bash
# List topics
docker exec -it kafka kafka-topics --list --bootstrap-server kafka:9092

# View messages in topic
docker exec -it kafka kafka-console-consumer \
  --bootstrap-server kafka:9092 \
  --topic url_hits \
  --from-beginning
```

### Database Access
```bash
# Connect to PostgreSQL
docker exec -it db psql -U postgres -d main

# View tables
\dt

# Query URL clicks
SELECT * FROM url_clicks ORDER BY timestamp DESC LIMIT 10;

# Query endpoint metrics
SELECT * FROM endpoint_metrics ORDER BY timestamp DESC LIMIT 10;
```

### Health Checks
```bash
# Check all services
curl http://localhost:8001/
curl http://localhost:8000/
curl http://localhost:8002/

# Check Kafka
docker exec -it kafka kafka-broker-api-versions --bootstrap-server kafka:9092
```

## Technology Stack

| Component | Technology |
|-----------|------------|
| **Backend Services** | Python 3.11, FastAPI |
| **Authentication** | JWT (PyJWT), Bcrypt |
| **Database** | PostgreSQL 15 |
| **ORM** | SQLAlchemy |
| **Message Broker** | Apache Kafka 7.5.0 |
| **Event Processing** | Aiokafka (async) |
| **Containerization** | Docker, Docker Compose |
| **Frontend** | HTML, CSS, JavaScript (Vanilla) |
| **Web Server** | Nginx (Alpine) |
| **Coordination** | Apache Zookeeper 7.5.0 |

## Project Structure

## Project Structure

```
Microservices_Final/
├── auth_service/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py          # FastAPI app, auth endpoints
│   │   ├── models.py        # User model
│   │   ├── database.py      # DB connection
│   │   └── kafka_producer.py
│   ├── Dockerfile
│   └── requirements.txt
├── shortener_service/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py          # URL shortening logic
│   │   ├── models.py        # URL model
│   │   ├── database.py
│   │   └── kafka_producer.py
│   ├── Dockerfile
│   └── requirements.txt
├── analytics_service/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py          # Analytics API
│   │   ├── models.py        # Metrics models
│   │   ├── database.py
│   │   └── consumer.py # Kafka event consumer
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── index.html           # App logic & looks
│   ├── Dockerfile           
├── docker-compose.yml       # Service orchestration
└── README.md                # This file
```

## Security Considerations

- ✅ JWT tokens expire after 30 minutes
- ✅ Passwords hashed with bcrypt
- ✅ CORS configured for cross-origin requests
- ✅ SQL injection prevention via SQLAlchemy ORM
- ⚠️ For production: Use environment secrets, HTTPS, rate limiting

## Future Enhancements

- [ ] Kubernetes orchestration
- [ ] Redis caching layer
- [ ] Custom domain support for short URLs
- [ ] URL expiration dates
- [ ] QR code generation
- [ ] A/B testing support
- [ ] Grafana/Prometheus monitoring
- [ ] Rate limiting per user
- [ ] Email notifications
- [ ] Machine learning for fraud detection

## License

This project is created for educational purposes as part of a microservices architecture course.

## Contributors

- Your Name (@coftad)

## Acknowledgments

- FastAPI for the excellent async framework
- Apache Kafka for reliable event streaming
- Docker for simplified deployment

---

**Live Demo:** http://159.223.136.60 (Replace with your server IP)
