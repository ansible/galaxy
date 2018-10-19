import { Injectable } from '@angular/core';

import { HttpClient, HttpHeaders } from '@angular/common/http';

import { Observable, of } from 'rxjs';

import { map } from 'rxjs/operators';

import {
    ActivatedRouteSnapshot,
    CanActivate,
    Router,
    RouterStateSnapshot,
} from '@angular/router';

export interface IMe {
    url: string;
    related: object;
    summary_fields: object;
    id: number;
    authenticated: boolean;
    staff: boolean;
    username: string;
    created: string;
    modified: string;
    active: boolean;
}

@Injectable()
export class AuthService implements CanActivate {
    constructor(private http: HttpClient, private router: Router) {}

    headers: HttpHeaders = new HttpHeaders().set(
        'Content-Type',
        'application/json',
    );
    meCache: IMe = null;
    meUrl = '/api/v1/me/';
    redirectUrl = '/home';

    me(): Observable<IMe> {
        if (this.meCache) {
            return of(this.meCache);
        }
        return this.http.get<IMe>(this.meUrl, { headers: this.headers }).pipe(
            map(result => {
                this.meCache = result;
                return result;
            }),
        );
    }

    logout(): Observable<any> {
        this.meCache = null;
        return this.http
            .post('/api/v1/account/logout', {}, { headers: this.headers })
            .pipe(
                map(result => {
                    this.meCache = null;
                    this.redirectUrl = '/home';
                    return result;
                }),
            );
    }

    checkPermissions(route: ActivatedRouteSnapshot): boolean {
        let result = true;
        if (!this.meCache.authenticated) {
            // User is not authenticated
            this.router.navigate(['/login', { error: true }]);
            result = false;
        }
        if (route['data'] && route['data']['expectedRole']) {
            if (
                route['data']['expectedRole'] === 'isStaff' &&
                !this.meCache.staff
            ) {
                // User does not have is_staff=True
                this.router.navigate(['/access-denied', { error: true }]);
                result = false;
            }
        }
        return result;
    }

    canActivate(
        route: ActivatedRouteSnapshot,
        state: RouterStateSnapshot,
    ): Observable<boolean> {
        this.redirectUrl = state.url;
        if (this.meCache) {
            return Observable.create(observer => {
                observer.next(this.checkPermissions(route));
                observer.complete();
            });
        }
        return this.http.get<IMe>(this.meUrl, { headers: this.headers }).pipe(
            map(result => {
                this.meCache = result;
                return this.checkPermissions(route);
            }),
        );
    }
}
