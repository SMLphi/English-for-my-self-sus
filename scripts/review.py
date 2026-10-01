import os
import glob
from google import genai

# Lấy API key từ biến môi trường
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found.")

client = genai.Client(api_key=api_key)

# 1. Tìm các file bài tập mới nhất trong thư mục journals/ (hoặc file daily_writing.md)
input_file = "daily_writing.md"

if not os.path.exists(input_file):
    print(f"File {input_file} chua ton tai. Tao file mau.")
    with open(input_file, "w", encoding="utf-8") as f:
        f.write("# My English Writing\n\nToday I start learning English with Gemini.")

with open(input_file, "r", encoding="utf-8") as f:
    user_content = f.read()

# 2. Định hình prompt cho Gemini
prompt = f"""
You are an expert English tutor and language coach.
Analyze the following English text written by the user:

---
{user_content}
---

Please provide a detailed, easy-to-understand feedback report in Vietnamese & English:
1. **Grammar & Spelling Corrections**: Point out mistakes, why they are wrong, and how to fix them.
2. **Better Phrasing**: Suggest more natural ways native speakers would say these sentences.
3. **Vocabulary Expansion**: Pick 3-5 useful words/collocations related to the topic.
4. **Overall Score**: Rate clarity, coherence, and grammar on a scale of 1-10 with encouraging feedback.
"""

# 3. Gửi yêu cầu tới Gemini
response = client.models.generate_content(
    model="gemini-3.8-flash",
    contents=prompt
)

# 4. Ghi kết quả nhận xét ra file feedback.md
with open("feedback.md", "w", encoding="utf-8") as f:
    f.write(response.text)

print("Feedback has been generated and saved to feedback.md!")
