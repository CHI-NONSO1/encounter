import os
from django.db import models
from django.utils import timezone


class JissUser(models.Model):
    firstname = models.CharField(max_length=50)
    lastname = models.CharField(max_length=50)
    password = models.CharField(max_length=500)
    followings = models.ManyToManyField(
        'self', symmetrical=False, blank=True, related_name='followers')
    refresh_token = models.CharField(
        max_length=200, default=None, blank=True, null=True)
    verify_token = models.CharField(
        max_length=350, default=None, blank=True, null=True)
    reset_token = models.CharField(
        max_length=350, default=None, blank=True, null=True)
    email = models.EmailField(max_length=50)
    image = models.ImageField(
        upload_to='images/', default=None, blank=True, null=True)
    phoneno = models.CharField(max_length=15)
    city = models.CharField(
        max_length=200, default=None, blank=True, null=True)
    address = models.CharField(
        max_length=255, default=None, blank=True, null=True)
    rating = models.IntegerField(default=0, blank=True, null=True)
    rate = models.IntegerField(default=0, blank=True, null=True)
    jissCoin = models.IntegerField(default=1, blank=True, null=True)
    isActive = models.BooleanField(default=False)
    isAdmin = models.BooleanField(default=False)
    profession = models.CharField(
        max_length=255, default=None, blank=True, null=True)
    reserved_account = models.DecimalField(
        max_digits=10, decimal_places=2, default=0)
    working_account = models.DecimalField(
        max_digits=10, decimal_places=2, default=0)
    target_investment = models.DecimalField(
        max_digits=10, decimal_places=2, default=0)
    last_payment_date = models.DateTimeField(null=True, blank=True)
    next_payment_date = models.DateTimeField(null=True, blank=True)
    investing = models.BooleanField(default=False)

    createdAt = models.DateTimeField(auto_now=True)
    updatedAt = models.DateTimeField(default=None, null=True)
    duration = models.IntegerField(default=22, null=True)

    def __str__(self):
        return self.refresh_token
    # Add other fields as needed


class Interest(models.Model):
    borrower = models.ForeignKey(
        JissUser, related_name='interest', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)


class Investment(models.Model):
    investor = models.ForeignKey(
        JissUser, related_name='lender', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    borrower = models.ForeignKey(
        JissUser, related_name='borrowed_from', on_delete=models.CASCADE)
    is_shared = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


class Follower_Request(models.Model):
    requester_id = models.IntegerField(default=0)
    requesting_id = models.IntegerField(default=0)
    parent_id = models.IntegerField(default=0, blank=True, null=True)
    createdAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'followers {self.following_id, self.follower_id}'


class Notification(models.Model):
    sender = models.ForeignKey(JissUser, on_delete=models.CASCADE)
    recipient = models.ForeignKey(
        JissUser, on_delete=models.CASCADE, related_name='notifications')
    createdAt = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.recipient}'


class EncaGroups(models.Model):
    members = models.ManyToManyField(JissUser, related_name='groups')
    group_name = models.CharField(max_length=100)
    group_image = models.FileField(
        upload_to='group/', default=None, blank=True, null=True)
    is_admin = models.BooleanField(default=False)
    is_banned = models.BooleanField(default=False)
    description = models.TextField()

    memberid = models.IntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.members,self.group_name,self.description}'


