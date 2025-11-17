# How to Add Environment Variable and Redeploy on Render

## 📋 Step-by-Step Instructions

### Step 1: Add the DATABASE_URL Environment Variable

1. **Go to your Render Dashboard**
   - Visit: https://dashboard.render.com
   - Log in to your account

2. **Find Your Web Service**
   - Click on your web service (the one running `projectplayground.onrender.com`)
   - It should be listed under "Services" or "Web Services"

3. **Navigate to Environment Variables**
   - In your service page, look for the left sidebar menu
   - Click on **"Environment"** (or scroll down to find "Environment Variables" section)

4. **Add the DATABASE_URL Variable**
   - Click **"Add Environment Variable"** or the **"+"** button
   - In the **Key** field, enter: `DATABASE_URL`
   - In the **Value** field, paste your database URL:
     ```
     postgresql://matcher_pd0r_user:fpvTvmTXSQz1YupF55mO5Iwq5tq2JAh7@dpg-d4d67ck9c44c7396eveg-a.oregon-postgres.render.com/matcher_pd0r
     ```
   - Click **"Save Changes"** or **"Add"**

### Step 2: Redeploy Your Service

You have **two options** to redeploy:

#### Option A: Manual Redeploy (Fastest)
1. Still on your service page
2. Look for the **"Manual Deploy"** section (usually at the top)
3. Click **"Deploy latest commit"** or **"Redeploy"** button
4. Render will start a new deployment

#### Option B: Push to GitHub (If using Git)
1. Make sure your code is committed:
   ```bash
   git add .
   git commit -m "Add PostgreSQL support"
   git push
   ```
2. Render will automatically detect the push and redeploy
3. You can watch the deployment in the "Events" or "Logs" tab

### Step 3: Monitor the Deployment

1. **Watch the Build Logs**
   - On your service page, click **"Logs"** tab
   - You should see:
     - Installing dependencies (including `psycopg2-binary`)
     - Starting the application
     - Database initialization

2. **Check for Success**
   - Look for: `Application is live` or `Deploy successful`
   - The status should show as "Live" (green)

### Step 4: Verify It's Working

1. **Test the Connection**
   - Visit: https://projectplayground.onrender.com/admin/designers
   - Should show an empty array `[]` (or existing data if any)

2. **Test Form Submission**
   - Go to: https://projectplayground.onrender.com/designer
   - Submit a test form
   - Check admin endpoints again - data should persist

3. **Verify Database is Being Used**
   - Check the logs for any database connection messages
   - Data should persist even after service restarts

## 🔍 Troubleshooting

### If the deployment fails:

1. **Check Build Logs**
   - Look for error messages in the "Logs" tab
   - Common issues:
     - Missing dependencies → Check `requirements.txt` includes `psycopg2-binary`
     - Import errors → Make sure code is pushed correctly

2. **Verify Environment Variable**
   - Go back to Environment section
   - Make sure `DATABASE_URL` is exactly as shown above
   - No extra spaces or quotes

3. **Check Database Connection**
   - Ensure your PostgreSQL database is running
   - Verify the database URL is correct

### If data isn't persisting:

1. **Check Logs for Database Errors**
   - Look for connection errors or SQL errors
   - Should see successful table creation messages

2. **Verify DATABASE_URL is Set**
   - In your service logs, you can add a temporary print statement
   - Or check if the app is using PostgreSQL vs SQLite

## ✅ Quick Checklist

- [ ] Added `DATABASE_URL` environment variable
- [ ] Value is correct (starts with `postgresql://`)
- [ ] Saved the environment variable
- [ ] Triggered a redeploy
- [ ] Deployment completed successfully
- [ ] Tested the app and data persists

## 📝 Notes

- **Environment variables take effect immediately** after redeploy
- **No code changes needed** - your code already supports PostgreSQL
- **Local development** will still use SQLite (no `DATABASE_URL` locally)
- **Database tables** will be created automatically on first run

---

**Need help?** Check the Render documentation: https://render.com/docs/environment-variables

