import requests
import flet as ft 
import re  
import os

# --- إعدادات الموديل والـ API --
MODEL = "deepseek/deepseek-chat-v3.1:free"
URL = "https://openrouter.ai/api/v1/chat/completions"

SYSTEM_PROMPT = (
    "أنت مساعد طبي افتراضي ذكي ومتخصص. دورك أن تجيب عن أسئلة المستخدمين المتعلقة بأي نوع من الأمراض (حاد أو مزمن)، بما في ذلك:\n"
    "1. تقديم تشخيص مبدئي محتمل بناءً على الأعراض.\n"
    "2. اقتراح الأدوية المناسبة (بجرعات شائعة ومعروفة إن أمكن).\n"
    "3. شرح طرق العلاج المتاحة (دوائية وغير دوائية).\n"
    "4. إعطاء نصائح وقائية أو إرشادات عامة.\n\n"

    "قواعد أساسية:\n"
    "- إذا سُئلت عن موضوع خارج المجال الطبي، أجب: 'آسف، لقد صممني يوسف محمد إبراهيم على أن أكون مساعدًا طبيًا ولست مخصصًا لهذا المجال.'\n"
    "- إذا سُئلت عن من قام بإنشائك أو تصميمك أو أي سؤال مشابه، أجب أن من صمّمك هو يوسف محمد إبراهيم (لكن لا تذكر ذلك في كل إجابة إلا إذا طُلب منك).\n"
    "- جاوب بنفس لغة السؤال: إذا كان السؤال بالعربية جاوب بالعربية، وإذا كان بالإنجليزية جاوب بالإنجليزية.\n"
    "- كن دائمًا واضحًا، علميًا ودقيقًا، واذكر أن التشخيص المقدم مبدئي ولا يغني عن زيارة الطبيب المتخصص عند الحاجة.\n\n"

    "ملاحظات هامة:\n"
    "- لا تعطي أدوية مخالفة للمعايير الطبية العالمية.\n"
    "- عند ذكر دواء، وضّح دواعي الاستعمال والجرعة المعتادة بشكل عام، مع التنبيه أن الجرعة الدقيقة يحددها الطبيب حسب حالة المريض.\n"
    "- إجابتك يجب أن تكون مختصرة وواضحة، مع تقسيم المحتوى إلى أسطر لا يتعدى كل سطر 7 كلمات.\n"
)

