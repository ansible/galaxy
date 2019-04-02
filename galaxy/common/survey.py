# (c) 2012-2019, Ansible by Red Hat
#
# This file is part of Ansible Galaxy
#
# Ansible Galaxy is free software: you can redistribute it and/or modify
# it under the terms of the Apache License as published by
# the Apache Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# Ansible Galaxy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# Apache License for more details.
#
# You should have received a copy of the Apache License
# along with Galaxy.  If not, see <http://www.apache.org/licenses/>.

SURVEY_FIElDS = (
    'docs',
    'ease_of_use',
    'does_what_it_says',
    'works_as_is',
    'used_in_production',
)


def calculate_survey_score(surveys):
    '''
    :var surveys: queryset container all of the surveys for a collection or a
    repository
    '''
    score = 0

    answer_count = 0
    survey_score = 0.0
    for survey in surveys:
        for k in SURVEY_FIElDS:
            data = getattr(survey, k)
            if data is not None:
                answer_count += 1
                survey_score += (data - 1) / 4

    # Average and convert to 0-5 scale
    score = (survey_score / answer_count) * 5

    return score
