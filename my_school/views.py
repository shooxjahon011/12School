
from django.utils import timezone
from django.shortcuts import redirect,get_object_or_404,render
from django.http import HttpResponse
from django.templatetags.static import static
from django.middleware.csrf import get_token
import json
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from .models import Post, Profile,Comment,Message,TeacherReels,TeacherTest,Subject,Competition,Schedule,VideoComment,ClassMessage,Teacher,TestResult, ProjectWork,Book,Notification,Order,User,Attendance,Video,Subject, Homework, HomeworkStatus,TeacherProfile
from django.contrib.auth import authenticate, login as auth_login
import re
from django.contrib.auth.decorators import login_required
import random
from django.db.models import Count
from django.db.models import Prefetch
from django.db import transaction
from datetime import date
def submit_project_view(request):
    user_login = request.session.get('user_login')
    if not user_login:
        return redirect('/')

    user = Profile.objects.filter(login=user_login).first()
    if not user:
        return redirect('/')

    subjects = Subject.objects.all()

    # POST so'rovi kelganda ma'lumotlarni saqlash
    if request.method == "POST":
        pdf = request.FILES.get('project_file')
        subject_id = request.POST.get('subject')
        info = request.POST.get('members_info')

        ProjectWork.objects.create(
            student=user,
            pdf_file=pdf,
            subject_id=subject_id,
            members_info=info
        )
        return redirect('/second/')

    token = get_token(request)
    bg_image_url = static('12.jpg')

    # Fanni tanlash opsiyalari
    subjects_options = ""
    for s in subjects:
        teacher_name = s.teacher_user.get_full_name() or s.teacher_user.username
        subjects_options += f'<option value="{s.id}">{s.name} (Ustoz: {teacher_name})</option>'

    html = f"""
    <!DOCTYPE html>
    <html lang="uz">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Loyiha Topshirish</title>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
        <style>
            :root {{ --neon: #00f2ff; --glass: rgba(255, 255, 255, 0.1); }}
            body {{ 
                margin: 0; background: url('{bg_image_url}') no-repeat center center fixed; 
                background-size: cover; font-family: 'Segoe UI', sans-serif; 
                display: flex; justify-content: center; align-items: center; 
                min-height: 100vh; color: #fff;
                padding-bottom: 80px; /* Navigatsiya uchun joy */
            }}
            .overlay {{ position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0, 0, 0, 0.85); z-index: -1; }}
            .card {{ 
                background: rgba(20, 20, 20, 0.6); backdrop-filter: blur(25px); 
                padding: 25px; border-radius: 35px; width: 90%; max-width: 400px; 
                border: 1px solid rgba(0, 242, 255, 0.2); box-shadow: 0 15px 35px rgba(0, 0, 0, 0.5);
                position: relative; z-index: 1;
            }}
            h2 {{ color: var(--neon); text-align: center; font-size: 20px; text-transform: uppercase; margin-bottom: 20px; letter-spacing: 1px; }}
            .input-group {{ margin-bottom: 15px; text-align: left; }}
            label {{ font-size: 11px; color: var(--neon); font-weight: bold; margin-left: 10px; text-transform: uppercase; opacity: 0.8; }}
            select, input, textarea {{ 
                width: 100%; padding: 14px; border-radius: 18px; border: 1px solid rgba(255,255,255,0.1); 
                background: rgba(0, 0, 0, 0.5); color: #fff; font-weight: 500; margin-top: 5px; outline: none; box-sizing: border-box;
            }}
            select:focus, textarea:focus {{ border-color: var(--neon); }}
            .file-upload-box {{ 
                border: 2px dashed rgba(0, 242, 255, 0.3); padding: 20px; border-radius: 20px; 
                text-align: center; cursor: pointer; display: block; transition: 0.3s;
                margin-top: 5px;
            }}
            .file-upload-box:hover {{ border-color: var(--neon); background: rgba(0, 242, 255, 0.05); }}
            .btn-submit {{ 
                width: 100%; padding: 18px; border-radius: 20px; border: none; 
                background: var(--neon); color: #000; font-weight: 900; cursor: pointer;
                text-transform: uppercase; margin-top: 10px; transition: 0.3s;
            }}
            .btn-submit:hover {{ transform: translateY(-2px); box-shadow: 0 5px 15px rgba(0, 242, 255, 0.4); }}

            /* BOTTOM NAV STYLE */
            .bottom-nav {{
                position: fixed;
                bottom: 0;
                left: 0;
                width: 100%;
                background: rgba(10, 10, 10, 0.95);
                backdrop-filter: blur(10px);
                display: flex;
                justify-content: space-around;
                padding: 12px 0;
                border-top: 1px solid rgba(255,255,255,0.1);
                z-index: 1000;
            }}
            .nav-item {{
                text-decoration: none;
                color: #888;
                display: flex;
                flex-direction: column;
                align-items: center;
                font-size: 11px;
                transition: 0.3s;
            }}
            .nav-item i {{ font-size: 20px; margin-bottom: 4px; }}
            .nav-item.active {{ color: var(--neon); }}
        </style>
    </head>
    <body>
        <div class="overlay"></div>
        <div class="card">
            <h2><i class="fas fa-file-alt"></i> LOYIHA TOPSHIRISH</h2>
            <form method="POST" enctype="multipart/form-data">
                <input type="hidden" name="csrfmiddlewaretoken" value="{token}">

                <div class="input-group">
                    <label>Loyiha fayli (Faqat PDF):</label>
                    <label for="project_file" class="file-upload-box">
                        <i class="fas fa-cloud-upload-alt" style="font-size:30px; color:var(--neon);"></i><br>
                        <span id="file-name" style="font-size: 13px;">PDF faylni tanlang</span>
                        <input type="file" name="project_file" id="project_file" accept=".pdf" required style="display:none;" onchange="updateFileName(this)">
                    </label>
                </div>

                <div class="input-group">
                    <label>Fanni tanlang:</label>
                    <select name="subject" required>
                        <option value="" disabled selected>Ro'yxatdan tanlang</option>
                        {subjects_options}
                    </select>
                </div>

                <div class="input-group">
                    <label>Guruh a'zolari (Ism-familiya):</label>
                    <textarea name="members_info" rows="3" placeholder="Masalan: Ali Valiyev 9-A, Guli Aliyeva 9-B" required></textarea>
                </div>

                <button type="submit" class="btn-submit">YUKLASHNI YAKUNLASH</button>
            </form>
        </div>

        <nav class="bottom-nav">
            <a href="/second/" class="nav-item active"><i class="fas fa-th-large"></i><span>Menyu</span></a>
            <a href="/library/" class="nav-item"><i class="fas fa-book"></i><span>Kutubxona</span></a>
            <a href="/reels/" class="nav-item"><i class="fas fa-play-circle"></i><span>Reels</span></a>
            <a href="/profile/" class="nav-item"><i class="fas fa-user"></i><span>Profil</span></a>
        </nav>

        <script>
            function updateFileName(input) {{
                const fileName = input.files[0] ? input.files[0].name : "PDF faylni tanlang";
                const display = document.getElementById('file-name');
                display.textContent = fileName;
                display.style.color = "#00f2ff";
                display.style.fontWeight = "bold";
            }}
        </script>
    </body>
    </html>
    """
    return HttpResponse(html)
@csrf_exempt
def comment_post(request, post_id):
    # 1. Foydalanuvchini tekshirish
    user_login = request.session.get('user_login')
    if not user_login:
        return JsonResponse({'status': 'error', 'message': 'Login talab qilinadi'}, status=403)

    user = Profile.objects.filter(login=user_login).first()
    post = get_object_or_404(Post, id=post_id)

    # 2. Yangi izoh qo'shish (POST)
    if request.method == "POST":
        text = request.POST.get('text')
        if text:
            comment = Comment.objects.create(
                post=post,
                author=user,
                text=text
            )

            # Izoh muvaffaqiyatli qo'shilgach, kerakli ma'lumotlarni qaytaramiz
            return JsonResponse({
                'status': 'ok',
                'count': post.comments.count(),
                'author': user.full_name,
                'author_login': user.login,
                'avatar': user.image.url if user.image else static('default_avatar.png'),
                'text': text,
                'created_at': "Hozirgina"
            })

    # 3. Izohlarni olish (GET yoki xato POST bo'lsa)
    comments_list = []
    for c in post.comments.all().order_by('-created_at'):
        comments_list.append({
            'author': c.author.full_name,
            'avatar': c.author.image.url if c.author.image else static('default_avatar.png'),
            'text': c.text,
            'date': c.created_at.strftime("%H:%M")
        })

    return JsonResponse({
        'comments': comments_list,
        'count': post.comments.count()
    })
def place_order(request, book_id):
    # 1. Foydalanuvchi tizimga kirganini tekshirish
    user_login = request.session.get('user_login')
    if not user_login:
        return redirect('/')

    # 2. Foydalanuvchi va Kitobni bazadan olish
    user = Profile.objects.filter(login=user_login).first()
    book = get_object_or_404(Book, id=book_id)

    # 3. Kitob zaxirasini tekshirish
    if book.count > 0:
        # Buyurtma yaratish (modelda 'student' emas 'user' deb o'zgartirganmiz)
        Order.objects.create(
            user=user,
            book=book,
            is_returned=False
        )

        # Kitob sonini bittaga kamaytirish
        book.count -= 1
        book.save()

        return HttpResponse("""
            <script>
                alert('Muvaffaqiyatli: Buyurtmangiz qabul qilindi. Kutubxonaga borib kitobni olishingiz mumkin!'); 
                window.location.href='/library/';
            </script>
        """)
    else:
        # Agar kitob qolmagan bo'lsa
        return HttpResponse("""
            <script>
                alert('Xatolik: Afsuski, ushbu kitobdan hozircha qolmagan.'); 
                window.location.href='/library/';
            </script>
        """)
def return_book_view(request, order_id):
    # 1. Faqat kutubxonachi kira olishini tekshirish (ixtiyoriy lekin tavsiya etiladi)
    user_login = request.session.get('user_login')
    if user_login != "Kutubxona2026":
        return redirect('/second/')

    # 2. Buyurtmani bazadan olish
    order = get_object_or_404(Order, id=order_id)

    # 3. Agar kitob hali qaytarilmagan bo'lsa, mantiqni bajaramiz
    if not order.is_returned:
        book = order.book
        book.count += 1  # Kitob zaxirasini bittaga ko'paytiramiz
        book.save()

        order.is_returned = True  # Buyurtma holatini "Qaytarildi"ga o'zgartiramiz
        order.save()

        # Bu yerda o'quvchiga "Rahmat" bildirishnomasi yuborish mantiqini ham qo'shsa bo'ladi
        Notification.objects.create(
            user=order.user,
            text=f"'{book.title}' kitobini qaytarganingiz uchun rahmat!"
        )

    # 4. Ro'yxat sahifasiga qaytarish
    return redirect('/library/orders/')
def book_orders_view(request):
    # 1. Faqat kutubxonachi kira olishini tekshirish
    if request.session.get('user_login') != "Kutubxona2026":
        return redirect('/second/')

    # 2. Qaytarilmagan buyurtmalarni olish
    orders = Order.objects.filter(is_returned=False).order_by('-order_date')
    order_list_html = ""

    for o in orders:
        # O'quvchining to'liq manzili
        u = o.user
        if u:
            address = f"{u.mahalla} mfy, {u.kocha} ko'chasi, {u.uy}-uy"
            full_name = u.full_name
            class_info = f"{u.sinf}-{u.parallel}"
            phone = u.phone if u.phone else u.parent_phone
        else:
            address = "Noma'lum"
            full_name = "O'chirilgan foydalanuvchi"
            class_info = "-"
            phone = "-"

        order_list_html += f"""
        <div class="order-card">
            <div class="order-header">
                <i class="fas fa-book" style="color:#00f2ff;"></i>
                <span style="font-weight:900; font-size:16px;">{o.book.title}</span>
            </div>
            <div class="order-body">
                <p><i class="fas fa-user"></i> <b>O'quvchi:</b> {full_name} ({class_info})</p>
                <p><i class="fas fa-phone"></i> <b>Tel:</b> {phone}</p>
                <p><i class="fas fa-map-marker-alt"></i> <b>Manzil:</b> {address}</p>
                <p><i class="fas fa-calendar-alt"></i> <b>Sana:</b> {o.order_date.strftime('%d.%m.%Y | %H:%M')}</p>
            </div>
            <a href="/library/return/{o.id}/" class="btn-return">KUTUBXONAGA QAYTARDI</a>
        </div>
        """

    bg_image_url = static('12.jpg')

    html = f"""
    <!DOCTYPE html>
    <html lang="uz">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Buyurtmalar Nazorati</title>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
        <style>
            body {{ 
                background: url('{bg_image_url}') no-repeat center center fixed; 
                background-size: cover; font-family: 'Segoe UI', sans-serif; 
                margin: 0; padding: 20px; color: #fff; 
            }}
            .overlay {{ position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.85); z-index: -1; }}
            .container {{ max-width: 500px; margin: 0 auto; }}

            h2 {{ color: #00f2ff; text-align: center; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 30px; }}

            .order-card {{ 
                background: rgba(255,255,255,0.05); backdrop-filter: blur(15px); 
                border-radius: 20px; padding: 20px; margin-bottom: 20px; 
                border: 1px solid rgba(0,242,255,0.2); box-shadow: 0 10px 30px rgba(0,0,0,0.5);
            }}
            .order-header {{ border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 10px; margin-bottom: 15px; }}
            .order-body p {{ margin: 8px 0; font-size: 14px; color: #ddd; }}
            .order-body i {{ width: 20px; color: #00f2ff; margin-right: 5px; }}

            .btn-return {{ 
                display: block; background: #00f2ff; color: #000; text-align: center; 
                padding: 12px; border-radius: 12px; text-decoration: none; 
                font-weight: 900; margin-top: 15px; transition: 0.3s;
            }}
            .btn-return:hover {{ background: #fff; transform: scale(1.02); }}
            .back-link {{ color: #fff; text-decoration: none; font-weight: bold; font-size: 14px; }}
        </style>
    </head>
    <body>
        <div class="overlay"></div>
        <div class="container">
            <a href="/second/" class="back-link"><i class="fas fa-arrow-left"></i> ASOSIY MENYU</a>
            <h2><i class="fas fa-clipboard-list"></i> Buyurtmalar</h2>

            {order_list_html if order_list_html else "<p style='text-align:center; opacity:0.5;'>Hozircha faol buyurtmalar yo'q.</p>"}
        </div>
    </body>
    </html>
    """
    return HttpResponse(html)
@csrf_exempt
def add_book_view(request):
    # 1. Faqat kutubxonachi kira olishini tekshirish
    if request.session.get('user_login') != "Kutubxona2026":
        return redirect('/second/')

    if request.method == "POST":
        title = request.POST.get('title')
        author = request.POST.get('author')
        genre = request.POST.get('genre')
        count = request.POST.get('count', 1)

        # Open Library API orqali muqova rasmini avtomatik shakllantirish
        img_url = f"https://covers.openlibrary.org/b/title/{title.replace(' ', '+')}-L.jpg"

        Book.objects.create(
            title=title,
            author=author,
            genre=genre,
            count=int(count),
            image_url=img_url
        )
        return HttpResponse("""
            <script>
                alert('Yangi kitob muvaffaqiyatli qo‘shildi!'); 
                window.location.href='/second/';
            </script>
        """)

    # Sahifa dizayni
    bg_image_url = static('12.jpg')  # Asosiy fon rasmi

    html = f"""
    <!DOCTYPE html>
    <html lang="uz">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Kitob Qo'shish | Kutubxona</title>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
        <style>
            :root {{ --neon: #00f2ff; --glass: rgba(255, 255, 255, 0.1); }}
            body {{ 
                margin: 0; background: url('{bg_image_url}') no-repeat center center fixed; 
                background-size: cover; font-family: 'Segoe UI', sans-serif; 
                display: flex; justify-content: center; align-items: center; 
                height: 100vh; color: #fff;
            }}
            .overlay {{ position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0, 0, 0, 0.8); z-index: -1; }}

            .box {{ 
                background: var(--glass); backdrop-filter: blur(20px); 
                padding: 40px 30px; border-radius: 30px; 
                width: 90%; max-width: 350px; 
                border: 1px solid rgba(0, 242, 255, 0.3); 
                box-shadow: 0 15px 35px rgba(0, 0, 0, 0.5);
                text-align: center;
            }}

            h3 {{ color: var(--neon); text-transform: uppercase; letter-spacing: 2px; margin-bottom: 25px; }}

            .input-group {{ position: relative; margin-bottom: 15px; }}
            .input-group i {{ position: absolute; left: 15px; top: 15px; color: var(--neon); }}

            input {{ 
                width: 100%; padding: 14px 15px 14px 45px; border-radius: 15px; 
                border: none; background: rgba(255, 255, 255, 0.9); 
                color: #000; font-weight: 600; outline: none; box-sizing: border-box;
            }}

            button {{ 
                width: 100%; padding: 15px; background: var(--neon); 
                border: none; border-radius: 15px; font-weight: 900; 
                color: #000; cursor: pointer; transition: 0.3s; 
                text-transform: uppercase; margin-top: 10px;
            }}
            button:hover {{ transform: scale(1.03); background: #fff; box-shadow: 0 0 20px var(--neon); }}

            .back-btn {{ display: block; margin-top: 20px; color: #aaa; text-decoration: none; font-size: 13px; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="overlay"></div>
        <div class="box">
            <i class="fas fa-book-medical" style="font-size: 40px; color: var(--neon); margin-bottom: 15px;"></i>
            <h3>Yangi Kitob</h3>

            <form method="POST">
                <div class="input-group">
                    <i class="fas fa-heading"></i>
                    <input type="text" name="title" placeholder="Kitob nomi" required>
                </div>
                <div class="input-group">
                    <i class="fas fa-user-edit"></i>
                    <input type="text" name="author" placeholder="Muallifi" required>
                </div>
                <div class="input-group">
                    <i class="fas fa-tags"></i>
                    <input type="text" name="genre" placeholder="Janri (masalan: Badiiy)" required>
                </div>
                <div class="input-group">
                    <i class="fas fa-sort-numeric-up"></i>
                    <input type="number" name="count" placeholder="Soni" min="1" value="1" required>
                </div>

                <button type="submit">JOYLASHTIRISH</button>
            </form>

            <a href="/second/" class="back-btn">← ORQAGA QAYTISH</a>
        </div>
    </body>
    </html>
    """
    return HttpResponse(html)
@csrf_exempt
def order_process_view(request, book_id):
    # 1. Sessiyadan foydalanuvchi loginini olish
    user_login = request.session.get('user_login')
    if not user_login:
        return redirect('/')

    # 2. Foydalanuvchi va Kitobni bazadan olish (Xatolikdan himoyalangan holda)
    user = Profile.objects.filter(login=user_login).first()
    if not user:
        return redirect('/')

    book = get_object_or_404(Book, id=book_id)

    # 3. Kitob mavjudligini tekshirish
    if book.count > 0:
        # Buyurtma yaratish
        Order.objects.create(
            book=book,
            user=user,
            is_returned=False  # Yangi buyurtma hali qaytarilmagan holatda bo'ladi
        )

        # Kitob sonini bazada bittaga kamaytirish
        book.count -= 1
        book.save()

        # O'quvchiga bildirishnoma yuborish (ixtiyoriy)
        Notification.objects.create(
            user=user,
            text=f"Siz '{book.title}' kitobiga buyurtma berdingiz. Uni kutubxonadan olishingiz mumkin."
        )

        return HttpResponse("""
            <script>
                alert('Buyurtma berildi! Kutubxonaga borib kitobingizni oling.'); 
                window.location.href='/library/';
            </script>
        """)
    else:
        # Agar kitob soni 0 bo'lsa
        return HttpResponse("""
            <script>
                alert('Afsuski, bu kitob hozircha qolmagan!'); 
                window.location.href='/library/';
            </script>
        """)
def library_view(request):
    user_login = request.session.get('user_login')
    if not user_login:
        return redirect('/')

    query = request.GET.get('q', '')
    # Faqat soni 0 dan ko'p kitoblar chiqadi
    books = Book.objects.filter(
        (Q(title__icontains=query) | Q(author__icontains=query)),
        count__gt=0
    ).order_by('-id')

    book_cards = ""
    for b in books:
        book_cards += f"""
        <div class="book-card" onclick="openOrderModal('{b.title}', '{b.author}', '{b.image_url}', '{b.id}')">
            <div class="badge">Yangi</div>
            <img src="{b.image_url}" onerror="this.src='https://via.placeholder.com/150x220?text=Muqova+yoq'" class="book-img">
            <div class="book-info">
                <h4>{b.title}</h4>
                <p>{b.author}</p>
                <div class="book-footer">
                    <span><i class="fas fa-layer-group"></i> {b.count} ta</span>
                    <span class="genre-tag">{b.genre}</span>
                </div>
            </div>
        </div>
        """

    bg_image_url = static('12.jpg')  # Fon rasmi

    html = f"""
    <!DOCTYPE html>
    <html lang="uz">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Kutubxona | Digital School</title>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
        <style>
            :root {{ --neon: #00f2ff; --glass: rgba(255, 255, 255, 0.1); }}
            body {{ 
                background: url('{bg_image_url}') no-repeat center center fixed; 
                background-size: cover; font-family: 'Segoe UI', sans-serif; 
                margin: 0; padding: 20px; color: #fff; 
            }}
            .overlay {{ position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); z-index: -1; }}

            .header-nav {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }}
            .back-btn {{ color: var(--neon); text-decoration: none; font-weight: bold; font-size: 14px; }}

            .search-box {{ 
                position: relative; margin-bottom: 30px; 
            }}
            .search-bar {{ 
                width: 100%; padding: 15px 20px 15px 50px; border-radius: 20px; 
                border: 1px solid rgba(0,242,255,0.3); background: var(--glass); 
                backdrop-filter: blur(10px); color: #fff; outline: none; box-sizing: border-box;
                font-size: 16px; transition: 0.3s;
            }}
            .search-bar:focus {{ border-color: var(--neon); box-shadow: 0 0 15px rgba(0,242,255,0.2); }}
            .search-box i {{ position: absolute; left: 20px; top: 18px; color: var(--neon); }}

            .grid {{ 
                display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); 
                gap: 20px; padding-bottom: 40px;
            }}
            .book-card {{ 
                background: var(--glass); backdrop-filter: blur(15px); 
                border-radius: 20px; overflow: hidden; cursor: pointer; 
                transition: 0.3s; border: 1px solid rgba(255,255,255,0.1);
                position: relative;
            }}
            .book-card:hover {{ transform: translateY(-10px); border-color: var(--neon); }}
            .badge {{ 
                position: absolute; top: 10px; right: 10px; background: var(--neon); 
                color: #000; font-size: 10px; font-weight: 900; padding: 3px 8px; 
                border-radius: 5px; z-index: 1;
            }}
            .book-img {{ width: 100%; height: 220px; object-fit: cover; border-bottom: 1px solid rgba(255,255,255,0.1); }}
            .book-info {{ padding: 12px; }}
            .book-info h4 {{ margin: 0; color: var(--neon); font-size: 15px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
            .book-info p {{ margin: 5px 0; color: #ccc; font-size: 12px; }}

            .book-footer {{ display: flex; justify-content: space-between; align-items: center; margin-top: 10px; }}
            .book-footer span {{ font-size: 11px; font-weight: bold; color: #ffd700; }}
            .genre-tag {{ background: rgba(0,242,255,0.1); color: var(--neon) !important; padding: 2px 6px; border-radius: 4px; }}

            /* MODAL STYLES */
            #modalBackdrop {{ 
                display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; 
                background: rgba(0,0,0,0.9); backdrop-filter: blur(10px); z-index: 10000; 
                justify-content: center; align-items: center; padding: 20px;
            }}
            .modal-box {{ 
                background: rgba(20,20,20,0.95); padding: 30px; border-radius: 30px; 
                width: 100%; max-width: 350px; text-align: center; 
                border: 1.5px solid var(--neon); box-shadow: 0 0 50px rgba(0,242,255,0.2);
            }}
            .order-confirm-btn {{ 
                display: block; background: var(--neon); color: #000; padding: 15px; 
                border-radius: 15px; text-decoration: none; font-weight: 900; 
                margin-top: 25px; text-transform: uppercase; transition: 0.3s;
            }}
            .order-confirm-btn:hover {{ background: #fff; transform: scale(1.02); }}
            .cancel-btn {{ background: none; border: none; color: #ff4444; margin-top: 15px; font-weight: bold; cursor: pointer; }}
        </style>
    </head>
    <body>
        <div class="overlay"></div>

        <div class="header-nav">
            <a href="/second/" class="back-btn"><i class="fas fa-chevron-left"></i> ORQAGA</a>
            <i class="fas fa-book-reader" style="font-size: 24px; color: var(--neon);"></i>
        </div>

        <h2 style="text-align:center; font-weight:900; letter-spacing:1px; text-transform:uppercase;">Maktab Kutubxonasi</h2>

        <div class="search-box">
            <form method="GET">
                <i class="fas fa-search"></i>
                <input type="text" name="q" class="search-bar" placeholder="Kitob nomi yoki muallif..." value="{query}">
            </form>
        </div>

        <div class="grid">
            {book_cards if book_cards else "<p style='grid-column: 1/-1; text-align:center; opacity:0.5;'>Kitoblar topilmadi.</p>"}
        </div>

        <div id="modalBackdrop">
            <div class="modal-box">
                <img id="mImg" src="" style="width:120px; height:170px; border-radius:15px; object-fit:cover; margin-bottom:15px; box-shadow: 0 10px 20px rgba(0,0,0,0.5);">
                <h3 id="mTitle" style="color:var(--neon); margin:0 0 5px 0;"></h3>
                <p id="mAuthor" style="color:#aaa; font-size:14px; margin:0;"></p>

                <div style="margin-top:20px; font-size:13px; color:#eee; border-top:1px solid rgba(255,255,255,0.1); padding-top:15px; line-height:1.6;">
                    Ushbu kitobni 7 kunga ijaraga olishni <br><b>tasdiqlaysizmi?</b>
                </div>

                <a id="mLink" href="" class="order-confirm-btn">TASDIQLASH</a>
                <button onclick="closeModal()" class="cancel-btn">BEKOR QILISH</button>
            </div>
        </div>

        <script>
            function openOrderModal(title, author, img, id) {{
                document.getElementById('mTitle').innerText = title;
                document.getElementById('mAuthor').innerText = author;
                document.getElementById('mImg').src = img;
                document.getElementById('mLink').href = "/library/order/" + id + "/";
                document.getElementById('modalBackdrop').style.display = 'flex';
            }}

            function closeModal() {{
                document.getElementById('modalBackdrop').style.display = 'none';
            }}

            window.onclick = function(event) {{
                let modal = document.getElementById('modalBackdrop');
                if (event.target == modal) {{ closeModal(); }}
            }}
        </script>
    </body>
    </html>
    """
    return HttpResponse(html)
