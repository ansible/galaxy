import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';

import { NotificationService } from 'patternfly-ng';
import { PaginatedRepoCollection, RepoOrCollectionResponse } from './combined';

import { ServiceBase } from '../base/service-base';

import { Observable } from 'rxjs';
import { catchError, tap } from 'rxjs/operators';

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
export class RepoOrCollectionService extends ServiceBase {
    constructor(http: HttpClient, notificationService: NotificationService) {
        super(
            http,
            notificationService,
            '/api/internal/ui/repo-or-collection-detail/',
            'content-format',
        );
    }

    query(namespace, name): Observable<RepoOrCollectionResponse> {
        return this.http.get<RepoOrCollectionResponse>(this.url, {
            params: { namespace: namespace, name: name },
        });
    }
}
