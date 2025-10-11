from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from django.db.models import Q
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes

from .models import User, Training, TrainingModule
from .serializers import (
    UserSerializer, UserListSerializer, TrainingSerializer,
    TrainingListSerializer, TrainingModuleSerializer, RegisterSerializer
)
from .permissions import (
    IsManager, IsTrainer, IsManagerOrTrainer,
    CanAccessTraining, IsOwnerOrReadOnly
)


@extend_schema(tags=['Authentication'])
class RegisterView(generics.CreateAPIView):
    """
    Register a new user in the system.
    Only managers should create new users in production.
    """
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer


@extend_schema_view(
    list=extend_schema(
        summary="List all users",
        description="Get a list of all users. Managers see all users, Trainers see employees in their trainings, Employees see only themselves.",
        tags=['Users']
    ),
    retrieve=extend_schema(
        summary="Get user details",
        description="Retrieve detailed information about a specific user.",
        tags=['Users']
    ),
    create=extend_schema(
        summary="Create a new user",
        description="Create a new user (Manager only).",
        tags=['Users']
    ),
    update=extend_schema(
        summary="Update user",
        description="Update user information (Manager only).",
        tags=['Users']
    ),
    partial_update=extend_schema(
        summary="Partially update user",
        description="Partially update user information (Manager only).",
        tags=['Users']
    ),
    destroy=extend_schema(
        summary="Delete user",
        description="Delete a user from the system (Manager only).",
        tags=['Users']
    ),
)
class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for User management with role-based access control.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'list':
            return UserListSerializer
        return UserSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsManager()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user

        if user.role == 'manager':
            return User.objects.all()
        elif user.role == 'trainer':
            training_ids = Training.objects.filter(assigned_trainer=user).values_list('id', flat=True)
            employee_ids = Training.objects.filter(id__in=training_ids).values_list('employees', flat=True)
            return User.objects.filter(Q(id=user.id) | Q(id__in=employee_ids))
        else:
            return User.objects.filter(id=user.id)

    @extend_schema(
        summary="Get current user information",
        description="Retrieve information about the currently authenticated user.",
        responses={200: UserSerializer},
        tags=['Users']
    )
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user information"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @extend_schema(
        summary="Get users by role",
        description="Filter users by role (Manager only). Pass 'role' query parameter with values: manager, trainer, or employee.",
        parameters=[
            OpenApiParameter(
                name='role',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter by user role',
                enum=['manager', 'trainer', 'employee'],
                required=False
            )
        ],
        responses={200: UserListSerializer(many=True)},
        tags=['Users']
    )
    @action(detail=False, methods=['get'], permission_classes=[IsManager])
    def by_role(self, request):
        """Get users filtered by role (Manager only)"""
        role = request.query_params.get('role', None)
        if role:
            users = User.objects.filter(role=role)
        else:
            users = User.objects.all()
        serializer = UserListSerializer(users, many=True)
        return Response(serializer.data)