def second_view(request):
    user_login = request.session.get('user_login')
    if not user_login:
        return redirect('/')

    user = Profile.objects.filter(login=user_login).first()
    if not user:
        return redirect('/')

    is_librarian = (user_login == "Kutubxona2026")
    bg_image_url = static('12.jpg')

    try:
        avatar_url = user.image.url if user.image else static('default_avatar.png')
    except:
        avatar_url = static('default_avatar.png')

    display_name = user.full_name if user.full_name else user.login

    # 1. ACTION BUTTONS (Tugmalar qismi)
    if is_librarian:
        new_orders = Order.objects.filter(is_returned=False).count()
        action_btns_html = f"""
        <div class="action-btns">
            <a href="/library/orders/" class="mini-btn" style="background:#ffd700; color:#000;">
                <i class="fas fa-bell"></i> {new_orders} yangi
            </a>
            <a href="/post-view/" class="mini-btn plus-btn"><i class="fas fa-plus"></i></a>
        </div>"""
    else:
        # ODDIY FOYDALANUVCHILAR UCHUN VIDEO YUKLASH TUGMASI (+)
        action_btns_html = f"""
        <div class="action-btns">
            <a href="/upload-video/" class="mini-btn plus-btn" style="background: var(--accent); color: #000; width: 40px; height: 40px; font-size: 18px;">
                <i class="fas fa-plus"></i>
            </a>
        </div>"""

    # 2. MAIN MENU CONTENT (Asosiy menyu)
    if is_librarian:
        menu_content = f"""
        <div class="grid-2" style="grid-template-columns: 1fr;">
            <a href="/library/add/" class="glass-card" style="border: 2px solid #ffd700; padding: 40px 20px;">
                <i class="fas fa-plus-circle" style="color: #ffd700; font-size: 50px;"></i>
                <span style="font-size: 18px; font-weight: 900; margin-top: 15px; color: #ffd700;">YANGI KITOB QO'SHISH</span>
            </a>
            <div class="grid-2" style="margin-top:15px; width:100%;">
                <a href="/library/orders/" class="glass-card"><i class="fas fa-clipboard-list"></i><span>Buyurtmalar</span></a>
                <a href="/library/" class="glass-card"><i class="fas fa-book"></i><span>Kitoblar bazasi</span></a>
            </div>
        </div>"""
    else:
        menu_content = f"""
        <div class="grid-2">
            <a href="/student-schedule/" class="glass-card" style="border: 1px solid var(--accent); background: rgba(0,242,255,0.1);">
                <i class="fas fa-calendar-alt"></i>
                <span>Dars jadvalim</span>
                <small style="font-size: 9px; opacity: 0.7;">{user.sinf}-{user.parallel} sinfi</small>
            </a>
            <a href="/subjects/" class="glass-card"><i class="fas fa-tasks"></i><span>Vazifalar</span></a>
            <a href="/chat/" class="glass-card"><i class="fas fa-comment-dots"></i><span>Sinf Chat</span></a>
            <a href="/library/" class="glass-card"><i class="fas fa-book-reader"></i><span>Kutubxona</span></a>
            <a href="/compete/" class="glass-card"><i class="fas fa-trophy"></i><span>Testlar</span></a>
            <a href="/projects/" class="glass-card"><i class="fas fa-project-diagram"></i><span>Loyiha topshirish</span></a>

            <a href="https://kahoot.com/" class="glass-card" style="grid-column: span 2; background: rgba(70, 23, 143, 0.2); border: 1.5px solid #46178f;">
                <i class="fas fa-gamepad" style="color: #fff;"></i>
                <span style="font-size: 15px; font-weight: 800; letter-spacing: 1px;">Kahoot</span>
            </a>
        </div>"""

    # 3. FULL HTML STRUCTURE
    full_html = f"""
<!DOCTYPE html>
<html lang="uz">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>12-Maktab | Dashboard</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        :root {{ --accent: #00f2ff; --glass: rgba(255, 255, 255, 0.08); --blur: blur(20px); }}
        body {{ 
            margin: 0; background: url('{bg_image_url}') no-repeat center center fixed; 
            background-size: cover; color: #fff; font-family: 'Segoe UI', sans-serif;
            overflow-x: hidden;
        }}
        .overlay {{ position: fixed; inset: 0; background: rgba(0, 0, 0, 0.82); z-index: -1; }}
        .top-bar {{ display: flex; flex-direction: column; align-items: flex-end; padding: 20px 5%; position: relative; }}
        .google-logo {{ position: absolute; left: 5%; top: 25px; font-size: 22px; font-weight: 900; letter-spacing: -1px; }}
        .g-blue {{ color: #4285F4; }} .g-red {{ color: #EA4335; }} .g-yellow {{ color: #FBBC05; }} .g-green {{ color: #34A853; }}

        .prof-pill {{ 
            display: flex; align-items: center; gap: 10px; background: rgba(255,255,255,0.1); 
            padding: 6px 15px; border-radius: 30px; border: 1px solid var(--accent); 
            backdrop-filter: var(--blur); text-decoration: none; color: #fff; 
        }}
        .prof-pill img {{ width: 32px; height: 32px; border-radius: 50%; object-fit: cover; border: 1.5px solid #fff; }}

        .action-btns {{ display: flex; gap: 10px; margin-top: 12px; }}
        .mini-btn {{ background: var(--accent); color: #000; padding: 7px 15px; border-radius: 12px; font-size: 11px; font-weight: 800; text-decoration: none; transition: 0.3s; }}
        .plus-btn {{ width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; padding: 0; box-shadow: 0 0 15px var(--accent); }}
        .plus-btn:active {{ transform: scale(0.9); }}

        .main-content {{ max-width: 500px; margin: 0 auto; padding: 10px 15px 120px; }}
        .grid-2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }}
        .glass-card {{ 
            background: var(--glass); border: 1px solid rgba(255,255,255,0.1); 
            border-radius: 25px; padding: 22px 10px; text-align: center; 
            text-decoration: none; color: #fff; display: flex; 
            flex-direction: column; align-items: center; gap: 10px; 
            backdrop-filter: var(--blur); transition: 0.3s; 
        }}
        .glass-card:active {{ transform: scale(0.96); opacity: 0.8; }}
        .glass-card i {{ font-size: 30px; color: var(--accent); }}
        .glass-card span {{ font-size: 13px; font-weight: 600; }}

        .bottom-nav {{ 
            position: fixed; bottom: 15px; left: 5%; width: 90%; height: 65px; 
            background: rgba(255,255,255,0.1); backdrop-filter: blur(25px); 
            display: flex; justify-content: space-around; align-items: center; 
            border-radius: 25px; border: 1px solid rgba(255,255,255,0.1); z-index: 1000;
        }}
        .nav-item {{ display: flex; flex-direction: column; align-items: center; color: rgba(255,255,255,0.5); text-decoration: none; font-size: 10px; gap: 5px; }}
        .active {{ color: var(--accent); }}
    </style>
</head>
<body>
    <div class="overlay"></div>
    <div class="top-bar">
        <div class="google-logo">
            <span class="g-blue">1</span><span class="g-red">2</span><span class="g-yellow">-</span><span class="g-blue">M</span><span class="g-green">a</span><span class="g-red">k</span><span class="g-blue">t</span><span class="g-green">a</span><span class="g-yellow">b</span>
        </div>
        <a href="/profile/" class="prof-pill">
            <span style="font-size: 13px; font-weight: 700;">{display_name}</span>
            <img src="{avatar_url}">
        </a>
        {action_btns_html}
    </div>

    <div class="main-content">
        {menu_content}
    </div>

    <nav class="bottom-nav">
        <a href="/second/" class="nav-item active"><i class="fas fa-th-large"></i><span>Menyu</span></a>
        <a href="/library/" class="nav-item"><i class="fas fa-book"></i><span>Kutubxona</span></a>
        <a href="/reels/" class="nav-item"><i class="fas fa-play-circle"></i><span>Reels</span></a>
        <a href="/profile/" class="nav-item"><i class="fas fa-user"></i><span>Profil</span></a>
    </nav>
</body>
</html>"""

    return HttpResponse(full_html)
def profile_view(request, username=None):
    my_login = request.session.get('user_login')
    target_username = username if username else my_login
    if not target_username:
        return redirect('/')

    # Foydalanuvchini olish
    user = get_object_or_404(Profile, login=target_username)

    # 1. ROLLARNI TEKSHIRISH
    if not username and hasattr(user, 'is_teacher') and user.is_teacher:
        return redirect('teacher_dashboard')

    is_owner = (my_login == user.login)
    token = get_token(request)

    # Tizimga kirgan odam ob'ekti
    me = Profile.objects.filter(login=my_login).first()

    # 2. STATISTIKA (OBUNALAR)
    followers_count = user.followers.count() if hasattr(user, 'followers') else 0
    following_count = user.following.count() if hasattr(user, 'following') else 0

    # Obuna holati
    is_following = False
    if me and not is_owner:
        is_following = me.following.filter(id=user.id).exists()

    # 3. MA'LUMOTLARNI YANGILASH
    if request.method == "POST" and is_owner:
        new_nickname = request.POST.get('nickname')
        if new_nickname and new_nickname != user.login:
            if not Profile.objects.filter(login=new_nickname).exists():
                user.login = new_nickname
                request.session['user_login'] = new_nickname
        if request.FILES.get('profile_image'):
            user.image = request.FILES.get('profile_image')
        user.save()
        return redirect(f'/profile/{user.login}/')

    avatar_url = user.image.url if user.image else f"https://ui-avatars.com/api/?name={user.login}"
    bg_image = static('12.jpg')

    # OBUNA TUGMASI HTML
    follow_btn_html = ""
    if not is_owner:
        btn_text = "FOLLOWING" if is_following else "OBUNA BO'LISH"
        btn_style = "background:white; color:black;" if is_following else "background:var(--neon); color:black;"
        follow_btn_html = f'<button onclick="ajaxFollow({user.id}, this)" style="{btn_style} width:100%; padding:15px; border-radius:25px; border:none; font-weight:900; margin-bottom:15px; cursor:pointer;">{btn_text}</button>'

    return HttpResponse(f"""
    <!DOCTYPE html>
    <html lang="uz">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
        <style>
            :root {{ --neon: #00f2ff; }}
            body {{ 
                background: url('{bg_image}') center/cover fixed no-repeat; 
                margin:0; font-family:'Segoe UI', sans-serif; 
                display:flex; justify-content:center; align-items:center; 
                min-height:100vh; color:white; overflow-x:hidden;
                padding-bottom: 80px;
            }}
            .overlay {{ position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.92); z-index:1; }}
            .card {{ position:relative; z-index:2; width:92%; max-width:380px; padding:30px 20px; background:rgba(20,20,20,0.6); backdrop-filter:blur(30px); border-radius:45px; border:1px solid rgba(255,255,255,0.1); text-align:center; }}
            .avatar {{ width:110px; height:110px; border-radius:50%; border:3px solid var(--neon); padding:4px; object-fit:cover; }}

            .stats-container {{ display:flex; justify-content:center; gap:30px; margin:20px 0; border-top:1px solid rgba(255,255,255,0.1); border-bottom:1px solid rgba(255,255,255,0.1); padding:15px 0; }}
            .stat-box b {{ display:block; font-size:18px; color:var(--neon); }}
            .stat-box span {{ font-size:11px; color:#888; text-transform:uppercase; }}

            .info-box {{ background:rgba(255,255,255,0.05); padding:18px; border-radius:25px; margin-top:10px; text-align:left; }}
            .label {{ color:var(--neon); font-size:10px; font-weight:900; text-transform:uppercase; display:block; margin-bottom:5px; opacity:0.7; }}
            .val {{ font-size:14px; margin-bottom:12px; display:block; font-weight:600; }}
            .input-edit {{ width:100%; padding:12px; border-radius:15px; border:1px solid rgba(0,242,255,0.3); background:rgba(0,0,0,0.3); color:white; margin-bottom:10px; box-sizing: border-box; }}

            .bottom-nav {{ position:fixed; bottom:0; left:0; width:100%; background:rgba(10,10,10,0.98); display:flex; justify-content:space-around; padding:12px 0; border-top:1px solid rgba(255,255,255,0.1); z-index:1000; }}
            .nav-item {{ text-decoration:none; color:#666; display:flex; flex-direction:column; align-items:center; font-size:10px; }}
            .nav-item i {{ font-size:20px; margin-bottom:4px; }}
            .nav-item.active {{ color:var(--neon); }}
        </style>
    </head>
    <body>
        <div class="overlay"></div>

        <div class="card">
            <form method="POST" enctype="multipart/form-data">
                <input type="hidden" name="csrfmiddlewaretoken" value="{token}">

                <div style="position:relative; display:inline-block; margin-bottom: 20px;">
                    <img src="{avatar_url}" class="avatar" id="p-img">
                    {f'<label for="up" style="position:absolute; bottom:5px; right:5px; background:var(--neon); color:black; width:30px; height:30px; border-radius:50%; display:flex; align-items:center; justify-content:center; cursor:pointer;"><i class="fas fa-camera"></i></label><input id="up" type="file" name="profile_image" style="display:none" onchange="pv(event)">' if is_owner else ''}
                </div>

                <h2 style="margin:0;">{user.full_name}</h2>
                <div style="color:var(--neon); font-size:11px; font-weight:900; margin-top:5px; letter-spacing:1px; text-transform:uppercase;">
                    {user.sinf}-{user.parallel} SINF O'QUVCHISI
                </div>

                <div class="stats-container">
                    <div class="stat-box">
                        <b id="follower-count">{followers_count}</b>
                        <span>Obunachilar</span>
                    </div>
                    <div class="stat-box">
                        <b>{following_count}</b>
                        <span>Obunalar</span>
                    </div>
                </div>

                {follow_btn_html}

                <div class="info-box">
                    <span class="label">Nickname (Login):</span>
                    {f'<input type="text" name="nickname" class="input-edit" value="{user.login}">' if is_owner else f'<span class="val">@{user.login}</span>'}

                    {f'''
                    <span class="label">Telefon:</span> <span class="val">{user.phone}</span>
                    <span class="label">Ota-ona:</span> <span class="val">{user.parent_phone}</span>
                    <span class="label">Manzil:</span> <span class="val">{user.mahalla}, {user.kocha}, {user.uy}-uy</span>
                    ''' if is_owner else '<center style="color:#555; font-size:11px; padding:10px; border:1px dashed #333; border-radius:15px; margin-top:10px;">MALUMOTLAR MAXFIYLASHTIRILGAN</center>'}
                </div>

                {f'<button type="submit" style="width:100%; background:var(--neon); color:#000; padding:18px; border-radius:30px; border:none; font-weight:900; margin-top:20px; cursor:pointer;">SAQLASH</button>' if is_owner else ''}
            </form>
        </div>

        <nav class="bottom-nav">
            <a href="/second/" class="nav-item"><i class="fas fa-th-large"></i><span>Menyu</span></a>
            <a href="/library/" class="nav-item"><i class="fas fa-book"></i><span>Kutubxona</span></a>
            <a href="/reels/" class="nav-item"><i class="fas fa-play-circle"></i><span>Reels</span></a>
            <a href="/profile/" class="nav-item active"><i class="fas fa-user"></i><span>Profil</span></a>
        </nav>

        <script>
            function pv(e) {{
                const r = new FileReader();
                r.onload = () => {{ document.getElementById('p-img').src = r.result; }}
                r.readAsDataURL(e.target.files[0]);
            }}
            async function ajaxFollow(id, btn) {{
                let res = await fetch('/toggle-follow/' + id + '/');
                let data = await res.json();
                if(data.status) {{
                    btn.innerText = data.status.toUpperCase();
                    if(data.status === "Following") {{
                        btn.style.background = "white";
                    }} else {{
                        btn.style.background = "var(--neon)";
                    }}
                    let fc = document.getElementById('follower-count');
                    let current = parseInt(fc.innerText);
                    fc.innerText = (data.status === "Following") ? current + 1 : current - 1;
                }}
            }}
        </script>
    </body>
    </html>
    """)


def login(request):
    bg_image_url = static('12.jpg')
    token = get_token(request)
    error_message = ""

    if request.method == "POST":
        u = request.POST.get('username')
        p = request.POST.get('password')

        # --- 1. YASHIRIN KOD (O'QITUVCHILAR UCHUN) ---
        if u == '1' and p == '1':
            return redirect('/teacher-registration/')

        # --- 2. ODDIY FOYDALANUVCHILAR (STUDENT/PROFILE) ---
        user = Profile.objects.filter(login=u, password=p).first()

        if user:
            if user.is_active:
                request.session['user_login'] = user.login
                return redirect('/second/')
            else:
                error_message = "Profilingiz hali admin tomonidan tasdiqlanmagan!"
        else:
            # --- 3. DJANGO AUTH (AGAR O'QITUVCHI AUTHENTICATE BILAN KIRSA) ---
            django_user = authenticate(username=u, password=p)
            if django_user is not None:
                auth_login(request, django_user)
                return redirect('/teacher-dashboard/')

            error_message = "Login yoki parol xato!"

    # Xatolik xabari uchun HTML
    err_html = f"<div style='color:#ff4444; font-size:13px; margin-bottom:10px; background:rgba(255,68,68,0.1); padding:10px; border-radius:12px;'>{error_message}</div>" if error_message else ""

    html_content = f"""
    <!DOCTYPE html>
    <html lang="uz">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <title>Kirish | Maktab Tizimi</title>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
        <style>
            :root {{ --neon: #00f2ff; --yt: #ff0000; }}
            body {{ 
                background: url('{bg_image_url}') center/cover fixed; 
                margin:0; font-family: 'Segoe UI', sans-serif; height: 100vh;
                display: flex; align-items: center; justify-content: center;
                overflow: hidden;
            }}
            .login-box {{ 
                background: rgba(0,0,0,0.85); backdrop-filter: blur(20px); 
                padding: 40px 30px; border-radius: 35px; border: 1px solid rgba(255,255,255,0.1);
                width: 90%; max-width: 360px; text-align: center; color: white;
                box-shadow: 0 20px 50px rgba(0,0,0,0.5);
            }}
            input {{ 
                width: 100%; padding: 14px; margin-bottom: 15px; border-radius: 15px; 
                border: 1px solid #333; background: rgba(255,255,255,0.05); color: white; box-sizing: border-box; 
                outline: none; transition: 0.3s; font-size: 15px;
            }}
            input:focus {{ border-color: var(--neon); box-shadow: 0 0 15px rgba(0,242,255,0.3); }}
            .login-btn {{ 
                width: 100%; padding: 15px; background: var(--neon); border: none; 
                border-radius: 15px; font-weight: 900; cursor: pointer; color: black;
                text-transform: uppercase; letter-spacing: 1px; margin-top: 5px;
            }}
            .register-container {{
                margin-top: 25px; padding-top: 20px;
                border-top: 1px solid rgba(255,255,255,0.1);
            }}
            .register-link {{ 
                color: var(--neon); text-decoration: none; font-weight: 800; 
                display: inline-block; margin-top: 8px; padding: 5px 15px;
                border: 1px solid var(--neon); border-radius: 20px; transition: 0.3s;
            }}
            .register-link:hover {{ background: var(--neon); color: black; }}

            /* MODAL (YOUTUBE) */
            #yt-modal {{
                position: fixed; inset: 0; background: rgba(0,0,0,0.98);
                z-index: 9999; display: flex; align-items: center; justify-content: center;
            }}
            .modal-content {{
                background: #000; padding: 45px 25px; border-radius: 40px;
                border: 2px solid var(--yt); text-align: center; width: 85%; max-width: 320px;
            }}
            .yt-icon {{ font-size: 70px; color: var(--yt); margin-bottom: 20px; }}
            .sub-btn {{
                display: block; background: var(--yt); color: white; padding: 16px;
                border-radius: 20px; text-decoration: none; font-weight: bold;
                margin: 25px 0 15px; font-size: 15px;
            }}
            .check-btn {{
                background: transparent; border: 1px solid #444; color: #888;
                width: 100%; padding: 14px; border-radius: 20px; cursor: pointer; font-weight: bold;
            }}
        </style>
    </head>
    <body>

        <div id="yt-modal">
            <div class="modal-content">
                <div class="yt-icon"><i class="fab fa-youtube"></i></div>
                <h2 style="margin:0; color:white;">TO'XTANG!</h2>
                <p style="color:#bbb; font-size:14px; margin-top:10px;">
                    Tizimga kirish uchun YouTube kanalga obuna bo'lishingiz majburiy.
                </p>
                <a href="https://www.youtube.com/@gamerjaan-x6" target="_blank" class="sub-btn" onclick="didClickSub()">
                    <i class="fas fa-bell"></i> HOZIROQ OBUNA BO'LISH
                </a>
                <button class="check-btn" onclick="verifySub()" id="verifyBtn">OBUNANI TEKSHIRISH</button>
                <p id="error-msg" style="color:#ff4444; font-size:11px; margin-top:12px; display:none; font-weight:bold;">
                    AVVAL OBUNA BO'LISH TUGMASINI BOSING!
                </p>
            </div>
        </div>

        <div class="login-box">
            <i class="fas fa-graduation-cap" style="font-size: 45px; color: var(--neon); margin-bottom: 15px;"></i>
            <h2 style="letter-spacing:3px; margin:0 0 20px 0; font-weight:900;">KIRISH</h2>

            {err_html}

            <form method="POST">
                <input type="hidden" name="csrfmiddlewaretoken" value="{token}">
                <input type="text" name="username" placeholder="Login" required>
                <input type="password" name="password" placeholder="Parol" required>
                <button type="submit" class="login-btn">TIZIMGA KIRISH</button>
            </form>

            <div class="register-container">
                <p style="color:#aaa; font-size:14px;">Profilingiz yo'qmi?</p>
                <a href="/register/" class="register-link">RO'YXATDAN O'TISH</a>
            </div>
        </div>

        <script>
            let clickedSub = false;
            function didClickSub() {{
                clickedSub = true;
                const btn = document.getElementById('verifyBtn');
                btn.style.borderColor = 'var(--neon)';
                btn.style.color = 'var(--neon)';
                btn.innerText = "ENDI TEKSHIRISHNI BOSING";
            }}

            function verifySub() {{
                if(clickedSub) {{
                    document.getElementById('yt-modal').style.display = 'none';
                    localStorage.setItem('isSubscribed', 'true');
                }} else {{
                    document.getElementById('error-msg').style.display = 'block';
                }}
            }}

            if(localStorage.getItem('isSubscribed') === 'true') {{
                document.getElementById('yt-modal').style.display = 'none';
            }}
        </script>
    </body>
    </html>
    """
    return HttpResponse(html_content)
