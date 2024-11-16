import os
import yt_dlp
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from moviepy.editor import VideoFileClip
import requests

# Ganti dengan token bot Telegram kamu
TELEGRAM_BOT_TOKEN = 'YOUR_BOT_TOKEN'
FACEBOOK_ACCESS_TOKEN = 'YOUR_FACEBOOK_ACCESS_TOKEN'

# Fungsi untuk mendownload video TikTok menggunakan yt-dlp
def download_tiktok_video(url: str, output_path: str) -> str:
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',  # Pilih kualitas terbaik
        'outtmpl': output_path,  # Nama file output
        'quiet': True,  # Menyembunyikan log proses
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
        return output_path

# Fungsi untuk mengedit video (misalnya memotong bagian tertentu)
def edit_video(input_path: str, output_path: str) -> None:
    video = VideoFileClip(input_path)
    # Memotong video dari detik 0 sampai 10
    video = video.subclip(0, 10)
    video.write_videofile(output_path, codec="libx264", audio_codec="aac")

# Fungsi untuk mengupload video ke Facebook
def upload_video_to_facebook(video_path: str, access_token: str) -> None:
    url = f"https://graph-video.facebook.com/v12.0/me/videos"
    params = {'access_token': access_token}
    files = {'source': open(video_path, 'rb')}
    response = requests.post(url, params=params, files=files)
    print(response.json())  # Cek respons dari Facebook

# Fungsi untuk menangani perintah /start
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Halo! Kirimkan URL TikTok untuk mendownload dan mengedit video.')

# Fungsi untuk menangani pesan dengan URL TikTok
def download_and_edit(update: Update, context: CallbackContext) -> None:
    url = update.message.text.strip()
    
    if 'tiktok.com' in url:
        update.message.reply_text('Mendownload video TikTok...')
        
        try:
            # Nama file sementara untuk video
            video_path = 'tiktok_video.mp4'
            # Mendownload video
            download_tiktok_video(url, video_path)
            
            # Edit video (misalnya memotong 10 detik pertama)
            edited_video_path = 'edited_video.mp4'
            edit_video(video_path, edited_video_path)
            
            # Mengupload video yang sudah diedit ke Facebook
            update.message.reply_text('Video berhasil diedit! Mengupload ke Facebook...')
            upload_video_to_facebook(edited_video_path, FACEBOOK_ACCESS_TOKEN)
            
            # Mengirimkan video ke grup Telegram
            with open(edited_video_path, 'rb') as video:
                update.message.reply_video(video)
            
            # Menghapus file sementara
            os.remove(video_path)
            os.remove(edited_video_path)
        
        except Exception as e:
            update.message.reply_text(f'Gagal memproses video: {str(e)}')
    else:
        update.message.reply_text('URL tidak valid. Pastikan itu adalah URL TikTok.')

# Fungsi utama untuk menjalankan bot
def main() -> None:
    updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, download_and_edit))
    
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
