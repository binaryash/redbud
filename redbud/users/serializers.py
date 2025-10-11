#!/usr/bin/env python3

from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User, Training, TrainingModule
from typing import Optional


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model
    """
    password = serializers.CharField(write_only=True, required=False, validators=[validate_password])

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'first_name', 'last_name', 'role',
                  'phone_number', 'is_active', 'date_joined', 'password']
        read_only_fields = ['id', 'date_joined']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User.objects.create(**validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class UserListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for listing users
    """
    role_display = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'first_name', 'last_name', 'role', 'role_display']


class TrainingModuleSerializer(serializers.ModelSerializer):
    """
    Serializer for TrainingModule model
    """
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)

    class Meta:
        model = TrainingModule
        fields = ['id', 'training', 'title', 'description', 'order',
                  'duration_hours', 'created_by', 'created_by_name', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']


class TrainingSerializer(serializers.ModelSerializer):
    """
    Serializer for Training model
    """
    modules = TrainingModuleSerializer(many=True, read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    assigned_trainer_name = serializers.CharField(source='assigned_trainer.get_full_name', read_only=True)
    employee_count = serializers.SerializerMethodField()

    class Meta:
        model = Training
        fields = ['id', 'name', 'description', 'start_date', 'end_date', 'duration_days',
                  'created_by', 'created_by_name', 'assigned_trainer', 'assigned_trainer_name',
                  'employees', 'employee_count', 'is_active', 'created_at', 'updated_at', 'modules']
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']

    def get_employee_count(self, obj)-> int:
        return obj.employees.count()


class TrainingListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for listing trainings
    """
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    assigned_trainer_name = serializers.CharField(source='assigned_trainer.get_full_name', read_only=True)
    module_count = serializers.SerializerMethodField()

    class Meta:
        model = Training
        fields = ['id', 'name', 'start_date', 'end_date', 'duration_days',
                  'created_by_name', 'assigned_trainer_name', 'module_count', 'is_active']

    def get_module_count(self, obj)-> int:
        return obj.modules.count()


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration
    """
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'password2', 'first_name', 'last_name', 'role', 'phone_number']

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user
