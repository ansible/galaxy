import {
    Injectable
} from '@angular/core';

import {
    HttpClient,
    HttpHeaders
} from '@angular/common/http';

import {
    Observable,
    Subject
} from 'rxjs/Rx';

import {
    CanActivate,
    Router,
    RouterStateSnapshot,
    ActivatedRouteSnapshot
} from '@angular/router';


export interface Me {
    url:            string;
    related:        object;
    summary_fields: object;
    id:             number;
    authenticated:  boolean;
    staff:          boolean;
    username:       string;
    created:        string;
    modified:       string;
    active:         boolean;
}

@Injectable()
export class AuthService implements CanActivate {
    constructor(
        private http:  HttpClient,
        private router: Router
    ) {}

    headers: HttpHeaders = new HttpHeaders().set('Content-Type', 'application/json');
    meCache: Me = null;
    meUrl: string = '/api/v1/me/';
    redirectUrl: string = '/home';

    me(): Observable<Me> {
        if (this.meCache) {
            return new Observable<Me>(
                observer => { return observer.next(this.meCache); }
            );
        }
        return this.http.get<Me>(this.meUrl, {headers: this.headers})
            .map((result) => { this.meCache = result; return result; });
    }

    logout(): Observable<any> {
        this.meCache = null;
        return this.http.post('/api/v1/account/logout', {}, {headers: this.headers})
            .map((result) => {
                this.meCache = null;
                this.redirectUrl = '/home';
                return result;
            });
    }

    canActivate(route: ActivatedRouteSnapshot, state: RouterStateSnapshot): Observable<boolean> {
        this.redirectUrl = state.url;
        if (this.meCache) {
            return new Observable<boolean>(
                observer => {
                    if (!this.meCache.authenticated) {
                        this.router.navigate(['/login', {error: true}]);
                    }
                    observer.next(this.meCache.authenticated);
                }
            );
        }
        return this.http.get<Me>(this.meUrl, {headers: this.headers})
            .map((result) => {
                this.meCache = result;
                if (!result.authenticated) {
                    this.router.navigate(['/login', {error: true}]);
                }
                return result.authenticated;
            });
    }
}
