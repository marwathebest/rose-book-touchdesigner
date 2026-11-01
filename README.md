# Rose Book — كتاب الورود 🌹

**A TouchDesigner book you control with your hand. Twist your wrist in front of the camera and a page turns, and a rose grows out of it.**

**كتاب تفاعلي في TouchDesigner ينفتح بلفّة اليد. تلفّين كفّك قدام الكاميرا فتنقلب صفحة، وتطلع منها وردة تنمو وتتفتّح.**

![Rose Book preview](docs/preview.jpg)

## الفكرة | Concept

- اللفّة الأولى تفتح الغلاف، وكل لفّة بعدها تقلب صفحة.
- كل صفحة فيها وردة مختلفة: حمرا، وردية، وردتين فوشيا، وثلاث ورود بيضاء.
- الغصن ينمو والأوراق تطلع، وبعدها الوردة تتفتّح من برعم لين تكتمل، وحولها جزيئات ضوء.
- تلفّين بالعكس فترجع صفحة. وبعد الصفحة الرابعة يتقفّل الكتاب.

The wrist rotation is read from MediaPipe hand tracking. A "door-knob twist" gesture proved much more reliable than flipping the palm.

## التقنيات | Tech

- **TouchDesigner**: يبني الشبكة كاملة بسكربت بايثون، وفيها مكونات Geo وMaterials ونظام جزيئات
- **MediaPipe** hand tracking (via [torinmb/mediapipe-touchdesigner](https://github.com/torinmb/mediapipe-touchdesigner))
- **Python**: [`book_body.py`](book_body.py) يبني `/project1/rose_book` كامل من الصفر
- 4 × 48 PNG frames with transparent background (640×896) for the rose growth animation

## الملفات | Files

| File | What it does |
|---|---|
| `book_body.py` | يبني الكتاب: الصفحات، قلب الصفحة، الورود، الجزيئات، وقراءة اليد |
| `build_rose_book.py` | يشغّل `book_body.py` ويكتب أي خطأ في `build_log.txt` |
| `page1_red/` … `page4_white/` | إطارات نمو كل وردة (`frame_0000` فاضي، و`0047` الوردة مكتملة) |

## التشغيل | Run it

1. افتحي مشروع [mediapipe-touchdesigner](https://github.com/torinmb/mediapipe-touchdesigner) وتأكدي إن `hand_tracking` شغّال.
2. عدّلي `ROSE_FOLDER` في `book_body.py` و`_DIR` في `build_rose_book.py` لمسار هذا المجلد عندك.
3. في `/project1` أضيفي **Text DAT** باسم `rose_book_builder`، واربطيه بملف `build_rose_book.py`، واضغطي **Ctrl+R**.
4. الناتج النهائي في `rose_book/final`.

**للتجربة بدون كاميرا:** شغّلي *Test Without Camera* من صفحة **Book** في باراميترات `rose_book`، وحرّكي *Test Hand Roll* من 1 إلى ‎-1. لا تضغطين Space لأنه يوقف التايملاين.

---

Made by [Marwah Abdullah Sabei](https://github.com/marwathebest)
