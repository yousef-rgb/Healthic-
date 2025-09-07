import requests
import flet as ft 
import re  

# --- إعدادات الموديل والـ API --
MODEL = "deepseek/deepseek-chat-v3.1:free"
URL = "https://openrouter.ai/api/v1/chat/completions"

SYSTEM_PROMPT = (
    "أنت مساعد طبي افتراضي ذكي. دورك أن ترد على أسئلة المستخدمين المتعلقة "
    "بأي نوع من الأمراض (حاد أو مزمن). يجب أن تقدم إجابات تشمل: \n"
    "انت عبارة عن مساعد طبي متخصص قادر على الاجابة عن اي سؤال يتعلق باي شيء يخص الطب والادوية بالاضافة الى تشخيص الامراض وطرق علاجها "
    " لو اتسالت مين الي عملك او مين الي صممك او اي سؤال في السياق دا تجاوب بانه يوسف محمد ابراهيم لكن مش لازم تقول كدا في كل سؤال"
    "لو سُئلت عن أي شيء خارج المجال الطبي، رد: 'آسف، لقد صممني يوسف محمد ابراهيم على أن مساعد طبي ولست مخصصًا لهذا المجال.'"
    "جاوب عن كل سؤال بلغته بمعنى في حالة ان السؤال ان بالانجليزي جاوب بالانجليزي لو بالعربي جاوب بالعربي وكدا"
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
    page.padding = 20
    page.spacing = 15

    chat = ft.ListView(expand=True, spacing=10, padding=10, auto_scroll=True)

    user_input = ft.TextField(
        hint_text="✍️ اكتب سؤالك هنا...",
        autofocus=True,
        expand=True,
        border_radius=20,
        filled=True,
    )

    def send_question(e):
        question = user_input.value.strip()
        if not question:
            return

        # رسالة المستخدم
        chat.controls.append(
            ft.Row(
                [
                    ft.Image(src="user.png", width=24, height=24),
                    ft.Container(
                        content=ft.Text(question, size=16, color="white"),
                        bgcolor="#4a90e2",
                        padding=12,
                        border_radius=20,
                        margin=ft.margin.only(left=50),
                    )
                ],
                alignment="end"
            )
        )
        page.update()

        try:
            answer = ask_openrouter(question)
        except Exception as err:
            answer = f"[خطأ] {err}"

        # تنظيف الرموز المحددة فقط من الإجابة
        clean_answer = clean_text(answer)

        # رسالة البوت
        chat.controls.append(
            ft.Row(
                [
                    ft.Image(src="bot.png", width=24, height=24),
                    ft.Container(
                        content=ft.Text(clean_answer, size=16 , color='#0a59da' ),
                        bgcolor="#e2f7f5",
                        padding=12,
                        border_radius=20,
                        margin=ft.margin.only(right=50),
                    )
                ],
                alignment="start"
            )
        )

        user_input.value = ""  # تصفير حقل الإدخال
        page.update()

    send_btn = ft.TextButton(text="إرسال", on_click=send_question)

    def toggle_theme(e):
        page.theme_mode = "dark" if page.theme_mode == "light" else "light"
        page.update()

    theme_btn = ft.TextButton("🌓", on_click=toggle_theme)

    header = ft.Row(
        [
            ft.Image(src="Healthic.png", width=32, height=32),
            ft.Text("Healthic", size=22, weight="bold"),
            theme_btn
        ],
        alignment="spaceBetween"
    )

    page.add(
        ft.Column(
            [
                header,
                chat,
                ft.Container(
                    content=ft.Row([user_input, send_btn], spacing=10),
                    padding=10,
                )
            ],
            expand=True
        )
    )

ft.app(main)
