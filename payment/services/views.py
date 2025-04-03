from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Payment, PaymentState, PaymentMethod
from .serializers import PaymentSerializer, PaymentCreateSerializer, PaymentUpdateSerializer, NameAndIdSerializer

class PaymentAPIView(APIView):
    def get(self, request, order_id):
        payment = Payment.objects.filter(order_id=order_id).first()
        if not payment:
            return Response({"detail": "Payment not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = PaymentSerializer(payment)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, order_id):
        payment = Payment.objects.filter(order_id=order_id).first()
        if not payment:
            return Response({"detail": "Payment not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = PaymentUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        if 'payment_state' in serializer.validated_data:
            payment_state = PaymentState.objects.filter(id=serializer.validated_data['payment_state']).first()
            if not payment_state:
                return Response({"detail": "Payment state not found"}, status=status.HTTP_404_NOT_FOUND)
            payment.payment_state = payment_state

        if 'payment_method' in serializer.validated_data:
            payment_method = PaymentMethod.objects.filter(id=serializer.validated_data['payment_method']).first()
            if not payment_method:
                return Response({"detail": "Payment method not found"}, status=status.HTTP_404_NOT_FOUND)
            payment.payment_method = payment_method

        payment.save()
        return Response(PaymentSerializer(payment).data, status=status.HTTP_202_ACCEPTED)

class PaymentCreateAPIView(APIView):
    def post(self, request):
        print(request.data) 
        serializer = PaymentCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        order_id = serializer.data['order_id']
        if Payment.objects.filter(order_id=order_id).exists():
            return Response({"detail": "Payment for this order already exists"}, status=status.HTTP_400_BAD_REQUEST)

        payment_method = PaymentMethod.objects.filter(id=serializer.data['payment_method']).first()
        if not payment_method:
            return Response({"detail": "Payment method not found"}, status=status.HTTP_404_NOT_FOUND)

        payment_state = None
        if serializer.validated_data.get('payment_state'):
            payment_state = PaymentState.objects.filter(id=serializer.data['payment_state']).first()
            if not payment_state:
                return Response({"detail": "Payment state not found"}, status=status.HTTP_404_NOT_FOUND)

        payment = Payment.objects.create(
            order_id=order_id,
            payment_method=payment_method,
            payment_state=payment_state
        )
        return Response(PaymentSerializer(payment).data, status=status.HTTP_200_OK)

class PaymentStateListAPIView(APIView):
    def get(self, request):
        print(request.query_params)
        name = request.query_params.get('name')
        if name:
            states = PaymentState.objects.filter(name__iexact=name)
        else:
            states = PaymentState.objects.all()
        serializer = NameAndIdSerializer(states, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class PaymentMethodListAPIView(APIView):
    def get(self, request):
        methods = PaymentMethod.objects.all()
        serializer = NameAndIdSerializer(methods, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class PaymentMethodDetailAPIView(APIView):
    def get(self, request, id):
        method = PaymentMethod.objects.filter(id=id).first()
        if not method:
            return Response({"detail": "Payment method not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = NameAndIdSerializer(method)
        return Response(serializer.data, status=status.HTTP_200_OK)
