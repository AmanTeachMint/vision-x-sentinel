// PM2 Ecosystem Configuration for Vision X Sentinel
module.exports = {
  apps: [
    {
      name: 'vision-backend',
      script: 'run.py',
      cwd: '/home/aman_intern_teachmint_com/vision-x-sentinel/backend',
      interpreter: '/home/aman_intern_teachmint_com/vision-x-sentinel/backend/venv/bin/python',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '1G',
      env: {
        FLASK_PORT: 5000,
        CORS_ORIGIN: 'http://10.201.0.108:5173',
        MONGO_URI: 'mongodb://localhost:27017/',
        MONGO_DB_NAME: 'vision_x_sentinel'
      },
      error_file: '/home/aman_intern_teachmint_com/vision-x-sentinel/logs/backend-error.log',
      out_file: '/home/aman_intern_teachmint_com/vision-x-sentinel/logs/backend-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
    },
    {
      name: 'vision-frontend',
      script: 'npm',
      cwd: '/home/aman_intern_teachmint_com/vision-x-sentinel/frontend',
      args: 'run dev',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '500M',
      env: {
        NODE_ENV: 'development',
        PORT: 5173
      },
      error_file: '/home/aman_intern_teachmint_com/vision-x-sentinel/logs/frontend-error.log',
      out_file: '/home/aman_intern_teachmint_com/vision-x-sentinel/logs/frontend-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
    }
  ]
};