@extend_schema_view(
    list=extend_schema(
        summary="List trainings",
        description="Get a list of trainings based on user role. Managers see all, Trainers see assigned trainings, Employees see their trainings.",
        tags=['Trainings']
    ),
    retrieve=extend_schema(
        summary="Get training details",
        description="Retrieve detailed information about a specific training including modules.",
        tags=['Trainings']
    ),
    create=extend_schema(
        summary="Create training",
        description="Create a new training (Manager only).",
        tags=['Trainings']
    ),
    update=extend_schema(
        summary="Update training",
        description="Update training information (Manager or assigned Trainer).",
        tags=['Trainings']
    ),
    partial_update=extend_schema(
        summary="Partially update training",
        description="Partially update training information (Manager or assigned Trainer).",
        tags=['Trainings']
    ),
    destroy=extend_schema(
        summary="Delete training",
        description="Delete a training (Manager only).",
        tags=['Trainings']
    ),
)
class TrainingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Training management with role-based permissions.
    """
    queryset = Training.objects.all()
    serializer_class = TrainingSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'list':
            return TrainingListSerializer
        return TrainingSerializer

    def get_permissions(self):
        if self.action in ['create', 'destroy']:
            return [IsManager()]
        elif self.action in ['update', 'partial_update']:
            return [IsManagerOrTrainer()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user

        if user.role == 'manager':
            return Training.objects.all()
        elif user.role == 'trainer':
            return Training.objects.filter(assigned_trainer=user)
        else:
            return Training.objects.filter(employees=user)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @extend_schema(
        summary="Assign employees to training",
        description="Assign multiple employees to a training (Manager only).",
        request={
            'application/json': {
                'example': {
                    'employee_ids': [1, 2, 3]
                }
            }
        },
        responses={200: TrainingSerializer},
        tags=['Trainings']
    )
    @action(detail=True, methods=['post'], permission_classes=[IsManager])
    def assign_employees(self, request, pk=None):
        """Assign employees to a training (Manager only)"""
        training = self.get_object()
        employee_ids = request.data.get('employee_ids', [])

        employees = User.objects.filter(id__in=employee_ids, role='employee')
        training.employees.set(employees)

        serializer = self.get_serializer(training)
        return Response(serializer.data)

    @extend_schema(
        summary="Assign trainer to training",
        description="Assign a trainer to a training (Manager only).",
        request={
            'application/json': {
                'example': {
                    'trainer_id': 1
                }
            }
        },
        responses={200: TrainingSerializer},
        tags=['Trainings']
    )
    @action(detail=True, methods=['post'], permission_classes=[IsManager])
    def assign_trainer(self, request, pk=None):
        """Assign trainer to a training (Manager only)"""
        training = self.get_object()
        trainer_id = request.data.get('trainer_id')

        try:
            trainer = User.objects.get(id=trainer_id, role='trainer')
            training.assigned_trainer = trainer
            training.save()
            serializer = self.get_serializer(training)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response(
                {'error': 'Trainer not found'},
                status=status.HTTP_404_NOT_FOUND
            )


@extend_schema_view(
    list=extend_schema(
        summary="List training modules",
        description="Get a list of training modules based on user permissions.",
        tags=['Training Modules']
    ),
    retrieve=extend_schema(
        summary="Get module details",
        description="Retrieve detailed information about a specific training module.",
        tags=['Training Modules']
    ),
    create=extend_schema(
        summary="Create training module",
        description="Create a new training module (Manager or assigned Trainer).",
        tags=['Training Modules']
    ),
    update=extend_schema(
        summary="Update training module",
        description="Update training module information (Manager or assigned Trainer).",
        tags=['Training Modules']
    ),
    destroy=extend_schema(
        summary="Delete training module",
        description="Delete a training module (Manager or assigned Trainer).",
        tags=['Training Modules']
    ),
)
class TrainingModuleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for TrainingModule management.
    """
    queryset = TrainingModule.objects.all()
    serializer_class = TrainingModuleSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsManagerOrTrainer()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user

        if user.role == 'manager':
            return TrainingModule.objects.all()
        elif user.role == 'trainer':
            training_ids = Training.objects.filter(assigned_trainer=user).values_list('id', flat=True)
            return TrainingModule.objects.filter(training_id__in=training_ids)
        else:
            training_ids = user.trainings.values_list('id', flat=True)
            return TrainingModule.objects.filter(training_id__in=training_ids)

    def perform_create(self, serializer):
        training = serializer.validated_data.get('training')
        user = self.request.user

        if user.role == 'trainer' and training.assigned_trainer != user:
            return Response(
                {'error': 'You can only add modules to your assigned trainings'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer.save(created_by=self.request.user)

    @extend_schema(
        summary="Get modules by training",
        description="Filter modules by training ID.",
        parameters=[
            OpenApiParameter(
                name='training_id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Filter by training ID',
                required=True
            )
        ],
        responses={200: TrainingModuleSerializer(many=True)},
        tags=['Training Modules']
    )
    @action(detail=False, methods=['get'])
    def by_training(self, request):
        """Get modules filtered by training ID"""
        training_id = request.query_params.get('training_id', None)
        if training_id:
            modules = self.get_queryset().filter(training_id=training_id)
            serializer = self.get_serializer(modules, many=True)
            return Response(serializer.data)
        return Response({'error': 'training_id parameter is required'}, status=status.HTTP_400_BAD_REQUEST)
