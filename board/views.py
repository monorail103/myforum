from django.shortcuts import render, get_object_or_404, redirect
import hashlib
from .models import Thread, Post
from .forms import ThreadForm, PostForm

# スレ一覧を表示
def thread_list(request):
    if request.method == 'POST':
        form = ThreadForm(request.POST)
        if form.is_valid():
            thread = form.save()
            ip_address = request.META.get('REMOTE_ADDR')
            current_date = thread.created_at.strftime('%Y-%m-%d %H:%M:%S')
            # 日をまたいだら変わるIDを生成
            thread.user_id = f"{ip_address}_{current_date}"
            return redirect('thread_detail', pk=thread.pk)
    else:
        form = ThreadForm()
    
    threads = Thread.objects.all()
    thread_data = []
    for thread in threads:
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
            post.thread = thread
            ip_address = request.META.get('REMOTE_ADDR')
            current_date = post.created_at.strftime('%Y-%m-%d %H:%M:%S')
            post.ip_address = request.META.get('REMOTE_ADDR')
            post.user_agent = request.META.get('HTTP_USER_AGENT')

            # 日をまたいだら変わるIDを生成
            unique_string = f"{ip_address}_{current_date}"
            post.user_id = hashlib.sha256(unique_string.encode()).hexdigest()
            post.save()
            return redirect('thread_detail', pk=pk)
    else:
        form = PostForm()

    # スレ書き込み数が1000県を超えたらものは表面上削除
    if thread.post_set.count() > 1000:
        return redirect('thread_list')
    posts = thread.post_set.all() 
    return render(request, 'board/thread_detail.html', {'form': form, 'thread': thread, 'posts': posts})
