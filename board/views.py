from django.shortcuts import render, get_object_or_404, redirect
import hashlib
import re
import datetime
from .models import Thread, Post
from .forms import ThreadForm, PostForm

# スレ一覧を表示
def thread_list(request):
    if request.method == 'POST':
        form = ThreadForm(request.POST)
        if form.is_valid():
            thread = form.save()
            ip_address = request.META.get('REMOTE_ADDR')
            current_date = datetime.datetime.now().strftime('%Y-%m-%d')
            # 日をまたいだら変わるIDを生成
            unique_string = f"{ip_address}_{current_date}"
            thread.user_id = hashlib.sha256(unique_string.encode()).hexdigest()[:8]
            return redirect('thread_detail', pk=thread.pk)
    else:
        form = ThreadForm()
    
    threads = Thread.objects.all()
    thread_data = []

    # 表示用スレッドデータを作成
    for thread in threads:
        if thread.post_set.count() <= 1000:
            thread_data.append({
                'thread': thread,
                'post_count': thread.post_set.count(),
                'user_id': thread.user_id
            })
    return render(request, 'board/thread_list.html', {'form': form, 'thread_data': thread_data})

def thread_detail(request, pk):
    thread = get_object_or_404(Thread, pk=pk)

    # POSTメソッドの場合は新規投稿を受け付ける
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            # 対象スレッド
            post.thread = thread
            ip_address = request.META.get('REMOTE_ADDR')
            current_date = datetime.datetime.now().strftime('%Y-%m-%d')
            # 投稿者のIPアドレス
            post.ip_address = request.META.get('REMOTE_ADDR')
            # 投稿者のUser-Agent
            post.user_agent = request.META.get('HTTP_USER_AGENT')

            # 日をまたいだら変わるIDを生成
            unique_string = f"{ip_address}_{current_date}"
            post.user_id = hashlib.sha256(unique_string.encode()).hexdigest()[:8]
            post.save()
            return redirect('thread_detail', pk=pk)
    else:
        form = PostForm()

    # スレ書き込み数が1000県を超えたらものは表面上削除
    if thread.post_set.count() > 1000:
        return redirect('thread_list')
    posts = thread.post_set.all() 

    post_data = []

    for i, post in enumerate(posts):
        # URLをリンクに変換
        post.content = re.sub(r'(https?://[a-zA-Z0-9.-]*)', r'<a href="\1">\1</a>', post.content)
        # >>1のようなレス番号をリンクに変換
        post.content = re.sub(r'>>(\d+)', r'<a href="#post-\1">>>\1</a>', post.content)
        # 投稿に付番したい
        post_data.append({
            'post': post,
            'post_number': i + 1,
            'user_id': post.user_id,
            'created_at': post.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'content' : post.content
        })

    return render(request, 'board/thread_detail.html', {'form': form, 'thread': thread, 'post_data': post_data})
