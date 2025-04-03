from rest_framework import serializers

class UserSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField(max_length=50)

class CommentSerializer(serializers.Serializer):
    id = serializers.CharField()
    user = UserSerializer()
    content = serializers.CharField()
    created_at = serializers.DateTimeField()

class CommentCreateSerializer(serializers.Serializer):
    content = serializers.CharField(required=True)