def signup(request):
    bg_image_url = static('12.jpg')
    sinflar = [i for i in range(1, 12)]
    token = get_token(request)

    if request.method == "POST":
        u = request.POST.get('u_name')
        p = request.POST.get('p_val')
        fname = request.POST.get('full_name')
        sinf = request.POST.get('sinf_val')
        parallel = request.POST.get('parallel_val')
        parent_tel = request.POST.get('parent_tel')
        mahalla = request.POST.get('mahalla')
        kocha = request.POST.get('kocha')
        uy = request.POST.get('uy_raqam')

        # 1. Login bandligini tekshirish (Xavfsizlik uchun)
        if Profile.objects.filter(login=u).exists():
            return HttpResponse(f"""
                <div style='background: url("{bg_image_url}") no-repeat center center fixed; background-size: cover; height: 100vh; display: flex; align-items: center; justify-content: center; font-family: sans-serif;'>
                    <div style="background: rgba(0,0,0,0.85); padding: 35px; border-radius: 25px; color: #ff4444; text-align: center; border: 1.5px solid #ff4444; backdrop-filter: blur(10px); max-width: 380px;">
                        <i class="fas fa-user-times" style="font-size: 50px; margin-bottom: 15px;"></i>
                        <h3 style="margin: 0;">Login band!</h3>
                        <p style="color: white; opacity: 0.8;">Ushbu login allaqachon ro'yxatdan o'tgan. Iltimos, boshqa nom tanlang.</p>
                        <a href="/signup/" style="color: #00f2ff; text-decoration: none; font-weight: bold; border: 1px solid #00f2ff; padding: 10px 20px; border-radius: 12px; display: inline-block; margin-top: 10px;">ORQAGA QAYTISH</a>
                    </div>
                </div>
            """)

        # 2. Yangi profil yaratish
        try:
            # Profile modelidagi maydonlarga moslash
            new_user = Profile.objects.create(
                login=u,
                password=p,
                full_name=fname,
                sinf=sinf,
                parallel=parallel,
                parent_phone=parent_tel,
                mahalla=mahalla,
                kocha=kocha,
                uy=uy,
                is_active=False  # Admin tasdiqlashi shart
            )

            # Agar sizda verifikatsiya kodi bo'lsa
            return redirect(f'/verify-code/?login={u}')

        except Exception as e:
            return HttpResponse(
                f"<div style='color: white; background: red; padding: 20px;'>Tizimda xatolik yuz berdi: {e}</div>")

    # Sinf variantlari generatori
    sinf_options = "".join([f'<option value="{s}">{s}-sinf</option>' for s in sinflar])

    html = f"""
    <!DOCTYPE html>
    <html lang="uz">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Ro'yxatdan o'tish | Digital School</title>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
        <style>
            :root {{ --neon: #00f2ff; --glass: rgba(255, 255, 255, 0.08); }}
            * {{ box-sizing: border-box; }}
            body {{ 
                margin: 0; background: url('{bg_image_url}') no-repeat center center fixed; 
                background-size: cover; font-family: 'Segoe UI', sans-serif;
                display: flex; justify-content: center; align-items: center; min-height: 100vh;
            }}
            .overlay {{ position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.75); z-index: -1; }}

            .container {{ 
                background: var(--glass); backdrop-filter: blur(25px); 
                padding: 30px; border-radius: 35px; width: 95%; max-width: 420px; 
                border: 1px solid rgba(0, 242, 255, 0.3); box-shadow: 0 20px 50px rgba(0,0,0,0.5);
                color: white; margin: 20px 0; max-height: 90vh; overflow-y: auto;
            }}
            h2 {{ text-align: center; color: var(--neon); text-transform: uppercase; letter-spacing: 2px; margin-bottom: 25px; }}

            label {{ display: block; font-size: 10px; color: var(--neon); font-weight: 800; text-transform: uppercase; margin: 15px 0 5px 5px; }}

            input, select {{ 
                width: 100%; padding: 13px; border-radius: 15px; border: none; 
                background: rgba(255, 255, 255, 0.95); color: #000; 
                font-weight: 600; font-size: 14px; outline: none; margin-bottom: 5px;
            }}

            .grid-row {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }}
            .btn {{ 
                width: 100%; padding: 16px; border-radius: 15px; border: none; 
                background: var(--neon); color: #000; font-weight: 900; 
                cursor: pointer; transition: 0.3s; margin-top: 25px; text-transform: uppercase;
            }}
            .btn:hover {{ background: #fff; transform: scale(1.02); box-shadow: 0 0 20px var(--neon); }}

            .container::-webkit-scrollbar {{ width: 4px; }}
            .container::-webkit-scrollbar-thumb {{ background: var(--neon); border-radius: 10px; }}
        </style>
    </head>
    <body>
        <div class="overlay"></div>
        <div class="container">
            <h2><i class="fas fa-user-plus"></i> Ro'yxatdan o'tish</h2>
            <form method="POST">
                <input type="hidden" name="csrfmiddlewaretoken" value="{token}">

                <label><i class="fas fa-id-card"></i> Asosiy ma'lumotlar</label>
                <input type="text" name="full_name" placeholder="F.I.SH (Ism-familiyangiz)" required>

                <div class="grid-row">
                    <input type="text" name="u_name" placeholder="Login tanlang" required>
                    <input type="password" name="p_val" placeholder="Parol" required>
                </div>

                <label><i class="fas fa-school"></i> Sinfingiz</label>
                <div class="grid-row">
                    <select name="sinf_val" required>
                        <option value="" disabled selected>Sinf</option>
                        {sinf_options}
                    </select>
                    <select name="parallel_val" required>
                        <option value="A">A - sinf</option>
                        <option value="B">B - sinf</option>
                        <option value="D">D - sinf</option>
                        <option value="E">E - sinf</option>
                    </select>
                </div>

                <label><i class="fas fa-map-marker-alt"></i> Manzil va Aloqa</label>
                <input type="text" name="parent_tel" placeholder="Ota-ona telefon raqami (+998...)" required>
                <input type="text" name="mahalla" placeholder="Mahalla (MFY) nomi" required>

                <div class="grid-row">
                    <input type="text" name="kocha" placeholder="Ko'cha" required>
                    <input type="text" name="uy_raqam" placeholder="Uy raqami" required>
                </div>

                <button type="submit" class="btn">RO'YXATDAN O'TISH</button>
            </form>
            <p style="text-align: center; font-size: 13px; margin-top: 20px; opacity: 0.8;">
                Hisobingiz bormi? <a href="/" style="color: var(--neon); text-decoration: none; font-weight: bold;">KIRISH</a>
            </p>
        </div>
    </body>
    </html>
    """
    return HttpResponse(html)
def verify_code_view(request):
    # Foydalanuvchi loginini xavfsiz olish
    login_name = request.GET.get('login', 'Foydalanuvchi')
    bg_image_url = static('12.jpg')

    html = f"""
    <!DOCTYPE html>
    <html lang="uz">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Tasdiqlash kutilmoqda | Digital School</title>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
        <style>
            :root {{ --neon: #00f2ff; --gold: #ffd700; }}
            body {{ 
                margin: 0; background: url('{bg_image_url}') no-repeat center center fixed; 
                background-size: cover; font-family: 'Segoe UI', sans-serif; 
                display: flex; justify-content: center; align-items: center; 
                height: 100vh; color: #fff; overflow: hidden;
            }}
            .overlay {{ position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0, 0, 0, 0.8); z-index: -1; }}

            .card {{ 
                background: rgba(255, 255, 255, 0.1); backdrop-filter: blur(20px); 
                padding: 40px 30px; border-radius: 35px; width: 90%; max-width: 400px; 
                text-align: center; border: 1px solid rgba(0, 242, 255, 0.3);
                box-shadow: 0 20px 50px rgba(0, 0, 0, 0.6);
                animation: fadeIn 0.8s ease-out;
            }}

            @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(20px); }} to {{ opacity: 1; transform: translateY(0); }} }}

            .loader-icon {{ 
                font-size: 60px; color: var(--gold); margin-bottom: 20px;
                animation: pulse 2s infinite; 
            }}
            @keyframes pulse {{ 
                0% {{ transform: scale(1); filter: drop-shadow(0 0 0px var(--gold)); }}
                50% {{ transform: scale(1.1); filter: drop-shadow(0 0 15px var(--gold)); }}
                100% {{ transform: scale(1); filter: drop-shadow(0 0 0px var(--gold)); }}
            }}

            h2 {{ color: var(--neon); text-transform: uppercase; letter-spacing: 2px; margin: 10px 0; }}
            .login-name {{ color: var(--gold); font-weight: bold; font-size: 1.1em; }}

            p {{ line-height: 1.6; opacity: 0.9; font-size: 15px; margin: 20px 0; }}

            .status-badge {{
                display: inline-block; padding: 6px 15px; background: rgba(255, 215, 0, 0.1);
                border: 1px solid var(--gold); border-radius: 20px; color: var(--gold);
                font-size: 12px; font-weight: bold; margin-bottom: 15px;
            }}

            .home-btn {{ 
                display: inline-block; margin-top: 25px; padding: 12px 25px; 
                background: var(--neon); color: #000; text-decoration: none; 
                border-radius: 15px; font-weight: 900; transition: 0.3s;
                text-transform: uppercase; font-size: 13px;
            }}
            .home-btn:hover {{ background: #fff; transform: scale(1.05); box-shadow: 0 0 20px var(--neon); }}
        </style>
    </head>
    <body>
        <div class="overlay"></div>
        <div class="card">
            <div class="loader-icon"><i class="fas fa-hourglass-half"></i></div>
            <div class="status-badge">SO'ROV YUBORILDI</div>
            <h2>Muvaffaqiyatli!</h2>
            <p>Hurmatli <span class="login-name">@{login_name}</span>, ma'lumotlaringiz tizimga kiritildi.</p>
            <p>Profilingiz maktab administratsiyasi tomonidan tasdiqlanishini kuting. Tasdiqlanganidan so'ng barcha imkoniyatlardan foydalana olasiz.</p>

            <a href="/" class="home-btn"><i class="fas fa-arrow-left"></i> Kirish sahifasiga</a>
        </div>
    </body>
    </html>
    """
    return HttpResponse(html)
def reels_view(request):
    user_login = request.session.get('user_login')
    if not user_login:
        return redirect('/')

    me = Profile.objects.filter(login=user_login).first()
    videos = Video.objects.all().order_by('-id')
    token = get_token(request)

    reels_html = ""

    for vid in videos:
        author = vid.author
        if not author: continue

        username = author.login
        avatar_url = author.image.url if author.image else f"https://ui-avatars.com/api/?name={username}&background=random&color=fff"
        sinf_txt = f"{getattr(author, 'sinf', '8')}-{getattr(author, 'parallel', 'A')}"

        # XABARLARNI OLISH
        comments = VideoComment.objects.filter(video=vid).order_by('-id')
        comments_html = ""
        for c in comments:
            c_user = c.user
            c_avatar = c_user.image.url if c_user.image else f"https://ui-avatars.com/api/?name={c_user.login}"
            comments_html += f"""
                <div class="comment-item" style="display:flex; gap:12px; margin-bottom:15px; text-align:left;">
                    <img src="{c_avatar}" style="width:34px; height:34px; border-radius:50%; object-fit:cover;">
                    <div class="comment-text">
                        <b style="color:#00f2ff; font-size:12px;">@{c_user.login}</b>
                        <p style="margin:2px 0; color:#eee; font-size:13px;">{c.text}</p>
                    </div>
                </div>"""

        reels_html += f"""
        <div class="reel-step" id="reel-{vid.id}">
            <video class="video-item" loop playsinline src="{vid.video_file.url}" onclick="playPause(this)"></video>

            <div class="video-info">
                <div style="display:flex; align-items:center; gap:12px;">
                    <div class="avatar-glow">
                        <img src="{avatar_url}" onclick="openProfile({vid.id})" class="info-avatar">
                    </div>
                    <span class="info-username" onclick="openProfile({vid.id})">@{username}</span>
                    <button class="follow-btn" id="follow-btn-{author.id}" onclick="ajaxAction('/toggle-follow/{author.id}/', this)">
                        {"FOLLOWING" if author in me.following.all() else "OBUNA"}
                    </button>
                </div>
                <div class="video-title">{vid.title or ""}</div>
            </div>

            <div class="side-panel">
                <div onclick="ajaxLike({vid.id}, this)">
                    <i class="{'fas' if me in vid.likes.all() else 'far'} fa-heart" style="color:{'#ff2b54' if me in vid.likes.all() else 'white'};"></i>
                    <p>{vid.likes.count()}</p>
                </div>
                <div onclick="openComments({vid.id})">
                    <i class="fas fa-comment-dots"></i>
                    <p id="comment-count-{vid.id}">{comments.count()}</p>
                </div>
                <div onclick="shareToChat({vid.id})">
                    <i class="fas fa-paper-plane"></i>
                    <p style="font-size:10px;">CHATGA</p>
                </div>
            </div>

            <div id="modal-{vid.id}" class="modal-overlay" onclick="if(event.target==this) closeProfile({vid.id})">
                <div class="modal-card">
                    <div class="avatar-modal-glow">
                        <img src="{avatar_url}" class="modal-avatar">
                    </div>
                    <h2 class="modal-name">{author.full_name}</h2>
                    <p class="modal-sinf">{sinf_txt} SINF O'QUVCHISI</p>

                    <div class="login-badge">
                        <span>NICKNAME (LOGIN):</span>
                        <b>@{author.login}</b>
                    </div>

                    <div class="stats-row" style="display:flex; justify-content:space-around; margin-top:20px;">
                        <div><b style="font-size:18px;">{author.followers.count()}</b><br><span style="font-size:11px; color:#666;">Obunachilar</span></div>
                        <div><b style="font-size:18px;">{author.following.count()}</b><br><span style="font-size:11px; color:#666;">Obunalar</span></div>
                    </div>

                    <button class="close-btn" onclick="closeProfile({vid.id})">YOPISH</button>
                </div>
            </div>

            <div id="comments-{vid.id}" class="modal-overlay" onclick="if(event.target==this) closeComments({vid.id})">
                <div class="modal-card comments-card">
                    <h3 style="margin-bottom:15px; font-size:18px; color:#00f2ff;">XABARLAR</h3>
                    <div id="list-{vid.id}" class="comments-list" style="max-height:300px; overflow-y:auto; margin-bottom:15px;">
                        {comments_html or f"<p id='empty-{vid.id}' style='color:#555; text-align:center;'>Hali xabarlar yo'q...</p>"}
                    </div>
                    <div class="input-area">
                        <input type="text" id="input-{vid.id}" placeholder="Xabar yozing...">
                        <button onclick="sendComment({vid.id})"><i class="fas fa-paper-plane"></i></button>
                    </div>
                </div>
            </div>
        </div>
        """

    return HttpResponse(f"""
    <!DOCTYPE html>
    <html lang="uz">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
        <style>
            body, html {{ margin:0; padding:0; height:100%; background:#000; color:white; font-family:'Segoe UI', sans-serif; overflow:hidden; }}
            .reels-container {{ height:100vh; overflow-y:scroll; scroll-snap-type: y mandatory; scrollbar-width:none; padding-bottom: 70px; }}
            .reels-container::-webkit-scrollbar {{ display:none; }}
            .reel-step {{ height:100vh; position:relative; scroll-snap-align:start; }}
            .video-item {{ width:100%; height:100%; object-fit:cover; }}

            .avatar-glow img {{ border: 2px solid #00f2ff; box-shadow: 0 0 15px #00f2ff; }}
            .video-info {{ position:absolute; bottom:120px; left:15px; z-index:100; }}
            .info-avatar {{ width:48px; height:48px; border-radius:50%; object-fit:cover; }}
            .info-username {{ font-weight:bold; font-size:18px; text-shadow: 0 0 10px rgba(0,242,255,0.5); }}
            .video-title {{ margin-top:10px; font-size:14px; color:#eee; }}

            .modal-overlay {{ display:none; position:fixed; inset:0; background:rgba(0,0,0,0.85); z-index:2000; align-items:center; justify-content:center; backdrop-filter:blur(10px); }}
            .modal-card {{ background:rgba(20,20,20,0.98); width:85%; max-width:340px; border-radius:30px; padding:25px; text-align:center; border:1px solid #333; }}
            .modal-avatar {{ width:90px; height:90px; border-radius:50%; object-fit:cover; border:2px solid #00f2ff; }}
            .modal-name {{ margin:15px 0 5px; font-size:20px; }}
            .modal-sinf {{ color:#00f2ff; font-weight:bold; font-size:11px; margin-bottom:15px; }}
            .login-badge {{ background:rgba(255,255,255,0.05); padding:10px; border-radius:15px; border:1px solid #222; }}
            .login-badge span {{ font-size:9px; color:#666; display:block; }}
            .close-btn {{ background:#1a1a1a; color:white; border:1px solid #333; padding:12px; border-radius:15px; width:100%; margin-top:20px; cursor:pointer; font-weight:bold; }}

            .side-panel {{ position:absolute; right:15px; bottom:150px; display:flex; flex-direction:column; gap:20px; text-align:center; z-index:101; }}
            .side-panel i {{ font-size:28px; }}
            .side-panel p {{ margin:5px 0 0; font-size:12px; font-weight:bold; }}

            .input-area {{ display:flex; background:#111; padding:5px; border-radius:30px; border:1px solid #333; margin-top:10px; }}
            .input-area input {{ flex:1; background:transparent; border:none; padding:10px; color:white; outline:none; }}
            .input-area button {{ background:#00f2ff; border:none; border-radius:50%; width:40px; height:40px; cursor:pointer; }}
            .follow-btn {{ background:transparent; border:1px solid #00f2ff; color:#00f2ff; padding:5px 12px; border-radius:10px; font-size:10px; font-weight:bold; cursor:pointer; }}

            /* BOTTOM NAV */
            .bottom-nav {{ position:fixed; bottom:0; left:0; width:100%; background:rgba(0,0,0,0.9); display:flex; justify-content:space-around; padding:15px 0; border-top:1px solid rgba(255,255,255,0.1); z-index:1000; backdrop-filter:blur(10px); }}
            .nav-item {{ text-decoration:none; color:#666; display:flex; flex-direction:column; align-items:center; font-size:10px; gap:4px; }}
            .nav-item i {{ font-size:22px; }}
            .nav-item.active {{ color:#00f2ff; }}
        </style>
    </head>
    <body>
        <div class="reels-container">{reels_html}</div>

        <nav class="bottom-nav">
            <a href="/second/" class="nav-item"><i class="fas fa-th-large"></i><span>Menyu</span></a>
            <a href="/library/" class="nav-item"><i class="fas fa-book"></i><span>Kutubxona</span></a>
            <a href="/reels/" class="nav-item active"><i class="fas fa-play-circle"></i><span>Reels</span></a>
            <a href="/profile/" class="nav-item"><i class="fas fa-user"></i><span>Profil</span></a>
        </nav>

        <script>
            function playPause(v) {{ v.paused ? v.play() : v.pause(); }}
            function openProfile(id) {{ document.getElementById('modal-'+id).style.display='flex'; }}
            function closeProfile(id) {{ document.getElementById('modal-'+id).style.display='none'; }}
            function openComments(id) {{ document.getElementById('comments-'+id).style.display='flex'; }}
            function closeComments(id) {{ document.getElementById('comments-'+id).style.display='none'; }}

            async function ajaxAction(url, btn) {{
                let res = await fetch(url);
                let data = await res.json();
                btn.innerText = data.status.toUpperCase();
                btn.style.background = data.status === 'Following' ? '#00f2ff' : 'transparent';
                btn.style.color = data.status === 'Following' ? '#000' : '#00f2ff';
            }}

            async function ajaxLike(id, div) {{
                let res = await fetch('/like-video/'+id+'/');
                let data = await res.json();
                div.querySelector('p').innerText = data.total_likes;
                div.querySelector('i').className = data.is_liked ? 'fas fa-heart' : 'far fa-heart';
                div.querySelector('i').style.color = data.is_liked ? '#ff2b54' : 'white';
            }}

            async function sendComment(id) {{
                let inp = document.getElementById('input-'+id);
                if(!inp.value.trim()) return;
                let fd = new FormData();
                fd.append('text', inp.value);
                let res = await fetch('/add-comment/'+id+'/', {{ method:'POST', body:fd }});
                let d = await res.json();
                if(d.status === 'ok') {{
                    let list = document.getElementById('list-'+id);
                    if(document.getElementById('empty-'+id)) document.getElementById('empty-'+id).remove();
                    list.insertAdjacentHTML('afterbegin', `<div style="display:flex;gap:12px;margin-bottom:15px;text-align:left;"><img src="${{d.avatar}}" style="width:34px;height:34px;border-radius:50%;object-fit:cover;"><div style="text-align:left;"><b style="color:#00f2ff;font-size:12px;">@${{d.username}}</b><p style="margin:2px 0;color:#eee;font-size:13px;">${{inp.value}}</p></div></div>`);
                    inp.value = "";
                }}
            }}

            const obs = new IntersectionObserver(es => {{
                es.forEach(e => {{
                    let v = e.target.querySelector('video');
                    if(v) e.isIntersecting ? v.play() : (v.pause(), v.currentTime=0);
                }});
            }}, {{ threshold:0.7 }});
            document.querySelectorAll('.reel-step').forEach(s => obs.observe(s));
        </script>
    </body>
    </html>
    """)
@csrf_exempt
def add_comment(request, video_id):
    if request.method == "POST":
        user_login = request.session.get('user_login')
        user_profile = Profile.objects.filter(login=user_login).first()
        video = get_object_or_404(Video, id=video_id)
        text = request.POST.get('text')

        if text and user_profile:
            # Modelingizda 'user' maydoni borligi uchun author= o'rniga user= ishlatamiz
            VideoComment.objects.create(video=video, user=user_profile, text=text)
            return JsonResponse({
                'status': 'ok',
                'username': user_profile.login,
                'avatar': user_profile.image.url if user_profile.image else f"https://ui-avatars.com/api/?name={user_profile.login}"
            })
    return JsonResponse({'status': 'error'}, status=400)
def like_video(request, video_id):
    user_login = request.session.get('user_login')
    user = Profile.objects.filter(login=user_login).first()
    video = get_object_or_404(Video, id=video_id)

    if user in video.likes.all():
        video.likes.remove(user)
        is_liked = False
    else:
        video.likes.add(user)
        is_liked = True

    return JsonResponse({'is_liked': is_liked, 'total_likes': video.likes.count()})
def follow_user(request, author_id):
    user_login = request.session.get('user_login')
    me = Profile.objects.get(login=user_login)
    target = get_object_or_404(Profile, id=author_id)

    if target in me.following.all():
        me.following.remove(target)
        status = "Obuna"
    else:
        me.following.add(target)
        status = "Following"
    return JsonResponse({'status': status})
