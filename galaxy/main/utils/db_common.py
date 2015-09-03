# (c) 2012-2014, Ansible, Inc. <support@ansible.com>
#
# This file is part of Ansible Galaxy
#
# Ansible Galaxy is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible Galaxy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.

# from django.conf import settings
# from django.core.cache import cache
# from django.db import transaction
# from django.db.models import Avg, Count
# from django.contrib.auth import get_user_model

# from galaxy.main.models import Role, RoleRating

# User = get_user_model()

# @transaction.atomic
# def calculate_top_roles(max_roles=5):
#     """
#     """
#     # first calculate the average score of all of the ratings
#     all_avg_score = RoleRating.objects.all().aggregate(average_score=Avg('score'))['average_score']
#     if not all_avg_score:
#         print "No average score, is the database empty?"
#         return False

#     print "Average score of all role ratings is: %0.3f" % all_avg_score

#     roles = Role.objects.all()
#     for role in roles:
#         role_ratings = role.ratings.all()
#         avg_score = role.average_rating
#         if not avg_score:
#             avg_score = 0.0
#         w = len(role_ratings) / float(len(role_ratings) + settings.GALAXY_COMMENTS_THRESHOLD)
#         bayesian_score = (avg_score + avg_score*w + (1-w)*all_avg_score) / 2
#         # Update the top roles list
#         role.bayesian_score = bayesian_score
#         role.save()

#     return True

# @transaction.atomic
# def calculate_top_users():
#     users = User.objects.all()
#     for user in users:
#         avg_score = 0.0
#         num_ratings = 0
#         for role in user.roles.filter(active=True,is_valid=True):
#             for rating in role.ratings.filter(active=True):
#                 avg_score += rating.score
#                 num_ratings += 1
#         if num_ratings > 0.0:
#             avg_score /= float(num_ratings)
#         user.average_score = avg_score
#         user.save()
#     return True

# @transaction.atomic
# def calculate_top_reviewers():
#     users = User.objects.all()
#     for user in users:
#         karma = 0
#         if user.is_active:
#             ratings = user.ratings.filter(active=True, role__active=True)
#             for rating in ratings:
#                 karma += len(rating.up_votes.all()) - len(rating.down_votes.all())
#             karma += 5 * len(ratings)
#             user.karma = karma
#         else:
#             user.karma = 0
#         user.save()
#     return True
