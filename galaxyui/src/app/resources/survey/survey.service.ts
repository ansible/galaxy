import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';

import { NotificationService } from 'patternfly-ng/notification/notification-service/notification.service';
import { Survey } from './survey';

import { GenericQuerySave } from '../base/generic-query-save';

@Injectable()
export class SurveyService extends GenericQuerySave<Survey> {
    constructor(http: HttpClient, notificationService: NotificationService) {
        super(
            http,
            notificationService,
            '/api/v1/community_surveys/',
            'survey',
        );
    }
}