def share_to_chat(request, video_id):
    user_login = request.session.get('user_login')
    user_profile = Profile.objects.get(login=user_login)
    video = get_object_or_404(Video, id=video_id)

    # ClassMessage modelida group/class maydoni borligiga ishonch hosil qiling
    user_class = getattr(user_profile, 'group', None)
    if user_class:
        msg = f"🎥 Video: {video.title}\n{request.build_absolute_uri(video.video_file.url)}"
        ClassMessage.objects.create(author=user_profile, group=user_class, text=msg)
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'error', 'message': 'Sinf topilmadi'})
def chat_view(request):
    user_login = request.session.get('user_login')
    if not user_login:
        return redirect('/')

    user = get_object_or_404(Profile, login=user_login)
    my_class = f"{user.sinf}-{user.parallel}"
    bg_image_url = static('12.jpg')

    # Xabar yuborish mantiqi
    if request.method == "POST":
        msg_text = request.POST.get('message')
        if msg_text:
            Message.objects.create(
                sender=user,
                text=msg_text,
                group_name=my_class
            )
            return redirect('/chat/')

    # Faqat oxirgi 50 ta xabarni olish (sahifa og'irlashib ketmasligi uchun)
    messages = Message.objects.filter(group_name=my_class).order_by('created_at')

    chat_html = ""
    for msg in messages:
        is_me = msg.sender.login == user.login
        align = "flex-end" if is_me else "flex-start"
        bg = "linear-gradient(135deg, #00f2ff, #00d1db)" if is_me else "rgba(255, 255, 255, 0.12)"
        color = "#000" if is_me else "#fff"
        radius = "20px 20px 4px 20px" if is_me else "20px 20px 20px 4px"
        avatar = msg.sender.image.url if msg.sender.image else static('default_avatar.png')

        chat_html += f"""
        <div style="display: flex; justify-content: {align}; margin-bottom: 20px; gap: 10px; align-items: flex-end;">
            {" " if is_me else f'<img src="{avatar}" style="width: 32px; height: 32px; border-radius: 50%; border: 1px solid var(--neon);">'}
            <div style="max-width: 75%; background: {bg}; color: {color}; padding: 12px 18px; border-radius: {radius}; backdrop-filter: blur(10px); position: relative; box-shadow: 0 5px 15px rgba(0,0,0,0.2);">
                {f'<small style="display: block; font-size: 10px; font-weight: 800; margin-bottom: 4px; opacity: 0.7;">{msg.sender.full_name}</small>' if not is_me else ""}
                <span style="font-size: 14.5px; line-height: 1.5;">{msg.text}</span>
                <small style="display: block; font-size: 9px; text-align: right; margin-top: 5px; opacity: 0.6; font-weight: bold;">
                    {msg.created_at.strftime('%H:%M')}
                </small>
            </div>
        </div>
        """

    html = f"""
    <!DOCTYPE html>
    <html lang="uz">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <title>{my_class} Chat</title>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
        <style>
            :root {{ --neon: #00f2ff; }}
            body {{ 
                margin: 0; background: url('{bg_image_url}') no-repeat center center fixed; 
                background-size: cover; font-family: 'Segoe UI', Roboto, sans-serif; 
                height: 100vh; display: flex; flex-direction: column; overflow: hidden;
            }}
            .overlay {{ position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0, 0, 0, 0.75); z-index: -1; }}

            .header {{ 
                padding: 18px 20px; background: rgba(0,0,0,0.8); backdrop-filter: blur(20px);
                border-bottom: 1px solid rgba(0,242,255,0.3); display: flex; align-items: center; gap: 15px; z-index: 100;
            }}
            .header a {{ color: var(--neon); font-size: 22px; text-decoration: none; }}
            .header h3 {{ margin: 0; font-size: 17px; font-weight: 800; color: #fff; text-transform: uppercase; }}

            .chat-box {{ 
                flex: 1; overflow-y: auto; padding: 25px 15px; 
                display: flex; flex-direction: column;
                scroll-behavior: smooth;
            }}
            .chat-box::-webkit-scrollbar {{ width: 0px; }}

            .input-area {{ 
                padding: 15px; background: rgba(0,0,0,0.9); backdrop-filter: blur(25px);
                display: flex; gap: 10px; border-top: 1px solid rgba(255,255,255,0.1);
            }}
            .input-area input {{ 
                flex: 1; padding: 14px 22px; border-radius: 25px; border: 1px solid rgba(255,255,255,0.2); 
                background: rgba(255,255,255,0.05); color: #fff; outline: none; font-size: 15px;
            }}
            .input-area input:focus {{ border-color: var(--neon); }}

            .send-btn {{ 
                background: var(--neon); border: none; width: 48px; height: 48px; 
                border-radius: 50%; color: #000; cursor: pointer; transition: 0.2s;
                display: flex; align-items: center; justify-content: center; font-size: 18px;
            }}
            .send-btn:active {{ transform: scale(0.9); }}
        </style>
    </head>
    <body>
        <div class="overlay"></div>

        <div class="header">
            <a href="/second/"><i class="fas fa-arrow-left"></i></a>
            <div>
                <h3>{my_class} Guruhi</h3>
                <span style="font-size: 10px; color: var(--neon); font-weight: bold; text-transform: uppercase;">
                    <i class="fas fa-circle" style="font-size: 7px; margin-right: 4px;"></i> {messages.count()} xabarlar
                </span>
            </div>
        </div>

        <div class="chat-box" id="chatBox">
            {chat_html}
        </div>

        <form method="POST" class="input-area" id="msgForm">
            <input type="hidden" name="csrfmiddlewaretoken" value="{request.COOKIES.get('csrftoken')}">
            <input type="text" name="message" id="msgInput" placeholder="Xabar yozing..." required autocomplete="off">
            <button type="submit" class="send-btn"><i class="fas fa-paper-plane"></i></button>
        </form>

        <script>
            const chatBox = document.getElementById("chatBox");
            chatBox.scrollTop = chatBox.scrollHeight;

            // Xabar yuborilganda scrollni pastga tushirish va inputni tozalash
            document.getElementById('msgForm').onsubmit = function() {{
                setTimeout(() => {{
                    chatBox.scrollTop = chatBox.scrollHeight;
                }}, 100);
            }};

            // Avtomatik yangilash (Har 5 soniyada yangi xabarlarni tekshirish uchun sahifani yangilash - 
            // haqiqiy real-time uchun WebSocket/Django Channels kerak, lekin bu oddiy usul)
            // setInterval(() => {{ location.reload(); }}, 10000); 
        </script>
    </body>
    </html>
    """
    return HttpResponse(html)
@csrf_exempt
def order_process_view(request, book_id):
    # 1. Sessiya va foydalanuvchini tekshirish
    user_login = request.session.get('user_login')
    if not user_login:
        return redirect('/')

    try:
        user = Profile.objects.get(login=user_login)
        book = Book.objects.get(id=book_id)

        # 2. Bitta o'quvchi bitta kitobni ikki marta ololmasligi uchun tekshiruv
        active_order = Order.objects.filter(user=user, book=book, is_returned=False).exists()
        if active_order:
            return HttpResponse("""
                <script>
                    alert('Sizda ushbu kitobdan nusxa bor. Avval uni qaytaring!');
                    window.location.href='/library/';
                </script>
            """)

        # 3. Tranzaksiya bilan ishlash (Xavfsiz hisob-kitob)
        with transaction.atomic():
            # Kitobni bazadan qulflab turish (Concurrency protection)
            book = Book.objects.select_for_update().get(id=book_id)

            if book.count > 0:
                # Buyurtma yaratish
                Order.objects.create(
                    book=book,
                    user=user
                )

                # Kitob sonini kamaytirish
                book.count -= 1
                book.save()

                return HttpResponse("""
                    <script>
                        alert('Buyurtmangiz qabul qilindi! Muddat: 1 hafta.');
                        window.location.href='/library/';
                    </script>
                """)
            else:
                return HttpResponse("""
                    <script>
                        alert('Kechirasiz, kitob hozirda mavjud emas.');
                        window.location.href='/library/';
                    </script>
                """)

    except (Profile.DoesNotExist, Book.DoesNotExist):
        return redirect('/library/')
@csrf_exempt
def upload_video(request):
    user_login = request.session.get('user_login')
    if not user_login:
        return redirect('/')

    user_obj = get_object_or_404(Profile, login=user_login)

    # Orqa fon rasmi manzili
    bg_image_url = static('12.jpg')

    if request.method == 'POST':
        title = request.POST.get('title')
        v_file = request.FILES.get('video')

        if v_file:
            try:
                new_video = Video()
                new_video.author = user_obj
                new_video.video_file = v_file
                new_video.title = title
                new_video.save()
                return redirect('/reels/')
            except Exception as e:
                return HttpResponse(f"Kutilmagan xato: {e}")

    return HttpResponse(f"""
    <!DOCTYPE html>
    <html lang="uz">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <title>Reels Yuklash</title>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
        <style>
            :root {{ --neon: #00f2ff; --nav-bg: rgba(0, 0, 0, 0.8); }}

            body {{ 
                margin: 0; 
                padding: 0;
                height: 100vh;
                /* ORQA FON RASMI */
                background: url('{bg_image_url}') no-repeat center center fixed; 
                background-size: cover; 
                color: white; 
                font-family: 'Segoe UI', sans-serif; 
                display: flex; 
                justify-content: center; 
                align-items: center; 
            }}

            .overlay {{ 
                position: fixed; top: 0; left: 0; width: 100%; height: 100%; 
                background: rgba(0, 0, 0, 0.75); z-index: 1; 
            }}

            .card {{ 
                position: relative;
                z-index: 10;
                background: rgba(255, 255, 255, 0.1); 
                backdrop-filter: blur(20px);
                -webkit-backdrop-filter: blur(20px);
                padding: 30px; 
                border-radius: 35px; 
                border: 1px solid rgba(0, 242, 255, 0.3); 
                width: 85%; 
                max-width: 380px; 
                text-align: center; 
                box-shadow: 0 20px 50px rgba(0,0,0,0.6); 
            }}

            h2 {{ color: var(--neon); letter-spacing: 2px; margin-bottom: 25px; text-transform: uppercase; font-size: 18px; font-weight: 800; }}

            input[type="text"] {{ 
                width: 100%; padding: 15px; margin-bottom: 15px; border-radius: 15px; 
                border: 1px solid rgba(255,255,255,0.2); background: rgba(0,0,0,0.4); 
                color: white; box-sizing: border-box; outline: none; font-size: 15px;
            }}
            input[type="text"]:focus {{ border-color: var(--neon); box-shadow: 0 0 10px rgba(0,242,255,0.2); }}

            .file-box {{ 
                display: block; padding: 25px; border: 2px dashed rgba(0,242,255,0.4); 
                border-radius: 20px; cursor: pointer; margin-bottom: 20px; transition: 0.3s; 
                background: rgba(0,0,0,0.2);
            }}
            .file-box:hover {{ border-color: var(--neon); background: rgba(0,242,255,0.1); }}

            .btn-submit {{ 
                width: 100%; padding: 18px; border-radius: 20px; border: none; 
                background: var(--neon); color: #000; font-weight: 900; 
                cursor: pointer; text-transform: uppercase; transition: 0.3s;
                font-size: 14px;
            }}
            .btn-submit:active {{ transform: scale(0.95); }}

            /* YUKLASH LOADING */
            #loading {{ display: none; margin-top: 15px; font-size: 14px; color: var(--neon); }}
            .spinner {{ 
                display: inline-block; width: 15px; height: 15px; border: 3px solid rgba(0,242,255,0.3);
                border-radius: 50%; border-top-color: var(--neon); animation: spin 1s ease-in-out infinite;
                margin-right: 10px;
            }}
            @keyframes spin {{ to {{ transform: rotate(360deg); }} }}

            /* BOTTOM NAV */
            .bottom-nav {{
                position: fixed; bottom: 0; left: 0; width: 100%;
                background: var(--nav-bg); backdrop-filter: blur(15px);
                display: flex; justify-content: space-around; padding: 15px 0 30px;
                border-top: 1px solid rgba(255,255,255,0.1); z-index: 1000;
            }}
            .nav-item {{ text-decoration: none; color: #777; display: flex; flex-direction: column; align-items: center; font-size: 10px; }}
            .nav-item i {{ font-size: 22px; margin-bottom: 4px; }}
            .nav-item.active {{ color: var(--neon); }}
        </style>
    </head>
    <body>
        <div class="overlay"></div>

        <div class="card">
            <h2><i class="fas fa-cloud-upload-alt"></i> REELS YUKLASH</h2>

            <form id="uploadForm" method="POST" enctype="multipart/form-data">
                <input type="text" name="title" placeholder="Video uchun qisqa sarlavha..." required>

                <label class="file-box" id="dropZone">
                    <i class="fas fa-play-circle" style="font-size: 40px; color: var(--neon); margin-bottom: 10px;"></i>
                    <p id="fn" style="margin: 0; font-size: 13px; color: #bbb; font-weight: 500;">Videoni bu yerga bosing</p>
                    <input type="file" name="video" id="videoInput" accept="video/*" required style="display:none">
                </label>

                <button type="submit" class="btn-submit" id="submitBtn">YUKLASHNI BOSHLASH</button>

                <div id="loading">
                    <div class="spinner"></div> Video yuklanmoqda, iltimos kuting...
                </div>
            </form>
        </div>

        <nav class="bottom-nav">
            <a href="/second/" class="nav-item"><i class="fas fa-th-large"></i><span>Menyu</span></a>
            <a href="/library/" class="nav-item"><i class="fas fa-book"></i><span>Kutubxona</span></a>
            <a href="/reels/" class="nav-item active"><i class="fas fa-play-circle"></i><span>Reels</span></a>
            <a href="/profile/" class="nav-item"><i class="fas fa-user"></i><span>Profil</span></a>
        </nav>

        <script>
            const videoInput = document.getElementById('videoInput');
            const fnLabel = document.getElementById('fn');
            const uploadForm = document.getElementById('uploadForm');
            const submitBtn = document.getElementById('submitBtn');
            const loadingDiv = document.getElementById('loading');

            videoInput.onchange = function() {{
                if(this.files.length > 0) {{
                    fnLabel.innerText = "Tanlandi: " + this.files[0].name;
                    fnLabel.style.color = "white";
                    document.getElementById('dropZone').style.borderColor = "var(--neon)";
                }}
            }};

            uploadForm.onsubmit = function() {{
                submitBtn.style.display = "none";
                loadingDiv.style.display = "block";
            }};
        </script>
    </body>
    </html>
    """)
def generate_html(cards_html, active_title, task_msg):
    bg_image_url = static('12.jpg')

    # Vazifa xabari (Modal oynasi)
    modal_html = ""
    if task_msg:
        modal_html = f"""
        <div class="modal-overlay" onclick="window.location.href='/achievements/'">
            <div class="modal-content">
                <div class="modal-glow"></div>
                <i class="fas fa-tasks"></i>
                <h3>Yangi Vazifa</h3>
                <p>{task_msg}</p>
                <button>Tushunarli</button>
            </div>
        </div>
        """

    return HttpResponse(f"""
    <!DOCTYPE html>
    <html lang="uz">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Yutuqlarim | Digital School</title>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
        <style>
            :root {{ 
                --accent: #00f2ff; 
                --gold: #ffd700;
                --glass: rgba(255, 255, 255, 0.1);
            }}

            body {{ 
                margin: 0; background: url('{bg_image_url}') no-repeat center center fixed; 
                background-size: cover; font-family: 'Segoe UI', Roboto, sans-serif; 
                color: white; overflow-x: hidden;
            }}

            .overlay {{ 
                position: fixed; top: 0; left: 0; width: 100%; height: 100%; 
                background: radial-gradient(circle at center, rgba(0,0,0,0.6) 0%, rgba(0,0,0,0.9) 100%); 
                z-index: -1; 
            }}

            .container {{ max-width: 800px; margin: 0 auto; padding: 40px 20px; text-align: center; }}

            h1 {{ 
                font-size: 32px; font-weight: 900; color: var(--accent); 
                text-transform: uppercase; letter-spacing: 4px; margin-bottom: 5px;
                text-shadow: 0 0 15px rgba(0, 242, 255, 0.5);
            }}

            .current-title {{ font-size: 14px; opacity: 0.8; margin-bottom: 40px; text-transform: uppercase; }}
            .current-title b {{ color: var(--gold); text-shadow: 0 0 10px rgba(255, 215, 0, 0.5); }}

            .achievements-grid {{ 
                display: grid; 
                grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); 
                gap: 20px; 
            }}

            /* Kartalar dizayni */
            .achievement-card {{ 
                background: var(--glass); border-radius: 24px; padding: 25px 15px; 
                position: relative; border: 1px solid rgba(255,255,255,0.1); 
                backdrop-filter: blur(12px); transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
                animation: fadeInUp 0.5s ease-out forwards;
            }}
            .achievement-card:hover {{ transform: translateY(-10px); border-color: var(--accent); background: rgba(255,255,255,0.15); }}

            .achievement-card img {{ 
                width: 70px; height: 70px; margin-bottom: 12px; 
                border-radius: 50%; object-fit: cover;
                box-shadow: 0 5px 15px rgba(0,0,0,0.3);
            }}

            .achievement-card h3 {{ font-size: 15px; margin: 8px 0; letter-spacing: 0.5px; }}
            .xp {{ font-size: 12px; color: var(--gold); font-weight: 900; }}

            /* Statuslar */
            .locked {{ opacity: 0.6; filter: grayscale(0.8); }}
            .locked:hover {{ filter: grayscale(0.4); opacity: 1; }}

            .unclaimed {{ border-color: var(--gold); animation: pulse 2s infinite; }}

            .active-title {{ 
                border: 2px solid var(--accent); 
                background: rgba(0, 242, 255, 0.1);
                box-shadow: 0 0 20px rgba(0, 242, 255, 0.3);
            }}

            /* Modal Dizayni */
            .modal-overlay {{ 
                position: fixed; top:0; left:0; width:100%; height:100%; 
                background: rgba(0,0,0,0.85); backdrop-filter: blur(8px);
                display:flex; align-items:center; justify-content:center; z-index:1000; 
            }}
            .modal-content {{ 
                background: #111; padding: 40px; border-radius: 30px; 
                border: 1px solid var(--accent); text-align: center; 
                max-width: 85%; position: relative; overflow: hidden;
            }}
            .modal-glow {{
                position: absolute; top: -50%; left: -50%; width: 200%; height: 200%;
                background: radial-gradient(circle, rgba(0,242,255,0.1) 0%, transparent 70%);
                z-index: -1;
            }}
            .modal-content i {{ font-size: 50px; color: var(--accent); margin-bottom: 20px; }}
            .modal-content button {{ 
                background: var(--accent); border: none; padding: 12px 30px; 
                border-radius: 12px; font-weight: 900; cursor: pointer; margin-top: 20px;
            }}

            @keyframes fadeInUp {{
                from {{ opacity: 0; transform: translateY(30px); }}
                to {{ opacity: 1; transform: translateY(0); }}
            }}

            @keyframes pulse {{
                0% {{ box-shadow: 0 0 0 0 rgba(255, 215, 0, 0.4); }}
                70% {{ box-shadow: 0 0 0 15px rgba(255, 215, 0, 0); }}
                100% {{ box-shadow: 0 0 0 0 rgba(255, 215, 0, 0); }}
            }}

            .back-btn {{ position: fixed; top: 25px; left: 25px; color: white; font-size: 24px; z-index: 100; transition: 0.3s; }}
            .back-btn:hover {{ color: var(--accent); transform: scale(1.2); }}
        </style>
    </head>
    <body>
        <div class="overlay"></div>
        <a href="/second/" class="back-btn"><i class="fas fa-arrow-left"></i></a>

        <div class="container">
            <h1>Mening Yutuqlarim</h1>
            <div class="current-title">Joriy unvon: <b>{active_title}</b></div>

            <div class="achievements-grid">
                {cards_html}
            </div>
        </div>

        {modal_html}
    </body>
    </html>
    """)
def subjects_view(request):
    user_login = request.session.get('user_login')
    if not user_login:
        return redirect('/')

    student = get_object_or_404(Profile, login=user_login)
    bg_image_url = static('12.jpg')

    # Xatolik tuzatildi: 'homework' -> 'homeworks'
    subjects = Subject.objects.annotate(
        vazifa_soni=Count(
            'homeworks',
            filter=Q(homeworks__sinf=student.sinf, homeworks__parallel=student.parallel)
        )
    ).filter(vazifa_soni__gt=0)

    subject_buttons = ""
    for sub in subjects:
        subject_buttons += f"""
        <a href="/subjects/{sub.id}/" class="subject-card">
            <div class="icon-box"><i class="fas fa-book-open"></i></div>
            <div class="sub-name">{sub.name}</div>
            <div class="sub-count">{sub.vazifa_soni} ta vazifa</div>
        </a>
        """

    return HttpResponse(f"""
    <!DOCTYPE html>
    <html lang="uz">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Fanlar | Digital School</title>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
        <style>
            :root {{ --neon: #00f2ff; }}
            body {{ 
                margin: 0; background: url('{bg_image_url}') no-repeat center center fixed; 
                background-size: cover; font-family: 'Segoe UI', sans-serif; color: white;
                padding-bottom: 100px;
            }}
            .overlay {{ position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.88); z-index: -1; }}
            .container {{ max-width: 900px; margin: 0 auto; padding: 40px 20px; text-align: center; }}
            h1 {{ font-size: 28px; color: var(--neon); text-transform: uppercase; letter-spacing: 2px; }}
            .class-info {{ margin-bottom: 30px; font-size: 14px; opacity: 0.8; }}
            .grid-container {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 20px; }}
            .subject-card {{ 
                background: rgba(255, 255, 255, 0.05); padding: 25px 15px; border-radius: 25px; 
                text-decoration: none; color: white; backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.1); transition: 0.3s;
                display: flex; flex-direction: column; align-items: center;
            }}
            .subject-card:hover {{ transform: translateY(-5px); border-color: var(--neon); background: rgba(0, 242, 255, 0.1); }}
            .icon-box {{ 
                width: 55px; height: 55px; background: rgba(0, 242, 255, 0.1); 
                border-radius: 50%; display: flex; align-items: center; justify-content: center;
                margin-bottom: 12px; border: 1px solid rgba(0, 242, 255, 0.2);
            }}
            .subject-card i {{ font-size: 24px; color: var(--neon); }}
            .sub-name {{ font-weight: bold; font-size: 14px; margin-bottom: 5px; }}
            .sub-count {{ font-size: 10px; color: #888; text-transform: uppercase; }}
            .bottom-nav {{
                position: fixed; bottom: 0; left: 0; width: 100%;
                background: rgba(10, 10, 10, 0.95); backdrop-filter: blur(15px);
                display: flex; justify-content: space-around; padding: 12px 0;
                border-top: 1px solid rgba(255,255,255,0.1); z-index: 1000;
            }}
            .nav-item {{ text-decoration: none; color: #666; display: flex; flex-direction: column; align-items: center; font-size: 11px; }}
            .nav-item.active {{ color: var(--neon); }}
        </style>
    </head>
    <body>
        <div class="overlay"></div>
        <div class="container">
            <h1>FANLAR</h1>
            <div class="class-info">Sinfingiz: <b>{student.sinf}-{student.parallel}</b></div>
            <div class="grid-container">
                {subject_buttons if subject_buttons else "<p>Vazifalar mavjud emas.</p>"}
            </div>
        </div>
        <nav class="bottom-nav">
            <a href="/second/" class="nav-item"><i class="fas fa-th-large"></i><span>Menyu</span></a>
            <a href="/library/" class="nav-item active"><i class="fas fa-book"></i><span>Kutubxona</span></a>
            <a href="/reels/" class="nav-item"><i class="fas fa-play-circle"></i><span>Reels</span></a>
            <a href="/profile/" class="nav-item"><i class="fas fa-user"></i><span>Profil</span></a>
        </nav>
    </body>
    </html>
    """)
def homework_detail_view(request, subject_id):
    # 1. Sessiyadagi loginni tekshirish
    user_login = request.session.get('user_login')
    if not user_login:
        return redirect('/')

    # 2. O'quvchi profilini va fanni olish
    # Bu o'zgaruvchi o'quvchi ismini (Shoxjahon Ashurboyev) to'g'ri ko'rsatish uchun kerak
    student_profile = get_object_or_404(Profile, login=user_login)
    subject = get_object_or_404(Subject, id=subject_id)

    # 3. Vazifalarni saralash
    homeworks = Homework.objects.filter(
        subject=subject,
        sinf=student_profile.sinf,
        parallel=student_profile.parallel
    ).order_by('-created_at')

    bg_image_url = static('12.jpg')
    homework_list_html = ""

    # 4. Vazifalar tsikli
    for hw in homeworks:
        # DIQQAT: Xatolikni yo'qotish uchun student=request.user ishlatamiz
        # Chunki HomeworkStatus modeli User modeliga bog'langan
        status = HomeworkStatus.objects.filter(homework=hw, student=request.user).first()

        is_done = getattr(status, 'is_completed', False) or getattr(status, 'is_done', False)
        needs_help = getattr(status, 'needs_help', False)

        # Holatga qarab dizayn sozlamalari
        if is_done:
            color, text, icon = "#00ff88", "BAJARILDI", "fa-check-circle"
            btn_style = "style='opacity:0.5; pointer-events:none; background:#222; color:#555; flex:1; padding:12px; border-radius:12px; text-decoration:none; text-align:center; font-weight:bold;'"
            btn_text = "Bajarilgan"
        else:
            color = "#ff4444" if needs_help else "#00f2ff"
            text = "YORDAM KERAK" if needs_help else "KUTILMOQDA"
            icon = "fa-hand-paper" if needs_help else "fa-clock"
            btn_style = "style='background:#00f2ff; color:black; flex:1; padding:12px; border-radius:12px; text-decoration:none; text-align:center; font-weight:bold;'"
            btn_text = "Bajardim"

        # O'qituvchi javobi (Mentor panelidan yozilgan xabar)
        teacher_msg = ""
        if status and hasattr(status, 'teacher_reply') and status.teacher_reply:
            teacher_msg = f"""
            <div style="background: rgba(0,242,255,0.1); border: 1px dashed #00f2ff; padding: 12px; border-radius: 12px; margin: 10px 0; border-left: 4px solid #00f2ff;">
                <small style="color:#00f2ff; font-weight:bold; font-size:10px;">USTOZ JAVOBI:</small>
                <p style="margin:5px 0 0 0; font-size:13px; color:#eee;">{status.teacher_reply}</p>
            </div>"""

        formatted_date = hw.created_at.strftime('%d.%m.%Y')

        homework_list_html += f"""
        <div class="hw-card" style="background: rgba(0,0,0,0.6); backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.1); border-left: 4px solid {color}; margin-bottom: 20px; padding: 20px; border-radius: 20px;">
            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 12px;">
                <h3 style="margin: 0; color: white;">{hw.title}</h3>
                <span style="background: {color}22; color: {color}; padding: 4px 10px; border-radius: 8px; font-size: 10px; font-weight: 900; border: 1px solid {color}44;">
                    <i class="fas {icon}"></i> {text}
                </span>
            </div>
            <p style="color: #bbb; font-size: 14px; margin-bottom: 10px;">{hw.description}</p>
            {teacher_msg}
            <div style="display: flex; gap: 10px; margin-top: 15px;">
                <a href="/homework-action/{hw.id}/done/" {btn_style}>{btn_text}</a>
                <a href="/homework-action/{hw.id}/help/" style="flex: 1; padding: 12px; border-radius: 12px; text-decoration: none; text-align: center; font-size: 14px; background: rgba(255,255,255,0.05); border: 1px solid {'#ff4444' if needs_help else '#444'}; color: {'#ff4444' if needs_help else 'white'};">
                    {'Yordam soraldi' if needs_help else 'Tushunmadim'}
                </a>
            </div>
        </div>"""

    # Asosiy HTML sahifa
    return HttpResponse(f"""
    <!DOCTYPE html>
    <html lang="uz">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
        <style>
            body {{ background: #0a0a0a url('{bg_image_url}') center/cover fixed; font-family: 'Segoe UI', sans-serif; margin: 0; color: white; }}
            .container {{ max-width: 500px; margin: 0 auto; padding: 20px; }}
            .header {{ display: flex; align-items: center; gap: 15px; margin-bottom: 30px; }}
            .back-btn {{ width: 40px; height: 40px; background: rgba(255,255,255,0.1); border-radius: 50%; display: flex; align-items: center; justify-content: center; color: #00f2ff; text-decoration: none; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <a href="/subjects/" class="back-btn"><i class="fas fa-chevron-left"></i></a>
                <div>
                    <h1 style="margin:0; font-size:22px; color:#00f2ff;">{subject.name}</h1>
                    <p style="margin:0; font-size:12px; color:#888;">{student_profile.full_name} ({student_profile.sinf}-{student_profile.parallel})</p>
                </div>
            </div>
            {homework_list_html if homework_list_html else "<p style='text-align:center; opacity:0.5;'>Vazifalar yo'q.</p>"}
        </div>
    </body>
    </html>
    """)
