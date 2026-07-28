FROM python:3.11-slim

# ffmpeg'ni o'rnatish (video qayta ishlash uchun)
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "yumaloq_video_bot.py"]
