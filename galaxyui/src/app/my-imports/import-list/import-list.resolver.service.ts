import {
    Injectable
} from '@angular/core';

import {
    ActivatedRouteSnapshot,
    Resolve,
    Router,
    RouterStateSnapshot
} from '@angular/router';

import { Observable }            from 'rxjs/Observable';
import { ImportsService }        from '../../resources/imports/imports.service';
import { ImportLatest }          from '../../resources/imports/import-latest';
import { AuthService }           from '../../auth/auth.service';
import * as moment               from 'moment';

@Injectable()
export class ImportListResolver implements Resolve<ImportLatest[]> {

    constructor(
        private importsService: ImportsService,
        private router: Router,
        private authService: AuthService
    ){}

    resolve(route: ActivatedRouteSnapshot, state: RouterStateSnapshot): Observable<ImportLatest[]> {
        console.log(route.queryParams);
        let query = null;
        if (route.queryParams) {
            let namespace = route.queryParams['namespace'];
            let repositoryName = route.queryParams['repository_name'];
            query = '';
            if (namespace) {
                query += (query == '') ? '' : '&';
                query += `repository__provider_namespace__namespace__name=${namespace}`;
            }
            if (repositoryName) {
                query += (query == '') ? '' : '&';
                query += `repository__name=${repositoryName}`;
            }
        }
        return this.importsService.latest(query);
    }
}
