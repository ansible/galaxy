import { Injectable }           from '@angular/core';
import { catchError, map, tap } from 'rxjs/operators';
import { NotificationService }  from 'patternfly-ng/notification/notification-service/notification.service';
import { Observable }           from 'rxjs/Observable';
import { HttpClient }           from '@angular/common/http';
import { PagedResponse }        from '../paged-response';
import { User }                 from './user';
import { of }                   from 'rxjs/observable/of';


@Injectable()
export class UserService {

    private url = '/api/v1/users/';

    constructor(private http: HttpClient,
                private notificationService: NotificationService) {
    }

    query(params?: any): Observable<User[]> {
        let userUrl = this.url;
        let userParams = null;
        if (params) {
            if (typeof params === 'string') {
                userUrl += `?${params}`;
            } else {
                userParams = params;
            }
        }
        return this.http.get<PagedResponse>(userUrl, {'params':  userParams})
            .pipe(
                map(response => response.results as User[]),
                tap(_ => this.log('fetched users')),
                catchError(this.handleError('Query', []))
            );
    }

    private handleError<T>(operation = '', result?: T) {
        return (error: any): Observable<T> => {
            console.error(`${operation} failed, error:`, error);
            this.log(`${operation} user error: ${error.message}`);
            this.notificationService.httpError(`${operation} user failed:`, {data: error});

            // Let the app keep running by returning an empty result.
            return of(result as T);
        };
    }

    private log(message: string) {
        console.log('UserService: ' + message);
    }
}
