import { Component, EventEmitter, Input, OnInit, Output } from '@angular/core';

import { Router } from '@angular/router';

import { CardConfig } from 'patternfly-ng/card/basic-card/card-config';

import { Survey } from '../../../resources/survey/survey';
import { SurveyService } from '../../../resources/survey/survey.service';

import { AuthService } from '../../../auth/auth.service';

import { CommunityDetails, DetailMessage } from './types';

@Component({
    selector: 'card-community-survey',
    templateUrl: './community-survey.component.html',
    styleUrls: ['./community-survey.component.less'],
})
export class CardCommunitySurveyComponent implements OnInit {
    // Used to track which component is being loaded
    componentName = 'CardCommunitySurveyComponent';

    constructor(
        private surveyService: SurveyService,
        private authService: AuthService,
        private router: Router,
    ) {}

    config: CardConfig;
    communitySurveys: Survey[];
    mySurvey: Survey;
    myUserId: number;
    surveyKeys: string[];
    surveyConfig: any;
    categoryAverages = {};
    numberOfSurveys: number;
    qualityBarText: string;
    communityBarText: string;

    hideSurvey = false;
    loading = true;
    waitingForId = false;

    @Input()
    contentId: number;

    @Input()
    communityScore: number;

    @Input()
    qualityScore: number;

    @Input()
    showCommunityDetails = false;

    @Input()
    showQualityDetails = false;

    @Input()
    lastScored: string;

    @Output()
    emitDetails = new EventEmitter<DetailMessage>();

    ngOnInit() {
        this.config = {
            titleBorder: true,
            topBorder: true,
        } as CardConfig;

        if (this.communityScore === null) {
            this.communityScore = 0;
            this.communityBarText = 'No Surveys';
        } else {
            this.setCommunityScore(this.communityScore);
        }

        if (this.qualityScore === null) {
            this.qualityScore = 0;
            this.qualityBarText = 'No Score Available';
        } else {
            this.setQualityScore(this.qualityScore);
        }

        // surveyKeys are used to match the question's text to the corresponding
        // database/api field

        const likehartType = [
            { symbol: '-', value: 1 },
            { symbol: '', value: 2 },
            { symbol: '', value: 3 },
            { symbol: '', value: 4 },
            { symbol: '+', value: 5 },
        ];
        const boolType = [{ symbol: 'Y', value: 5 }, { symbol: 'N', value: 1 }];

        this.surveyConfig = {
            // These keys NEED to match up with the fields recieved from the API
            docs: {
                question: 'Quality of docs?',
                type: likehartType,
            },
            ease_of_use: {
                question: 'Ease of use?',
                type: likehartType,
            },
            does_what_it_says: {
                question: 'Does what it promises?',
                type: boolType,
            },
            works_as_is: {
                question: 'Works without change?',
                type: boolType,
            },
            used_in_production: {
                question: 'Used in production?',
                type: boolType,
            },
        };

        this.surveyKeys = Object.keys(this.surveyConfig);

        this.authService.me().subscribe(me => {
            this.myUserId = me.id;

            // The user id has to be set before surveys are loaded from the API
            this.surveyService
                .query({ repository: this.contentId, page_size: 1000 })
                .subscribe(surveys => {
                    this.communitySurveys = surveys;
                    this.numberOfSurveys = this.communitySurveys.length;
                    this.loadMySurvey();
                    this.loading = false;
                });
        });
    }

    // Loads the list of survey that belong to this repo
    private loadMySurvey() {
        this.mySurvey = this.communitySurveys.find(
            x => x.user === this.myUserId,
        );

        if (!this.mySurvey) {
            this.mySurvey = {
                user: this.myUserId,
                repository: this.contentId,
            } as Survey;

            for (const key of this.surveyKeys) {
                this.mySurvey[key] = null;
            }

            this.communitySurveys.push(this.mySurvey);
        }
    }

    // Averages the scores of all the surveys.
    private calculateCategoryScores() {
        for (const key of this.surveyKeys) {
            this.categoryAverages[key] = {};
            this.categoryAverages[key].count = 0;
            this.categoryAverages[key].value = 0;
        }

        if (this.communitySurveys.length === 0) {
            return;
        }

        for (const survey of this.communitySurveys) {
            for (const key of this.surveyKeys) {
                // Unanswered questions should be skipped rather than counted as 0
                if (survey[key] !== undefined && survey[key] !== null) {
                    // Calculate the category averages for the details view:
                    this.categoryAverages[key].count += 1;
                    this.categoryAverages[key].value += (survey[key] - 1) / 4;
                }
            }
        }

        this.normalizeCategoryScores();
    }

