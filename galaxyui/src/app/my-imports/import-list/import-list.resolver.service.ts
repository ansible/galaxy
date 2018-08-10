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
import { PagedResponse }         from '../../resources/paged-response';

@Injectable()
export class ImportListResolver implements Resolve<PagedResponse> {

    constructor(
        private importsService: ImportsService,
        private router: Router,
        private authService: AuthService
    ) {}

    resolve(route: ActivatedRouteSnapshot, state: RouterStateSnapshot): Observable<PagedResponse> {
        let params = '';
        for (const key in route.queryParams) {
            if (route.queryParams.hasOwnProperty(key)) {
                const values = (typeof route.queryParams[key] === 'object') ? route.queryParams[key] : [route.queryParams[key]];
                values.forEach(value => {
                    if (params !== '') {
                        params += '&';
                    }
                    if (key === 'namespace') {
                        params += `repository__provider_namespace__namespace__name__iexact=${value.toLowerCase()}`;
                    } else if (key === 'repository_name') {
                        params += `repository__name__icontains=${value.toLowerCase()}`;
                    } else if (key !== 'selected') {
                        params += `${key}=${value}`;
                    }
                });
            }
        }
        if (!route.queryParams['namespace']) {
            const username = this.authService.meCache.username.toLowerCase();
            params += `repository__provider_namespace__namespace__name__icontains=${username}`;
        }
        return this.importsService.latest(params);
    }
}
