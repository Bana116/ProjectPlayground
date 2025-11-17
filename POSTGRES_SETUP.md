# PostgreSQL Setup for Render

## ✅ Code Migration Complete

Your app now supports both PostgreSQL (for Render) and SQLite (for local development).

## 🚀 Setting Up PostgreSQL on Render

### Step 1: Create PostgreSQL Database on Render

1. Go to your Render dashboard: https://dashboard.render.com
2. Click **"New +"** → **"PostgreSQL"**
3. Configure:
   - **Name**: `projectplayground-db` (or any name you prefer)
   - **Database**: `matcher` (or any name)
   - **User**: Auto-generated
   - **Region**: Same as your web service
   - **Plan**: Free tier is fine to start
4. Click **"Create Database"**

### Step 2: Link Database to Your Web Service

1. Go to your web service settings
2. Under **"Environment"**, find **"Environment Variables"**
3. Render should automatically add `DATABASE_URL` if you linked the database
   - If not, manually add it:
   - **Key**: `DATABASE_URL`
   - **Value**: Copy from your PostgreSQL service's "Connections" tab
   - Format: `postgres://user:password@host:port/dbname`

### Step 3: Deploy

1. Push your changes to GitHub (if using Git)
2. Render will automatically redeploy
3. The app will detect `DATABASE_URL` and use PostgreSQL instead of SQLite

## 🔍 How It Works

- **On Render**: Detects `DATABASE_URL` → Uses PostgreSQL
- **Locally**: No `DATABASE_URL` → Falls back to SQLite (`matcher.db`)

## ✅ Verification

After deployment, check:
- https://projectplayground.onrender.com/admin/designers
- https://projectplayground.onrender.com/admin/founders
- https://projectplayground.onrender.com/admin/raw-matches

Data should now persist across restarts!

## 📝 Notes

- The `matches.json` file is no longer used - matches are stored in the database
- All existing functionality remains the same
- Local development still uses SQLite (no changes needed)

