# Deployment instructions for GitHub Pages

## Prerequisites
1. Repository created at: https://github.com/gear-go/epof_app
2. Initialize this repository with the files in this directory

## Quick Deploy Commands

```bash
# Initialize git repository
git init

# Add all files
git add .

# Initial commit
git commit -m "Initial commit: RAREPol POC - Generador de Trayectorias EPOF"

# Add remote repository
git remote add origin https://github.com/gear-go/epof_app.git

# Push to main branch
git branch -M main
git push -u origin main

# Install dependencies
npm install

# Build for production
npm run build

# Deploy to GitHub Pages
npm run deploy
```

## Alternative: Manual GitHub Pages Setup

1. Go to https://github.com/gear-go/epof_app/settings
2. Navigate to "Pages" section
3. Select "Deploy from a branch"
4. Choose "gh-pages" branch
5. Click "Save"

Your site will be available at: `https://gear-go.github.io/epof_app/`

## Local Development

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

## Directory Structure After Setup

```
epof_app/
├── .git/
├── dist/                  # Built files (created after npm run build)
├── node_modules/          # Dependencies (created after npm install)
├── public/
│   ├── index.html
│   └── favicon.ico
├── src/
│   ├── components/
│   │   └── RareDiseasePOC.jsx
│   ├── App.jsx
│   ├── main.jsx
│   └── index.css
├── .gitignore
├── index.html
├── package.json
├── postcss.config.js
├── README.md
├── tailwind.config.js
└── vite.config.js
```

## Environment Variables (Optional)

Create a `.env.local` file for custom configuration:

```bash
VITE_ANTHROPIC_API_KEY=your_api_key_here
VITE_APP_TITLE=RAREPol POC
```

## Troubleshooting

- If deployment fails, check that `base: '/epof_app/'` is set correctly in `vite.config.js`
- Ensure the repository name matches the base path
- Check that GitHub Pages is enabled in repository settings
- Wait 5-10 minutes after deployment for changes to appear

## Security Note

The current implementation includes an API key in the frontend code for demonstration purposes only. In production:

1. Move API calls to a backend service
2. Use environment variables for sensitive data
3. Implement proper authentication
4. Add rate limiting and error handling
