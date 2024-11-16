import os
import requests
from bs4 import BeautifulSoup
import facebook
from telegram.ext import ApplicationContext
from telegram import Update
from moviepy.editor import VideoFileClip

# Fungsi untuk mengunduh video dari Snack Video
def download_snack_video(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Mencari URL video dalam halaman Snack Video
    video_url = None
    for script in soup.find_all('script'):
        if 'video_url' in script.text:
            start_index = script.text.find('video_url') + len('video_url":"')
            end_index = script.text.find('"', start_index)
            video_url = script.text[start_index:end_index]
            break
    
    if video_url:
        # Mengunduh video dari URL yang ditemukan
        video_data = requests.get(video_url).content
        video_filename = "snack_video.mp4"
        
        # Menyimpan video
        with open(video_filename, "wb") as file:
            file.write(video_data)
        
        print(f"Video berhasil diunduh: {video_filename}")
        return video_filename
    else:
        print("Tidak dapat menemukan URL video.")
        return None

# Fungsi untuk mengedit video (contoh: menambahkan teks ke video)
def edit_video(video_file):
    # Menggunakan moviepy untuk menambahkan teks pada video
    clip = VideoFileClip(video_file)
    clip = clip.subclip(0, min(10, clip.duration))  # Ambil 10 detik pertama (opsional)
    clip = clip.fx(vfx.resize, width=720)  # Resize video (opsional)

    # Menambahkan teks (contoh)
    from moviepy.editor import TextClip, CompositeVideoClip
    txt_clip = TextClip("Video dari Snack Video", fontsize=24, color='white')
    txt_clip = txt_clip.set_pos('center').set_duration(clip.duration)

    # Gabungkan video dengan teks
    video_with_text = CompositeVideoClip([clip, txt_clip])

    edited_video_filename = "edited_snack_video.mp4"
    video_with_text.write_videofile(edited_video_filename, codec="libx264")

    print(f"Video berhasil diedit: {edited_video_filename}")
    return edited_video_filename

# Fungsi untuk mengunggah video ke Facebook
def upload_to_facebook(video_file, access_token):
    graph = facebook.GraphAPI(access_token=access_token, version="3.0")
    
    # Unggah video ke Facebook
    with open(video_file, "rb") as video:
        response = graph.put_video(video, title="Video Snack", description="Video dari Snack Video yang telah diunduh.")
    
    print("Video berhasil diunggah ke Facebook.")
    return response

# Fungsi untuk menangani pesan dan mengunduh video
def handle_message(update: Update, context: CallbackContext):
    message = update.message
    text = message.text

    if "snackvideo.com" in text:  # Cek apakah URL Snack Video ada dalam pesan
        try:
            video_file = download_snack_video(text)  # Mengunduh video dari Snack Video
            if video_file:
                # Mengedit video (misalnya menambahkan teks)
                edited_video_file = edit_video(video_file)

                # Token akses Facebook
                facebook_access_token = "EAAWtPtjWwGYBO2sA7uuxbTD5WymdgZCaeJZAViqZBqDpo7nLZCzOACQIRebs9y95ObylhmmoFbb78dtTBZBjfVUbYm98UqNdKh84j4FZBrNp5snKhuvPe9meWZBXCrIuy56HEF9SWAB2yRjFeRrB9jsflyskq6ZCfITJ0cEvEmwY8Qi9WKyTWaJMqagQMm9oJSIHBIx3ckfNPMoJ0WSVZAwAqWRGIRe9ewA4qPiPEoGlAjFlxbQhJBkDtg8iSh5gVBwZDZD"  # Ganti dengan token akses Facebook Anda
                
                # Mengunggah video ke Facebook
                upload_to_facebook(edited_video_file, facebook_access_token)
                
                # Mengirimkan pesan ke pengguna
                update.message.reply_text("Video berhasil diunduh, diedit, dan diunggah ke Facebook!")
                
                # Menghapus file setelah diunggah
                os.remove(video_file)
                os.remove(edited_video_file)
            else:
                update.message.reply_text("Gagal mengunduh video, pastikan URL valid.")
        except Exception as e:
            update.message.reply_text(f"Terjadi kesalahan: {str(e)}")
    else:
        update.message.reply_text("Harap kirimkan link video Snack Video.")

# Fungsi utama untuk menjalankan bot Telegram
def main():
    bot_token = "8087088334:AAEBy-5HeePWxLOfU3fbNdXPAswrarjziL4"  # Ganti dengan token API bot Telegram Anda
    updater = Updater(bot_token, use_context=True)
    
    dp = updater.dispatcher
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    
    # Mulai bot
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
    
