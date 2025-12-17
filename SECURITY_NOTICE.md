# Security Notice

## ⚠️ Important: Change Your MongoDB Password

If your MongoDB Atlas password was previously exposed in documentation files, please change it immediately:

### Steps to Change MongoDB Atlas Password

1. **Log into MongoDB Atlas:**
   - Go to https://cloud.mongodb.com
   - Sign in to your account

2. **Navigate to Database Access:**
   - Click "Database Access" in the left sidebar
   - Find your database user

3. **Change Password:**
   - Click "Edit" on your user
   - Click "Edit Password"
   - Enter a new strong password
   - Save changes

4. **Update Your Environment Variables:**
   ```bash
   export MONGO_URI="mongodb+srv://<username>:<NEW_PASSWORD>@cluster0.jwaekxl.mongodb.net/?appName=Cluster0"
   ```

5. **Update All Team Members:**
   - Share the new password securely (use a password manager)
   - Update all local environments

## ✅ Security Best Practices

### 1. Never Commit Credentials
- ✅ All passwords have been removed from code
- ✅ `.env` files are in `.gitignore`
- ✅ Use environment variables or `.env` files

### 2. Use Environment Variables
```bash
# Set in your shell (not in code)
export MONGO_URI="mongodb+srv://username:password@cluster.mongodb.net/..."
export MONGO_DB="disinfo_project"
```

### 3. Use .env Files (Recommended)
Create a `.env` file in the project root:
```
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/...
MONGO_DB=disinfo_project
```

**Note:** `.env` is already in `.gitignore` and will NOT be committed.

### 4. Rotate Passwords Regularly
- Change passwords every 90 days
- Use strong, unique passwords
- Use a password manager

## 🔒 Current Security Status

- ✅ No hardcoded passwords in code
- ✅ `.env` files excluded from git
- ✅ Documentation uses placeholders
- ✅ Environment variables used throughout

## 📝 For Team Members

When setting up locally:
1. Get MongoDB credentials from team lead (securely)
2. Set environment variables in your shell
3. Never commit `.env` files
4. Never share credentials in chat/email (use secure channels)

