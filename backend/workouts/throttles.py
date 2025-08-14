from rest_framework.throttling import UserRateThrottle

class ExerciseInfoThrottle(UserRateThrottle):
    rate = '4/day' 