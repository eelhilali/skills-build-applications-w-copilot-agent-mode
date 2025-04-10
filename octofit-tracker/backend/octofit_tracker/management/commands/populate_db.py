import json
from datetime import timedelta
from django.core.management.base import BaseCommand
from octofit_tracker.models import User, Team, Activity, Leaderboard, Workout
from bson import ObjectId

class Command(BaseCommand):
    help = 'Populate the database with test data'

    def handle(self, *args, **kwargs):
        with open('octofit-tracker/backend/octofit_tracker/test_data.json') as f:
            data = json.load(f)

        # Populate users
        for user_data in data['users']:
            User.objects.get_or_create(**user_data)

        # Populate teams
        for team_data in data['teams']:
            members = team_data.pop('members')
            team, _ = Team.objects.get_or_create(**team_data)
            team.members.clear()
            for member in members:
                user = User.objects.get(username=member)
                team.members.add(user)

        # Convert duration string to timedelta
        for activity_data in data['activities']:
            user = User.objects.get(username=activity_data.pop('user'))
            duration_str = activity_data.pop('duration')
            hours, minutes, seconds = map(int, duration_str.split(':'))
            activity_data['duration'] = timedelta(hours=hours, minutes=minutes, seconds=seconds)
            Activity.objects.get_or_create(user=user, **activity_data)

        # Populate leaderboard
        for leaderboard_data in data['leaderboard']:
            user = User.objects.get(username=leaderboard_data.pop('user'))
            Leaderboard.objects.get_or_create(user=user, **leaderboard_data)

        # Populate workouts
        for workout_data in data['workouts']:
            Workout.objects.get_or_create(**workout_data)

        # Additional test data for users
        additional_users = [
            User(_id=ObjectId(), username='ironman', email='ironman@mhigh.edu', password='ironmanpassword'),
            User(_id=ObjectId(), username='blackwidow', email='blackwidow@mhigh.edu', password='blackwidowpassword')
        ]
        User.objects.bulk_create(additional_users)

        # Additional test data for teams
        additional_team = Team(_id=ObjectId(), name='Red Team')
        additional_team.save()
        additional_team.members.add(*additional_users)

        # Additional test data for activities
        additional_activities = [
            Activity(_id=ObjectId(), user=additional_users[0], activity_type='Yoga', duration=timedelta(minutes=45)),
            Activity(_id=ObjectId(), user=additional_users[1], activity_type='Pilates', duration=timedelta(minutes=30))
        ]
        Activity.objects.bulk_create(additional_activities)

        # Additional test data for leaderboard
        additional_leaderboard_entries = [
            Leaderboard(_id=ObjectId(), user=additional_users[0], score=110),
            Leaderboard(_id=ObjectId(), user=additional_users[1], score=120)
        ]
        Leaderboard.objects.bulk_create(additional_leaderboard_entries)

        # Additional test data for workouts
        additional_workouts = [
            Workout(_id=ObjectId(), name='Yoga Session', description='A calming yoga session for flexibility and relaxation'),
            Workout(_id=ObjectId(), name='Pilates Class', description='A core-strengthening pilates class')
        ]
        Workout.objects.bulk_create(additional_workouts)

        self.stdout.write(self.style.SUCCESS('Successfully populated the database with test data'))
