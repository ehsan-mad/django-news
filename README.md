# Django News Portal

A Django-based news portal with breaking news functionality, categories, and Neon PostgreSQL integration.

## Features

- News articles with categories
- Breaking news banner system
- Optional breaking news images
- Admin interface for content management
- Responsive design with Bootstrap
- PostgreSQL database (Neon)

## Local Development Setup

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd news_portal
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # or
   source venv/bin/activate  # Linux/Mac
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   - Copy `.env.example` to `.env` (if you have one)
   - Or create `.env` file with your database URL and secret key
   
5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run development server**
   ```bash
   python manage.py runserver
   ```

## Production Deployment on Render

### Prerequisites
- GitHub repository with your code
- Render account (free tier available)
- Neon PostgreSQL database

### Step 1: Prepare your environment variables
Create these environment variables in Render:

```
DATABASE_URL=postgresql://neondb_owner:your_password@your-endpoint.aws.neon.tech/neondb?sslmode=require&options=endpoint%3Dyour-endpoint
SECRET_KEY=your-production-secret-key
DEBUG=False
ALLOWED_HOSTS=your-render-app.onrender.com
```

### Step 2: Deploy on Render

1. **Connect to Render**
   - Go to [render.com](https://render.com)
   - Sign up/Login with GitHub
   - Click "New +" → "Web Service"

2. **Configure the service**
   - Connect your GitHub repository
   - Choose the repository containing your Django project
   - Configure the following settings:

   **Basic Settings:**
   - Name: `news-portal` (or your preferred name)
   - Region: Choose closest to your users
   - Branch: `main` (or your default branch)

   **Build & Deploy:**
   - Build Command: `./build.sh`
   - Start Command: `gunicorn news_portal.wsgi:application`

3. **Environment Variables**
   Add the environment variables listed above in the "Environment" section

4. **Deploy**
   - Click "Create Web Service"
   - Render will build and deploy your application
   - Your app will be available at `https://your-app-name.onrender.com`

### Step 3: Post-deployment tasks

1. **Create superuser** (via Render Shell)
   - Go to your service dashboard
   - Click "Shell" tab
   - Run: `python manage.py createsuperuser`

2. **Access admin panel**
   - Visit: `https://your-app-name.onrender.com/admin/`
   - Login with superuser credentials

## Project Structure

```
news_portal/
├── manage.py
├── requirements.txt
├── build.sh                 # Render deployment script
├── .env                     # Environment variables (local)
├── news/                    # Main app
│   ├── models.py           # News and Category models
│   ├── views.py            # View functions
│   ├── admin.py            # Admin interface
│   ├── urls.py             # URL patterns
│   └── migrations/         # Database migrations
├── news_portal/            # Project settings
│   ├── settings.py         # Django settings
│   ├── urls.py             # Main URL configuration
│   └── wsgi.py             # WSGI application
├── templates/              # HTML templates
│   └── news/
│       └── base.html
└── static/                 # Static files (CSS, JS, images)
```

## Breaking News Feature

The portal includes a breaking news banner system:

1. **Admin Interface**: Mark articles as breaking news in the admin panel
2. **Custom Text**: Add custom breaking news text (optional)
3. **Images**: Toggle breaking news image display
4. **Multiple Articles**: All articles marked as breaking news will appear in the banner

## Database Schema

### Article Model
- `title`: Article headline
- `content`: Article body
- `category`: Foreign key to Category
- `image`: Optional article image
- `is_breaking_news`: Boolean flag for breaking news
- `breaking_news_text`: Custom breaking news text
- `show_breaking_image`: Boolean to show/hide image in breaking news banner
- `created_at`: Timestamp

### Category Model
- `name`: Category name
- `description`: Category description

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@host/db` |
| `SECRET_KEY` | Django secret key | `random-50-character-string` |
| `DEBUG` | Debug mode (False in production) | `False` |
| `ALLOWED_HOSTS` | Comma-separated list of allowed hosts | `yourapp.onrender.com` |

## Troubleshooting

### Common Issues

1. **Static files not loading**
   - Ensure `STATIC_ROOT` is set correctly in `settings.py`
   - Run `python manage.py collectstatic` during deployment

2. **Database connection errors**
   - Verify your `DATABASE_URL` format
   - Ensure Neon database is accessible
   - Check if `endpoint` parameter is included in the URL

3. **502 Bad Gateway on Render**
   - Check build logs for errors
   - Verify `gunicorn` is installed
   - Ensure `wsgi.py` path is correct in start command

### Getting Help

- Check Render build and deploy logs
- Review Django error logs in Render dashboard
- Ensure all dependencies are in `requirements.txt`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

[Add your license information here]
