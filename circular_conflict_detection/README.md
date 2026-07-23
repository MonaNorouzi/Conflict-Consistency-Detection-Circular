# Circular Conflict & Consistency Detection

This scaffold separates backend, frontend, and AI/vector services for a banking regulation analysis platform.

## Structure
- Backend: FastAPI + service-layer modules
- Frontend: Streamlit UI
- Vector DB: Qdrant
- LLM: Ollama or Gemini


# ⚖️ سامانه هوشمند تشخیص مغایرت و تعارض بخشنامه‌های بانکی

### Automated Circular Conflict & Consistency Detection System

این پروژه یک سامانه هوشمند مبتنی بر **FastAPI** و **Streamlit** است که برای تحلیل حقوقی، خردسازی، تطبیق مقررات و کشف تعارضات در بخشنامه‌های بانکی و متون مقرراتی طراحی شده است. سیستم قادر است متون خام یا ساختاریافته (JSON) را پردازش کرده و بر اساس **قوانین اولویت حقوقی (Precedence Engine)** تعارضات را شناسایی، تحلیل و اولویت‌بندی کند.

---

## 🏗️ معماری و ساختار پروژه

پروژه بر اساس معماری چندلایه و کاملاً ماژولار (Production-Ready) پیاده‌سازی شده است:

```text
circular-conflict-detector/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                   # نقطه ورود FastAPI (Entry Point)
│   │   ├── api/                      # مسیرها و Endpointهای API
│   │   │   ├── __init__.py
│   │   │   └── circulars.py
│   │   ├── models/                   # اسکیماهای Pydantic و مدل‌های داده
│   │   │   ├── __init__.py
│   │   │   └── schemas.py
│   │   ├── services/                 # موتور منطق تجاری و تعیین اولویت (Precedence Engine)
│   │   │   ├── __init__.py
│   │   │   └── precedence_service.py
│   │   └── core/                     # تنظیمات برنامه و کانفیگ‌ها
│   │       ├── __init__.py
│   │       └── config.py
│   └── tests/                        # تست‌های واحد (Unit Tests)
│       ├── __init__.py
│       └── test_precedence.py
├── ui/
│   └── app.py                        # داشبورد تعاملی Streamlit
├── docker-compose.yml                # ارکستراسیون کانتینرها
├── Dockerfile.backend                # ایمیج سرویس بک‌اند
├── Dockerfile.ui                     # ایمیج سرویس فرانت‌اند
├── requirements.txt                  # وابستگی‌های پروژه
└── README.md

```

---

## ⚖️ قوانین اولویت حقوقی (Precedence Rules Engine)

موتور تصمیم‌گیری حقوقی (`PrecedenceEngine`) تعارضات شناسایی‌شده بین بندهای مختلف را بر اساس ۶ قانون کلیدی ارزیابی می‌کند:

| نوع برتری | توضیح | نمونه شواهد ارزیابی |
| --- | --- | --- |
| **برتری زمانی (Temporal Priority)** | اگر دو بخشنامه از یک واحد صادرکننده و هم‌رتبه باشند، بخشنامه جدیدتر معتبر است. | `GT-01`, `GT-06` |
| **برتری سلسله‌مراتبی (Hierarchical Priority)** | بخشنامه مرجع بالادستی (بانک مرکزی/نظارتی) همواره بر بخشنامه داخلی ارجح است. | `GT-02`, `GT-03` |
| **برتری نسخ صریح (Explicit Override)** | اگر در متن جدید صراحتاً به لغو/نسخ بند یا بخشنامه قبلی اشاره شده باشد. | `GT-07` |
| **برتری اصلاح/نسخ جزئی (Partial Override)** | فقط بند جدید جایگزین می‌شود و سایر بندهای بخشنامه قبلی معتبر می‌مانند. | `GT-05` |
| **برتری زنجیره‌ای (Transitive / Chain Priority)** | ابتدا نسخ‌های قبلی اعمال شده و مقایسه روی آخرین نسخه معتبر انجام می‌شود. | `GT-08` |
| **عدم وجود برتری (No Applicable Priority)** | دو بخشنامه هم‌رتبه از دو واحد متفاوت بدون تقدم حقوقی (ارجاع به انسانی). | `GT-04`, `GT-08` |

---

## 🚀 نحوه راه‌اندازی و اجرا

### روش اول: اجرا با Docker Compose (پیشنهادی)

برای اجرای یکپارچه تمامی سرویس‌ها (FastAPI + Streamlit)، کافی است دستور زیر را اجرا کنید:

```bash
docker-compose up --build -d

```

پس از بالا آمدن کانتینرها:

* 🌐 **داشبورد Streamlit:** [http://localhost:8501](http://localhost:8501)
* 📄 **مستندات Swagger API:** [http://localhost:8000/docs](http://localhost:8000/docs)

---

### روش دوم: اجرای دستی و محلی (Local Development)

#### ۱. راه‌اندازی و اجرای بک‌اند (FastAPI)

```bash
# نصب وابستگی‌ها
pip install -r requirements.txt

# اجرای سرویس FastAPI
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload

```

#### ۲. اجرای رابط کاربری (Streamlit)

در یک ترمینال مجزا دستور زیر را وارد کنید:

```bash
streamlit run ui/app.py --server.port 8501

```

---

## 🧪 اجرای تست‌های واحد (Unit Tests)

برای اطمینان از صحت کارکرد منطق تعیین اولویت حقوقی و پوشش سناریوهای مختلف:

```bash
pytest backend/tests/

```

---

## 📡 راهنمای APIهای اصلی (`Endpoints`)

### ۱. پردازش متن خام بخشنامه

* **Endpoint:** `POST /api/v1/circulars/process-text`
* **Body:**
```json
{
  "text": "بخشنامه شماره C-015\nعنوان: سقف جدید تسهیلات...\nبند ۱: ..."
}

```



### ۲. ثبت و تحلیل فایل JSON

* **Endpoint:** `POST /api/v1/circulars/upload-json`
* **Input:** فایل با فرمت `.json` شامل فیلدهای `circular_id`, `doc_type`, `issuer`, `issue_date` و `clauses`.

### ۳. پایش دوره‌ای کل آرشیو (Periodic Audit)

* **Endpoint:** `GET /api/v1/circulars/periodic-audit`
* **کاربرد:** کشف تعارضات پنهان و زنجیره‌ای موجود در کل آرشیو پایگاه داده بخشنامه‌ها.

---

## 🛠️ تکنولوژی‌های استفاده‌شده

* **Backend:** Python 3.10, FastAPI, Pydantic v2, Uvicorn
* **Frontend:** Streamlit
* **DevOps & Infrastructure:** Docker, Docker Compose
* **Testing:** Pytest
