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
        return this.importsService.latest().map(
            results => {
                results.forEach(item => {
                    item.finished = moment(item.modified).fromNow();
                    item.state = item.state.charAt(0).toUpperCase() + item.state.slice(1).toLowerCase();
                });
                return results;
            }
        );
    }
}
