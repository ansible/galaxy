import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';

import { NotificationService } from 'patternfly-ng';
import { PaginatedRepoCollection } from './combined';
import { ContentFormat } from '../../enums/format';

import { ServiceBase } from '../base/service-base';

import { Observable } from 'rxjs';
import { catchError, tap, map } from 'rxjs/operators';

@Injectable()
export class RepoCollectionListService extends ServiceBase {
    constructor(http: HttpClient, notificationService: NotificationService) {
        super(
            http,
            notificationService,
            '/api/internal/ui/repos-and-collections',
            'collection',
        );
    }

    query(params): Observable<PaginatedRepoCollection> {
        return this.http
            .get<PaginatedRepoCollection>(this.url, { params: params })
            .pipe(
                tap(_ => this.log('fetched collection and repository list')),
                catchError(
                    this.handleError('Get', {} as PaginatedRepoCollection),
                ),
            );
    }
}

@Injectable()
export class ContentFormatService extends ServiceBase {
    constructor(http: HttpClient, notificationService: NotificationService) {
        super(
            http,
            notificationService,
            '/api/internal/ui/type-checker',
            'content-format',
        );
    }

    query(namespace, name): Observable<ContentFormat> {
        return this.http
            .get<ContentFormat>(this.url, {
                params: { namespace: namespace, name: name },
            })
            .pipe(
                tap(_ => this.log('fetched object type')),
                map(result => result['type']),
                catchError(this.handleError('Get', {} as ContentFormat)),
            );
    }
}