class EncaPost(models.Model):
    user = models.ForeignKey(JissUser, on_delete=models.CASCADE)
    is_sponsored = models.BooleanField(default=False)
    image = models.FileField(
        upload_to='post-images/', default=None, blank=True, null=True)
    video = models.FileField(
        upload_to='post-videos/', default=None, blank=True, null=True)
    content = models.TextField()
    groups = models.ManyToManyField(
        EncaGroups, default=None, blank=True, related_name='posts')
    updatedAt = models.DateTimeField(default=None, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=100, default=None, null=True)
    active = models.BooleanField(default=True)
    like = models.ManyToManyField(
        JissUser, default=0, related_name='likes', blank=True)
    share = models.ManyToManyField(
        JissUser, default=0, related_name='sharedby', blank=True)
    hashtags = models.ManyToManyField(
        'Hashtag', related_name='posts', default=None)

    def total_likes(self):
        return self.like.count()

    def total_shared(self):
        return self.share.count()

    def delete(self, *args, **kwargs):

        if self.image:
            os.remove(self.image.path)
        if self.video:
            os.remove(self.video.path)
        super(EncaPost, self).delete(*args, **kwargs)

    def __str__(self):
        return f'{self.user.firstname,self.user.lastname,self.user.image,self.title,self.content,self.video,self.total_likes(),self.total_shared()}'


class Hashtag(models.Model):
    name = models.CharField(max_length=100, unique=True)


class SharedPost(models.Model):
    post = models.ForeignKey(EncaPost, on_delete=models.CASCADE)
    name = models.ForeignKey(JissUser, on_delete=models.CASCADE)
    shared_with = models.ManyToManyField(JissUser, related_name='who')
    timestamp = models.DateTimeField(auto_now_add=True)
    message = models.TextField(blank=True)
    image = models.FileField(
        upload_to='sharedpost-images/', default=None, blank=True, null=True)
    video = models.FileField(
        upload_to='sharedpost-videos/', default=None, blank=True, null=True)
    
    content = models.TextField( blank=True, null=True)
    groups = models.ManyToManyField(
        EncaGroups, default=None, blank=True, related_name='sharedposts')
    likes = models.ManyToManyField(
        JissUser, default=0, related_name='sharedpost_likes', blank=True)
    share = models.ManyToManyField(
        JissUser, default=0, related_name='shared_post_by', blank=True)
    hashtags = models.ManyToManyField(
        'Hashtag', related_name='shareposts', default=None)

    def total_likes(self):
        return self.likes.count()

    def total_shared(self):
        return self.share.count()

    def delete(self, *args, **kwargs):
        if self.image:
            os.remove(self.image.path)
        if self.video:
            os.remove(self.video.path)
        super(SharedPost, self).delete(*args, **kwargs)


class EncaPostNotification(models.Model):
    user = models.ForeignKey(JissUser, on_delete=models.CASCADE)
    post = models.ForeignKey(EncaPost, on_delete=models.CASCADE)
    createdAt = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user}'