def update_homework_status(request, hw_id, action):
    user_login = request.session.get('user_login')
    if not user_login:
        return redirect('/')

    user_profile = get_object_or_404(Profile, login=user_login)

    # Xavfsizlik: Faqat o'z sinfiga tegishli vazifani olish
    hw = get_object_or_404(Homework, id=hw_id, sinf=user_profile.sinf, parallel=user_profile.parallel)

    with transaction.atomic():
        status, created = HomeworkStatus.objects.get_or_create(
            homework=hw,
            student=user_profile
        )

        if action == "done":
            # Agar vazifa allaqachon bajarilgan bo'lsa, ballni qayta qo'shmaslik uchun tekshiruv
            if not status.is_done:
                # Gamifikatsiya: Vazifani bajargani uchun ball berish
                user_profile.points += 5  # Har bir vazifa uchun 5 XP
                user_profile.save()

            status.is_done = True
            status.needs_help = False

        elif action == "help":
            # Agar o'quvchi yordam so'rasa, holatni yangilaymiz
            status.is_done = False
            status.needs_help = True

            # Ustozga bildirishnoma (faqat bir marta yuborilishi uchun tekshiruv)
            # Notification modelida teacher maydoni borligiga ishonch hosil qiling
            teacher = getattr(hw.subject, 'teacher', None)
            if teacher:
                Notification.objects.get_or_create(
                    receiver=teacher,
                    sender=user_profile,
                    message=f"{user_profile.full_name} '{hw.title}' vazifasiga tushunmadi.",
                    defaults={'link': f"/check-homework/{hw.id}/"}
                )

        status.save()

    return redirect(f"/subjects/{hw.subject.id}/")
def delete_student(request, student_id): # student_id nomi urls.py bilan bir xil bo'lishi kerak
    std = get_object_or_404(Profile, id=student_id)
    std.delete()
    return redirect('/teacher-dashboard/')
def teacher_dashboard(request):
    if not request.user.is_authenticated:
        return redirect('/')

    teacher = TeacherProfile.objects.filter(user=request.user).first()
    if not teacher:
        return HttpResponse("O'qituvchi profili topilmadi.")

    token = get_token(request)

    # 1. Sinf ma'lumotlarini olish
    s_n, s_p = "0", ""
    if teacher.class_leader and '-' in teacher.class_leader:
        parts = teacher.class_leader.split('-')
        s_n, s_p = parts[0].strip(), parts[1].strip()

    # 2. O'quvchilar ro'yxati va Davomat
    students = Profile.objects.filter(sinf=s_n, parallel=s_p).order_by('full_name')
    students_html = ""
    for i, std in enumerate(students, 1):
        students_html += f"""
        <div class="std-card glass" style="display: flex; justify-content: space-between; align-items: center; padding: 12px 18px; margin-bottom: 10px; border-radius: 20px;">
            <div class="std-left" style="display: flex; align-items: center; gap: 12px;">
                <span style="color: #00f2ff; font-weight: bold; font-size:12px;">{i}</span>
                <span style="font-size: 14px; color: white;">{std.full_name}</span>
            </div>
            <div class="std-right" style="display: flex; align-items: center; gap: 10px;">
                <label class="kelmadi-toggle">
                    <input type="checkbox" name="absent" value="{std.id}" style="display: none;">
                    <span class="toggle-btn">KELMADI</span>
                </label>
                <a href="/delete-student/{std.id}/" style="color: rgba(255,255,255,0.2); font-size: 14px;"><i class="fas fa-trash-alt"></i></a>
            </div>
        </div>"""

    # 3. Test Natijalari (Yangi qo'shilgan qism)
    my_tests = TeacherTest.objects.filter(teacher=request.user)
    results = TestResult.objects.filter(test__in=my_tests).select_related('student', 'test').order_by('-date')[:10]

    results_rows = ""
    for res in results:
        results_rows += f"""
        <div style="display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid rgba(255,255,255,0.05); font-size: 12px;">
            <span style="color: #eee;">{res.student.full_name.split()[0]}</span>
            <span style="color: #888;">{res.test.title[:15]}...</span>
            <span style="color: #00f2ff; font-weight: bold;">{res.score} ball</span>
        </div>"""

    if not results:
        results_rows = "<p style='text-align:center; color:#555; font-size:12px; padding:10px;'>Hali natijalar yo'q</p>"

    # 4. Top O'quvchi va Statistika
    top_std = students.order_by('-points').first()
    top_html = f"<span>{top_std.full_name}</span> <b style='color:#00f2ff;'>{top_std.points} XP</b>" if top_std else "Ma'lumot yo'q"

    html = f"""
<!DOCTYPE html>
<html lang="uz">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        :root {{ --neon: #00f2ff; --red: #ff4d4d; --glass: rgba(255, 255, 255, 0.08); }}
        body {{ 
            margin: 0; 
            background: #0a0a0a url('/static/12.jpg') no-repeat center fixed; 
            background-size: cover; 
            font-family: 'Segoe UI', Roboto, sans-serif; 
            color: white; 
            padding-bottom: 100px; 
        }}
        .overlay {{ position: fixed; inset: 0; background: rgba(0,0,0,0.72); backdrop-filter: blur(15px); z-index: -1; }}
        .container {{ max-width: 450px; margin: 0 auto; padding: 20px; }}
        .glass {{ background: var(--glass); backdrop-filter: blur(20px); border: 1px solid rgba(255,255,255,0.1); }}

        .header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 25px; }}
        .user-chip {{ 
            background: rgba(0,0,0,0.5); border: 1.5px solid var(--neon); padding: 4px 10px; 
            border-radius: 20px; display: flex; align-items: center; gap: 8px; 
            text-decoration: none; color: white; font-size: 12px; 
        }}

        .menu-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 25px; }}
        .menu-btn {{ 
            background: var(--glass); border-radius: 18px; padding: 15px; 
            text-align: center; text-decoration: none; color: white; 
            border: 1px solid rgba(255,255,255,0.05); transition: 0.3s;
        }}
        .menu-btn:active {{ transform: scale(0.95); background: rgba(0,242,255,0.1); }}
        .menu-btn i {{ display: block; font-size: 22px; color: var(--neon); margin-bottom: 8px; }}

        .section-title {{ color: var(--neon); font-size: 11px; font-weight: 900; letter-spacing: 1px; margin-bottom: 15px; text-transform: uppercase; display: flex; align-items: center; gap: 8px; }}

        .add-std-btn {{ 
            text-decoration: none; color: var(--neon); font-size: 10px; 
            background: rgba(0,242,255,0.1); padding: 6px 14px; border-radius: 12px; 
            border: 1px solid var(--neon); float: right; 
        }}

        .toggle-btn {{ 
            background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); 
            padding: 6px 12px; border-radius: 8px; font-size: 9px; color: #777; 
            cursor: pointer; transition: 0.3s; font-weight: bold;
        }}
        input:checked + .toggle-btn {{ background: var(--red); color: white; border-color: var(--red); box-shadow: 0 0 10px var(--red); }}

        .save-btn {{ 
            width: 100%; padding: 18px; border: none; border-radius: 20px; 
            background: var(--neon); color: black; font-weight: 900; 
            margin-top: 15px; cursor: pointer; box-shadow: 0 5px 20px rgba(0,242,255,0.4); 
        }}

        .bottom-nav {{ 
            position: fixed; bottom: 0; left: 0; right: 0; height: 75px; 
            background: rgba(10,10,10,0.9); backdrop-filter: blur(20px); 
            border-top: 1px solid rgba(255,255,255,0.1); display: flex; 
            justify-content: space-around; align-items: center; z-index: 1000; 
        }}
        .nav-item {{ text-decoration: none; color: #555; font-size: 10px; text-align: center; }}
        .nav-item.active {{ color: var(--neon); }}
        .nav-item i {{ font-size: 20px; display: block; margin-bottom: 4px; }}
    </style>
</head>
<body>
    <div class="overlay"></div>
    <div class="container">
        <div class="header">
            <div style="color:var(--neon); font-weight:900; font-size:18px; letter-spacing:-1px;">MENTOR<span style="color:white; font-weight:100;">PRO</span></div>
            <a href="/teacher-profile/" class="user-chip">
                <span>{teacher.full_name.split()[0]}</span>
                <div style="width:22px; height:22px; background:var(--neon); border-radius:50%; color:black; display:flex; align-items:center; justify-content:center; font-weight:bold; font-size:11px;">{teacher.full_name[0]}</div>
            </a>
        </div>

        <div class="menu-grid">
            <a href="/reels/" class="menu-btn glass"><i class="fas fa-bolt"></i><span style="font-size:10px;">Reels</span></a>
            <a href="/teacher-schedule/" class="menu-btn glass"><i class="fas fa-clock"></i><span style="font-size:10px;">Jadval</span></a>
            <a href="/create-test/" class="menu-btn glass"><i class="fas fa-plus-circle"></i><span style="font-size:10px;">Testlar</span></a>
        </div>

        <div class="section-title"><i class="fas fa-chart-line"></i> Sinf statistikasi</div>
        <div class="glass" style="padding:18px; border-radius:22px; margin-bottom:25px;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                <span style="color:#888; font-size:11px;">TOP O'QUVCHI:</span>
                <div style="font-size:13px;">{top_html}</div>
            </div>
            <div style="height:1px; background:rgba(255,255,255,0.05); margin-bottom:12px;"></div>
            <div style="color:#888; font-size:11px; margin-bottom:8px;">SO'NGGI TEST NATIJALARI:</div>
            {results_rows}
        </div>

        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:15px;">
            <div class="section-title" style="margin-bottom:0;"><i class="fas fa-users"></i> {s_n}-{s_p} Sinf o'quvchilari</div>
            <a href="/add-student/" class="add-std-btn"><i class="fas fa-plus"></i></a>
        </div>

        <form method="POST" action="/save-attendance/">
            <input type="hidden" name="csrfmiddlewaretoken" value="{token}">
            {students_html}
            <button type="submit" class="save-btn">DAVOMATNI YAKUNLASH</button>
        </form>
    </div>

    <nav class="bottom-nav">
        <a href="/teacher-dashboard/" class="nav-item active"><i class="fas fa-home"></i><span>Asosiy</span></a>
        <a href="/teacher-homeworks/" class="nav-item"><i class="fas fa-book"></i><span>Vazifalar</span></a>
        <a href="/compete/" class="nav-item"><i class="fas fa-trophy"></i><span>Reyting</span></a>
        <a href="/teacher-profile/" class="nav-item"><i class="fas fa-cog"></i><span>Profil</span></a>
    </nav>
</body>
</html>
    """
    return HttpResponse(html)
def teacher_statistics(request):
    return HttpResponse("<h2 style='color:white; text-align:center; margin-top:50px;'>Statistika sahifasi tayyorlanmoqda...</h2>")
def teacher_schedule(request):
    if not request.user.is_authenticated: return redirect('/')

    # 1. O'qituvchi profilini olish
    teacher_prof = TeacherProfile.objects.filter(user=request.user).first()
    if not teacher_prof: return HttpResponse("Mentor profili topilmadi")

    token = get_token(request)
    days = ['Dushanba', 'Seshanba', 'Chorshanba', 'Payshanba', 'Juma', 'Shanba']

    # Sinf ma'lumotlari
    sinf_info = teacher_prof.class_leader.split('-') if teacher_prof.class_leader else ["0", "X"]
    sinf_n, par_n = sinf_info[0], sinf_info[1]

    # 2. SAQLASH MANTIQI (POST)
    if request.method == "POST":
        for day in days:
            day_subjects = []
            for i in range(1, 7):
                s = request.POST.get(f'subject_{day}_{i}', '').strip()
                if s: day_subjects.append(s)

            # Xatoni tuzatuvchi qism: teacher maydonini ham qo'shamiz
            Schedule.objects.update_or_create(
                teacher=request.user,  # Xatolik shu yerda edi, endi u to'ldirildi
                day=day,
                defaults={
                    'sinf': sinf_n,
                    'parallel': par_n,
                    'subjects_list': " | ".join(day_subjects)
                }
            )
        return redirect('/teacher-dashboard/')

    # 3. MAVJUD MA'LUMOTLARNI OLISH
    # Har bir kun uchun darslarni qidiramiz
    raw_schedule = Schedule.objects.filter(teacher=request.user)
    current_schedule = {s.day: s.subjects_list.split(" | ") for s in raw_schedule}

    # 4. FORM GENERATSIYASI (6 ta qatordan)
    form_content = ""
    for d in days:
        existing_subjs = current_schedule.get(d, [])
        # Har doim kamida 6 ta katak bo'lishini ta'minlaymiz
        while len(existing_subjs) < 6: existing_subjs.append("")

        inputs = ""
        for i in range(1, 7):
            val = existing_subjs[i - 1]
            inputs += f'<input type="text" name="subject_{d}_{i}" value="{val}" placeholder="{i}-dars">'

        form_content += f"""
        <div class="day-card glass">
            <h3>{d}</h3>
            <div class="input-grid">
                {inputs}
            </div>
        </div>"""

    return HttpResponse(f"""
<!DOCTYPE html>
<html lang="uz">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        :root {{ --neon: #00f2ff; --glass: rgba(255, 255, 255, 0.05); }}
        body {{ 
            margin: 0; background: #0a0a0a url('{static('12.jpg')}') no-repeat center fixed; 
            background-size: cover; font-family: sans-serif; color: white; padding: 20px 15px;
        }}
        .overlay {{ position: fixed; inset: 0; background: rgba(0,0,0,0.85); backdrop-filter: blur(15px); z-index: -1; }}
        .container {{ max-width: 450px; margin: 0 auto; }}

        h2 {{ color: var(--neon); text-align: center; text-transform: uppercase; font-size: 18px; margin-bottom: 5px; }}
        .info {{ text-align: center; opacity: 0.6; font-size: 12px; margin-bottom: 25px; display: block; }}

        .day-card {{ padding: 20px; margin-bottom: 15px; border-radius: 20px; border: 1px solid rgba(255,255,255,0.1); }}
        .day-card h3 {{ margin: 0 0 15px 0; font-size: 13px; color: var(--neon); text-transform: uppercase; }}

        .input-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }}
        input {{ 
            width: 100%; padding: 10px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.1); 
            background: rgba(0,0,0,0.3); color: white; outline: none; box-sizing: border-box; font-size: 12px;
        }}
        input:focus {{ border-color: var(--neon); }}

        .save-btn {{ 
            width: 100%; padding: 18px; border: none; border-radius: 18px; background: var(--neon); 
            color: black; font-weight: 900; font-size: 14px; cursor: pointer; margin-top: 15px;
            box-shadow: 0 5px 15px rgba(0, 242, 255, 0.3);
        }}
        .back {{ display: block; text-align: center; margin-top: 20px; color: white; text-decoration: none; font-size: 13px; opacity: 0.5; }}
        .glass {{ background: var(--glass); backdrop-filter: blur(20px); }}
    </style>
</head>
<body>
    <div class="overlay"></div>
    <div class="container">
        <h2>DARS JADVALINI TAHRIRLASH</h2>
        <span class="info">{sinf_n}-{par_n} sinfi uchun</span>

        <form method="POST">
            <input type="hidden" name="csrfmiddlewaretoken" value="{token}">
            {form_content}
            <button class="save-btn">SAQLASH VA QAYTISH</button>
        </form>

        <a href="/teacher-dashboard/" class="back"><i class="fas fa-arrow-left"></i> Orqaga qaytish</a>
    </div>
</body>
</html>
""")
def upload_video_view(request):
    # 1. Foydalanuvchini sessiyadan tekshirish
    user_login = request.session.get('user_login')
    if not user_login:
        return redirect('/')

    user_profile = get_object_or_404(Profile, login=user_login)
    token = get_token(request)

    # 2. POST so'rovi kelganda videoni saqlash
    if request.method == "POST" and request.FILES.get('video_file'):
        try:
            # Videoni bazaga yaratish
            Video.objects.create(
                author=user_profile,
                video_file=request.FILES.get('video_file'),
                title=request.POST.get('description', '')
            )

            # Muvaffaqiyatli yuklangandan keyin reels sahifasiga o'tish
            return redirect('/reels/')

        except Exception as e:
            # Xatolik yuz bersa terminalga va ekranga chiqarish
            print(f"Video yuklashda xato: {e}")
            return HttpResponse(f"Xatolik yuz berdi: {e}")

    # 3. GET so'rovi yoki xatolik bo'lmaganda sahifa dizaynini ko'rsatish
    bg_image = static('12.jpg')
    avatar = user_profile.image.url if user_profile.image else static('default_avatar.png')

    html = f"""
    <!DOCTYPE html>
    <html lang="uz">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
        <style>
            :root {{ --neon: #00f2ff; }}
            body {{ 
                margin: 0; background: #000 url('{bg_image}') no-repeat center center fixed; 
                background-size: cover; font-family: sans-serif;
                display: flex; justify-content: center; align-items: center; height: 100vh;
            }}
            .card {{ 
                background: rgba(255,255,255,0.1); backdrop-filter: blur(20px); 
                border-radius: 30px; border: 1px solid rgba(0,242,255,0.3);
                width: 85%; max-width: 380px; padding: 30px; text-align: center; color: white;
            }}
            .avatar-img {{ width: 70px; height: 70px; border-radius: 50%; border: 2px solid var(--neon); object-fit: cover; margin-bottom: 10px; }}
            .btn {{ width: 100%; padding: 15px; border-radius: 15px; border: none; background: var(--neon); color: #000; font-weight: bold; cursor: pointer; margin-top: 15px; transition: 0.3s; }}
            .btn:hover {{ opacity: 0.8; transform: scale(1.02); }}
            textarea {{ width: 100%; padding: 10px; margin: 10px 0; border-radius: 10px; background: rgba(0,0,0,0.4); color: white; border: 1px solid #444; box-sizing: border-box; resize: none; outline: none; }}
            textarea:focus {{ border-color: var(--neon); }}
            input[type="file"] {{ margin: 15px 0; color: #ccc; font-size: 13px; }}
        </style>
    </head>
    <body>
        <div class="card">
            <img src="{avatar}" class="avatar-img">
            <h2 style="margin: 0 0 10px 0; letter-spacing: 1px; text-transform: uppercase;">Video Yuklash</h2>
            <form method="POST" enctype="multipart/form-data">
                <input type="hidden" name="csrfmiddlewaretoken" value="{token}">
                <input type="file" name="video_file" accept="video/*" required>
                <textarea name="description" placeholder="Video haqida qisqacha..." rows="2" required></textarea>
                <button type="submit" class="btn">ULASHISH</button>
            </form>
            <a href="/reels/" style="color: #888; text-decoration: none; display: block; margin-top: 20px; font-size: 13px;">BEKOR QILISH</a>
        </div>
    </body>
    </html>
    """
    return HttpResponse(html)
def add_student_view(request):
    teacher = TeacherProfile.objects.filter(user=request.user).first()

    if request.method == "POST":
        full_name = request.POST.get('full_name')

        if full_name and teacher:
            # Sinf va parallel ma'lumotlarini o'qituvchidan olamiz
            s_n, s_p = "0", ""
            if teacher.class_leader and '-' in teacher.class_leader:
                parts = teacher.class_leader.split('-')
                s_n, s_p = parts[0], parts[1]

            # Yangi o'quvchi (jadval bandi) yaratish
            # Login qismi takrorlanmasligi uchun ism va sinfni birlashtiramiz
            import random
            generated_login = f"std_{random.randint(1000, 9999)}"

            Profile.objects.create(
                full_name=full_name,
                login=generated_login,
                sinf=s_n,
                parallel=s_p,
                points=0
            )
            return redirect('/teacher-dashboard/')

    token = get_token(request)
    html = f"""
<!DOCTYPE html>
<html lang="uz">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{ 
            margin: 0; background: #0a0a0a url('{static('12.jpg')}') no-repeat center center fixed; 
            background-size: cover; font-family: sans-serif; height: 100vh;
            display: flex; align-items: center; justify-content: center;
        }}
        .overlay {{ position: fixed; inset: 0; background: rgba(0,0,0,0.7); backdrop-filter: blur(15px); z-index: -1; }}
        .glass-card {{ 
            background: rgba(255,255,255,0.1); backdrop-filter: blur(25px); 
            border: 1px solid rgba(255,255,255,0.1); border-radius: 30px; 
            padding: 40px 30px; width: 85%; max-width: 380px; text-align: center;
            box-shadow: 0 20px 50px rgba(0,0,0,0.5);
        }}
        input {{ 
            width: 100%; padding: 18px; border-radius: 15px; border: 1px solid rgba(255,255,255,0.2); 
            background: rgba(0,0,0,0.4); color: white; font-size: 16px; margin: 25px 0; outline: none; box-sizing: border-box;
        }}
        input:focus {{ border-color: #00f2ff; box-shadow: 0 0 15px rgba(0,242,255,0.2); }}
        .save-btn {{ 
            width: 100%; padding: 18px; background: #00f2ff; color: black; 
            border: none; border-radius: 15px; font-weight: 900; cursor: pointer; text-transform: uppercase;
        }}
    </style>
</head>
<body>
    <div class="overlay"></div>
    <div class="glass-card">
        <h2 style="color:white; margin:0;">F.I.SH ni kiriting</h2>
        <form method="POST">
            <input type="hidden" name="csrfmiddlewaretoken" value="{token}">
            <input type="text" name="full_name" placeholder="Ism Familiya" required autocomplete="off">
            <button type="submit" class="save-btn">SAQLASH VA QO'SHISH</button>
            <a href="/teacher-dashboard/" style="display:block; margin-top:20px; color:#666; text-decoration:none; font-size:14px;">Bekor qilish</a>
        </form>
    </div>
</body>
</html>
    """
    return HttpResponse(html)
