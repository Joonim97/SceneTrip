from rest_framework import serializers
from .models import Comment, CommentLike, Journal, JournalImage, JournalLike


class RecursiveSerializer(serializers.Serializer):
    def to_representation(self, value):
        serializer = self.parent.__class__(value, context=self.context)
        return serializer.data


class CommentSerializer(serializers.ModelSerializer):
    like_count = serializers.SerializerMethodField()
    dislike_count = serializers.SerializerMethodField()
    replies = RecursiveSerializer(many=True, read_only=True)

    class Meta:
        model = Comment
        fields = [
            "id",
            "journal",
            "user",
            "content",
            "parent",
            "created_at",
            "like_count",
            "dislike_count",
            "replies",
        ]
        read_only_fields = [
            "journal",
            "user",
            "created_at",
            "like_count",
            "dislike_count",
            "replies",
        ]

    def get_like_count(self, comment):
        return CommentLike.objects.filter(comment=comment, like_type="like").count()

    def get_dislike_count(self, comment):
        return CommentLike.objects.filter(comment=comment, like_type="dislike").count()

    def create(self, validated_data):
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            validated_data["user"] = request.user
        return super().create(validated_data)


class CommentLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentLike
        fields = ["id", "user", "comment", "like_type"]
        read_only_fields = ["user"]

    def create(self, validated_data):
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            validated_data["user"] = request.user
        return super().create(validated_data)


class JournalImageSerializer(serializers.ModelSerializer):  # 저널이미지 시리얼라이저
    class Meta:
        model = JournalImage
        fields = ["id", "journal_image"]  # 이미지 필드만 포함


class JournalLikeSerializer(serializers.ModelSerializer):  # 저널좋아요시리얼라이저
    class Meta:
        model = JournalLike
        fields = ["journalLikeKey", "user", "liked_at"]  # 필요한 필드만 포함


class JournalSerializer(serializers.ModelSerializer):
    likes_count = serializers.SerializerMethodField()  # 좋아요 수
    author_nickname = serializers.ReadOnlyField(source="author.nickname")
    journal_images = JournalImageSerializer(
        many=True, read_only=True
    )  # 다중 이미지 시리얼라이저

    journal_likes = JournalLikeSerializer(many=True, read_only=True)

    class Meta:
        model = Journal
        fields = [
            "id",
            "journalKey",
            "title",
            "journal_images",
            "content",
            "created_at",
            "likes_count",
            "hit_count",
            "author_nickname",
            "journal_likes",
        ]
        read_only_fields = [
            "id",
            "author_nickname",
            "created_at",
            "updated_at",
            "likes",
            "likes_count",
            "hit_count",
            "journal_likes",
        ]

    def get_likes_count(self, journal_id):
        return journal_id.journal_likes.count()


class JournalDetailSerializer(JournalSerializer):  # 저널디테일
    comments = CommentSerializer(many=True, read_only=True, source="journal_comments")
    comments_count = serializers.SerializerMethodField()  # 댓글 수

    class Meta(JournalSerializer.Meta):
        fields = JournalSerializer.Meta.fields + [
            "updated_at",
            "comments_count",
            "comments",
        ]
        read_only_fields = (
            "id",
            "author",
            "created_at",
            "updated_at",
            "likes",
            "likes_count",
            "comments_count",
            "comments",
            "journal_likes",
            "hit_count"
        )

    def get_comments_count(self, journal_id):
        return journal_id.journal_comments.count()
