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
import { catchError, map, tap } from 'rxjs/operators';

import { HttpClient, HttpHeaders } from '@angular/common/http';

import { Observable, of } from 'rxjs';
import { PagedResponse } from '../paged-response';
import { Import } from './import';

export class SaveParams {
    github_user: string;
    github_repo: string;
}

const httpOptions = {
    headers: new HttpHeaders({
        'Content-Type': 'application/json',
    }),
};

@Injectable()
export class ImportsService {
    constructor(
        private http: HttpClient,
        private notificationService: NotificationService,
    ) {}

    private url = '/api/v1/imports';

    latest(query?: string): Observable<PagedResponse> {
        let requestUrl = `${this.url}/latest/`;
        if (query) {
            requestUrl += `?${query}`;
        }
        return this.http.get<PagedResponse>(requestUrl).pipe(
            tap(_ => this.log('fetched latest imports')),
            catchError(this.handleError('Latest', {} as PagedResponse)),
        );
    }

    query(params?: any): Observable<Import[]> {
        return this.http
            .get<PagedResponse>(this.url + '/', { params: params })
            .pipe(
                map(response => response.results),
                tap(_ => this.log('fetched imports')),
                catchError(this.handleError('Query', [] as Import[])),
            );
    }

    get(id: number): Observable<Import> {
        return this.http.get<any>(`${this.url}/${id.toString()}/`).pipe(
            tap(_ => this.log('fetched import')),
            catchError(this.handleError('Get', {} as Import)),
        );
    }

    save(params: SaveParams): Observable<Import> {
        let httpResult: Observable<Object>;
        httpResult = this.http.post<Import>(this.url, params, httpOptions);
        return httpResult.pipe(
            tap((newImport: Import) =>
                this.log(`Saved import w/ id=${newImport.id}`),
            ),
            catchError(this.handleError<Import>('Save')),
        );
    }

    private handleError<T>(operation = '', result?: T) {
        return (error: any): Observable<T> => {
            console.error(`${operation} failed, error:`, error);
            this.log(`${operation} provider source error: ${error.message}`);
            this.notificationService.httpError(`${operation} user failed:`, {
                data: error,
            });

            // Let the app keep running by returning an empty result.
            return of(result as T);
        };
    }

    private log(message: string) {
        console.log('ImportService: ' + message);
    }
}
