# Vizart AI - Virtual Try-On/Off Application

An AI-powered web application for virtual try-on and try-off of clothing items, built with FastAPI backend and Next.js frontend.

## Features

### Virtual Try-On
- Upload a model image and garment image
- AI-powered garment warping and fitting
- Realistic pose transfer
- Support for upper, lower, and full-body garments

### Virtual Try-Off
- Upload a model image with garments
- AI-powered garment extraction and segmentation
- Classification of garment types (Upper, Lower, Full)
- Export extracted garments with transparent backgrounds

## Technology Stack

### Backend (FastAPI)
- **FastAPI**: Modern Python web framework
- **OpenCV**: Computer vision operations
- **MediaPipe**: Human pose detection
- **Rembg**: Background removal
- **PyTorch**: Deep learning framework
- **PostgreSQL**: Database for job management
- **Redis**: Job queue and caching
- **Docker**: Containerization

### Frontend (Next.js)
- **Next.js 14**: React framework with App Router
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Utility-first CSS framework
- **React Dropzone**: File upload handling
- **Lucide React**: Icon library

## Quick Start

### Prerequisites

- Node.js 18+ and npm
- Python 3.11+
- PostgreSQL 13+
- Redis
- CUDA-compatible GPU (optional, for faster processing)

### Backend Setup

1. **Clone and navigate to backend directory:**
```bash
cd backend
```

2. **Run setup script:**
```bash
python setup.py
```

3. **Configure environment:**
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. **Start the backend server:**
```bash
uvicorn main:app --reload
```

### Frontend Setup

1. **Navigate to frontend directory:**
```bash
cd frontend
```

2. **Install dependencies:**
```bash
npm install
```

3. **Start the development server:**
```bash
npm run dev
```

### Docker Setup (Recommended)

1. **Start all services with Docker Compose:**
```bash
cd backend
docker-compose up --build
```

2. **Access the application:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## API Documentation

### Try-On Endpoint
```http
POST /api/v1/processing/try-on
Content-Type: multipart/form-data

model_image: File
garment_image: File
options: JSON string (optional)
```

### Try-Off Endpoint
```http
POST /api/v1/processing/try-off
Content-Type: multipart/form-data

model_image: File
options: JSON string (optional)
```

### Job Status Endpoint
```http
GET /api/v1/jobs/{job_id}
```

## Configuration

### Environment Variables

#### Backend (.env)
```bash
# Application
DEBUG=true
SECRET_KEY=your-secret-key

# Database
DATABASE_URL=postgresql://user:pass@localhost/vizart_db

# AI/ML
ENABLE_GPU=true
MODEL_DEVICE=cuda  # or cpu
MAX_CONCURRENT_JOBS=4
```

#### Frontend (.env.local)
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Architecture

### Processing Pipeline

1. **Upload**: Images are uploaded and validated
2. **Queue**: Jobs are placed in Redis queue
3. **AI Processing**:
   - Pose detection (MediaPipe)
   - Background removal (Rembg)
   - Garment warping/extraction
   - Image blending/composition
4. **Results**: Processed images are stored and served

### AI Models

- **MediaPipe Pose**: Human pose estimation
- **U2Net**: Background removal and segmentation
- **Custom Models**: Garment-specific processing (under development)

## Development

### Adding New AI Models

1. **Model Definition**: Add model configuration in `app/workers/ai_processor.py`
2. **Processing Pipeline**: Implement processing logic in relevant methods
3. **API Integration**: Update endpoints if needed
4. **Frontend Integration**: Add UI components for new features

### Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

### Monitoring

- **Structured Logging**: JSON-formatted logs for production
- **Health Checks**: `/health` endpoint for monitoring
- **Sentry Integration**: Optional error tracking

## Performance Considerations

- **GPU Acceleration**: CUDA support for faster AI processing
- **Job Queuing**: Redis-based job management for scalability
- **Caching**: Redis caching for frequently accessed data
- **Async Processing**: Background task processing

## Limitations

- **Current Stage**: MVP with basic AI functionality
- **Processing Time**: 30-120 seconds per request
- **GPU Requirements**: Recommended for production use
- **Model Quality**: Under development and improvement

## Future Enhancements

- **Advanced AI Models**: More sophisticated try-on/off algorithms
- **Real-time Processing**: WebSocket-based progress updates
- **Cloud Deployment**: Scalable cloud infrastructure
- **3D Support**: 3D garment models and AR integration
- **Style Transfer**: AI-powered fashion style recommendations

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
- Create an issue on GitHub
- Check API documentation at `/docs`
- Review configuration requirements

---

**Note**: This is an MVP implementation focused on demonstrating the technical architecture. The AI models are basic implementations and would require further training and optimization for production use.