def teacher_reg_view(request):
    """GET so'rovi uchun chiroyli ro'yxatdan o'tish formasi"""
    bg_image = static('12.jpg')
    # CSRF token olish
    from django.middleware.csrf import get_token
    token = get_token(request)

    return HttpResponse(f"""
    <!DOCTYPE html>
    <html lang="uz">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Ustozlar Ro'yxati</title>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
        <style>
            :root {{ --neon: #00f2ff; }}
            body {{ 
                margin: 0; background: url('{bg_image}') center/cover fixed no-repeat; 
                font-family: 'Segoe UI', sans-serif; color: white;
                display: flex; justify-content: center; align-items: center; min-height: 100vh;
            }}
            .overlay {{ position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.88); z-index: 1; }}
            .card {{ 
                position: relative; z-index: 2; width: 90%; max-width: 480px; 
                background: rgba(20,20,20,0.75); backdrop-filter: blur(25px);
                padding: 35px; border-radius: 30px; border: 1px solid rgba(0,242,255,0.25);
                box-shadow: 0 15px 35px rgba(0,0,0,0.5);
            }}
            h2 {{ color: var(--neon); text-align: center; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 25px; font-size: 22px; }}
            .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }}
            .full {{ grid-column: 1 / -1; }}
            label {{ font-size: 11px; color: var(--neon); font-weight: bold; margin-left: 5px; text-transform: uppercase; opacity: 0.8; }}
            input {{ 
                width: 100%; padding: 12px; margin-top: 5px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.1);
                background: rgba(0,0,0,0.4); color: white; outline: none; box-sizing: border-box; transition: 0.3s;
            }}
            input:focus {{ border-color: var(--neon); box-shadow: 0 0 10px rgba(0,242,255,0.2); }}
            .btn-reg {{ 
                width: 100%; padding: 16px; margin-top: 25px; border-radius: 15px; border: none;
                background: var(--neon); color: black; font-weight: 900; cursor: pointer;
                text-transform: uppercase; letter-spacing: 1px; transition: 0.3s;
            }}
            .btn-reg:hover {{ box-shadow: 0 0 25px rgba(0,242,255,0.5); transform: translateY(-2px); }}
        </style>
    </head>
    <body>
        <div class="overlay"></div>
        <div class="card">
            <h2><i class="fas fa-user-plus"></i> Ustozlar Registratsiyasi</h2>
            <form method="POST" action="/teacher-registration-save/">
                <input type="hidden" name="csrfmiddlewaretoken" value="{token}">

                <div class="grid">
                    <div class="full">
                        <label>To'liq ism-familiya:</label>
                        <input type="text" name="full_name" placeholder="Masalan: Azizov Anvar" required>
                    </div>
                    <div>
                        <label>Login:</label>
                        <input type="text" name="username" placeholder="Login" required>
                    </div>
                    <div>
                        <label>Parol:</label>
                        <input type="password" name="password" placeholder="Parol" required>
                    </div>
                    <div class="full">
                        <label>Dars beradigan faningiz:</label>
                        <input type="text" name="subject" placeholder="Masalan: Matematika" required>
                    </div>
                    <div>
                        <label>Sinf rahbari (ixtiyoriy):</label>
                        <input type="text" name="class_leader" placeholder="Masalan: 7-B">
                    </div>
                    <div>
                        <label>Telefon raqam:</label>
                        <input type="text" name="phone" placeholder="+998" required>
                    </div>
                    <div class="full">
                        <label>Manzil (Mahalla, Ko'cha, Uy):</label>
                        <div style="display:flex; gap:5px;">
                            <input type="text" name="mahalla" placeholder="Mahalla">
                            <input type="text" name="street" placeholder="Ko'cha">
                            <input type="text" name="home" placeholder="Uy" style="width:70px;">
                        </div>
                    </div>
                </div>

                <button type="submit" class="btn-reg">Ro'yxatdan o'tish</button>
            </form>
        </div>
    </body>
    </html>
    """)
def teacher_registration_save(request):
    if request.method == "POST":
        data = request.POST
        username = data.get('username')
        password = data.get('password')
        full_name = data.get('full_name')

        # 1. Login tekshiruvi
        if User.objects.filter(username=username).exists():
            return HttpResponse(
                "<script>alert('Bu login band! Iltimos, boshqa login tanlang.'); window.history.back();</script>")

        try:
            with transaction.atomic():
                # 2. Django User yaratish
                user = User.objects.create_user(
                    username=username,
                    password=password,
                    is_staff=True,
                    first_name=full_name.split()[0] if full_name else ""
                )

                # 3. ASOSIY Profile yaratish (MUHIM!)
                # Dashboard "Profile.objects.get(login=...)" deb qidirayotgani uchun bu shart
                Profile.objects.create(
                    login=username,
                    password=password,  # Shifrlanmagan holda saqlash profilingiz mantiqiga qarab
                    full_name=full_name,
                    phone=data.get('phone'),
                    sinf=data.get('class_leader', '').split('-')[0] if '-' in data.get('class_leader', '') else "0",
                    parallel=data.get('class_leader', '').split('-')[1] if '-' in data.get('class_leader', '') else ""
                )

                # 4. TeacherProfile yaratish
                TeacherProfile.objects.create(
                    user=user,
                    full_name=full_name,
                    subject_name=data.get('subject'),
                    class_leader=data.get('class_leader'),
                    phone=data.get('phone'),
                    address_mahalla=data.get('mahalla'),
                    address_street=data.get('street'),
                    address_home_number=data.get('home')
                )

                # 5. Subject (Fan) yaratish yoki yangilash
                subject_name = data.get('subject')
                if subject_name:
                    Subject.objects.update_or_create(
                        name=subject_name,
                        defaults={'teacher_user': user}
                    )

                # 6. Tizimga avtomatik kirish
                auth_login(request, user)

                # Muvaffaqiyatli xabar va o'tish
                return redirect('/teacher-dashboard/')

        except Exception as e:
            # Xatolikni konsolga chiqarish (debugging uchun)
            print(f"REGISTRATION ERROR: {e}")
            return HttpResponse(f"Xatolik yuz berdi: {str(e)}")

    return redirect('/teacher-register/')
def give_homework_view(request):
    if request.method == "POST":
        title = request.POST.get('title')
        desc = request.POST.get('desc')
        sinf_tanlangan = request.POST.get('sinf')
        parallel_tanlangan = request.POST.get('parallel')

        subject = Subject.objects.filter(teacher=request.user).first()

        if subject:
            with transaction.atomic():
                # 1. Vazifani yaratamiz
                new_hw = Homework.objects.create(
                    subject=subject,
                    title=title,
                    description=desc,
                    sinf=sinf_tanlangan,
                    parallel=parallel_tanlangan
                )

                # 2. Shu sinfdagi barcha o'quvchilarga bildirishnoma yuboramiz
                students_in_class = Profile.objects.filter(sinf=sinf_tanlangan, parallel=parallel_tanlangan)

                # Agar Notification modelingiz bo'lsa:
                notifications = [
                    Notification(
                        receiver_student=student,
                        message=f"Yangi vazifa: {subject.name} fanidan '{title}' mavzusida vazifa berildi.",
                        link=f"/subjects/{subject.id}/"
                    ) for student in students_in_class
                ]
                Notification.objects.bulk_create(notifications)  # Tezkor saqlash uchun bulk_create

            # Muvaffaqiyatli sahifa (Siz yozgan HTML qismi shu yerda)
            # ...
def save_test_view(request):
    # Faqat tizimga kirgan va o'qituvchi statusiga ega foydalanuvchilar uchun
    if request.method == "POST" and request.user.is_staff:
        try:
            teacher_prof = TeacherProfile.objects.get(user=request.user)

            # Formadan ma'lumotlarni yig'ish va tozalash
            title = request.POST.get('test_title').strip()
            questions_text = request.POST.get('questions').strip()
            answers_text = request.POST.get('answers').strip()
            sinf_val = request.POST.get('sinf')
            parallel_val = request.POST.get('parallel')

            with transaction.atomic():
                # 3. Testni yaratish
                TeacherTest.objects.create(
                    teacher=request.user,
                    subject=teacher_prof.subject_name,
                    title=title,
                    questions=questions_text,
                    correct_answers=answers_text,
                    sinf=sinf_val,
                    parallel=parallel_val
                )

            return HttpResponse(f"""
                <script>
                    alert('{sinf_val}-{parallel_val} sinfi uchun "{title}" testi muvaffaqiyatli e'lon qilindi!');
                    window.location.href = '/teacher-dashboard/';
                </script>
            """)

        except TeacherProfile.DoesNotExist:
            return HttpResponse("Xatolik: O'qituvchi profili topilmadi.")
        except Exception as e:
            return HttpResponse(f"Xatolik yuz berdi: {e}")

    return redirect('/teacher-dashboard/')
