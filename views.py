from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from events.models import Team, Event
from .serealizers import TeamSerializer, CreateTeamSerializer
from users.serializers import CreateUserSerializer
from users.models import CustomUser as User
from wabot.wabot import WABot
from django.core.exceptions import ObjectDoesNotExist


class CreateTeamView(generics.CreateAPIView):
    """
    Create Team, capitan first user and view chat.
    """
    serializer_class = CreateTeamSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        request.data['captain'] = request.user.id
        request.data['players'] = [request.user.id]
        request.data['city'] = 1
        return self.create(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        phone = str(self.request.user.phone)[1:]
        bot = WABot()
        serializer = self.get_serializer(data=request.data)
        headers = self.get_success_headers(serializer.initial_data)
        if serializer.is_valid():
            response = bot.add_group_and_promote(phone=phone, chatName=f"Шейкер - {request.data.get('title')}")
            print(response)
            if response.get('groupId'):
                team = serializer.save()
                team.WA_chatId = response['groupId']
                team.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

        return Response(data={'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST, headers=headers)


class UpdateTeamAndCreateUser(generics.CreateAPIView):
    """
    Create player from chat
    """
    def create(self, request, *args, **kwargs):
        errors = []
        chatId = request.data.get('groupId')
        new_user_phone = '+' + request.data.get('phone')
        if new_user_phone and chatId:
            try:
                new_user = User.objects.get(phone=new_user_phone)
                serializer = CreateUserSerializer(instance=new_user)
                serializer.data['user_exists'] = True
            except ObjectDoesNotExist:
                data = {
                    'phone': new_user_phone,
                    'password': new_user_phone[-4:],
                }
                serializer = CreateUserSerializer(data=data)
                serializer.is_valid(raise_exception=True)
                new_user = serializer.save()
                serializer.data['user_exists'] = False

            try:
                team = Team.objects.get(WA_chatId=chatId)
            except Team.DoesNotExist:
                errors.append({'chatId': 'нет команды с таким chatId'})
                return Response(data={'errors': errors}, status=status.HTTP_400_BAD_REQUEST)

            team.players.add(new_user)
            team.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if not new_user_phone:
            errors.append({'phone': 'не указан телефон'})
        if not chatId:
            errors.append({'chatId': 'не указа chatId'})
        return Response(data={'errors': errors}, status=status.HTTP_400_BAD_REQUEST)
