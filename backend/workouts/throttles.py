from rest_framework.throttling import UserRateThrottle

class ExerciseInfoThrottle(UserRateThrottle):
    rate = '8/day' 