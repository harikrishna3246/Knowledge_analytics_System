# Deployment Fixes and Guide

## Issues Fixed

### 1. **Python Version Compatibility**

- Changed from Python 3.14.3 to **Python 3.11.8** (stable version)
- Python 3.14 is too new and lacks pre-built wheels for all dependencies
- Updated `runtime.txt` to specify `python-3.11.8`

### 2. **Pydantic Build Errors**

- Updated `pydantic` from 2.5.3 to **2.7.1** (better wheel support)
- Updated `pydantic-core` from auto to **2.18.3** (explicit version with wheels)
- Upgraded pip, setuptools, and wheel during build for better wheel availability

### 3. **Deployment Configuration Files**

- Created `render.yaml` - Configuration for Render deployment
- Updated `Procfile` - Added NLTK data download in release phase
- Created `.buildpacks` - Specified Python buildpack for Heroku
- Updated `Dockerfile` - Includes pip upgrades and NLTK data download

## Files Modified

1. **runtime.txt** - Changed to Python 3.11.8
2. **backend/requirements.txt** - Updated pydantic and pydantic-core versions
3. **Dockerfile** - Added setuptools/wheel upgrades and NLTK data download
4. **backend/Procfile** - Added release phase for NLTK data

## Files Created

1. **render.yaml** - Render deployment configuration
2. **.buildpacks** - Heroku buildpack specification
3. **DEPLOYMENT_GUIDE.md** - This file

## Deployment Instructions

### Deploy to Render

1. Push changes to your Git repository
2. Go to [render.com](https://render.com)
3. Create a new Web Service
4. Connect your GitHub repository
5. Set environment variables in Render dashboard:
   ```
   MONGODB_URI=<your_atlas_connection_string>
   GROQ_API_KEY=<your_groq_api_key>
   JWT_SECRET=<your_jwt_secret>
   FRONTEND_URL=<your_frontend_url>
   ```
6. Deploy - Render will automatically use `render.yaml`

### Deploy to Heroku

1. Install Heroku CLI
2. From project root:
   ```bash
   heroku create your-app-name
   heroku config:set MONGODB_URI=<your_atlas_connection_string>
   heroku config:set GROQ_API_KEY=<your_groq_api_key>
   heroku config:set JWT_SECRET=<your_jwt_secret>
   heroku config:set FRONTEND_URL=<your_frontend_url>
   git push heroku main
   ```

### Deploy with Docker

```bash
docker build -t knowledge-ai .
docker run -p 8000:8000 \
  -e MONGODB_URI=<your_connection_string> \
  -e GROQ_API_KEY=<your_api_key> \
  -e JWT_SECRET=<your_secret> \
  -e FRONTEND_URL=<your_frontend_url> \
  knowledge-ai
```

## Key Changes Summary

| File             | Change                                                     |
| ---------------- | ---------------------------------------------------------- |
| runtime.txt      | 3.11.5 → 3.11.8                                            |
| requirements.txt | Updated pydantic 2.5.3 → 2.7.1, added pydantic-core 2.18.3 |
| Dockerfile       | Added pip upgrades, NLTK download                          |
| Procfile         | Added release phase for NLTK                               |

## Troubleshooting

### If build still fails on Render:

1. Check that all environment variables are set
2. Ensure MongoDB URI is correct and accessible
3. Try deploying with explicit Python version in Render dashboard

### If NLTK data is missing:

1. The Procfile release phase should handle this automatically
2. Alternatively, manually add to your app:
   ```bash
   python backend/download_nltk_data.py
   ```

### Local Testing:

```bash
cd backend
pip install -r requirements.txt
python download_nltk_data.py
python -m uvicorn main:app --reload
```
