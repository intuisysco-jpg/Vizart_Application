# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Architecture Overview

This is a full-stack AI-powered virtual try-on/try-off application with two main components:

### Backend (FastAPI)
- **FastAPI App**: Main application in `main.py` with auto-generated API docs at `/docs`
- **AI Processing**: Core AI logic in `app/workers/ai_processor.py` using MediaPipe (pose detection) and RemBG (background removal)
- **Job Management**: Asynchronous job processing stored in PostgreSQL jobs table, managed through `app/services/job_service.py`
- **File Handling**: Images processed via `app/services/image_service.py` with validation in `app/utils/validation.py`
- **Background Tasks**: Processing jobs run in background using BackgroundTasks pattern

### Frontend (Next.js)
- **App Router**: Modern Next.js 14 with TypeScript and Tailwind CSS
- **File Upload**: Dropzone interface in `src/components/ImageUpload.tsx` with drag-and-drop functionality
- **Real-time Processing**: Progress tracking via `src/hooks/useProcessing.ts`
- **Job Integration**: API client in `src/lib/api.ts` with polling for job status updates

## Key Technical Patterns

### AI Processing Pipeline
1. Jobs are created and stored in PostgreSQL via `JobService.create_job()`
2. BackgroundTasks trigger AI processing in `ProcessingService._process_try_on/off_job()`
3. Progress updates use callbacks to update job status in real-time
4. Results are stored as JSON in `job.result_data` and served from `static/results/`

### API Design
- RESTful endpoints under `/api/v1/` namespace
- `ProcessingService` handles both try-on (requires 2 files) and try-off (single file) operations
- `JobService` provides job status tracking and result retrieval
- All file uploads validated and saved with UUID-based filenames

## Development Commands

### Backend
```bash
cd backend

# Setup (creates directories, installs dependencies, creates .env)
python setup.py

# Run development server
uvicorn main:app --reload

# Run tests
pytest
pytest tests/test_specific_file.py  # Run specific test
pytest tests/test_file.py::test_function  # Run specific test function

# Run with coverage
pytest --cov=app

# Install development requirements
pip install -r requirements-dev.txt
```

### Frontend
```bash
cd frontend

# Install dependencies
npm install

# Development server
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Lint code
npm run lint
```

### Docker (Recommended)
```bash
cd backend

# Start all services
docker-compose up --build

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Key Configuration Files

### Backend
- `.env`: Main configuration (copy from `.env.example`)
- `app/core/config.py`: Settings with environment variable overrides
- `requirements.txt`: Production dependencies
- `requirements-dev.txt`: Development dependencies

### Frontend
- `src/lib/api.ts`: API client configuration
- `.env.local`: Frontend environment variables (copy from `.env.local.example`)

## API Endpoints

### Core Processing
- `POST /api/v1/processing/try-on`: Submit try-on job (model + garment images)
- `POST /api/v1/processing/try-off`: Submit try-off job (model image only)
- `GET /api/v1/jobs/{job_id}`: Check job status
- `GET /api/v1/jobs/{job_id}/result`: Get completed job results

### File Handling
- `POST /api/v1/upload`: Upload image (currently handled via processing endpoints)
- `GET /api/v1/images/uploads/{filename}`: Serve uploaded images
- `GET /api/v1/images/results/{filename}`: Serve result images

## AI Models

### Current Implementation
- **MediaPipe Pose**: Human pose detection for garment alignment
- **U2Net (RemBG)**: Background removal and segmentation
- **OpenCV**: Image processing operations

### Model Management
- Models cached in `models/` directory
- GPU support via `MODEL_DEVICE` environment variable (cuda/cpu)
- Custom AI processor in `app/workers/ai_processor.py`

## File Storage

- **Uploads**: `static/uploads/` - original uploaded files
- **Results**: `static/results/` - processed images with UUID-based filenames
- **Models**: `models/` - AI model weights (empty in setup)

## Error Handling

- Structured logging with `structlog` in JSON format for production
- Global exception handler in `main.py` for centralized error responses
- Input validation using Pydantic models and custom validators
- Graceful degradation for AI model failures

## Database Schema

### Job Table
- `id`: UUID primary key
- `status`: PENDING/PROCESSING/COMPLETED/FAILED/CANCELLED
- `job_type`: 'try-on' or 'try-off'
- `progress`: 0-100 percentage
- `model_image_path`/`garment_image_path`: file paths
- `result_data`: JSON storage for processed results
- `processing_time`: seconds to complete job

## Performance Considerations

- GPU acceleration for AI processing (set ENABLE_GPU=true)
- Background task processing to avoid blocking API calls
- Redis caching configuration ready (not currently used)
- File uploads limited to 10MB by default