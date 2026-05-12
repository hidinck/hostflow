<div align="center">
  <h1>🏠 HostFlow</h1>
  <p><strong>The All-in-One Rental Property Management SaaS</strong></p>

  <p>
    <img src="https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white" alt="Django" />
    <img src="https://img.shields.io/badge/Bootstrap-563D7C?style=for-the-badge&logo=bootstrap&logoColor=white" alt="Bootstrap" />
    <img src="https://img.shields.io/badge/Celery-37814A?style=for-the-badge&logo=celery&logoColor=white" alt="Celery" />
    <img src="https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white" alt="Redis" />
  </p>
</div>

---

## 🛑 The Problem: Chaos in Property Management
Managing rental properties traditionally involves a messy web of disconnected tools. Landlords and property managers constantly struggle with:
- **Scattered Data:** Tracking leases in Excel, communicating over WhatsApp, and managing files in Google Drive.
- **Manual Rent Collection:** Chasing down late payments, manually calculating late fees, and reconciling bank transfers.
- **Lost Maintenance Requests:** Repair requests get buried in text messages, leading to unhappy tenants and delayed fixes.
- **Lack of Transparency:** Tenants have no central place to view their lease, payment history, or maintenance status.
- **Time-Consuming Paperwork:** Manually generating rent invoices and payment receipts every month.

---

## 💡 The Solution: HostFlow
**HostFlow** is a modern, unified SaaS platform designed to put your rental business on autopilot. It bridges the gap between landlords and tenants by bringing properties, leases, payments, and maintenance into one seamless, automated dashboard.

Whether you're managing a 5-unit apartment building or a portfolio of 50+ properties, HostFlow eliminates the busywork so you can focus on growth.

---

## 🌟 Key Features

### 🏢 1. Centralized Property & Unit Management
- Create and manage multiple properties and their respective units in one place.
- Track occupancy status, rent amounts, and unit details instantly.

### 👥 2. Dedicated Portals (Multi-Role Access)
- **Landlords/Admins:** Complete control over properties, financial reports, and tenant management.
- **Tenants:** A self-service portal to view active leases, pay rent securely, download receipts, and submit maintenance requests.

### 💳 3. Automated Billing & Online Payments
- **Razorpay Integration:** Tenants can pay rent online via UPI, Cards, or Netbanking.
- **Automated Rent Generation:** System automatically generates rent dues on the 1st of every month.
- **Smart Late Fees:** Automatically calculates and applies late fees for overdue payments.
- **PDF Receipts:** Instantly generates professional, downloadable PDF payment receipts.

### 🛠️ 4. Streamlined Maintenance Ticketing
- Tenants can submit repair requests with priority levels and photo attachments.
- Threaded comments allow landlords and tenants to communicate directly on the ticket.
- Track ticket status from *Open* to *In Progress* to *Resolved*.

### 📊 5. Financial Insights & Reporting
- Visual dashboards featuring **Chart.js** integration.
- Track revenue trends, outstanding balances, and occupancy rates at a glance.
- Export payment histories to CSV for accounting purposes.

### 🔔 6. Automated Notifications (Email & In-App)
- Auto-reminders for upcoming rent and lease expirations.
- Real-time in-app notifications for ticket updates and payment confirmations.

### 🔐 7. Security & Audit Trails
- Comprehensive **Audit Logs** track every critical action (who did what, and when).
- Strict tenant data isolation.

---

## 🚀 How to Operate HostFlow (User Workflow)

### For the Landlord/Property Manager:
1. **Onboarding:** Log in and navigate to the `Properties` tab. Add your building/property details.
2. **Add Units:** Under your new property, add units (e.g., Apt 101, Apt 102), setting the base rent for each.
3. **Invite Tenants:** Go to `Tenants` and add a new tenant. They will receive credentials to log in.
4. **Sign Leases:** Create a `Lease` linking the Tenant to a Unit, setting the start/end dates.
5. **Sit Back:** HostFlow will now automatically bill the tenant on the 1st of the month, apply late fees if they miss the deadline, and notify you when they pay seamlessly via Razorpay.
6. **Manage Day-to-Day:** Use the `Dashboard` and `Reports` to monitor your cash flow, and check the `Tickets` board to resolve maintenance requests.

### For the Tenant:
1. **Log In:** Access the clean, mobile-responsive Tenant Portal.
2. **Dashboard:** Immediately see if rent is due.
3. **Pay Rent:** Click "Pay Now" to open the Razorpay checkout. Once paid, instantly download your PDF receipt.
4. **Need a Repair?:** Click "Submit Maintenance Ticket", upload a photo of that leaky sink, set it to "High Priority", and track the landlord's response in real-time.

---

## 🛠️ Technical Stack
- **Backend Framework:** Django 4.x
- **Database:** SQLite (Local) / PostgreSQL (Production)
- **Asynchronous Tasks:** Celery + Redis (Message Broker & Cache)
- **Frontend:** HTML5, Bootstrap 5, Chart.js
- **Payment Gateway:** Razorpay API
- **Document Generation:** ReportLab (PDFs)
- **Environment Management:** python-decouple

---

## ⚙️ Installation & Developer Setup

Follow these steps to get HostFlow running on your local machine.

### Prerequisites
- Python 3.8+
- Redis Server (Must be installed and running on default port `6379` for background tasks)

### 1. Clone & Install Dependencies
```bash
git clone <your-repo-url>
cd HostFlow
python -m venv envv
source envv/scripts/activate  # On Windows use: envv\Scripts\activate
pip install -r requirements.txt
```

### 2. Environment Variables Configuration
Create a `.env` file in the root directory alongside `manage.py` and configure the following:
```ini
DEBUG=True
SECRET_KEY=your_super_secret_django_key_here
ALLOWED_HOSTS=127.0.0.1,localhost

# Razorpay Credentials
RAZORPAY_KEY_ID=your_razorpay_key_id
RAZORPAY_KEY_SECRET=your_razorpay_secret

# Email Config (optional for local dev, used for notifications)
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
```

### 3. Database Migration & Superuser
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser  # Create your admin/landlord account
```

### 4. Run the Application
You will need **three terminal windows** to run the full stack locally.

**Terminal 1: Start Django Server**
```bash
python manage.py runserver
```

**Terminal 2: Start Celery Worker (Task Executor)**
```bash
# Windows
celery -A website worker -l info -P eventlet
# Mac/Linux
celery -A website worker --loglevel=info
```

**Terminal 3: Start Celery Beat (Task Scheduler)**
```bash
celery -A website beat --loglevel=info
```

*Your application is now live at `http://127.0.0.1:8000`!*

---

## 🔮 Roadmap (What's Next?)
- **Production DB:** Full migration to PostgreSQL.
- **Cloud Storage:** Integration with AWS S3 via `django-storages` for lease documents and maintenance images.
- **DRF API:** Building out a RESTful API using Django Rest Framework for a future mobile app.
- **SMS Notifications:** Twilio integration for instant SMS billing alerts.

---

> *Built with ❤️ to make property management painless.*
