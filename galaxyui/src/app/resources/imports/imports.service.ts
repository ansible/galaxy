/* (c) 2012-2018, Ansible by Red Hat
 *
 * This file is part of Ansible Galaxy
 *
 * Ansible Galaxy is free software: you can redistribute it and/or modify
 * it under the terms of the Apache License as published by
 * the Apache Software Foundation, either version 2 of the License, or
 * (at your option) any later version.
 *
 * Ansible Galaxy is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * Apache License for more details.
 *
 * You should have received a copy of the Apache License
 * along with Galaxy.  If not, see <http://www.apache.org/licenses/>.
 */

import { Injectable } from '@angular/core';
import { NotificationService } from 'patternfly-ng/notification/notification-service/notification.service';
import { catchError, tap, map } from 'rxjs/operators';

import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';

import { PagedResponse } from '../paged-response';
import { CollectionImport, RepoImport, ImportList } from './import';

import { ServiceBase } from '../base/service-base';

@Injectable()
export class ImportsService extends ServiceBase {
    constructor(http: HttpClient, notificationService: NotificationService) {
        super(http, notificationService);
    }

    collection_url = import_id => `/api/v2/collection-imports/${import_id}/`;
    repo_url = import_id => `/api/v1/imports/${import_id}/`;
    combined_url = namespace_id =>
        /* tslint:disable */
        `/api/internal/ui/namespaces/${namespace_id}/imports/`;

    get_collection_import(id): Observable<CollectionImport> {
        return this.http.get<CollectionImport>(this.collection_url(id)).pipe(
            tap(_ => this.log(`fetched collection import`)),
            catchError(this.handleError('Get', {} as CollectionImport)),
        );
    }

    get_repo_import(id): Observable<RepoImport> {
        return this.http.get<RepoImport>(this.repo_url(id)).pipe(
            tap(_ => this.log(`fetched repository import`)),
            catchError(this.handleError('Get', {} as RepoImport)),
        );
    }

    get_import_list(namespace_id, params?): Observable<PagedResponse> {
        return this.http
            .get<PagedResponse>(this.combined_url(namespace_id), {
                params: params,
            })
            .pipe(
                tap(_ => this.log(`fetched import list`)),
                catchError(this.handleError('Query', {} as PagedResponse)),
            );
    }
}
