from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Comment
from .serializers import CommentSerializer, CommentCreateSerializer
import logging

logger = logging.getLogger(__name__)

class CommentListView(APIView):
    def get(self, request):
        product_id = request.query_params.get('product_id')
        page = int(request.query_params.get('page', 1))
        per_page = int(request.query_params.get('per_page', 10))

        if product_id:
            comments = Comment.filter(order_item_id=int(product_id))
        else:
            comments = Comment.all()

        total_comments = len(comments)
        total_pages = (total_comments + per_page - 1) // per_page
        start = (page - 1) * per_page
        end = start + per_page
        paginated_comments = comments[start:end]

        auth_token = request.headers.get('Authorization')
        content = []
        for comment in paginated_comments:
            user_data = self.get_user_info(auth_token, comment.user_id)
            comment_data = {
                'id': comment.id,
                'content': comment.content,
                'created_at': comment.created_at,
                'user': user_data
            }
            serializer = CommentSerializer(comment_data)
            content.append(serializer.data)

        response_data = {
            'page': page,
            'per_page': per_page,
            'total_page': total_pages,
            'comments': content
        }
        return Response(response_data, status=status.HTTP_200_OK)

    def get_user_info(self, auth_token, user_id):
        user_service_url = os.getenv('USER_SERVICE_URL', 'http://user-service:8000')
        try:
            response = requests.get(f"{user_service_url}/api/user/get-user-info",
                                  headers={'Authorization': auth_token},
                                  params={'user_id': user_id})
            return response.json() if response.status_code == 200 else {'id': user_id, 'username': 'unknown'}
        except Exception as e:
            logger.error(f"Error fetching user info: {e}")
            return {'id': user_id, 'username': 'unknown'}

class CommentCreateView(APIView):
    def post(self, request):
        order_id = request.query_params.get('order_id')
        if not order_id:
            return Response({"detail": "order_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = CommentCreateSerializer(data=request.data)
        if serializer.is_valid():
            auth_token = request.headers.get('Authorization')
            user_data = self.get_user_info(auth_token)
            if not user_data or 'id' not in user_data:
                return Response({"detail": "Invalid user"}, status=status.HTTP_401_UNAUTHORIZED)

            comment = Comment.create(
                user_id=user_data['id'],
                order_item_id=int(order_id),
                content=serializer.validated_data['content']
            )
            return Response({"id": comment.id}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_user_info(self, auth_token):
        user_service_url = os.getenv('USER_SERVICE_URL', 'http://user-service:8000')
        try:
            response = requests.get(f"{user_service_url}/api/user/get-user-info",
                                  headers={'Authorization': auth_token})
            return response.json() if response.status_code == 200 else None
        except Exception as e:
            logger.error(f"Error fetching user info: {e}")
            return None

class CommentDetailView(APIView):
    def put(self, request, comment_id):
        comment = Comment.get(comment_id)
        if not comment:
            return Response({"detail": "Comment not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = CommentCreateSerializer(data=request.data)
        if serializer.is_valid():
            comment.content = serializer.validated_data['content']
            comment.save()
            return Response(status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, comment_id):
        comment = Comment.get(comment_id)
        if not comment:
            return Response({"detail": "Comment not found"}, status=status.HTTP_404_NOT_FOUND)
        comment.delete()
        return Response(status=status.HTTP_200_OK)
