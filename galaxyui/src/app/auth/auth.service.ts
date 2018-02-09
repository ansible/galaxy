import { Injectable }          from '@angular/core';

import { HttpClient,
         HttpHeaders }         from '@angular/common/http';

import { Observable,
         Subject }             from 'rxjs/Rx';


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
export class AuthService {
    constructor(
        private http:  HttpClient,
    ) {}

    me(): Observable<Me> {
        let headers = new HttpHeaders().set('Content-Type', 'application/json');
        return this.http.get<Me>('/api/v1/me/', {headers: headers});
    }
}
