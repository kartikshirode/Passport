# Passport Photo WebApp — Production Ready

A complete React + FastAPI web application that processes user photos into Indian passport-sized photos (51×51 mm) with face detection, background removal/replacement, and A4 printable sheet generation.

## Featuresg

- **Smart Photo Processing**: Automatic face detection and centering using OpenCV and MediaPipe
- **Background Removal**: High-quality segmentation using U²-Net via rembg library
- **Multiple Background Options**: White, blue, red, or custom colors
- **Print Ready Output**: 600×600 px at 300 DPI for perfect passport compliance
- **A4 Sheet Generation**: Multiple passport photos arranged on A4 for bulk printing
- **Client-Side Optimization**: MediaPipe face detection reduces server load
- **Production Ready**: Dockerized backend, Vercel-ready frontend

## Tech Stack

- **Frontend**: React 18 + Vite + TailwindCSS + MediaPipe
- **Backend**: FastAPI + OpenCV + rembg (U²-Net) + Pillow
- **Processing**: ONNX optimization for faster CPU inference
- **Deployment**: Vercel (Frontend) + Render/Railway (Backend)

## Quick Start

### Backend Setup
```bash
cd backend
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate

pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

## Project Structure

```
passport-photo-app/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── requirements.txt        # Python dependencies
│   ├── Dockerfile             # Production container
│   └── utils/
│       ├── process_photo.py   # Core photo processing
│       ├── a4_generator.py    # A4 sheet creation
│       └── convert_u2net_to_onnx.py  # ONNX optimization
├── frontend/
│   ├── src/
│   │   ├── App.jsx           # Main application
│   │   ├── main.jsx          # React entry point
│   │   ├── api.js            # API client
│   │   ├── styles.css        # Global styles
│   │   └── components/
│   │       └── ImageUploader.jsx  # Upload component
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── index.html
├── .github/
│   └── workflows/
│       └── ci.yml            # GitHub Actions
└── README.md
```

## API Endpoints

- `GET /health` - Health check
- `POST /process` - Process single image
  - Parameters: `file`, `bg_color`, `make_a4`
  - Returns: Base64 encoded image or PDF

## Deployment

### Frontend (Vercel)
1. Connect GitHub repository
2. Set build command: `npm run build`
3. Set output directory: `dist`
4. Deploy automatically on push

### Backend (Render/Railway)
1. Connect GitHub repository
2. Use Dockerfile or set start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
3. Set environment variables as needed

## Performance Optimization

- **ONNX Conversion**: Convert U²-Net to ONNX for 2-3x faster CPU inference
- **Client-Side Processing**: MediaPipe face detection reduces bandwidth
- **Memory Optimization**: Stream processing without disk writes
- **Caching**: Reuse processed masks for different background colors

## Privacy & Security

- **Transient Processing**: Images processed in memory, not stored
- **CORS Configuration**: Secure cross-origin requests
- **Rate Limiting**: Built-in protection against abuse
- **Content Validation**: Image format and size validation

## Testing

Run the test suite with sample images:
```bash
# Backend tests
cd backend
python -m pytest tests/

# Frontend tests
cd frontend
npm test
```

## License

MIT License - see LICENSE file for details

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## Support

For issues and questions, please open a GitHub issue or contact the maintainers.