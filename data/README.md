# data

## מקור
- **מאגר:** Online Retail & E-Commerce Dataset, מאת Ertuğrul EŞOL
- **קישור:** https://www.kaggle.com/datasets/ertugrulesol/online-retail-data
- **רישיון:** CC0: Public Domain
- **הורד:** 2026-11-03, כקובץ `archive.zip`
- **הקובץ:** `raw/synthetic_online_retail_data.csv`, נשמר כפי שהורד, ללא שינוי

## אופי הנתונים
נתונים **מומצאים** (נוצרו בספריית Faker). אין בהם אנשים אמיתיים.

## מה נבדק בקובץ (2026-11-03)
- 1,000 שורות, כל שורה היא הזמנה אחת.
- עמודות: `customer_id`, `order_date`, `product_id`, `category_id`, `category_name`, `product_name`, `quantity`, `price`, `payment_method`, `city`, `review_score`, `gender`, `age`.
- טווח תאריכים: 2024-03-19 עד 2025-03-19.
- `review_score` חסר ב-201 שורות.
- **1,000 לקוחות ייחודיים, ולכל לקוח הזמנה אחת בלבד.** משמעות: אין "לקוחות חוזרים" ואין היסטוריית קניות ללקוח. לכן המשימה השלישית הותאמה: במקום "לקוחות שלא קנו 60 יום", היא מסכמת הזמנות עם דירוג נמוך או בלי דירוג (`review_score`). הניסוח הסופי ייקבע ב-`spec.md`.

## כלל
`raw/` הוא חומר גלם. לא עורכים אותו. כל טרנספורמציה נעשית בקוד ונשמרת במקום אחר.