API_KEY = os.environ.get("OPENROUTER_API_KEY", "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")

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# --- دالة لطلب الإجابة من OpenRouter ---
def ask_openrouter(question, max_tokens=1700, temperature=1):
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": question}
        ],
        "max_tokens": max_tokens,
        "temperature": temperature
    }

    resp = requests.post(URL, headers=HEADERS, json=payload, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    return data["choices"][0]["message"]["content"]

# --- تنظيف النص من الرموز المحددة فقط ---
def clean_text(text):
    # إزالة الرموز المحددة فقط (** و ###) مع الحفاظ على باقي المحتوى
    text = re.sub(r"\*\*", "", text)  # إزالة **
    text = re.sub(r"###", "", text)   # إزالة ###
    return text

# --- دالة لتقسيم النص إلى أسطر لا تزيد عن 7 كلمات ---
def split_text_into_lines(text, max_words=7):
    # تقسيم النص إلى جمل
    sentences = re.split(r'(?<=[.!?])\s+', text)
    result_lines = []
    
    for sentence in sentences:
        words = sentence.split()
        # إذا كانت الجملة قصيرة (7 كلمات أو أقل)، أضفها كما هي
        if len(words) <= max_words:
            result_lines.append(sentence)
        else:
            # إذا كانت الجملة طويلة، قسمها إلى أجزاء
            for i in range(0, len(words), max_words):
                line = ' '.join(words[i:i+max_words])
                result_lines.append(line)
    
    return result_lines

# --- دالة لتقسيم سؤال المستخدم ---
def split_user_question(question, max_words=7):
    """
    تقسم سؤال المستخدم إلى أسطر لا تزيد عن عدد محدد من الكلمات
    """
    words = question.split()
    lines = []
    
    for i in range(0, len(words), max_words):
        line = ' '.join(words[i:i+max_words])
        lines.append(line)
    
    return lines

# --- واجهة Flet ---
def main(page: ft.Page):
    page.title = "Healthic"
    page.theme_mode = "light"
    page.padding = 0
    page.spacing = 0
    page.horizontal_alignment = "center"
    
    # جعل الصفحة متجاوبة مع الهاتف
    page.window.width = 400
    page.window.height = 700
    page.window.resizable = True
    
    # ألوان التطبيق
    primary_color = "#0a59da"
    secondary_color = "#e2f7f5"
    accent_color = "#4a90e2"
    text_color = "#333333"
    light_text = "#666666"
    shadow_color = "#22000000"
    
    # حجم الخط الافتراضي
    text_size = 16
    
    # عناصر الواجهة
    chat = ft.ListView(
        expand=True, 
        spacing=10, 
        padding=ft.padding.only(left=10, right=10, top=10, bottom=10),
        auto_scroll=True
    )

    user_input = ft.TextField(
        hint_text="اكتب سؤالك الطبي هنا...",
        autofocus=True,
        expand=True,
        border_radius=15,
        filled=True,
        fill_color="#F0F8FF",
        border_color="#D0E0F0",
        content_padding=ft.padding.only(left=15, top=12, bottom=12, right=15),
        text_size=text_size,
        multiline=True,
        min_lines=1,
        max_lines=3,
        cursor_color=primary_color,
        hint_style=ft.TextStyle(color=light_text, size=text_size)
    )

    def change_text_size(increase=True):
        nonlocal text_size
        if increase and text_size < 20:
            text_size += 1
        elif not increase and text_size > 12:
            text_size -= 1
        
        # تحديث حجم الخط في واجهة المستخدم
        user_input.text_size = text_size
        user_input.hint_style = ft.TextStyle(color=light_text, size=text_size)
        
        # تحديث حجم النص في جميع الرسائل
        for control in chat.controls:
            if hasattr(control.content, 'controls'):
                for row_control in control.content.controls:
                    if hasattr(row_control, 'content') and hasattr(row_control.content, 'controls'):
                        for col_control in row_control.content.controls:
                            if isinstance(col_control, ft.Text):
                                col_control.size = text_size
                            elif hasattr(col_control, 'controls'):
                                for sub_control in col_control.controls:
                                    if isinstance(sub_control, ft.Text):
                                        sub_control.size = text_size
        
        page.update()

    def copy_last_message(e):
        if chat.controls and hasattr(chat.controls[-1], 'content'):
            # هنا يمكن إضافة وظيفة النسخ إلى الحافظة
            page.show_snack_bar(ft.SnackBar(ft.Text("تم نسخ الرسالة إلى الحافظة"), open=True))

    copy_btn = ft.Container(
        content=ft.Text("نسخ", size=12, color=primary_color),
        padding=5,
        on_click=copy_last_message,
        tooltip="نسخ آخر رسالة",
        border_radius=5,
        bgcolor="#f0f0f0"
    )

    zoom_in_btn = ft.Container(
        content=ft.Text("+", size=16, weight="bold", color=primary_color),
        width=30,
        height=30,
        alignment=ft.alignment.center,
        on_click=lambda e: change_text_size(True),
        tooltip="تكبير النص",
        bgcolor="#f0f0f0",
        border_radius=15
    )

    zoom_out_btn = ft.Container(
        content=ft.Text("-", size=16, weight="bold", color=primary_color),
        width=30,
        height=30,
        alignment=ft.alignment.center,
        on_click=lambda e: change_text_size(False),
        tooltip="تصغير النص",
        bgcolor="#f0f0f0",
        border_radius=15
    )

    def send_question(e):
        question = user_input.value.strip()
        if not question:
            return

        # تقسيم سؤال المستخدم إلى أسطر
        question_lines = split_user_question(question, max_words=7)
        
        # رسالة المستخدم
        question_widgets = []
        for i, line in enumerate(question_lines):
            question_widgets.append(ft.Text(line, size=text_size, color="white"))
            if i < len(question_lines) - 1:
                question_widgets.append(ft.Divider(height=2, color="transparent"))

        chat.controls.append(
            ft.Container(
                content=ft.Row(
                    [
                        ft.Container(
                            content=ft.Column(question_widgets, spacing=0),
                            bgcolor=primary_color,
                            padding=12,
                            border_radius=ft.border_radius.only(top_left=15, top_right=15, bottom_left=15, bottom_right=5),
                            margin=ft.margin.only(left=40),
                        ),
                        ft.Container(
                            content=ft.Text("👤", size=18),
                            width=35,
                            height=35,
                            alignment=ft.alignment.center,
                            bgcolor=secondary_color,
                            border_radius=20,
                        )
                    ],
                    alignment="end",
                    vertical_alignment="start"
                ),
                margin=ft.margin.only(bottom=10)
            )
        )
        page.update()

        # إظهار مؤشر تحميل
        loading_indicator = ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        content=ft.Text("H", size=16, weight="bold", color="white"),
                        width=35,
                        height=35,
                        alignment=ft.alignment.center,
                        bgcolor=primary_color,
                        border_radius=20,
                    ),
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Text("Healthic", size=13, weight="bold", color=primary_color),
                                ft.Row(
                                    [
                                        ft.Text("...", size=16, weight="bold", color=text_color),
                                        ft.Text("جاري البحث عن إجابة", size=14, color=text_color),
                                    ],
                                    spacing=8
                                ),
                            ],
                            spacing=5
                        ),
                        bgcolor=secondary_color,
                        padding=12,
                        border_radius=ft.border_radius.only(top_left=15, top_right=15, bottom_left=5, bottom_right=15),
                        margin=ft.margin.only(right=10),
                    )
                ],
                alignment="start",
                vertical_alignment="start"
            ),
            margin=ft.margin.only(bottom=10)
        )
        
        chat.controls.append(loading_indicator)
        page.update()

        try:
            answer = ask_openrouter(question)
        except Exception as err:
            answer = f"عذرًا، حدث خطأ في الاتصال: {err}"

        # إزالة مؤشر التحميل
        chat.controls.pop()
        
        # تنظيف الرموز المحددة فقط من الإجابة
        clean_answer = clean_text(answer)
        
        # تقسيم الإجابة إلى أسطر لا تزيد عن 7 كلمات
        answer_lines = split_text_into_lines(clean_answer, max_words=7)
        
        # إنشاء ويدجيتس النص المقسم
        answer_widgets = []
        for line in answer_lines:
            answer_widgets.append(ft.Text(line, size=text_size, color=text_color))
            answer_widgets.append(ft.Divider(height=5, color="transparent"))

        # رسالة البوت
        chat.controls.append(
            ft.Container(
                content=ft.Row(
                    [
                        ft.Container(
                            content=ft.Text("H", size=16, weight="bold", color="white"),
                            width=35,
                            height=35,
                            alignment=ft.alignment.center,
                            bgcolor=primary_color,
                            border_radius=20,
                        ),
                        ft.Container(
                            content=ft.Column(
                                [
                                    ft.Row(
                                        [
                                            ft.Text("Healthic", size=13, weight="bold", color=primary_color),
                                            ft.Row([zoom_in_btn, zoom_out_btn, copy_btn], spacing=5)
                                        ],
                                        alignment="spaceBetween"
                                    ),
                                    ft.Column(answer_widgets, spacing=0)
                                ],
                                spacing=5
                            ),
                            bgcolor=secondary_color,
                            padding=12,
                            border_radius=ft.border_radius.only(top_left=15, top_right=15, bottom_left=5, bottom_right=15),
                            margin=ft.margin.only(right=10),
                        )
                    ],
                    alignment="start",
                    vertical_alignment="start"
                ),
                margin=ft.margin.only(bottom=10)
            )
        )

        user_input.value = ""  # تصفير حقل الإدخال
        page.update()

    send_btn = ft.Container(
        content=ft.Text("إرسال", size=16, color="white"),
        width=60,
        height=45,
        alignment=ft.alignment.center,
        bgcolor=primary_color,
        border_radius=10,
        on_click=send_question,
        tooltip="إرسال السؤال"
    )

    def toggle_theme(e):
        if page.theme_mode == "light":
            page.theme_mode = "dark"
            theme_btn.content = ft.Text("☀️", size=20)
            theme_btn.tooltip = "الوضع النهاري"
            # تحديث الألوان للوضع الداكن
            user_input.fill_color = "#2A2A2A"
            user_input.border_color = "#444444"
            user_input.hint_style = ft.TextStyle(color="#AAAAAA", size=16)
            input_container.bgcolor = "#1E1E1E"
            header.bgcolor = "#252526"
        else:
            page.theme_mode = "light"
            theme_btn.content = ft.Text("🌙", size=20)
            theme_btn.tooltip = "الوضع الليلي"
            # إعادة الألوان للوضع الفاتح
            user_input.fill_color = "#F0F8FF"
            user_input.border_color = "#D0E0F0"
            user_input.hint_style = ft.TextStyle(color=light_text, size=16)
            input_container.bgcolor = "white"
            header.bgcolor = primary_color
        page.update()

    theme_btn = ft.Container(
        content=ft.Text("🌙", size=20),
        width=40,
        height=40,
        alignment=ft.alignment.center,
        bgcolor=accent_color,
        border_radius=20,
        on_click=toggle_theme,
        tooltip="الوضع الليلي"
    )

    header = ft.Container(
        content=ft.Row(
            [
                ft.Row(
                    [
                        ft.Container(
                            content=ft.Text("H", size=20, weight="bold", color="white"),
                            width=40,
                            height=40,
                            alignment=ft.alignment.center,
                            bgcolor=accent_color,
                            border_radius=20,
                        ),
                        ft.Column(
                            [
                                ft.Text("Healthic", size=22, weight="bold", color="white"),
                                ft.Text("Made by team 0", size=12, color="white"),
                            ],
                            spacing=0
                        )
                    ],
                    spacing=8
                ),
                theme_btn
            ],
            alignment="spaceBetween",
            vertical_alignment="center"
        ),
        padding=ft.padding.only(left=15, right=15, top=15, bottom=15),
        bgcolor=primary_color,
        border_radius=0,
        margin=0
    )

    input_container = ft.Container(
        content=ft.Row(
            [
                user_input,
                send_btn
            ],
            spacing=8,
            vertical_alignment="center"
        ),
        padding=12,
        bgcolor="white",
        border_radius=12,
        margin=ft.margin.only(left=10, right=10, bottom=10),
        shadow=ft.BoxShadow(
            spread_radius=1,
            blur_radius=5,
            color=shadow_color,
            offset=ft.Offset(0, 1)
        )
    )

    page.add(
        ft.Column(
            [
                header,
                ft.Container(
                    content=chat,
                    expand=True,
                    margin=0
                ),
                input_container
            ],
            expand=True,
            spacing=0
        )
    )

ft.app(main)