class Comment(models.Model):
    firstname = models.CharField(max_length=50, default=None, blank=True)
    lastname = models.CharField(max_length=50, default=None, blank=True)
    user_image = models.CharField(max_length=50, default=None, blank=True)
    post = models.ForeignKey(
        EncaPost, on_delete=models.CASCADE, related_name='comments', default=None, blank=True, null=True)
    shared_post = models.ForeignKey(
        SharedPost, on_delete=models.CASCADE, related_name='comment', default=None, blank=True, null=True)
    user = models.ForeignKey(JissUser, on_delete=models.CASCADE)
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, default=None,  null=True, blank=True, related_name='replies')
    content = models.TextField()
    likes = models.ManyToManyField(
        JissUser, default=0, related_name='like', blank=True)
    share = models.ManyToManyField(
        JissUser, default=0, related_name='shared', blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    image = models.FileField(upload_to='comments/',
                             default=None, blank=True, null=True)
    active = models.BooleanField(default=True)
    updatedAt = models.DateTimeField(default=None, null=True)

    def total_likes(self):
        return self.likes.count()

    def total_shared(self):
        return self.share.count()

    def __str__(self):
        return f'Comment by {self.user.firstname,self.user.lastname} on {self.content,self.parent,self.total_likes(),self.total_shared(),self.image}'


class SharedPostComment(models.Model):
    firstname = models.CharField(max_length=50, default=None, blank=True)
    lastname = models.CharField(max_length=50, default=None, blank=True)
    user_image = models.CharField(max_length=50, default=None, blank=True)
    shared_post = models.ForeignKey(
        SharedPost, on_delete=models.CASCADE, related_name='shared_post_comments', default=None, blank=True, null=True)
    user = models.ForeignKey(JissUser, on_delete=models.CASCADE)
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, default=None,  null=True, blank=True, related_name='shared_post_replies')
    content = models.TextField()
    like = models.ManyToManyField(
        JissUser, default=0, related_name='shared_post_likes', blank=True)
    shared = models.ManyToManyField(
        JissUser, default=0, related_name='share_post', blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    image = models.FileField(upload_to='comments/',
                             default=None, blank=True, null=True)
    active = models.BooleanField(default=True)
    updatedAt = models.DateTimeField(default=None, null=True)

    def total_likes(self):
        return self.like.count()

    def total_shared(self):
        return self.shared.count()

    def __str__(self):
        return f'Comment by {self.user.firstname,self.user.lastname} on {self.content,self.parent,self.total_likes(),self.total_shared(),self.image}'


class EncaGroupRooms(models.Model):
    members = models.ManyToManyField(JissUser, related_name='rooms')
    group = models.ForeignKey(
        EncaGroups, on_delete=models.CASCADE, default=1, related_name='chat_room')
    room_name = models.CharField(max_length=100)
    room_image = models.FileField(
        upload_to='rooms/', default=None, blank=True, null=True)
    groupid = models.IntegerField(default=1)
    is_admin = models.BooleanField(default=False)
    is_banned = models.BooleanField(default=False)
    description = models.TextField()
    memberid = models.IntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.members,self.group_name,self.description}'


class Message(models.Model):
    sender = models.ForeignKey(JissUser, on_delete=models.CASCADE)
    receiver = models.ForeignKey(
        JissUser, on_delete=models.CASCADE, related_name='receivers')
    content = models.TextField()
    connections = models.IntegerField()
    active = models.BooleanField(default=True)
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.firstname, self.sender.lastname}: {self.id,self.content}"


class MessageNotification(models.Model):
    sender = models.ForeignKey(JissUser, on_delete=models.CASCADE)
    recipient = models.ForeignKey(
        JissUser, on_delete=models.CASCADE, related_name='notify')
    
    message = models.ForeignKey(
        Message, on_delete=models.CASCADE)
    createdAt = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.sender,self.recipient}'


class Invitation(models.Model):
    group = models.ForeignKey(
        EncaGroups, on_delete=models.CASCADE, related_name='invitations')
    inviter = models.ForeignKey(
        JissUser, on_delete=models.CASCADE, related_name='sent_invitations')
    invitee = models.ForeignKey(
        JissUser, on_delete=models.CASCADE, related_name='received_invitations')
    accepted = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.invitee, self.inviter}'


class EncaGroupChat(models.Model):
    sender = models.ForeignKey(JissUser, on_delete=models.CASCADE)
    group = models.ForeignKey(EncaGroups, on_delete=models.CASCADE)
    room_name = models.TextField(default='lubby')
    content = models.TextField()
    groupid = models.IntegerField()
    chat_image = models.FileField(
        upload_to='group-chat-image/', default=None, blank=True, null=True)
    chat_video = models.FileField(
        upload_to='group-chat-videos/', default=None, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.sender,self.group,self.content,self.timestamp}'


class EncaGroupChatNotification(models.Model):
    sender = models.ForeignKey(JissUser, on_delete=models.CASCADE)
    group = models.ForeignKey(EncaGroups, on_delete=models.CASCADE)
    message = models.ForeignKey(EncaGroupChat, on_delete=models.CASCADE)
    groupid = models.IntegerField()
    room_name = models.TextField(default='lubby')
    createdAt = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.sender}'


class EncaGroupPostNotification(models.Model):
    user = models.ForeignKey(JissUser, on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    createdAt = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user}'
