import os

from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render

# Create your views here.
from django.views.generic.base import View

from core.forms import ChannelForm, CommentForm
from core.models import Video, Channel, Comment


class ChannelView(View):
    template_name = "channel_view.html"

    def get(self, request, user):
        if request.user.is_authenticated:
            videos = Video.objects.filter(user__username=user).order_by("-datetime")
            channel = Channel.objects.filter(user__username=user).get()
            context = {'videos': videos,
                       'channel': channel}
        return render(request, self.template_name, context)


class CreateChannelView(View):
    template_name = "channel_create.html"

    def get(self, request):
        if request.user.is_authenticated:
            try:
                if Channel.objects.filter(user__username=request.user).get().channel_name != "":
                    return HttpResponseRedirect('/')
            except Channel.DoesNotExist:
                form = ChannelForm()
                channel = False
                return render(request, self.template_name, {'form': form, 'channel': channel})

    def post(self, request):
        # pass filled out HTML-Form from View to RegisterForm()
        form = ChannelForm(request.POST)
        if form.is_valid():
            # create a User account
            print(form.cleaned_data['channel_name'])
            channel_name = form.cleaned_data['channel_name']
            user = request.user
            subscribers = 0
            new_channel = Channel(channel_name=channel_name, user=user, subscribers=subscribers)
            new_channel.save()
            return HttpResponseRedirect('/')
        return HttpResponse('This is Register view. POST Request.')


class HomeView(View):
    template_name = 'index.html'

    def get(self, request):
        most_recent_videos = Video.objects.order_by('-datetime')[:8]
        most_recent_channels = Channel.objects.filter()

        channel = False
        print(request.user.username)
        if request.user.username != "":
            # print("YEs")
            try:
                channel = Channel.objects.filter(user__username=request.user)
                print(channel)
                channel = channel.get()
            except Channel.DoesNotExist:
                channel = False
            # if channel:
        # print(request.user)
        return render(request, self.template_name,
                      {'menu_active_item': 'home', 'most_recent_videos': most_recent_videos,
                       'most_recent_channels': most_recent_channels, 'channel': channel})


class VideoView(View):
    template_name = 'video.html'

    def get(self, request, id):
        # fetch video from DB by ID
        video_by_id = Video.objects.get(id=id)
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        video_by_id.path = 'http://localhost:5000/get_video/' + video_by_id.path
        print(video_by_id)
        print(video_by_id.path)

        context = {'video': video_by_id}

        if request.user.is_authenticated:
            print('user signed in')
            comment_form = CommentForm()
            context['form'] = comment_form

        comments = Comment.objects.filter(video__id=id).order_by('-datetime')[:5]
        print(comments)
        context['comments'] = comments

        try:
            channel = Channel.objects.filter(user__username=request.user).get().channel_name != ""
            print(channel)
            context['channel'] = channel
        except Channel.DoesNotExist:
            channel = False

        return render(request, self.template_name, context)


class CommentView(View):
    template_name = 'comment.html'

    def post(self, request):
        # pass filled out HTML-Form from View to CommentForm()
        form = CommentForm(request.POST)
        if form.is_valid():
            # create a Comment DB Entry
            text = form.cleaned_data['text']
            video_id = request.POST['video']
            video = Video.objects.get(id=video_id)

            new_comment = Comment(text=text, user=request.user, video=video)
            new_comment.save()
            return HttpResponseRedirect('/video/{}'.format(str(video_id)))
        return HttpResponse('This is Register view. POST Request.')