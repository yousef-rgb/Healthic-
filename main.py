import requests
import flet as ft 
import re  

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
    "- كن دائمًا واضحًا، علميًا، ودقيقًا، واذكر أن التشخيص المقدم مبدئي ولا يغني عن زيارة الطبيب المتخصص عند الحاجة.\n\n"

    "ملاحظات هامة:\n"
    "- لا تعطي أدوية مخالفة للمعايير الطبية العالمية.\n"
    "- عند ذكر دواء، وضّح دواعي الاستعمال والجرعة المعتادة بشكل عام، مع التنبيه أن الجرعة الدقيقة يحددها الطبيب حسب حالة المريض.\n"
)

API_KEY = "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"

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

# --- واجهة Flet ---
def main(page: ft.Page):
    page.title = "Healthic"
    page.theme_mode = "light"
    page.padding = 0
    page.spacing = 0
    
    # ألوان التطبيق
    primary_color = "#0a59da"
    secondary_color = "#e2f7f5"
    accent_color = "#4a90e2"
    text_color = "#333333"
    light_text = "#666666"
    shadow_color = "#22000000"
    
    # عناصر الواجهة
    chat = ft.ListView(
        expand=True, 
        spacing=10, 
        padding=ft.padding.only(left=15, right=15, top=10, bottom=10),
        auto_scroll=True
    )

    user_input = ft.TextField(
        hint_text="✍️ اكتب سؤالك الطبي هنا...",
        autofocus=True,
        expand=True,
        border_radius=15,
        filled=True,
        fill_color="#F0F8FF",
        border_color="#D0E0F0",
        content_padding=ft.padding.only(left=20, top=15, bottom=15, right=20),
        text_size=16,
        multiline=True,
        min_lines=1,
        max_lines=3,
        cursor_color=primary_color,
        hint_style=ft.TextStyle(color=light_text, size=16)
    )

    def send_question(e):
        question = user_input.value.strip()
        if not question:
            return

        # رسالة المستخدم
        chat.controls.append(
            ft.Container(
                content=ft.Row(
                    [
                        ft.Container(
                            content=ft.Text(question, size=16, color="white"),
                            bgcolor=primary_color,
                            padding=15,
                            border_radius=ft.border_radius.only(top_left=20, top_right=20, bottom_left=20, bottom_right=5),
                            margin=ft.margin.only(left=50),
                        ),
                        ft.Container(
                            content=ft.Text("👤", size=20),
                            width=40,
                            height=40,
                            alignment=ft.alignment.center,
                            bgcolor=secondary_color,
                            border_radius=20,
                        )
                    ],
                    alignment="end",
                    vertical_alignment="start"
                ),
                margin=ft.margin.only(bottom=15)
            )
        )
        page.update()

        try:
            answer = ask_openrouter(question)
        except Exception as err:
            answer = f"عذرًا، حدث خطأ في الاتصال: {err}"

        # تنظيف الرموز المحددة فقط من الإجابة
        clean_answer = clean_text(answer)

        # رسالة البوت
        chat.controls.append(
            ft.Container(
                content=ft.Row(
                    [
                        ft.Container(
                            content=ft.Image(
                            src="D:\\healthic\\app\\Healthic.png",   
                            width=32,                   
                            height=32,                  
                            fit=ft.ImageFit.CONTAIN,    
                        ),
                            width=40,
                            height=40,
                            alignment=ft.alignment.center,
                            bgcolor=primary_color,
                            border_radius=20,
                        ),
                        ft.Container(
                            content=ft.Column(
                                [
                                    ft.Text("Healthic", size=14, weight="bold", color=primary_color),
                                    ft.Text(clean_answer, size=16, color=text_color),
                                ],
                                spacing=5
                            ),
                            bgcolor=secondary_color,
                            padding=15,
                            border_radius=ft.border_radius.only(top_left=20, top_right=20, bottom_left=5, bottom_right=20),
                            margin=ft.margin.only(right=10),
                        )
                    ],
                    alignment="start",
                    vertical_alignment="start"
                ),
                margin=ft.margin.only(bottom=15)
            )
        )

        user_input.value = ""  # تصفير حقل الإدخال
        page.update()

    send_btn = ft.Container(
        content=ft.Text("➤", size=20, color="white"),
        width=50,
        height=50,
        alignment=ft.alignment.center,
        bgcolor=primary_color,
        border_radius=25,
        on_click=send_question,
        tooltip="إرسال السؤال"
    )

    def toggle_theme(e):
        if page.theme_mode == "light":
            page.theme_mode = "dark"
            theme_btn.content = ft.Text("☀️", size=20)
            theme_btn.tooltip = "الوضع النهاري"
        else:
            page.theme_mode = "light"
            theme_btn.content = ft.Text("🌙", size=20)
            theme_btn.tooltip = "الوضع الليلي"
        page.update()

    theme_btn = ft.Container(
        content=ft.Text("🌙", size=20),
        width=40,
        height=40,
        alignment=ft.alignment.center,
        on_click=toggle_theme,
        tooltip="الوضع الليلي"
    )

    header = ft.Container(
        content=ft.Row(
            [
                ft.Row(
                    [
                        ft.Container(
                        content=ft.Image(
                            src="D:\\healthic\\app\\Healthic.png",   
                            width=32,                   
                            height=32,                  
                            fit=ft.ImageFit.CONTAIN,    
                        )
                        ),
                        ft.Text("Healthic", size=24, weight="bold", color=primary_color),
                    ],
                    spacing=10
                ),
                theme_btn
            ],
            alignment="spaceBetween",
            vertical_alignment="center"
        ),
        padding=ft.padding.only(left=20, right=20, top=15, bottom=15),
        bgcolor="#E8F0FE",
        border_radius=ft.border_radius.only(bottom_left=20, bottom_right=20)
    )

    input_container = ft.Container(
        content=ft.Row(
            [
                user_input,
                send_btn
            ],
            spacing=10,
            vertical_alignment="center"
        ),
        padding=15,
        bgcolor="white",
        border_radius=15,
        margin=ft.margin.only(left=15, right=15, bottom=15),
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
                    margin=ft.margin.only(top=10)
                ),
                input_container
            ],
            expand=True,
            spacing=0
        )
    )

ft.app(main)