    private normalizeCategoryScores() {
        for (const key of this.surveyKeys) {
            if (this.categoryAverages[key].count === 0) {
                continue;
            }

            let value = this.categoryAverages[key].value;
            const count = this.categoryAverages[key].count;

            value = value / count;
            value = value * 5;
            value = Math.round(value * 10) / 10;

            this.categoryAverages[key].value = value;
        }
    }

    private setCommunityScore(score: number) {
        this.communityScore = Math.round(score * 10) / 10;
    }

    private setQualityScore(score: number) {
        this.qualityScore = Math.round(score * 10) / 10;
    }

    submitRating(questionKey: string, rating: number) {
        // Prevent non users from submitting surveys.
        if (!this.myUserId) {
            return;
        }

        this.mySurvey[questionKey] = rating;

        if (this.waitingForId) {
            return;
        }

        // If the survey doesn't have an ID, that means it's not in the database.
        // If this is the case, we can create a new survey, but not update an
        // existing one. This causes problems when someone submits a new survey
        // because all the requests after the first one need to have an ID associated
        // with them, but the ID isn't available until after the initial POST request
        // completes
        // To solve this problem, set the waitingForId flag to true, and if a new
        // question is answered while waiting for the ID to come in, cache it
        // and send it after the ID is available.
        if (!this.mySurvey.id) {
            this.waitingForId = true;
            this.numberOfSurveys += 1;
        }

        this.surveyService.save(this.mySurvey).subscribe(dbSurvey => {
            this.mySurvey.id = dbSurvey.id;
            this.communityBarText = null;
            this.setCommunityScore(
                dbSurvey.summary_fields.repository.community_score,
            );

            // Submit the cached survey data.
            if (this.waitingForId) {
                this.waitingForId = false;
                let submitCached = false;

                // Submit cached changes if they are different from what's
                // in the DB.
                for (const key of this.surveyKeys) {
                    if (this.mySurvey[key] !== dbSurvey[key]) {
                        submitCached = true;
                        break;
                    }
                }

                if (submitCached) {
                    this.surveyService.save(this.mySurvey).subscribe();
                }
            }
        });

        this.calculateCategoryScores();
        this.updateCommunityDetails();
    }

    // Calculates the width of the green rating bar.
    getWidthPercentage(rating: number): string {
        return (rating / 5) * 100 + '%';
    }

    // Sets the correct color for buttons that have been clicked or are
    // being hovered over
    getButtonClass(buttonVal: number, answerVal: number) {
        if (!this.myUserId) {
            return '';
        }

        let divClass = '';
        switch (buttonVal) {
            case 1: {
                divClass += 'input-low';
                break;
            }
            case 5: {
                divClass += 'input-high';
                break;
            }
            default: {
                divClass += 'input-med';
                break;
            }
        }

        if (buttonVal === answerVal) {
            switch (buttonVal) {
                case 1: {
                    divClass += ' input-clicked-low';
                    break;
                }
                case 5: {
                    divClass += ' input-clicked-high';
                    break;
                }
                default: {
                    divClass += ' input-clicked-med';
                    break;
                }
            }
        }
        return divClass;
    }

    showWall(hasEntered: boolean) {
        if (this.myUserId) {
            return false;
        }
        this.hideSurvey = hasEntered;
    }

    updateCommunityDetails() {
        const data = [] as CommunityDetails[];

        for (const key of this.surveyKeys) {
            data.push({
                question: this.surveyConfig[key].question,
                value: this.categoryAverages[key].value,
                count: this.categoryAverages[key].count,
            } as CommunityDetails);
        }

        const event = {
            visible: this.showCommunityDetails,
            type: 'community',
            payload: data,
        } as DetailMessage;

        this.emitDetails.emit(event);
    }

    toggleDetails(key: string) {
        this[key] = !this[key];

        if (key === 'showCommunityDetails') {
            if (this.categoryAverages !== {}) {
                this.calculateCategoryScores();
            }
            this.updateCommunityDetails();
        } else if (key === 'showQualityDetails') {
            this.emitDetails.emit({
                visible: this[key],
                type: 'quality',
                payload: '',
            } as DetailMessage);
        }
    }
}