def compete_view(request):
    user_login = request.session.get('user_login')
    if not user_login:
        return redirect('/')

    # O'quvchini olish
    user = Profile.objects.get(login=user_login)

    # 1. O'quvchining sinfiga mos va faol BELLASHUVLARNI (Competition) olish
    # Competition -> TeacherTest orqali bog'langan
    active_competitions = Competition.objects.filter(
        test__sinf=user.sinf,
        test__parallel=user.parallel,
        is_active=True
    ).order_by('-start_time')

    # 2. O'quvchi topshirib bo'lgan testlar ID ro'yxati
    finished_test_ids = TestResult.objects.filter(student=user).values_list('test_id', flat=True)

    tests_html = ""
    now = timezone.now()

    for comp in active_competitions:
        test = comp.test

        # Vaqtni tekshirish
        is_expired = now > comp.end_time
        is_not_started = now < comp.start_time

        if test.id in finished_test_ids:
            # Bajarilgan holat
            btn_style = "background: rgba(0, 255, 136, 0.2); border: 1px solid #00ff88; color: #00ff88; cursor: default;"
            btn_text = "TOPSHIRILDI"
            status_icon = "fa-check-double"
            glow_color = "#00ff88"
        elif is_expired:
            # Vaqti tugagan
            btn_style = "background: #222; color: #555; cursor: not-allowed;"
            btn_text = "YOPILGAN"
            status_icon = "fa-clock"
            glow_color = "#444"
        elif is_not_started:
            # Hali boshlanmagan
            btn_style = "background: #333; color: #aaa; cursor: wait;"
            btn_text = f"SOAT {comp.start_time.strftime('%H:%M')} DA"
            status_icon = "fa-hourglass-start"
            glow_color = "#ffcc00"
        else:
            # Faol holat
            btn_style = "background: #ff00ff; box-shadow: 0 0 15px #ff00ff; color: white;"
            btn_text = "YECHISH"
            status_icon = "fa-bolt"
            glow_color = "#ff00ff"

        tests_html += f"""
        <div class="test-card" style="border-left: 4px solid {glow_color};">
            <div class="test-info">
                <div class="icon-wrap" style="background: {glow_color}22;">
                    <i class="fas {status_icon}" style="color: {glow_color};"></i>
                </div>
                <div class="text-content">
                    <h3>{comp.title}</h3>
                    <p>{test.subject} | {test.teacher.first_name or "Ustoz"}</p>
                    <small>Tugash vaqti: {comp.end_time.strftime('%d-%b, %H:%M')}</small>
                </div>
            </div>
            <a href="/start-test/{test.id}/" class="start-btn" style="{btn_style}">{btn_text}</a>
        </div>
        """

    # 3. HTMLni render qilish (RETURN qilish shart!)
    return HttpResponse(f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
        <style>
            body {{ 
                background: url('{static('12.jpg')}') no-repeat center center fixed; 
                background-size: cover; font-family: sans-serif; margin: 0; color: white;
            }}
            .overlay {{ background: rgba(0,0,0,0.85); min-height: 100vh; padding: 20px; }}
            .header {{ text-align: center; margin-bottom: 30px; }}
            .header h1 {{ color: #00f2ff; text-shadow: 0 0 10px #00f2ff; margin: 0; }}

            .test-list-container {{ max-width: 500px; margin: 0 auto; display: flex; flex-direction: column; gap: 15px; }}

            .test-card {{ 
                background: rgba(20,20,20,0.9); border-radius: 15px; padding: 15px;
                display: flex; align-items: center; justify-content: space-between;
                backdrop-filter: blur(5px); border: 1px solid #333;
            }}
            .test-info {{ display: flex; align-items: center; gap: 15px; }}
            .icon-wrap {{ width: 50px; height: 50px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 20px; }}
            .text-content h3 {{ margin: 0; font-size: 16px; color: #fff; }}
            .text-content p {{ margin: 3px 0; font-size: 12px; color: #aaa; }}
            .text-content small {{ font-size: 10px; color: #666; }}

            .start-btn {{ 
                padding: 10px 20px; border-radius: 10px; text-decoration: none; 
                font-weight: bold; font-size: 12px; transition: 0.3s; 
            }}
        </style>
    </head>
    <body>
        <div class="overlay">
            <div class="header">
                <h1>Testlarni Yeching!</h1>
                <p style="color: #666;">{user.sinf}-{user.parallel} sinf o'quvchilari uchun</p>
            </div>
            <div class="test-list-container">
                {tests_html or '<p style="text-align:center; color:#444;">Hozircha bellashuvlar yoq </p> '}
        </div>
        </div>
        </body>
        </html>
""")
def start_test_view(request, test_id):
    test = get_object_or_404(TeacherTest, id=test_id)

    # Avval yechganligini tekshirish (Double check)
    user_login = request.session.get('user_login')
    user_profile = Profile.objects.get(login=user_login)
    if TestResult.objects.filter(student=user_profile, test=test).exists():
        return HttpResponse(
            "<script>alert('Siz bu testni topshirib bo'lgansiz!'); window.location.href='/compete/';</script>")

    bg_image_url = static('12.jpg')
    token = get_token(request)

    return HttpResponse(f"""
    <!DOCTYPE html>
    <html>
    <head>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
        <style>
            body {{ margin: 0; background: url('{bg_image_url}') center/cover fixed; font-family: 'Segoe UI', sans-serif; color: white; padding: 20px; }}
            .overlay {{ position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.85); z-index: -1; }}

            .test-container {{ background: rgba(255,255,255,0.1); backdrop-filter: blur(20px); padding: 30px; border-radius: 30px; max-width: 750px; margin: 0 auto; border: 1px solid #ff00ff; box-shadow: 0 0 20px rgba(255, 0, 255, 0.2); }}

            .timer-box {{ position: sticky; top: 0; background: #ff00ff; color: white; padding: 10px; border-radius: 10px; text-align: center; font-weight: bold; font-size: 20px; margin-bottom: 20px; z-index: 10; }}

            h2 {{ color: #ff00ff; text-align: center; margin-top: 0; }}
            .q-box {{ background: rgba(0,0,0,0.4); padding: 25px; border-radius: 20px; margin-bottom: 25px; white-space: pre-wrap; line-height: 1.8; border: 1px solid rgba(255,255,255,0.15); font-size: 17px; }}

            .ans-input {{ width: 100%; padding: 18px; border-radius: 15px; background: white; border: 2px solid #ff00ff; color: black; font-weight: 800; font-size: 18px; box-sizing: border-box; text-align: center; letter-spacing: 2px; }}
            .btn-submit {{ width: 100%; padding: 18px; background: #ff00ff; color: white; border: none; border-radius: 15px; font-weight: 900; margin-top: 25px; cursor: pointer; transition: 0.3s; text-transform: uppercase; }}
            .btn-submit:hover {{ background: white; color: #ff00ff; transform: scale(1.02); }}
        </style>
    </head>
    <body>
        <div class="overlay"></div>
        <div class="test-container">
            <div class="timer-box" id="timer">15:00</div>

            <h2><i class="fas fa-bolt"></i> {test.title}</h2>
            <p style="text-align:center; opacity:0.8; margin-bottom:20px;">{test.subject} | To'g'ri javoblarni ketma-ket yozing</p>

            <div class="q-box">{test.questions}</div>

            <form id="testForm" action="/check-test/{test.id}/" method="POST">
                <input type="hidden" name="csrfmiddlewaretoken" value="{token}">
                <p style="color: #ff00ff; font-weight: bold; text-align:center;">Javoblar formati:</p>
                <p style="font-size: 13px; opacity: 0.7; text-align:center; margin-bottom:15px;">Faqat harflarni yozing: <b>abcd...</b></p>

                <input type="text" name="student_answers" class="ans-input" placeholder="Masalan: abccdb..." autocomplete="off" required>

                <button type="submit" class="btn-submit">NATIJANI KO'RISH</button>
            </form>
        </div>

        <script>
            let timeLeft = 15 * 60; // 15 minut
            const timerDisplay = document.getElementById('timer');

            const countdown = setInterval(() => {{
                let minutes = Math.floor(timeLeft / 60);
                let seconds = timeLeft % 60;
                seconds = seconds < 10 ? '0' + seconds : seconds;

                timerDisplay.innerHTML = minutes + ":" + seconds;

                if (timeLeft <= 0) {{
                    clearInterval(countdown);
                    document.getElementById('testForm').submit();
                }}
                timeLeft--;
            }}, 1000);
        </script>
    </body>
    </html>
    """)
def extract_answers(text):
    if not text:
        return {}
    # Sleshlar (\d, \s) f-string ichida bo'lmagani uchun endi xato bermaydi
    return dict(re.findall(r'(\d+)\s*[\)\.\-]?\s*([a-z])', text.lower()))
def check_test_view(request, test_id):
    if request.method == "POST":
        test = get_object_or_404(TeacherTest, id=test_id)
        user_login = request.session.get('user_login')

        if not user_login:
            return redirect('/')

        student = get_object_or_404(Profile, login=user_login)

        student_ans = request.POST.get('student_answers', '').lower()
        teacher_ans = test.correct_answers.lower()

        # Javoblarni ajratib olish
        s_dict = extract_answers(student_ans)
        t_dict = extract_answers(teacher_ans)

        # Ball hisoblash
        score = 0
        for q_num, correct_val in t_dict.items():
            if s_dict.get(q_num) == correct_val:
                score += 1

        # XP hisoblash (f-stringdan tashqarida)
        earned_xp = score * 10
        total_questions = len(t_dict) if len(t_dict) > 0 else 15

        # Natijani bazaga saqlash
        with transaction.atomic():
            TestResult.objects.get_or_create(
                student=student,
                test=test,
                defaults={'score': score}
            )
            student.points += earned_xp
            student.save()

        # HTML uchun rang va statik fayllarni tayyorlash
        bg_image_url = static('12.jpg')
        result_color = "#00ff88" if score >= (total_questions / 2) else "#ff00ff"

        # 2. HTML javobi (Jingalak qavslar ichida faqat tayyor o'zgaruvchilar)
        html = f"""
        <!DOCTYPE html>
        <html lang="uz">
        <head>
            <meta charset="UTF-8">
            <title>Natija</title>
        </head>
        <body style="background: url('{bg_image_url}') center/cover fixed; height: 100vh; display: flex; align-items: center; justify-content: center; font-family: 'Segoe UI', sans-serif; color: white; margin: 0;">
            <div style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.85); z-index: -1;"></div>
            <div style="background: rgba(255,255,255,0.1); backdrop-filter: blur(15px); padding: 50px; border-radius: 40px; text-align: center; border: 2px solid {result_color}; box-shadow: 0 0 30px {result_color}; width: 300px;">
                <div style="font-size: 80px; font-weight: 900; color: {result_color}; text-shadow: 0 0 20px {result_color};">{score}</div>
                <div style="font-size: 20px; letter-spacing: 5px; margin: 10px 0; opacity: 0.7;">/ {total_questions}</div>
                <p style="font-size: 18px; margin: 25px 0; font-weight: 600;">To'g'ri javoblar</p>
                <p style="color: gold; font-size: 14px; margin-bottom: 30px;">+{earned_xp} XP to'pladingiz!</p>
                <a href="/compete/" style="display: block; padding: 15px; background: {result_color}; color: black; text-decoration: none; border-radius: 15px; font-weight: 900; text-transform: uppercase;">Ajoyib!</a>
            </div>
        </body>
        </html>
        """
        return HttpResponse(html)

    return redirect('/compete/')
def subjects_list_view(request):
    if not request.user.is_authenticated:
        return redirect('/')

    # Foydalanuvchi o'qituvchi ekanligini tekshiramiz
    is_teacher = TeacherProfile.objects.filter(user=request.user).exists()

    # --- O'QITUVCHI UCHUN LOGIKA ---
    if is_teacher:
        teacher = request.user.teacherprofile
        requests_html = ""

        if teacher.class_leader and '-' in teacher.class_leader:
            s_n, s_p = teacher.class_leader.split('-')

            # XATONI TO'G'IRLASH:
            # Comment modeli ForeignKey bo'lgani uchun, murojaati borlarni
            # comment__isnull=False orqali topamiz.
            students_with_requests = Profile.objects.filter(
                sinf=s_n,
                parallel=s_p,
                comment__isnull=False
            ).distinct()

            for std in students_with_requests:
                # O'quvchining oxirgi yozgan murojaatlarini matn sifatida chiqaramiz
                # Agar std.comment ForeignKey bo'lsa, std.comment.text (yoki sizdagi maydon nomi) deb yozing
                # Hozircha std.comment deb qoldiramiz, agar u bog'langan model bo'lsa .text qo'shing
                murojaat_matni = std.comment if hasattr(std.comment,
                                                        'encode') else "Yordam so'ralgan (Murojaatni ko'rish)"

                requests_html += f"""
                <div class="glass" style="padding:15px; margin-bottom:15px; border-left:4px solid #00f2ff; background:rgba(255,255,255,0.05); border-radius:15px;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                        <b style="color:#00f2ff;">{std.full_name}</b>
                        <span style="font-size:10px; background:rgba(0,242,255,0.1); padding:3px 8px; border-radius:10px; color:white;">{std.sinf}-{std.parallel}</span>
                    </div>
                    <p style="margin:0; font-size:14px; color:#eee;">{murojaat_matni}</p>
                    <div style="text-align:right; margin-top:10px;">
                        <a href="/clear-request/{std.id}/" style="color:#ff4444; text-decoration:none; font-size:12px; font-weight:bold;">
                            <i class="fas fa-check-circle"></i> Yordam berildi (O'chirish)
                        </a>
                    </div>
                </div>"""

        return HttpResponse(f"""
            <html>
            <head>
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
                <style>
                    body {{ background:#0a0a0a; color:white; font-family:sans-serif; padding:20px; }}
                    .glass {{ backdrop-filter:blur(10px); border:1px solid rgba(255,255,255,0.1); }}
                    .header {{ color:#00f2ff; margin-bottom:20px; display:flex; align-items:center; gap:15px; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <a href="/teacher-dashboard/" style="color:white; text-decoration:none;"><i class="fas fa-arrow-left"></i> Orqaga</a>
                    <h2 style="margin:0; font-size:18px;">O'quvchilar murojaatlari</h2>
                </div>
                {requests_html if requests_html else "<p style='color:#666; text-align:center; margin-top:50px;'>Hozircha yordam so'rovlari yo'q.</p>"}
            </body>
            </html>
        """)

    # --- O'QUVCHI UCHUN LOGIKA ---
    else:
        # select_related('teacher_user') xatolikni oldini oladi
        subjects = Subject.objects.all().select_related('teacher_user')

        subs_html = ""
        for s in subjects:
            t_name = s.teacher_user.full_name if s.teacher_user else "Noma'lum"
            subs_html += f"""
            <div class="glass" style="padding:15px; margin-bottom:12px; display:flex; justify-content:space-between; align-items:center; background:rgba(255,255,255,0.05); border-radius:15px; border:1px solid rgba(255,255,255,0.1);">
                <div>
                    <div style="font-weight:bold; color:#00f2ff;">{s.name}</div>
                    <div style="font-size:11px; color:#888;">Ustoz: {t_name}</div>
                </div>
                <a href="/send-help-request/{s.id}/" style="background:#00f2ff; color:black; padding:8px 15px; border-radius:10px; text-decoration:none; font-size:12px; font-weight:bold; box-shadow: 0 0 10px rgba(0,242,255,0.3);">
                    Yordam so'rash
                </a>
            </div>"""

        return HttpResponse(f"""
            <html>
            <head>
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
                <style>
                    body {{ background:#0a0a0a; color:white; font-family:sans-serif; padding:20px; }}
                    .glass {{ backdrop-filter:blur(10px); }}
                </style>
            </head>
            <body>
                <div style="display:flex; align-items:center; gap:15px; margin-bottom:20px;">
                    <a href="/second/" style="color:white; text-decoration:none;"><i class="fas fa-arrow-left">Orqaga</i></a>
                    <h2 style="color:#00f2ff; font-size:18px; margin:0;">Fanlar ro'yxati</h2>
                </div>
                {subs_html}
            </body>
            </html>
        """)
def teachers_by_subject_view(request, subject_id):
    # 1. Tanlangan fanni olamiz
    subject = get_object_or_404(Subject, id=subject_id)

    # 2. Xavfsizlik: Faqat tizimga kirgan o'quvchini aniqlash
    user_login = request.session.get('user_login')
    if not user_login:
        return redirect('/')

    # 3. Ustozlarni qidirish
    # Maslahat: Subject modelida 'teacher' ForeignKey bo'lsa,
    # teachers = TeacherProfile.objects.filter(user=subject.teacher) deb olish aniqroq
    teachers = TeacherProfile.objects.filter(subject_name__icontains=subject.name)

    bg_image_url = static('12.jpg')
    token = get_token(request)

    teacher_cards = ""
    for t in teachers:
        # Har bir ustoz kartochkasi
        teacher_cards += f"""
        <div class="teacher-card">
            <div style="display:flex; align-items:center; gap:15px; margin-bottom:15px;">
                <div class="avatar-circle">
                    <i class="fas fa-user-tie fa-lg"></i>
                </div>
                <div>
                    <h3 style="margin:0; color:#00f2ff;">{t.full_name}</h3>
                    <small style="opacity:0.7;">{t.subject_name} mutaxassisi</small>
                </div>
            </div>

            <form action="/send-help-request/{t.user.id}/" method="POST">
                <input type="hidden" name="csrfmiddlewaretoken" value="{token}">
                <input type="hidden" name="subject_id" value="{subject.id}">
                <textarea name="message" placeholder="{subject.name} bo'yicha savolingizni yozing..." required></textarea>
                <button type="submit" class="send-btn">
                    <i class="fas fa-paper-plane"></i> SAVOLNI YUBORISH
                </button>
            </form>
        </div>
        """

    # HttpResponse ichidagi CSS va HTML qismlari o'zingizda mavjud...
def send_help_request(request, teacher_id):
    if request.method == "POST":
        user_login = request.session.get('user_login')
        if not user_login:
            return redirect('/')

        student_profile = get_object_or_404(Profile, login=user_login)
        teacher_user = get_object_or_404(User, id=teacher_id)
        student_msg = request.POST.get('message', '').strip()

        if not student_msg:
            return HttpResponse("<script>alert('Xabar bo'sh bo'lishi mumkin emas!'); window.history.back();</script>")

        try:
            with transaction.atomic():
                # 1. Bildirishnoma yaratish (Ustozning notification panelida ko'rinadi)
                Notification.objects.create(
                    receiver=teacher_user,
                    sender_profile=student_profile,
                    message=f"❓ Yangi savol: {student_msg[:50]}...",
                    link=f"/teacher-messages/" # Bu yerda ustoz xabarlarni ko'radi
                )

                # 2. (Ixtiyoriy) Agar HelpRequest modelingiz bo'lsa, xabarni saqlash
                # HelpRequest.objects.create(student=student_profile, teacher=teacher_user, text=student_msg)

            bg_image_url = static('12.jpg')
            return HttpResponse(f"""
                <body style="background: url('{bg_image_url}') center/cover; height: 100vh; display: flex; align-items: center; justify-content: center; font-family: sans-serif; color: white;">
                    <div style="background: rgba(0,0,0,0.8); padding: 40px; border-radius: 25px; text-align: center; border: 1px solid #00f2ff; backdrop-filter: blur(10px);">
                        <i class="fas fa-check-circle" style="font-size: 50px; color: #00f2ff; margin-bottom: 20px;"></i>
                        <h2>XABAR YUBORILDI</h2>
                        <p style="opacity: 0.8;">Ustozingiz xabarni ko'rib chiqib, javob beradi.</p>
                        <script>
                            setTimeout(() => {{ window.location.href = '/second/'; }}, 3000);
                        </script>
                    </div>
                </body>
            """)
        except Exception as e:
            return HttpResponse(f"Xatolik yuz berdi: {e}")

    return redirect('/ask-teacher/')
def public_profile_view(request, username):
    # 1. Ma'lumotlarni bazadan olish (Yutuqlar olib tashlandi)
    target_user = get_object_or_404(Profile, login=username)
    posts_count = Post.objects.filter(author=target_user).count()

    # 2. Sessiyadagi foydalanuvchini tekshirish
    current_user_login = request.session.get('user_login')
    current_user = None
    is_following = False

    if current_user_login:
        current_user = Profile.objects.filter(login=current_user_login).first()
        if current_user:
            is_following = target_user.followers.filter(id=current_user.id).exists()

    # 3. Rasmlar va Statik fayllar
    avatar_url = target_user.image.url if target_user.image else static('default_avatar.png')
    bg_image = static('12.jpg')

    # 4. Tugma mantiqi
    if is_following:
        follow_btn_text = "Obunani bekor qilish"
        follow_btn_class = "unfollow-btn"
        follow_url = f"/unfollow/{target_user.login}/"
    else:
        follow_btn_text = "Obuna bo'lish"
        follow_btn_class = "follow-btn"
        follow_url = f"/follow/{target_user.login}/"

    # 5. HTML javobi (Yutuqlar va XP ballarsiz)
    html_content = f"""
    <!DOCTYPE html>
    <html lang="uz">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{target_user.full_name} | Profil</title>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
        <style>
            :root {{ --neon: #00f2ff; }}
            body {{
                background: url('{bg_image}') center/cover fixed;
                font-family: 'Segoe UI', sans-serif;
                margin: 0;
                color: white;
            }}
            .overlay {{
                position: fixed; top: 0; left: 0; width: 100%; height: 100%;
                background: rgba(0,0,0,0.85); z-index: -1;
            }}
            .profile-card {{
                max-width: 400px; margin: 60px auto; padding: 40px 20px;
                background: rgba(255,255,255,0.05); backdrop-filter: blur(20px);
                border-radius: 40px; text-align: center; border: 1px solid rgba(255,255,255,0.1);
            }}
            .avatar {{
                width: 110px; height: 110px; border-radius: 50%;
                border: 3px solid var(--neon); object-fit: cover;
                box-shadow: 0 0 20px rgba(0,242,255,0.3);
            }}
            .stats {{ display: flex; justify-content: space-around; margin: 30px 0; border-top: 1px solid #333; border-bottom: 1px solid #333; padding: 15px 0; }}
            .stats b {{ font-size: 18px; color: var(--neon); }}
            .stats small {{ color: #888; text-transform: uppercase; font-size: 10px; letter-spacing: 1px; }}

            .follow-btn {{ background: var(--neon); color: black; padding: 12px 30px; border-radius: 25px; text-decoration: none; font-weight: bold; display: inline-block; }}
            .unfollow-btn {{ background: rgba(255,255,255,0.1); color: white; padding: 12px 30px; border-radius: 25px; text-decoration: none; border: 1px solid #444; display: inline-block; }}

            .bottom-nav {{ position:fixed; bottom:0; left:0; width:100%; background:rgba(0,0,0,0.9); display:flex; justify-content:space-around; padding:15px 0; border-top:1px solid rgba(255,255,255,0.1); z-index:1000; }}
            .nav-item {{ text-decoration:none; color:#666; display:flex; flex-direction:column; align-items:center; font-size:10px; gap:4px; }}
            .nav-item i {{ font-size:22px; }}
        </style>
    </head>
    <body>
        <div class="overlay"></div>

        <div class="profile-card">
            <img src="{avatar_url}" class="avatar" alt="Avatar">
            <h2 style="margin: 15px 0 5px 0; letter-spacing: 1px;">{target_user.full_name}</h2>
            <p style="color: #888; margin-bottom: 25px;">@{target_user.login}</p>

            <div class="stats">
                <div><b>{posts_count}</b><br><small>Postlar</small></div>
                <div><b>{target_user.followers.count()}</b><br><small>Obunachilar</small></div>
                <div><b>{target_user.following.count()}</b><br><small>Obunalar</small></div>
            </div>

            <div style="margin-top: 25px; display: flex; align-items: center; justify-content: center; gap: 15px;">
                <a href="{follow_url}" class="{follow_btn_class}">{follow_btn_text}</a>
                <a href="/chat/{target_user.login}/" style="color: var(--neon); text-decoration: none; background: rgba(0,242,255,0.1); width: 45px; height: 45px; border-radius: 50%; display: flex; align-items: center; justify-content: center; border: 1px solid var(--neon);">
                    <i class="fas fa-comment-dots"></i>
                </a>
            </div>
        </div>

        <nav class="bottom-nav">
            <a href="/second/" class="nav-item"><i class="fas fa-th-large"></i><span>Menyu</span></a>
            <a href="/library/" class="nav-item"><i class="fas fa-book"></i><span>Kutubxona</span></a>
            <a href="/reels/" class="nav-item"><i class="fas fa-play-circle"></i><span>Reels</span></a>
            <a href="/profile/" class="nav-item"><i class="fas fa-user"></i><span>Profil</span></a>
        </nav>
    </body>
    </html>
    """
    return HttpResponse(html_content)
def teacher_homeworks(request):
    if not request.user.is_authenticated:
        return redirect('/')

    token = get_token(request)

    if request.method == "POST":
        title = request.POST.get('title')
        description = request.POST.get('description')
        sinf_n = request.POST.get('sinf_number')
        parallel_n = request.POST.get('parallel')

        # O'qituvchining fanini aniqlash (IntegrityError oldini olish uchun)
        subject = Subject.objects.filter(teacher_user=request.user).first()

        if not subject:
            # Agar fan topilmasa, bazada xato bermasligi uchun ogohlantirish
            return HttpResponse("<h2>Xato: Admin panelda sizga fan (Subject) biriktirilmagan!</h2>")

        Homework.objects.create(
            subject=subject,
            sinf=sinf_n,
            parallel=parallel_n,
            teacher_user=request.user,
            title=title,
            description=description
        )
        return redirect('/teacher-dashboard/')

    # Rasmda chiqmayotgan raqamlarni to'g'irlash uchun variantlar
    sinf_options = "".join([f'<option value="{i}">{i}-sinf</option>' for i in range(1, 12)])

    html = f"""
<!DOCTYPE html>
<html lang="uz">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        :root {{ --neon: #00f2ff; --glass: rgba(255, 255, 255, 0.08); }}
        body {{ 
            margin: 0; background: #0a0a0a url('/static/12.jpg') no-repeat center fixed; 
            background-size: cover; color: white; font-family: sans-serif; padding-bottom: 100px;
        }}
        .overlay {{ position: fixed; inset: 0; background: rgba(0,0,0,0.7); backdrop-filter: blur(15px); z-index: -1; }}
        .card {{ 
            background: rgba(0,0,0,0.6); padding: 25px; border-radius: 25px; 
            max-width: 400px; margin: 40px auto; border: 1px solid var(--neon); 
            backdrop-filter: blur(10px); box-shadow: 0 0 20px rgba(0,242,255,0.2);
        }}
        input, textarea, select {{ 
            width: 100%; padding: 12px; margin: 10px 0; border-radius: 12px; 
            border: 1px solid rgba(255,255,255,0.1); background: rgba(0,0,0,0.5); 
            color: white; outline: none; box-sizing: border-box;
        }}
        select option {{ background: #111; color: white; }}
        label {{ color: var(--neon); font-size: 11px; font-weight: bold; text-transform: uppercase; }}
        .btn {{ 
            width: 100%; padding: 16px; background: var(--neon); border: none; 
            border-radius: 20px; font-weight: 900; cursor: pointer; margin-top: 20px; color: black;
        }}
        .bottom-nav {{ 
            position: fixed; bottom: 0; left: 0; right: 0; height: 75px; 
            background: rgba(10,10,10,0.95); backdrop-filter: blur(20px); 
            border-top: 1px solid rgba(255,255,255,0.1); display: flex; 
            justify-content: space-around; align-items: center; z-index: 1000; 
        }}
        .nav-item {{ text-decoration: none; color: #555; font-size: 10px; text-align: center; }}
        .nav-item.active {{ color: var(--neon); }}
        .nav-item i {{ font-size: 20px; display: block; margin-bottom: 4px; }}
        .hidden {{ display: none; }}
    </style>
</head>
<body>
    <div class="overlay"></div>
    <div class="container">
        <div class="card">
            <h2 style="text-align:center; color:var(--neon); margin-top:0;">VAZIFA YARATISH</h2>
            <form method="POST">
                <input type="hidden" name="csrfmiddlewaretoken" value="{token}">

                <label>QAYSI SINFGA?</label>
                <select name="sinf_number" onchange="document.getElementById('p_box').classList.remove('hidden')" required>
                    <option value="" disabled selected>Sinfni tanlang</option>
                    {sinf_options}
                </select>

                <div id="p_box" class="hidden">
                    <label>PARALLELNI TANLANG</label>
                    <select name="parallel" required>
                        <option value="A">A-parallel</option>
                        <option value="B">B-parallel</option>
                        <option value="D">D-parallel</option>
                    </select>
                </div>

                <label>VAZIFA MATNI</label>
                <input type="text" name="title" placeholder="Mavzu nomi" required>
                <textarea name="description" rows="4" placeholder="Vazifa tafsilotlari..."></textarea>

                <label>TOPSHIRISH MUDDATI</label>
                <input type="date" required>
                <div style="font-size:11px; color:#888; display:flex; align-items:center; gap:8px;">
                    <input type="checkbox" checked onclick="return false;" style="width:auto;"> 
                    Qabul qilish vaqti avtomatik: 13:00 gacha
                </div>

                <button type="submit" class="btn">O'QUVCHILARGA YUBORISH</button>
            </form>
        </div>
    </div>

    <nav class="bottom-nav">
        <a href="/teacher-dashboard/" class="nav-item"><i class="fas fa-home"></i><span>Asosiy</span></a>
        <a href="/teacher-homeworks/" class="nav-item active"><i class="fas fa-book"></i><span>Vazifalar</span></a>
        <a href="/compete/" class="nav-item"><i class="fas fa-trophy"></i><span>Reyting</span></a>
        <a href="/teacher-profile/" class="nav-item"><i class="fas fa-cog"></i><span>Profil</span></a>
    </nav>
</body>
</html>
    """
    return HttpResponse(html)
def upload_reel(request):
    if not request.user.is_authenticated:
        return redirect('/')

    if request.method == "POST" and request.FILES.get('reel_video'):
        try:
            teacher = request.user.teacherprofile
            video = request.FILES['reel_video']
            caption = request.POST.get('caption', '')

            TeacherReels.objects.create(teacher=teacher, video=video, caption=caption)
            return redirect('/teacher-profile/')
        except Exception:
            return redirect('/')

    # Orqa fon rasmi va Token
    bg_image = static('12.jpg')
    token = get_token(request)

    return HttpResponse(f"""
<!DOCTYPE html>
<html lang="uz">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Video yuklash</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        :root {{ --neon: #00f2ff; }}
        body {{ 
            margin: 0; 
            background: url('{bg_image}') center/cover fixed no-repeat; 
            font-family: 'Segoe UI', sans-serif; 
            color: white; 
            height: 100vh; 
            display: flex; 
            align-items: center; 
            justify-content: center;
        }}
        .overlay {{ 
            position: fixed; top: 0; left: 0; width: 100%; height: 100%; 
            background: rgba(0,0,0,0.85); z-index: -1; 
        }}
        .upload-card {{
            background: rgba(255, 255, 255, 0.05);
            padding: 30px 20px;
            border-radius: 30px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(15px);
            width: 90%;
            max-width: 400px;
            text-align: center;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        }}
        h2 {{ color: var(--neon); margin-bottom: 25px; font-weight: 600; letter-spacing: 1px; }}

        .file-input-wrapper {{
            margin-bottom: 20px;
        }}
        input[type="file"] {{
            background: rgba(255, 255, 255, 0.1);
            padding: 15px;
            border-radius: 15px;
            width: 100%;
            box-sizing: border-box;
            color: #ccc;
            border: 1px dashed var(--neon);
            cursor: pointer;
        }}
        input[type="text"] {{
            background: rgba(255, 255, 255, 0.08);
            border: 1px solid rgba(0, 242, 255, 0.2);
            color: white;
            padding: 15px;
            border-radius: 15px;
            width: 100%;
            box-sizing: border-box;
            margin-bottom: 25px;
            font-size: 14px;
        }}
        .submit-btn {{
            background: var(--neon);
            color: black;
            border: none;
            padding: 18px;
            border-radius: 20px;
            width: 100%;
            font-weight: 800;
            cursor: pointer;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            box-shadow: 0 5px 20px rgba(0, 242, 255, 0.4);
            transition: 0.3s;
        }}
        .submit-btn:active {{ transform: scale(0.98); }}

        .back-link {{
            display: block;
            margin-top: 20px;
            color: #aaa;
            text-decoration: none;
            font-size: 13px;
        }}
        .back-link:hover {{ color: white; }}
    </style>
</head>
<body>
    <div class="overlay"></div>
    <div class="upload-card">
        <i class="fas fa-cloud-upload-alt" style="font-size: 40px; color: var(--neon); margin-bottom: 15px;"></i>
        <h2>Yangi Reel</h2>

        <form method="POST" enctype="multipart/form-data">
            <input type="hidden" name="csrfmiddlewaretoken" value="{token}">

            <div class="file-input-wrapper">
                <input type="file" name="reel_video" accept="video/*" required>
            </div>

            <input type="text" name="caption" placeholder="Video uchun qisqacha tavsif...">

            <button type="submit" class="submit-btn">
                <i class="fas fa-paper-plane"></i> Yuklash
            </button>
        </form>

        <a href="/teacher-profile/" class="back-link">
            <i class="fas fa-arrow-left"></i> Bekor qilish
        </a>
    </div>
</body>
</html>
    """)
def teacher_profile(request):
    if not request.user.is_authenticated:
        return redirect('/')

    try:
        teacher = request.user.teacherprofile
    except Exception:
        return redirect('/')

    # Ma'lumotlarni saqlash mantiqi
    if request.method == "POST":
        if request.FILES.get('avatar'):
            teacher.avatar = request.FILES['avatar']

        full_name = request.POST.get('full_name')
        subject = request.POST.get('subject')
        class_leader = request.POST.get('class_leader')

        if full_name: teacher.full_name = full_name
        if subject: teacher.subject_name = subject
        if class_leader: teacher.class_leader = class_leader

        teacher.save()
        return redirect('/teacher-profile/')

    bg_image = static('12.jpg')
    token = get_token(request)
    prof_pic_url = teacher.avatar.url if teacher.avatar else f"https://ui-avatars.com/api/?name={teacher.full_name}&background=00f2ff&color=000"

    # O'quvchilar soni
    st_count = 0
    if teacher.class_leader and '-' in teacher.class_leader:
        try:
            s_n, p_n = teacher.class_leader.split('-')
            st_count = Profile.objects.filter(sinf=s_n, parallel=p_n).count()
        except:
            st_count = 0

    html_content = f"""
    <!DOCTYPE html>
    <html lang="uz">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Profil | {teacher.full_name}</title>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
        <style>
            :root {{ --neon: #00f2ff; }}
            body {{ margin: 0; background: url('{bg_image}') center/cover fixed no-repeat; font-family: 'Segoe UI', sans-serif; color: white; padding-bottom: 100px; }}
            .overlay {{ position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.85); z-index: -1; }}
            .container {{ max-width: 450px; margin: 0 auto; padding: 40px 20px; text-align: center; }}

            /* Profil header va Plyus tugmasi */
            .profile-header {{ position: relative; width: fit-content; margin: 0 auto 20px; }}
            .prof-pic-container {{ position: relative; width: 130px; height: 130px; }}
            .prof-pic {{ width: 100%; height: 100%; border-radius: 50%; border: 3px solid var(--neon); object-fit: cover; box-shadow: 0 0 25px rgba(0,242,255,0.4); }}
            .upload-avatar {{ position: absolute; bottom: 5px; right: 5px; background: var(--neon); color: black; width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; cursor: pointer; border: 2px solid #000; z-index: 10; }}

            /* O'ng tarafdagi plyus tugmasi (Upload video uchun) */
            .plus-upload-btn {{ 
                position: absolute; top: 15px; right: -60px; 
                background: rgba(255, 255, 255, 0.05); border: 1.5px solid var(--neon); 
                color: var(--neon); width: 45px; height: 45px; border-radius: 50%; 
                display: flex; align-items: center; justify-content: center; 
                text-decoration: none; font-size: 22px; backdrop-filter: blur(5px);
                box-shadow: 0 0 15px rgba(0,242,255,0.3);
            }}

            /* Inputlar */
            input[type="text"] {{
                background: rgba(255,255,255,0.08); border: 1px solid rgba(0,242,255,0.2);
                color: white; padding: 12px; border-radius: 15px; width: 90%; text-align: center; font-size: 14px;
            }}
            .name-input {{ font-size: 26px !important; font-weight: bold; color: var(--neon) !important; border: none !important; background: transparent !important; margin-bottom: 10px; }}

            .info-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-top: 25px; }}
            .info-box {{ background: rgba(255,255,255,0.05); padding: 18px; border-radius: 25px; border: 1px solid rgba(255,255,255,0.1); backdrop-filter: blur(10px); }}
            .info-box i {{ color: var(--neon); font-size: 22px; margin-bottom: 8px; }}
            .info-box span {{ display: block; font-size: 10px; opacity: 0.6; text-transform: uppercase; }}

            /* Yutuqlar tugmasi (Plyusiz) */
            .ach-link {{ 
                display: flex; align-items: center; justify-content: center; gap: 10px;
                margin-top: 25px; padding: 18px; border-radius: 25px; 
                background: rgba(0, 242, 255, 0.05); color: var(--neon); text-decoration: none; 
                font-weight: bold; border: 1px solid rgba(0, 242, 255, 0.4);
            }}

            /* Saqlash tugmasi */
            .save-btn {{ 
                width: 100%; padding: 18px; border-radius: 25px; border: none; background: var(--neon); 
                color: black; font-weight: 800; margin-top: 15px; cursor: pointer; text-transform: uppercase;
                box-shadow: 0 0 20px rgba(0,242,255,0.6); letter-spacing: 1.5px;
            }}
        </style>
    </head>
    <body>
        <div class="overlay"></div>
        <div class="container">
            <form method="POST" enctype="multipart/form-data">
                <input type="hidden" name="csrfmiddlewaretoken" value="{token}">

                <div class="profile-header">
                    <div class="prof-pic-container">
                        <img src="{prof_pic_url}" class="prof-pic">
                        <label for="fileInput" class="upload-avatar"><i class="fas fa-camera"></i></label>
                        <input type="file" name="avatar" id="fileInput" style="display:none;" onchange="this.form.submit()">
                    </div>

                    <a href="/upload-reel/" class="plus-upload-btn">
                        <i class="fas fa-plus"></i>
                    </a>
                </div>

                <div style="font-size:11px; opacity:0.5; letter-spacing:3px; text-transform:uppercase;">Digital School Mentor</div>
                <input type="text" name="full_name" value="{teacher.full_name}" class="name-input">

                <div class="info-grid">
                    <div class="info-box">
                        <i class="fas fa-book-open"></i>
                        <span>Fan</span>
                        <input type="text" name="subject" value="{teacher.subject_name}">
                    </div>
                    <div class="info-box">
                        <i class="fas fa-chalkboard"></i>
                        <span>Sinf</span>
                        <input type="text" name="class_leader" value="{teacher.class_leader or ''}" placeholder="8-A">
                    </div>
                    <div class="info-box">
                        <i class="fas fa-user-friends"></i>
                        <span>O'quvchilar</span>
                        <div style="margin-top:10px; font-weight:bold; color:var(--neon);">{st_count} ta</div>
                    </div>
                    <div class="info-box">
                        <i class="fas fa-id-card"></i>
                        <span>ID Raqami</span>
                        <div style="margin-top:10px; font-weight:bold; color:var(--neon);">#T{teacher.id}</div>
                    </div>
                </div>
                <button type="submit" class="save-btn"><i class="fas fa-save"></i> SAQLASH</button>
            </form>

            <a href="/logout/" style="color: #ff4444; text-decoration: none; font-size: 13px; display: block; margin-top: 30px; opacity: 0.8;">
                <i class="fas fa-sign-out-alt"></i> Chiqish
            </a>
        </div>

        <nav style="position:fixed; bottom:0; left:0; width:100%; background:rgba(10,10,10,0.98); display:flex; justify-content:space-around; padding:15px 0; border-top:1px solid rgba(255,255,255,0.1); backdrop-filter:blur(10px);">
            <a href="/teacher-dashboard/" style="color:#555; font-size:22px;"><i class="fas fa-th-large"></i></a>
            <a href="/teacher-homeworks/" style="color:#555; font-size:22px;"><i class="fas fa-tasks"></i></a>
            <a href="/teacher-profile/" style="color:var(--neon); font-size:22px;"><i class="fas fa-user-circle"></i></a>
        </nav>
    </body>
    </html>
    """
    return HttpResponse(html_content)
def save_attendance(request):
    if request.method == "POST":
        teacher = TeacherProfile.objects.filter(user=request.user).first()
        # Formadan 'absent' nomli barcha tanlangan checkboxlarni oladi
        absent_ids = request.POST.getlist('absent')
        today = timezone.now().date()

        count = 0
        for s_id in absent_ids:
            student = Profile.objects.filter(id=s_id).first()
            if student:
                Attendance.objects.get_or_create(
                    student=student,
                    teacher=teacher,
                    date=today,
                    is_absent=True
                )
                count += 1

        print(f"DEBUG: Saqlandi {count} ta o'quvchi")
        return redirect('/teacher-dashboard/')
    return redirect('/teacher-dashboard/')
def student_action(request, hw_id, action_type):
    # Agar foydalanuvchi tizimga kirmagan bo'lsa
    if not request.user.is_authenticated:
        return redirect('login')

    # Statusni olish yoki yangi yaratish
    status, created = HomeworkStatus.objects.get_or_create(
        homework_id=hw_id,
        student=request.user
    )

    if action_type == 'help':
        # "Tushunmadim" holati
        status.needs_help = True
        status.is_completed = False
    elif action_type == 'done':
        # "Bajardim" holati
        status.is_completed = True
        status.needs_help = False

    status.save()

    # O'quvchi qaysi sahifadan kelgan bo'lsa, o'sha yerga qaytarish
    # Odatda fanlar yoki algebra sahifasiga qaytadi
    return redirect(request.META.get('HTTP_REFERER', '/'))
def student_schedule(request):
    user_login = request.session.get('user_login')
    if not user_login:
        return redirect('/')

    user = Profile.objects.filter(login=user_login).first()
    if not user:
        return redirect('/')

    # O'quvchining sinfiga tegishli jadvalni bazadan olish
    # Mentor jadvalni saqlayotganda sinf va parallel (masalan: 9 va A) bilan saqlagan
    schedule_data = Schedule.objects.filter(sinf=user.sinf, parallel=user.parallel)

    days = ['Dushanba', 'Seshanba', 'Chorshanba', 'Payshanba', 'Juma', 'Shanba']
    schedule_dict = {s.day: s.subjects_list.split(" | ") for s in schedule_data}

    schedule_cards = ""
    for day in days:
        subjects = schedule_dict.get(day, [])
        # Agar dars bo'lmasa, 6 ta bo'sh katak ko'rsatish
        while len(subjects) < 6:
            subjects.append("---")

        items = ""
        for i, sub in enumerate(subjects[:6]):
            items += f"<li><span class='num'>{i + 1}</span> <span class='subj'>{sub}</span></li>"

        schedule_cards += f"""
        <div class="day-card glass">
            <h3><i class="fas fa-calendar-day"></i> {day}</h3>
            <ul>{items}</ul>
        </div>"""

    html = f"""
<!DOCTYPE html>
<html lang="uz">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dars Jadvali | {user.sinf}-{user.parallel}</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        :root {{ --neon: #00f2ff; --glass: rgba(255, 255, 255, 0.07); }}
        body {{ 
            margin: 0; background: #0a0a0a url('{static('12.jpg')}') no-repeat center fixed; 
            background-size: cover; font-family: 'Segoe UI', sans-serif; color: white; padding: 20px 15px;
        }}
        .overlay {{ position: fixed; inset: 0; background: rgba(0,0,0,0.85); backdrop-filter: blur(15px); z-index: -1; }}
        .header {{ text-align: center; margin-bottom: 25px; }}
        .back-link {{ color: var(--neon); text-decoration: none; font-size: 14px; display: flex; align-items: center; gap: 8px; margin-bottom: 20px; }}

        .day-card {{ 
            background: var(--glass); border-radius: 25px; padding: 20px; margin-bottom: 15px; 
            border: 1px solid rgba(255,255,255,0.1); backdrop-filter: blur(10px);
        }}
        .day-card h3 {{ margin: 0 0 15px 0; font-size: 14px; color: var(--neon); text-transform: uppercase; letter-spacing: 1px; }}

        ul {{ list-style: none; padding: 0; margin: 0; }}
        li {{ 
            display: flex; align-items: center; padding: 10px 0; 
            border-bottom: 1px solid rgba(255,255,255,0.05); font-size: 15px; 
        }}
        li:last-child {{ border: none; }}
        .num {{ width: 25px; color: var(--neon); font-weight: 800; font-size: 12px; opacity: 0.8; }}
        .subj {{ font-weight: 500; }}
    </style>
</head>
<body>
    <div class="overlay"></div>
    <a href="/second/" class="back-link"><i class="fas fa-chevron-left"></i> Orqaga qaytish</a>

    <div class="header">
        <h2 style="margin:0; font-weight: 900; letter-spacing: 1px;">DARS JADVALI</h2>
        <p style="opacity:0.6; font-size:12px; margin-top:5px;">{user.sinf}-{user.parallel} sinfi o'quvchisi uchun</p>
    </div>

    {schedule_cards}
</body>
</html>
    """
    return HttpResponse(html)
@login_required
def create_competition_from_test(request, test_id):
    # Faqat o'qituvchi o'z testini bellashuvga qo'shishi mumkin
    test = get_object_or_404(TeacherTest, id=test_id, teacher=request.user)

    if request.method == "POST":
        title = request.POST.get('title')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')

        Competition.objects.create(
            title=title,
            test=test,
            start_time=start_time,
            end_time=end_time
        )
        return redirect('second_list')  # Bellashuvlar ro'yxati sahifasiga

    return render(request, 'teacher/create_competition.html', {'test': test})


def create_test_view(request):
    if request.method == "POST":
        sinf = request.POST.get('sinf')
        parallel = request.POST.get('parallel').upper()
        title = request.POST.get('title')
        subject = "Informatika"

        questions_list = []
        for key in request.POST:
            if key.startswith('q_text_'):
                num = key.split('_')[-1]
                q_text = request.POST.get(f'q_text_{num}')
                q_type = request.POST.get(f'q_type_{num}')

                question_data = {
                    'savol': q_text,
                    'turi': q_type,
                }

                if q_type == 'yopiq':
                    question_data['v_a'] = request.POST.get(f'q_v_a_{num}')
                    question_data['v_b'] = request.POST.get(f'q_v_b_{num}')
                    question_data['v_c'] = request.POST.get(f'q_v_c_{num}')
                    question_data['v_d'] = request.POST.get(f'q_v_d_{num}')
                    question_data['javob'] = request.POST.get(f'q_ans_yopiq_{num}')
                else:
                    question_data['javob'] = request.POST.get(f'q_ans_ochiq_{num}')

                if q_text:
                    questions_list.append(question_data)

        TeacherTest.objects.create(
            teacher=request.user,
            title=title,
            subject=subject,
            questions=json.dumps(questions_list, ensure_ascii=False),
            sinf=sinf,
            parallel=parallel
        )
        return redirect('/teacher-dashboard/')

    token = get_token(request)

    html_content = f"""
    <!DOCTYPE html>
    <html lang="uz">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Yangi Test Yaratish</title>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
        <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;800&display=swap" rel="stylesheet">
        <style>
            :root {{ 
                --neon: #00f2ff; 
                --glass: rgba(10, 10, 10, 0.8); 
                --border: rgba(0, 242, 255, 0.3); 
            }}
            body {{ 
                margin: 0; 
                background: #000 url('/static/12.jpg') no-repeat center center fixed; 
                background-size: cover; 
                color: white; 
                font-family: 'Poppins', sans-serif; 
                padding-bottom: 50px;
            }}
            .overlay {{ 
                position: fixed; inset: 0; 
                background: rgba(0, 0, 0, 0.75); 
                backdrop-filter: blur(12px); 
                z-index: -1; 
            }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .glass-card {{ 
                background: var(--glass); 
                border: 1px solid var(--border); 
                border-radius: 35px; 
                padding: 30px; 
                box-shadow: 0 20px 50px rgba(0,0,0,0.5); 
                backdrop-filter: blur(10px);
            }}
            h2 {{ 
                text-align:center; color:var(--neon); 
                text-transform:uppercase; font-size:22px; 
                letter-spacing: 2px; margin-bottom: 30px;
                text-shadow: 0 0 15px rgba(0,242,255,0.4);
            }}
            input, select, textarea {{ 
                width: 100%; padding: 15px; margin-top: 10px; 
                background: rgba(255,255,255,0.06); 
                border: 1px solid rgba(255,255,255,0.1); 
                border-radius: 15px; color: white; outline: none; box-sizing: border-box; 
                font-family: inherit;
            }}
            input:focus, textarea:focus {{ border-color: var(--neon); background: rgba(255,255,255,0.1); }}

            .count-selector {{ display: flex; justify-content: space-between; margin: 25px 0; gap: 10px; }}
            .count-btn {{ 
                flex: 1; background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); 
                padding: 12px; border-radius: 15px; color: white; cursor: pointer; 
                text-align: center; transition: 0.3s; font-weight: 600;
            }}
            .count-btn.active {{ background: var(--neon); color: #000; box-shadow: 0 0 20px rgba(0,242,255,0.4); }}

            .q-box {{ 
                background: rgba(255,255,255,0.03); border-radius: 25px; 
                padding: 20px; margin-bottom: 25px; border-left: 6px solid var(--neon);
                animation: fadeIn 0.5s ease;
            }}
            @keyframes fadeIn {{ from {{ opacity:0; transform: translateY(10px); }} to {{ opacity:1; transform: translateY(0); }} }}

            .variants-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-top: 15px; }}
            .type-switch {{ display: flex; gap: 8px; }}
            .type-btn {{ 
                font-size: 11px; padding: 6px 14px; border-radius: 20px; 
                cursor: pointer; border: 1px solid var(--neon); color: var(--neon); 
                text-transform: uppercase; font-weight: bold;
            }}
            .type-btn.active {{ background: var(--neon); color: black; }}

            .save-btn {{ 
                width: 100%; padding: 22px; background: var(--neon); color: black; 
                border: none; border-radius: 25px; font-weight: 900; font-size: 18px; 
                cursor: pointer; margin-top: 20px; text-transform: uppercase;
                box-shadow: 0 10px 30px rgba(0,242,255,0.3); transition: 0.3s;
            }}
            .save-btn:hover {{ transform: translateY(-3px); box-shadow: 0 15px 40px rgba(0,242,255,0.5); }}
        </style>
    </head>
    <body>
        <div class="overlay"></div>
        <div class="container">
            <div class="glass-card">
                <h2><i class="fas fa-plus-circle" style="margin-right:10px;"></i>Yangi Test Majmuasi</h2>
                <form method="POST">
                    <input type="hidden" name="csrfmiddlewaretoken" value="{token}">

                    <div style="display:flex; gap:12px;">
                        <input type="text" name="title" placeholder="Mavzu nomi" required>
                        <input type="number" name="sinf" placeholder="Sinf" style="width:100px" required>
                        <input type="text" name="parallel" placeholder="A" style="width:80px" required>
                    </div>

                    <div class="count-selector">
                        <div class="count-btn" onclick="generateQuestions(5, event)">5</div>
                        <div class="count-btn" onclick="generateQuestions(10, event)">10</div>
                        <div class="count-btn" onclick="generateQuestions(15, event)">15</div>
                        <div class="count-btn" onclick="generateQuestions(25, event)">25</div>
                    </div>

                    <div id="questionsContainer"></div>

                    <button type="submit" class="save-btn">TESTNI SAQLASH</button>
                </form>
            </div>
        </div>

        <script>
            function generateQuestions(count, event) {{
                const container = document.getElementById('questionsContainer');
                container.innerHTML = '';

                if(event) {{
                    document.querySelectorAll('.count-btn').forEach(btn => btn.classList.remove('active'));
                    event.target.classList.add('active');
                }}

                for(let i=1; i<=count; i++) {{
                    const qBox = document.createElement('div');
                    qBox.className = 'q-box';
                    qBox.innerHTML = `
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                            <span style="color:var(--neon); font-weight:bold; font-size:14px;">SAVOL #${{i}}</span>
                            <div class="type-switch">
                                <span class="type-btn active" id="btn_y_${{i}}" onclick="setType(${{i}}, 'yopiq')">Variantli</span>
                                <span class="type-btn" id="btn_o_${{i}}" onclick="setType(${{i}}, 'ochiq')">Ochiq</span>
                            </div>
                        </div>
                        <input type="hidden" name="q_type_${{i}}" id="type_${{i}}" value="yopiq">
                        <textarea name="q_text_${{i}}" placeholder="Savol matni..." required rows="2"></textarea>
                        <div id="area_${{i}}">
                            <div class="variants-grid">
                                <input type="text" name="q_v_a_${{i}}" placeholder="A varianti" required>
                                <input type="text" name="q_v_b_${{i}}" placeholder="B varianti" required>
                                <input type="text" name="q_v_c_${{i}}" placeholder="C varianti" required>
                                <input type="text" name="q_v_d_${{i}}" placeholder="D varianti" required>
                            </div>
                            <select name="q_ans_yopiq_${{i}}" style="border: 1px solid var(--neon); color: var(--neon);">
                                <option value="a">A to'g'ri javob</option>
                                <option value="b">B to'g'ri javob</option>
                                <option value="c">C to'g'ri javob</option>
                                <option value="d">D to'g'ri javob</option>
                            </select>
                        </div>`;
                    container.appendChild(qBox);
                }}
            }}

            function setType(id, type) {{
                const area = document.getElementById('area_'+id);
                document.getElementById('type_'+id).value = type;
                document.getElementById('btn_y_'+id).classList.toggle('active', type==='yopiq');
                document.getElementById('btn_o_'+id).classList.toggle('active', type==='ochiq');

                if(type === 'yopiq') {{
                    area.innerHTML = `
                        <div class="variants-grid">
                            <input type="text" name="q_v_a_${{id}}" placeholder="A varianti" required>
                            <input type="text" name="q_v_b_${{id}}" placeholder="B varianti" required>
                            <input type="text" name="q_v_c_${{id}}" placeholder="C varianti" required>
                            <input type="text" name="q_v_d_${{id}}" placeholder="D varianti" required>
                        </div>
                        <select name="q_ans_yopiq_${{id}}">
                            <option value="a">A to'g'ri</option><option value="b">B to'g'ri</option>
                            <option value="c">C to'g'ri</option><option value="d">D to'g'ri</option>
                        </select>`;
                }} else {{
                    area.innerHTML = `<input type="text" name="q_ans_ochiq_${{id}}" placeholder="To'g'ri javobni (so'z) yozing..." required style="border-color:var(--neon);">`;
                }}
            }}

            // Dastlabki 5 ta savolni yuklash
            window.onload = () => {{
                generateQuestions(5);
                document.querySelector('.count-btn').classList.add('active');
            }};
        </script>
    </body>
    </html>
    """
    return HttpResponse(html_content)
def student_test_list(request):
    # 1. O'quvchini aniqlash
    user_login = request.session.get('user_login') or request.user.username
    student = Profile.objects.filter(login=user_login).first()

    # 2. O'quvchining sinfi va paralleliga mos testlarni olish
    if student:
        tests = TeacherTest.objects.filter(
            sinf=student.sinf,
            parallel=student.parallel.upper()
        ).order_by('-id')
    else:
        tests = []

    # 3. Testlar ro'yxati HTML qismini shakllantirish
    list_html = ""
    if tests:
        for t in tests:
            list_html += f'''
            <div style="background:rgba(255,255,255,0.07); padding:20px; border-radius:25px; margin-bottom:15px; border: 1px solid rgba(255,255,255,0.1); display:flex; justify-content:space-between; align-items:center; backdrop-filter:blur(10px); border-left: 5px solid #00f2ff; box-shadow: 0 10px 30px rgba(0,0,0,0.3);">
                <div style="flex: 1; padding-right: 15px;">
                    <div style="font-weight:bold; color:#fff; font-size:16px; letter-spacing:0.5px;">{t.title}</div>
                    <div style="color:#00f2ff; font-size:12px; margin-top:6px; display:flex; gap:12px; opacity:0.9;">
                        <span><i class="fas fa-graduation-cap"></i> {t.sinf}-{t.parallel}</span>
                        <span><i class="fas fa-book"></i> {t.subject}</span>
                    </div>
                </div>
                <a href="/solve-test/{t.id}/" style="background:#00f2ff; color:black; padding:12px 22px; border-radius:18px; text-decoration:none; font-weight:900; font-size:13px; box-shadow: 0 5px 15px rgba(0,242,255,0.4); transition:0.3s; white-space:nowrap; text-transform:uppercase;">
                    Boshlash
                </a>
            </div>'''
    else:
        list_html = '''
        <div style="text-align:center; padding:60px 20px; color:#888; background:rgba(255,255,255,0.03); border-radius:30px; border:1px dashed rgba(255,255,255,0.1); backdrop-filter:blur(10px);">
            <i class="fas fa-box-open" style="font-size:50px; margin-bottom:15px; color:#333;"></i>
            <p style="margin:0; font-size:15px;">Hozircha sizning sinfingiz uchun<br>testlar mavjud emas</p>
        </div>'''

    # 4. To'liq sahifani qaytarish
    return HttpResponse(f"""
<!DOCTYPE html>
<html lang="uz">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Testlar Markazi</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;800&display=swap" rel="stylesheet">
    <style>
        body {{ 
            margin: 0; 
            padding: 0;
            background: #000 url('/static/12.jpg') no-repeat center center fixed; 
            background-size: cover; 
            font-family: 'Poppins', sans-serif; 
            color: white; 
            min-height: 100vh;
        }}
        .overlay {{ 
            position: fixed; inset: 0; background: rgba(0,0,0,0.8); 
            backdrop-filter: blur(15px); z-index: -1; 
        }}
        .container {{ max-width: 480px; margin: 0 auto; padding: 40px 20px 120px 20px; }}

        h2 {{ 
            color: #00f2ff; text-align: center; letter-spacing: 4px; 
            text-transform: uppercase; margin-bottom: 5px; font-weight: 800;
            text-shadow: 0 0 20px rgba(0,242,255,0.5);
            font-size: 26px;
        }}

        .bottom-nav {{ 
            position: fixed; bottom: 0; left: 0; right: 0; height: 85px; 
            background: rgba(10,10,10,0.9); backdrop-filter: blur(25px); 
            border-top: 1px solid rgba(255,255,255,0.1); display: flex; 
            justify-content: space-around; align-items: center; z-index: 1000; 
            padding-bottom: env(safe-area-inset-bottom);
        }}
        .nav-item {{ text-decoration: none; color: #666; font-size: 11px; text-align: center; transition: 0.3s; }}
        .nav-item.active {{ color: #00f2ff; transform: translateY(-5px); font-weight: 600; }}
        .nav-item i {{ font-size: 26px; display: block; margin-bottom: 5px; }}
        .nav-item.active i {{ text-shadow: 0 0 15px rgba(0,242,255,0.6); }}

        a:active {{ transform: scale(0.95); }}
    </style>
</head>
<body>
    <div class="overlay"></div>

    <div class="container">
        <h2>TESTLAR</h2>
        <div style="margin-bottom:35px; font-size:12px; color:#555; text-align:center; text-transform:uppercase; letter-spacing:1px;">
            Sinf: <span style="color:#00f2ff;">{student.sinf}-{student.parallel if student else '---'}</span>
        </div>

        {list_html}
    </div>

    <nav class="bottom-nav">
        <a href="/second/" class="nav-item">
            <i class="fas fa-home"></i><span>Asosiy</span>
        </a>
        <a href="/subjects/" class="nav-item">
            <i class="fas fa-book-open"></i><span>Vazifalar</span>
        </a>
        <a href="/compete/" class="nav-item active">
            <i class="fas fa-vial"></i><span>Testlar</span>
        </a>
        <a href="/profile/" class="nav-item">
            <i class="fas fa-user"></i><span>Profil</span>
        </a>
    </nav>
</body>
</html>
    """)
def solve_test_view(request, test_id):
    test = get_object_or_404(TeacherTest, id=test_id)

    # JSON ma'lumotni o'qiymiz
    try:
        current_questions = json.loads(test.questions)
    except (json.JSONDecodeError, TypeError):
        current_questions = []

    if request.method == "POST":
        score = 0
        total = len(current_questions)

        for i, q in enumerate(current_questions, 1):
            user_ans = request.POST.get(f'q_{i}')
            if user_ans:
                if str(user_ans).strip().lower() == str(q['javob']).strip().lower():
                    score += 1

        user_login = request.session.get('user_login') or request.user.username
        student = Profile.objects.filter(login=user_login).first()

        points_won = 0
        if student:
            points_won = score * 5
            student.points += points_won
            student.save()

            TestResult.objects.create(
                student=student,
                test=test,
                score=score,
                date=timezone.now()
            )

        return HttpResponse(f"""
            <!DOCTYPE html>
            <html lang="uz">
            <head>
                <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
                <style>
                    body {{ 
                        margin:0; padding:0; height:100vh; display:flex; align-items:center; justify-content:center;
                        background: url('/static/12.jpg') no-repeat center center fixed; 
                        background-size: cover; font-family: 'Poppins', sans-serif;
                    }}
                    .overlay {{ position:fixed; inset:0; background:rgba(0,0,0,0.85); backdrop-filter:blur(20px); z-index:1; }}
                    .result-card {{ 
                        position:relative; z-index:10; background:rgba(255,255,255,0.05); 
                        padding:40px; border-radius:35px; border:1px solid rgba(0,242,255,0.3); 
                        text-align:center; max-width:400px; width:90%; color:white;
                    }}
                </style>
            </head>
            <body>
                <div class="overlay"></div>
                <div class="result-card">
                    <i class="fas fa-trophy" style="font-size:60px; color:#00f2ff; margin-bottom:20px;"></i>
                    <h1 style="margin:0; color:#00f2ff; letter-spacing:2px;">NATIJA</h1>
                    <div style="font-size:48px; font-weight:900; margin:20px 0;">{score} / {total}</div>
                    <p style="color:#aaa;">Sizga <span style="color:#00f2ff; font-weight:bold;">+{points_won} XP</span> qo'shildi!</p>
                    <a href="/compete/" style="display:block; margin-top:30px; padding:18px; background:#00f2ff; color:black; text-decoration:none; border-radius:20px; font-weight:900; text-transform:uppercase;">Markazga Qaytish</a>
                </div>
            </body>
            </html>
        """)

    token = get_token(request)
    q_cards = ""
    for i, q in enumerate(current_questions, 1):
        if q.get('turi') == 'yopiq':
            input_html = f"""
            <div style="display:grid; grid-template-columns: 1fr; gap:12px; margin-top:15px;">
                <label style="background:rgba(255,255,255,0.03); padding:15px; border-radius:15px; cursor:pointer; border:1px solid rgba(255,255,255,0.1); display:flex; align-items:center;">
                    <input type="radio" name="q_{i}" value="a" required style="margin-right:12px;"> 
                    <span>A) {q.get('v_a')}</span>
                </label>
                <label style="background:rgba(255,255,255,0.03); padding:15px; border-radius:15px; cursor:pointer; border:1px solid rgba(255,255,255,0.1); display:flex; align-items:center;">
                    <input type="radio" name="q_{i}" value="b" style="margin-right:12px;"> 
                    <span>B) {q.get('v_b')}</span>
                </label>
                <label style="background:rgba(255,255,255,0.03); padding:15px; border-radius:15px; cursor:pointer; border:1px solid rgba(255,255,255,0.1); display:flex; align-items:center;">
                    <input type="radio" name="q_{i}" value="c" style="margin-right:12px;"> 
                    <span>C) {q.get('v_c')}</span>
                </label>
                <label style="background:rgba(255,255,255,0.03); padding:15px; border-radius:15px; cursor:pointer; border:1px solid rgba(255,255,255,0.1); display:flex; align-items:center;">
                    <input type="radio" name="q_{i}" value="d" style="margin-right:12px;"> 
                    <span>D) {q.get('v_d')}</span>
                </label>
            </div>"""
        else:
            input_html = f'<input type="text" name="q_{i}" placeholder="Javobni yozing..." required style="width:100%; padding:16px; background:rgba(255,255,255,0.05); border:1px solid rgba(0,242,255,0.3); color:white; border-radius:15px; outline:none; margin-top:15px;">'

        q_cards += f"""
        <div style="background:rgba(255,255,255,0.05); padding:25px; border-radius:30px; margin-bottom:20px; border-left:6px solid #00f2ff; backdrop-filter:blur(10px);">
            <div style="color:#00f2ff; font-weight:800; font-size:11px; text-transform:uppercase;">Savol #{i}</div>
            <p style="margin:10px 0; font-size:17px; color:white;">{q['savol']}</p>
            {input_html}
        </div>"""

    return HttpResponse(f"""
    <!DOCTYPE html>
    <html lang="uz">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
        <style>
            body {{ 
                margin:0; 
                background: url('/static/12.jpg') no-repeat center center fixed; 
                background-size: cover; 
                font-family: 'Poppins', sans-serif; 
                color: white; 
            }}
            .overlay {{ position:fixed; inset:0; background:rgba(0,0,0,0.8); backdrop-filter:blur(15px); z-index:-1; }}
            .container {{ max-width:550px; margin:0 auto; padding:20px; position:relative; z-index:2; }}
            .header {{ 
                position:sticky; top:0; background:rgba(0,0,0,0.6); padding:15px; 
                text-align:center; border-bottom:1px solid rgba(255,255,255,0.1); 
                margin-bottom:20px; border-radius:0 0 20px 20px;
            }}
            .save-btn {{ 
                width:100%; padding:20px; background:#00f2ff; color:black; border:none; 
                border-radius:22px; font-weight:900; font-size:16px; cursor:pointer; 
                margin-top:20px; box-shadow: 0 10px 25px rgba(0,242,255,0.3);
            }}
        </style>
    </head>
    <body>
        <div class="overlay"></div>
        <div class="header">
            <h3 style="margin:0; color:#00f2ff;">{test.title}</h3>
        </div>
        <div class="container">
            <form method="POST">
                <input type="hidden" name="csrfmiddlewaretoken" value="{token}">
                {q_cards}
                <button type="submit" class="save-btn">TESTNI YAKUNLASH</button>
            </form>
        </div>
    </body>
    </html>
    """)
