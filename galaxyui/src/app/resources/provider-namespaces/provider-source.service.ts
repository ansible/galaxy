import { Injectable }           from '@angular/core';
import { NotificationService }  from "patternfly-ng/notification/notification-service/notification.service";
import { catchError, map, tap } from "rxjs/operators";
import { HttpClient }           from "@angular/common/http";
import { Observable }           from "rxjs/Observable";
import { of }                   from "rxjs/observable/of";
import { ProviderNamespace }    from "./provider-namespace";
import { ProviderSource }       from "./provider-source";
import { RepositorySource }     from "../repositories/repository-source";

@Injectable()
export class ProviderSourceService {

    private url = '/api/v1/providers/sources';

    constructor(
        private http: HttpClient,
        private notificationService: NotificationService) {}

    query(): Observable<ProviderSource[]> {
        return this.http.get<ProviderSource[]>(this.url + '/')
            .pipe(
                tap(providerNamespaces => this.log('fetched provider sources')),
                catchError(this.handleError('Query', []))
            );
    }

    getRepoSources(params):  Observable<RepositorySource[]>{
        return this.http.get<RepositorySource[]>(`${this.url}/${params.providerName}/${params.name}/`)
        .pipe(
            tap(providerNamespaces => this.log('fetched source repositories')),
        catchError(this.handleError('Query', []))
        );
    }

    private handleError<T>(operation = '', result?: T) {
        return (error: any): Observable<T> => {
            console.error(`${operation} failed, error:`, error);
            this.log(`${operation} provider source error: ${error.message}`);
            this.notificationService.httpError(`${operation} user failed:`, {data: error});

            // Let the app keep running by returning an empty result.
            return of(result as T);
        };
    }

    private log(message: string) {
        console.log('ProviderSourceService: ' + message);
    }
}

