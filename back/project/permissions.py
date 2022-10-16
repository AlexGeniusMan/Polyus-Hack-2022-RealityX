from rest_framework import permissions


class CustomIsAuthenticated(permissions.IsAuthenticated):
    message = {'message': 'You are not authenticated.'}
