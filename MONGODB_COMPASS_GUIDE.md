# MongoDB Compass Connection Guide

## 🎯 Overview
This guide will help you connect MongoDB Compass to your Knowledge Analytics System database to view uploaded documents.

---

## 📋 Prerequisites
- ✅ MongoDB Compass installed on your laptop
- ✅ Internet connection (for MongoDB Atlas)

---

## 🔗 Step 1: Get Your Connection String

Your MongoDB connection string is stored in the `.env` file:

```
mongodb+srv://hari:qwerty123@software.vc55jwa.mongodb.net/knowledge_db
```

**Connection Details:**
- **Username:** `hari`
- **Password:** `qwerty123`
- **Cluster:** `software.vc55jwa.mongodb.net`
- **Database:** `knowledge_db`

---

## 🚀 Step 2: Connect MongoDB Compass

### Method 1: Using Connection String (Recommended)

1. **Open MongoDB Compass**

2. **Click "New Connection"** (or the green "Connect" button)

3. **Paste the connection string:**
   ```
   mongodb+srv://hari:qwerty123@software.vc55jwa.mongodb.net/knowledge_db
   ```

4. **Click "Connect"**

5. **Wait for connection** (may take 5-10 seconds)

### Method 2: Manual Configuration

If the connection string doesn't work, try manual setup:

1. Click **"Fill in connection fields individually"**

2. Enter the following:
   - **Hostname:** `software.vc55jwa.mongodb.net`
   - **Port:** `27017` (default)
   - **Authentication:** Username/Password
   - **Username:** `hari`
   - **Password:** `qwerty123`
   - **Authentication Database:** `admin`
   - **SSL/TLS:** ON (enabled)

3. Click **"Connect"**

---

## 📂 Step 3: Navigate to Your Database

Once connected:

1. **Expand the connection** in the left sidebar

2. **Find and click on `knowledge_db`** database

3. **Click on `documents`** collection

You should now see all uploaded documents!

---

## 📄 Step 4: View Document Data

Each document in the `documents` collection contains:

| Field | Description | Example |
|-------|-------------|---------|
| `_id` | Unique MongoDB ID | `ObjectId("...")` |
| `title` | Original filename | `"sample.pdf"` |
| `file_path` | Local storage path | `"documents/sample.pdf"` |
| `content_type` | File MIME type | `"application/pdf"` |
| `file_size` | Size in bytes | `245760` |
| `content` | Extracted text content | `"This is the document content..."` |
| `uploaded_at` | Upload timestamp | `ISODate("2024-02-07T12:30:00Z")` |

---

## 🔍 Step 5: Query and Filter Documents

### View All Documents
- Simply click on the `documents` collection

### Search by Filename
In the filter bar, enter:
```json
{ "title": "sample.pdf" }
```

### View Recent Uploads
```json
{ "uploaded_at": { "$exists": true } }
```
Then click the **Sort** button and sort by `uploaded_at: -1` (descending)

### View Documents by Type
```json
{ "content_type": "application/pdf" }
```

---

## 🛠️ Troubleshooting

### ❌ "Connection Timeout"
- Check your internet connection
- Verify the connection string is correct
- Make sure MongoDB Atlas cluster is running

### ❌ "Authentication Failed"
- Double-check username: `hari`
- Double-check password: `qwerty123`
- Ensure no extra spaces in the connection string

### ❌ "Database Not Found"
- Upload at least one document first
- The database is created automatically on first upload
- Refresh the connection in Compass

### ❌ "No Documents Visible"
- Make sure you uploaded files through the web app
- Check the backend server is running
- Verify the upload was successful (check console logs)

---

## 🧪 Testing the Connection

### Test 1: Run MongoDB Test Script
```bash
cd backend
python test_mongodb.py
```

**Expected Output:**
```
✅ MongoDB connected successfully!
📊 Database: knowledge_db
📁 Collection: documents
📄 Total documents: 3
```

### Test 2: Upload a Test File
1. Go to `http://localhost:3000`
2. Upload a PDF or DOCX file
3. Wait for success message
4. Refresh MongoDB Compass
5. You should see the new document appear!

### Test 3: Check via API
Visit in browser:
```
http://127.0.0.1:8000/get-documents
```

You should see JSON with all uploaded documents.

---

## 📊 Useful MongoDB Compass Features

### 1. **Schema Analysis**
Click the "Schema" tab to see:
- Field types
- Field frequency
- Data distribution

### 2. **Export Data**
- Click "Export Collection"
- Choose JSON or CSV format
- Save your documents locally

### 3. **Delete Documents**
- Hover over a document
- Click the trash icon
- Confirm deletion

### 4. **Edit Documents**
- Click on a document to expand
- Click the pencil icon
- Modify fields
- Click "Update"

---

## 🎉 Success Checklist

- [ ] MongoDB Compass connected successfully
- [ ] Can see `knowledge_db` database
- [ ] Can see `documents` collection
- [ ] Uploaded test document appears in Compass
- [ ] Can view document content field
- [ ] Can see upload timestamp

---

## 📞 Need Help?

If you're still having issues:

1. **Check backend logs** for MongoDB connection errors
2. **Verify .env file** has correct connection string
3. **Test connection** using `test_mongodb.py` script
4. **Check MongoDB Atlas** dashboard to ensure cluster is active

---

## 🔐 Security Note

> **⚠️ Important:** The connection string contains your database password. Keep the `.env` file secure and never commit it to version control (Git). The `.gitignore` file should already exclude `.env`.

---

**Happy Data Exploring! 🚀**
