# Aftersales-Service-App

A comprehensive Flask-based web application for managing after-sales service operations, including quotations, work orders, customer management, and invoice generation with PDF support.

---

## 📋 Table of Contents

- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage Guide](#-usage-guide)
- [Database Models](#-database-models)
- [Screenshots](#-screenshots)
- [API Endpoints](#-api-endpoints)
- [Contributing](#-contributing)
- [License](#-license)

---

## ✨ Features

### Core Functionality
- **User Management**
  - Admin and user role management
  - Secure authentication with password hashing
  - User profiles with designations and contact details
  - User initials for quotation numbering

- **Customer Management**
  - Customer creation and maintenance
  - GST registration details
  - Address and contact information
  - Kind attention contacts for correspondence
  - Email integration ready

- **Quotation Management**
  - Create and manage quotations with auto-numbering
  - Quotation numbers include: financial year, user initials, month, sequence
  - Item selection from master catalogue with autocomplete
  - PDF generation and download with company letterhead
  - Status tracking (Draft, Submitted, Accepted, Rejected)
  - HSN code support and tax calculation (CGST+SGST / IGST / No Tax)

- **Work Order Management**
  - Create work orders from quotations
  - Track work order status and progress
  - Link to customer and quotation data
  - PDF invoice generation with company branding
  - Payment terms and scope customization

- **Item Master**
  - Maintain ~2,900+ spare parts catalogue
  - Import items from CSV/Excel with validation
  - Item codes, descriptions, and pricing
  - Technical specifications and unit of measurement
  - PCR (Project Cost Rate) support
  - Live autocomplete search during quotation creation

- **Company Settings**
  - Configure company details for PDFs and letterhead
  - Bank account information
  - Tax registration numbers (GST, PAN, CIN)
  - Company logo upload and display
  - Letterhead customization

- **PDF Generation**
  - Professional quotation PDFs matching paper template
  - Formatted work order invoices
  - Company branding and letterhead
  - Itemized breakdowns with calculations
  - Tax calculations (CGST+SGST / IGST options)
  - Yellow-highlighted scope and payment terms rows

---

## 🛠 Tech Stack

### Backend
- **Flask 3.0.3** - Web framework
- **Flask-SQLAlchemy 3.1.1** - ORM for database management
- **Flask-Login 0.6.3** - Authentication and user session management
- **ReportLab 4.2.2** - PDF generation with professional formatting
- **Werkzeug 3.0.4** - WSGI utilities and security

### Frontend
- **HTML5** - Markup
- **CSS3** - Styling with responsive design
- **JavaScript (Vanilla)** - Client-side functionality and form handling
- **Bootstrap** - Responsive UI components

### Database
- **SQLite** - Lightweight, file-based database (no server required)

### Server
- **Python 3.8+** - Runtime environment

---

## 📁 Project Structure

```
aftersales_app/
├── app.py                          # Flask application factory & configuration
├── extensions.py                   # Extension initialization (DB, Login Manager)
├── models.py                       # Database models (User, Customer, Item, etc.)
├── migrations.py                   # Database migrations & schema updates
├── numbering.py                    # Quotation/Work order numbering logic
├── import_items.py                 # Item master CSV import functionality
├── requirements.txt                # Python dependencies
│
├── blueprints/                     # Flask blueprints (modular routes)
│   ├── __init__.py
│   ├── auth.py                     # Authentication routes (login, register, logout)
│   ├── main.py                     # Dashboard and home routes
│   ├── quotations.py               # Quotation CRUD and PDF generation routes
│   └── workorders.py               # Work order CRUD and invoice routes
│
├── templates/                      # HTML Jinja2 templates
│   ├── base.html                   # Base template with navigation & footer
│   ├── login.html                  # User authentication page
│   ├── dashboard.html              # Admin dashboard with statistics
│   ├── customers.html              # Customer list with search/filter
│   ├── customer_form.html          # Add/edit customer form
│   ├── quotation_list.html         # Quotations list with filters
│   ├── quotation_form.html         # Create/edit quotation form
│   ├── quotation_view.html         # View quotation details & download PDF
│   ├── workorder_list.html         # Work orders list
│   ├── workorder_form.html         # Create/edit work order form
│   ├── workorder_view.html         # View work order details & download invoice
│   ├── settings.html               # Company settings configuration
│   ├── users.html                  # User management (admin panel)
│   ├── setup.html                  # Initial setup & item import
│   └── _icons.html                 # SVG icons library
│
├── static/                         # Static files
│   ├── css/
│   │   └── style.css               # Custom CSS styling & responsive design
│   ├── js/
│   │   └── quotation.js            # Quotation form JavaScript (autocomplete, calculations)
│   └── uploads/                    # Directory for user uploads (logos, etc.)
│
├── utils/                          # Utility modules
│   ├── __init__.py
│   └── pdf_generator.py            # PDF generation utilities using ReportLab
│
├── data/
│   └── item_master.csv             # Sample item master data (import this)
│
└── aftersales.db                   # SQLite database (auto-created on first run)
```

---

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Git (for cloning repository)

### Step 1: Clone the Repository

```bash
git clone https://github.com/pratikcse/Aftersales-Service-App.git
cd Aftersales-Service-App
```

### Step 2: Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Initialize Database

```bash
python -c "from app import create_app; app = create_app()"
```

This will automatically:
- Create the SQLite database (`aftersales.db`)
- Initialize all tables
- Run migrations
- Create default company settings row

### Step 5: Run the Application

```bash
python app.py
```

The application will start on: **http://localhost:5000**

### First Time Setup

1. **Create Admin User** (if not auto-created):
   - Access setup page or use Flask shell to add admin user
   - Email and password will be credentials for login

2. **Configure Company Settings**:
   - Login and go to Settings
   - Fill in company name, GST number, address, bank details
   - Upload company logo

3. **Import Item Master**:
   - Go to Setup
   - Upload `data/item_master.csv` or your custom CSV
   - Verify items are imported correctly

4. **Add Users**:
   - Go to Users (admin only)
   - Create user accounts for team members
   - Assign initials (used in quotation numbering)

---

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
SECRET_KEY=your-very-secret-key-change-me-in-production
FLASK_ENV=development
FLASK_DEBUG=1
DATABASE_URL=sqlite:///aftersales.db
UPLOAD_FOLDER=static/uploads
MAX_CONTENT_LENGTH=16777216
```

### Database Configuration

**SQLite (Default):**
```python
# app.py
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "aftersales.db")
```

**PostgreSQL (Production):**
```python
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://user:password@localhost:5432/aftersales"
```

**MySQL:**
```python
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://user:password@localhost/aftersales"
```

### Application Configuration

Edit `app.py` to customize:

```python
# Secret key for session management
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret")

# SQLite database path
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///aftersales.db"

# Upload folder for company logos
app.config["UPLOAD_FOLDER"] = os.path.join(basedir, "static", "uploads")

# Max upload size (16MB default)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024
```

### Quotation Numbering

Edit `numbering.py` to customize quotation number format:

```python
# Example format: SP/HCR/26-27/PNR/JUL/1
# Components:
# - SP: Department prefix (customizable)
# - HCR: Category code (customizable)
# - 26-27: Financial year (auto)
# - PNR: User initials (from User model)
# - JUL: Month (auto)
# - 1: Running sequence (auto-increment)
```

---

## 📖 Usage Guide

### 1. Initial Setup

**Step 1: Admin Access**
- First login with admin credentials
- Navigate to Dashboard

**Step 2: Configure Company**
- Click **Settings** in sidebar
- Fill in company details:
  - Company Name
  - Address and State
  - GST Number, PAN, CIN
  - Telephone and bank details
- Upload company logo (optional but recommended)
- Click **Save**

**Step 3: Import Item Master**
- Click **Setup** in sidebar
- Upload CSV file with columns: `item_code`, `description`, `unit`, `rate`, `pcr_rate`
- Click **Import**
- Verify items appear in the Item Master list

**Step 4: Add Users**
- Click **Users** in sidebar (admin only)
- Click **Add New User**
- Fill in details:
  - Name
  - Email
  - Initials (2-3 characters, used in quotation numbers)
  - Designation (e.g., "Sales Manager")
  - Handphone
  - Set password
  - Check "Admin" if user should have admin privileges
- Click **Save**

### 2. Customer Management

**Add New Customer:**
1. Click **Customers** in sidebar
2. Click **Add New Customer**
3. Fill in details:
   - Customer Name (company name)
   - Address
   - State
   - GST Registration Number
   - Kind Attention (contact person name)
   - Email
4. Click **Save**

**Search/Filter Customers:**
1. Use search box on Customers list
2. Results filtered by customer name

**Edit Customer:**
1. Click on customer name in list
2. Modify details
3. Click **Update**

### 3. Creating a Quotation

**Step 1: Start New Quotation**
1. Click **Quotations** in sidebar
2. Click **New Quotation**

**Step 2: Select Customer**
1. Click customer dropdown
2. Type to search or scroll through list
3. Select customer (auto-fills address, GST, etc.)

**Step 3: Add Line Items**
1. In the items table, click "Add Item"
2. Type item code or description in search field
3. Results autocomplete as you type
4. Click item to select (auto-fills: description, unit, rate)
5. Adjust quantity if needed
6. Press Tab/Enter to add next item
7. Repeat for all items

**Step 4: Adjust Pricing**
1. Modify unit rates if needed
2. Select tax type: CGST+SGST, IGST, or No Tax
3. System auto-calculates totals
4. Add notes in "Scope of Work" section (yellow highlight)
5. Add "Payment Terms" (yellow highlight)

**Step 5: Save Quotation**
1. Click **Save Quotation**
2. System auto-generates quotation number
3. Status: Draft

**Step 6: Download PDF**
1. Click **View**
2. Review quotation details
3. Click **Download PDF**
4. PDF matches your paper template with company letterhead

**Step 7: Submit to Customer**
1. Change status to "Submitted"
2. Click **Save**
3. PDF ready for email to customer

### 4. Creating a Work Order

**Option A: From Existing Quotation**
1. Go to **Work Orders** → **New Work Order**
2. Click "Select from Quotation"
3. Search and select accepted quotation
4. Items auto-populate from quotation
5. Proceed to Step 3 below

**Option B: Create Fresh Work Order**
1. Go to **Work Orders** → **New Work Order**
2. Select customer
3. Add line items (same as quotation process)
4. Proceed to Step 3 below

**Step 3: Work Order Details**
1. Set work order date
2. Set delivery/completion date
3. Add work order notes
4. Specify payment terms
5. Click **Save**

**Step 4: Generate Invoice**
1. Click **View**
2. Review work order details
3. Click **Download Invoice PDF**
4. PDF formatted as professional invoice
5. Print or email to customer

---

## 🗄️ Database Models

### User Model
```
Table: user
├── id (Primary Key) - Auto-increment integer
├── name - User's full name (VARCHAR 120)
├── email - Unique email address (VARCHAR 120, UNIQUE)
├── initials - User initials for quotation numbering (VARCHAR 10)
├── designation - Job title/designation (VARCHAR 120)
├── handphone - Contact number (VARCHAR 40)
├── password_hash - Hashed password (VARCHAR 255)
├── is_admin - Admin role flag (Boolean, default: False)
└── created_at - Account creation timestamp (DateTime)
```

### Customer Model
```
Table: customer
├── id (Primary Key) - Auto-increment integer
├── name - Customer company name (VARCHAR 200, NOT NULL)
├── address - Full address (TEXT)
├── state - State/Province (VARCHAR 80)
├── gst_no - GST registration number (VARCHAR 30)
├── kind_attention - Contact person name (VARCHAR 120)
├── email - Contact email (VARCHAR 120)
└── created_at - Record creation timestamp (DateTime)
```

### Item Model
```
Table: item
├── id (Primary Key) - Auto-increment integer
├── item_code - Unique item code (VARCHAR 60, INDEXED)
├── description - Item description (TEXT, NOT NULL)
├── unit - Unit of measurement (VARCHAR 20, default: "Nos.")
├── rate - Standard unit rate (Float, default: 0)
├── pcr_rate - Project cost rate (Float, default: 0)
├── final_item_number - Final item number after processing (VARCHAR 60)
└── technical_description - Technical specs (TEXT)
```

### CompanySettings Model
```
Table: company_settings
├── id (Primary Key, always 1) - Singleton row
├── company_name - Organization name (VARCHAR 200)
├── address_line - Full address (TEXT)
├── state - State for GST (VARCHAR 80)
├── gst_no - GST registration number (VARCHAR 30)
├── pan_no - PAN number (VARCHAR 20)
├── cin_no - Corporate Identification Number (VARCHAR 30)
└── telephone - Contact telephone (VARCHAR 60)
```

---

## 📸 Screenshots

### 1. Login Page
**Path:** `/login`
- Email/password authentication
- Secure credential handling
- "Remember Me" option

### 2. Dashboard
**Path:** `/`
- Quick statistics (Total Customers, Quotations, Work Orders)
- Recent activities
- Navigation to all modules
- Admin-only features

### 3. Customer Management
**Path:** `/customers`
- List all customers with GST details
- Search and filter functionality
- Add, edit, delete customer
- Customer details form

### 4. Create Quotation
**Path:** `/quotations/new`
- Customer selection with autocomplete
- Item selection with live search
- Quantity and rate adjustment
- Tax calculation (CGST+SGST / IGST / No Tax)
- Scope and Payment Terms (highlighted rows)
- Auto-generated quotation number

### 5. Quotation View & PDF
**Path:** `/quotations/<id>`
- View quotation details
- Edit quotation (if not submitted)
- Download PDF with company letterhead
- Change quotation status
- Email ready format

### 6. Quotation PDF Output
- Professional PDF layout matching paper template
- Company logo and letterhead
- Item breakdown with HSN codes
- Tax calculations
- Payment terms and scope clearly marked

### 7. Work Order List
**Path:** `/workorders`
- List all work orders
- Filter by status
- Link to quotation
- Customer information
- Creation and due dates

### 8. Create Work Order
**Path:** `/workorders/new`
- Select from existing quotation (auto-populate items)
- Or create fresh work order
- Add line items with quantities
- Set delivery dates
- Payment terms

### 9. Work Order Invoice PDF
**Path:** `/workorders/<id>/pdf`
- Professional invoice format
- Company branding and letterhead
- Itemized breakdown
- Tax calculations
- Payment terms
- Print-ready format

### 10. Company Settings
**Path:** `/settings` (Admin only)
- Company name and address
- GST, PAN, CIN numbers
- Bank account details
- Logo upload
- Telephone and email

### 11. User Management
**Path:** `/users` (Admin only)
- List all users
- Add new user (with role assignment)
- Edit user details
- Delete user
- Set user initials and designations

---

## 📡 API Endpoints

### Authentication Routes
```
POST   /login              - User login with email/password
POST   /logout             - User logout (clear session)
```

### Dashboard Routes
```
GET    /                   - Main dashboard
```

### Customer Routes
```
GET    /customers          - List all customers
POST   /customers          - Create new customer (AJAX)
GET    /customers/<id>     - Get customer details (AJAX)
POST   /customers/<id>     - Update customer
DELETE /customers/<id>     - Delete customer
```

### Quotation Routes
```
GET    /quotations         - List all quotations
GET    /quotations/new     - New quotation form page
POST   /quotations         - Create quotation (AJAX)
GET    /quotations/<id>    - View quotation details
POST   /quotations/<id>    - Update quotation
DELETE /quotations/<id>    - Delete quotation
GET    /quotations/<id>/pdf - Download quotation PDF
GET    /api/items          - Search items (AJAX autocomplete)
```

### Work Order Routes
```
GET    /workorders         - List all work orders
GET    /workorders/new     - New work order form page
POST   /workorders         - Create work order (AJAX)
GET    /workorders/<id>    - View work order details
POST   /workorders/<id>    - Update work order
DELETE /workorders/<id>    - Delete work order
GET    /workorders/<id>/pdf - Download invoice PDF
```

### Settings Routes (Admin Only)
```
GET    /settings           - View company settings form
POST   /settings           - Update company settings
GET    /users              - List all users
POST   /users              - Create new user
DELETE /users/<id>         - Delete user
GET    /setup              - Setup/import page
POST   /setup/import-items - Import item master CSV
```

---

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork the Repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/Aftersales-Service-App.git
   cd Aftersales-Service-App
   ```

2. **Create Feature Branch**
   ```bash
   git checkout -b feature/YourFeatureName
   ```

3. **Make Changes**
   - Follow PEP 8 for Python code style
   - Write clean, well-commented code
   - Test your changes locally

4. **Commit Changes**
   ```bash
   git add .
   git commit -m "Add YourFeatureName: Brief description of changes"
   ```

5. **Push to Branch**
   ```bash
   git push origin feature/YourFeatureName
   ```

6. **Open Pull Request**
   - Describe your changes
   - Reference related issues
   - Request review

### Development Guidelines
- **Code Style:** PEP 8 (use `autopep8` or `black`)
- **Documentation:** Update docstrings and comments
- **Testing:** Write tests for new features
- **Commit Messages:** Use clear, descriptive messages
- **Pull Requests:** Include detailed description and screenshots if UI changes

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

**MIT License Summary:**
- ✅ Use for personal and commercial projects
- ✅ Modify and distribute
- ✅ Use privately
- ⚠️ Must include license and copyright notice
- ❌ No warranty or liability

---

## 🆘 Support & Issues

### Getting Help
1. **Check Documentation** - Review this README and code comments
2. **Search Issues** - Look for similar issues on [GitHub Issues](https://github.com/pratikcse/Aftersales-Service-App/issues)
3. **Create New Issue** - If not found, create detailed issue with:
   - Description of problem
   - Steps to reproduce
   - Screenshots if applicable
   - Your environment (Python version, OS, etc.)

### Report Bugs
- **Title:** Clear bug description
- **Details:** What you expected vs. what happened
- **Environment:** Python version, OS, Flask version
- **Logs:** Any error messages or stack traces

### Suggest Features
- **Title:** Feature name/summary
- **Description:** What would you like to add?
- **Use Case:** How would this help?
- **Implementation:** Any ideas on how to build it?

---

## 🎯 Future Roadmap

**v1.1 (In Progress)**
- [ ] Email notification system (quotation/WO updates)
- [ ] Advanced reporting and analytics dashboard
- [ ] Multi-currency support for international customers

**v1.2 (Planned)**
- [ ] WhatsApp integration for updates
- [ ] Mobile-responsive improvements
- [ ] Batch PDF generation for multiple quotations

**v2.0 (Future)**
- [ ] Mobile app (React Native/Flutter)
- [ ] Cloud deployment (AWS/GCP/Heroku guides)
- [ ] API with Swagger documentation
- [ ] Unit tests and integration tests
- [ ] CI/CD pipeline (GitHub Actions)
- [ ] Inventory tracking system
- [ ] Customer portal for online quotation viewing

---

## 👨‍💻 Author & Contact

**Pratik Rane**
- **GitHub:** [@pratikcse](https://github.com/pratikcse)
- **Email:** pratikcse@example.com
- **LinkedIn:** [Pratik Rane](https://linkedin.com/in/pratikcse)

---

## 📊 Project Statistics

- **Total Python Files:** 10+
- **HTML Templates:** 13
- **Database Models:** 4 core models
- **API Endpoints:** 30+
- **Lines of Code:** 5,600+

---

**Version:** 1.0.0  
**Last Updated:** July 2024  
**Status:** Active Development  
**Python:** 3.8+  
**License:** MIT