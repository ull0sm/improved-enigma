# 🥋 EntryDesk - Karate Tournament Manager

A high-performance Streamlit web application for managing karate tournament registrations with Supabase backend.

## ✨ Features

### For Coaches
- 📝 **Single & Bulk Registration** - Register athletes individually or via Excel upload
- 👥 **Athlete Management** - View, search, edit, and delete your registered athletes
- 📥 **Export Data** - Download your roster as Excel or CSV
- 🔐 **Secure Access** - Only whitelisted emails can access the system

### For Admins
- 📊 **Global Overview** - View statistics across all dojos
- 👥 **All Athletes View** - See registrations from every dojo
- 📧 **Access Management** - Control who can use the system
- ⚙️ **Tournament Settings** - Configure name, dates, and registration windows
- 📜 **Audit Logs** - Immutable record of all data changes

## 🚀 Quick Start

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd improved-enigma
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up Supabase

1. Create a new project at [supabase.com](https://supabase.com)
2. Go to **SQL Editor** and run:
   - `database/schema.sql` - Creates all tables
   - `database/rls_policies.sql` - Sets up Row Level Security
3. **Important**: Edit `schema.sql` to add your admin email before running:
   ```sql
   INSERT INTO allowed_emails (email, is_admin) VALUES 
       ('your-email@example.com', TRUE);
   ```

### 4. Configure credentials

Create `.streamlit/secrets.toml`:
```toml
[supabase]
url = "https://your-project.supabase.co"
key = "your-anon-key"
```

### 5. Run the app
```bash
streamlit run app.py
```

## 🔒 Security Features

- **Email Whitelist**: Only pre-approved emails can sign in
- **Row Level Security**: Coaches can only see their own athletes
- **Audit Logging**: All data changes are logged immutably
- **Route Protection**: Direct URL access is blocked for unauthorized users

## 📁 Project Structure

```
├── app.py                    # Main entry point
├── requirements.txt          # Dependencies
├── .streamlit/
│   ├── config.toml          # Theme configuration
│   └── secrets.toml         # Supabase credentials (create this)
├── database/
│   ├── schema.sql           # Database tables
│   └── rls_policies.sql     # Security policies
├── src/
│   ├── auth/                # Authentication modules
│   ├── components/          # Reusable UI components
│   ├── pages/               # Page implementations
│   ├── services/            # Business logic
│   └── utils/               # Helpers (validators, Excel)
├── pages/                   # Streamlit pages
└── assets/
    └── styles.css           # Custom styling
```

## 🔑 Authentication

### Email/Password
- Sign up with whitelisted email
- Complete onboarding to select/create dojo

### Google OAuth
- Enable in Supabase Dashboard → Authentication → Providers
- Configure Google Cloud Console OAuth credentials
- Add redirect URL to your Supabase project

## 📊 Database Schema

| Table | Purpose |
|-------|---------|
| `allowed_emails` | Email whitelist (admin controlled) |
| `dojos` | Dojo/Club registry |
| `coaches` | User profiles linked to Supabase Auth |
| `athletes` | Registered athletes |
| `audit_logs` | Immutable activity log |
| `config` | Dynamic tournament settings |

## 🎨 Customization

### Theme
Edit `.streamlit/config.toml` to change colors:
```toml
[theme]
primaryColor = "#6366f1"
backgroundColor = "#0f0f23"
```

### Tournament Name
Admins can change via Settings page or directly in the `config` table.

## 📝 License

MIT License - feel free to use and modify for your tournaments!

---

Built with ❤️ using [Streamlit](https://streamlit.io) and [Supabase](https://supabase.com)
